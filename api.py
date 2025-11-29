import os
import sys
import warnings
import io
import time
from pathlib import Path

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# 添加当前目录到sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, "indextts"))

from indextts.infer_v2 import IndexTTS2

# 创建FastAPI应用
app = FastAPI(title="IndexTTS API", description="文本转语音API服务", version="1.0.0")

# 配置CORS - 允许浏览器访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)

# 全局变量存储模型实例
tts_model = None
reference_audio_path = None
available_audio_files = []  # 存储所有可用的参考音频

# 请求模型
class TTSRequest(BaseModel):
    text: str
    reference_audio: str = None  # 可选：指定参考音频文件名
    max_text_tokens_per_segment: int = 120
    # 可选的生成参数
    do_sample: bool = True
    top_p: float = 0.8
    top_k: int = 30
    temperature: float = 0.8
    length_penalty: float = 0.0
    num_beams: int = 3
    repetition_penalty: float = 10.0
    max_mel_tokens: int = 1500

    class Config:
        schema_extra = {
            "example": {
                "text": "你好，欢迎使用IndexTTS语音合成服务。",
                "reference_audio": "我的音频.m4a",
                "max_text_tokens_per_segment": 120
            }
        }

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化模型"""
    global tts_model, reference_audio_path, available_audio_files
    
    print("正在初始化IndexTTS模型...")
    
    # 模型配置
    model_dir = "./checkpoints"
    cfg_path = os.path.join(model_dir, "config.yaml")
    
    # 检查模型文件是否存在
    if not os.path.exists(model_dir):
        raise RuntimeError(f"模型目录不存在: {model_dir}")
    
    if not os.path.exists(cfg_path):
        raise RuntimeError(f"配置文件不存在: {cfg_path}")
    
    # 检查参考音频目录
    sample_audio_dir = "./sampleAudios"
    if not os.path.exists(sample_audio_dir):
        raise RuntimeError(f"参考音频目录不存在: {sample_audio_dir}")
    
    # 查找参考音频文件
    audio_files = list(Path(sample_audio_dir).glob("*.m4a")) + \
                  list(Path(sample_audio_dir).glob("*.wav")) + \
                  list(Path(sample_audio_dir).glob("*.mp3"))
    
    if not audio_files:
        raise RuntimeError(f"在 {sample_audio_dir} 目录下未找到音频文件")
    
    # 存储所有可用的音频文件
    available_audio_files = [str(f) for f in audio_files]
    
    # 使用第一个找到的音频文件作为默认参考
    reference_audio_path = available_audio_files[0]
    print(f"默认参考音频: {reference_audio_path}")
    print(f"可用音频列表: {[os.path.basename(f) for f in available_audio_files]}")
    
    # 初始化模型
    try:
        tts_model = IndexTTS2(
            model_dir=model_dir,
            cfg_path=cfg_path,
            use_fp16=False,  # 根据需要调整
            use_deepspeed=False,
            use_cuda_kernel=False
        )
        print("IndexTTS模型初始化完成！")
    except Exception as e:
        raise RuntimeError(f"模型初始化失败: {str(e)}")

@app.get("/")
async def root():
    """API根路径"""
    return {
        "message": "IndexTTS API服务正在运行",
        "version": "1.0.0",
        "endpoints": {
            "tts": "/tts (POST)",
            "health": "/health (GET)",
            "info": "/info (GET)"
        }
    }

@app.get("/health")
async def health_check():
    """健康检查接口"""
    if tts_model is None:
        raise HTTPException(status_code=503, detail="模型未初始化")
    
    return {
        "status": "healthy",
        "model_loaded": tts_model is not None,
        "reference_audio": reference_audio_path
    }

@app.get("/info")
async def get_info():
    """获取API信息"""
    if tts_model is None:
        raise HTTPException(status_code=503, detail="模型未初始化")
    
    return {
        "model_version": tts_model.model_version if hasattr(tts_model, 'model_version') else "unknown",
        "device": str(tts_model.device),
        "current_reference_audio": reference_audio_path,
        "available_reference_audios": [os.path.basename(f) for f in available_audio_files],
        "use_fp16": tts_model.use_fp16
    }

@app.get("/audios")
async def list_reference_audios():
    """获取所有可用的参考音频列表"""
    if tts_model is None:
        raise HTTPException(status_code=503, detail="模型未初始化")
    
    audios = []
    for audio_path in available_audio_files:
        filename = os.path.basename(audio_path)
        file_size = os.path.getsize(audio_path) / 1024  # KB
        is_current = (audio_path == reference_audio_path)
        
        audios.append({
            "filename": filename,
            "path": audio_path,
            "size_kb": round(file_size, 2),
            "is_current": is_current
        })
    
    return {
        "total": len(audios),
        "audios": audios
    }

@app.post("/audios/switch")
async def switch_reference_audio(filename: str):
    """切换当前使用的参考音频"""
    global reference_audio_path
    
    if tts_model is None:
        raise HTTPException(status_code=503, detail="模型未初始化")
    
    # 查找指定的音频文件
    target_path = None
    for audio_path in available_audio_files:
        if os.path.basename(audio_path) == filename:
            target_path = audio_path
            break
    
    if target_path is None:
        raise HTTPException(
            status_code=404, 
            detail=f"音频文件未找到: {filename}，可用文件: {[os.path.basename(f) for f in available_audio_files]}"
        )
    
    reference_audio_path = target_path
    print(f"切换参考音频: {reference_audio_path}")
    
    return {
        "success": True,
        "current_reference_audio": reference_audio_path,
        "message": f"已切换到: {filename}"
    }

@app.post("/tts")
async def text_to_speech(request: TTSRequest):
    """
    文本转语音接口
    
    接收文本，返回音频流（WAV格式）
    """
    if tts_model is None:
        raise HTTPException(status_code=503, detail="模型未初始化")
    
    if not request.text or len(request.text.strip()) == 0:
        raise HTTPException(status_code=400, detail="文本不能为空")
    
    # 确定使用哪个参考音频
    audio_to_use = reference_audio_path
    if request.reference_audio:
        # 如果指定了参考音频，查找对应的文件
        found = False
        for audio_path in available_audio_files:
            if os.path.basename(audio_path) == request.reference_audio:
                audio_to_use = audio_path
                found = True
                break
        
        if not found:
            raise HTTPException(
                status_code=400,
                detail=f"指定的参考音频不存在: {request.reference_audio}"
            )
    
    try:
        # 生成临时文件路径
        output_path = os.path.join("outputs", f"temp_{int(time.time())}.wav")
        os.makedirs("outputs", exist_ok=True)
        
        print(f"正在生成语音: {request.text[:50]}...")
        
        # 准备生成参数
        kwargs = {
            "do_sample": request.do_sample,
            "top_p": request.top_p,
            "top_k": request.top_k,
            "temperature": request.temperature,
            "length_penalty": request.length_penalty,
            "num_beams": request.num_beams,
            "repetition_penalty": request.repetition_penalty,
            "max_mel_tokens": request.max_mel_tokens,
        }
        
        # 调用模型生成音频
        result = tts_model.infer(
            spk_audio_prompt=audio_to_use,
            text=request.text,
            output_path=output_path,
            emo_audio_prompt=None,
            emo_alpha=0.65,
            emo_vector=None,
            use_emo_text=False,
            emo_text=None,
            use_random=False,
            verbose=False,
            max_text_tokens_per_segment=request.max_text_tokens_per_segment,
            **kwargs
        )
        
        # 读取生成的音频文件
        if not os.path.exists(output_path):
            raise HTTPException(status_code=500, detail="音频生成失败")
        
        # 读取音频文件到内存
        with open(output_path, "rb") as f:
            audio_data = f.read()
        
        # 删除临时文件
        try:
            os.remove(output_path)
        except:
            pass
        
        # 返回音频流
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/wav",
            headers={
                "Content-Disposition": f"attachment; filename=speech.wav"
            }
        )
        
    except Exception as e:
        print(f"生成语音时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成语音失败: {str(e)}")

@app.post("/tts_json")
async def text_to_speech_json(request: TTSRequest):
    """
    文本转语音接口（返回JSON）
    
    接收文本，返回包含音频文件路径的JSON
    """
    if tts_model is None:
        raise HTTPException(status_code=503, detail="模型未初始化")
    
    if not request.text or len(request.text.strip()) == 0:
        raise HTTPException(status_code=400, detail="文本不能为空")
    
    # 确定使用哪个参考音频
    audio_to_use = reference_audio_path
    if request.reference_audio:
        found = False
        for audio_path in available_audio_files:
            if os.path.basename(audio_path) == request.reference_audio:
                audio_to_use = audio_path
                found = True
                break
        
        if not found:
            raise HTTPException(
                status_code=400,
                detail=f"指定的参考音频不存在: {request.reference_audio}"
            )
    
    try:
        # 生成文件路径
        output_path = os.path.join("outputs", f"spk_{int(time.time())}.wav")
        os.makedirs("outputs", exist_ok=True)
        
        print(f"正在生成语音: {request.text[:50]}...")
        
        # 准备生成参数
        kwargs = {
            "do_sample": request.do_sample,
            "top_p": request.top_p,
            "top_k": request.top_k,
            "temperature": request.temperature,
            "length_penalty": request.length_penalty,
            "num_beams": request.num_beams,
            "repetition_penalty": request.repetition_penalty,
            "max_mel_tokens": request.max_mel_tokens,
        }
        
        # 调用模型生成音频
        result = tts_model.infer(
            spk_audio_prompt=reference_audio_path,
            text=request.text,
            output_path=output_path,
            emo_audio_prompt=None,
            emo_alpha=0.65,
            emo_vector=None,
            use_emo_text=False,
            emo_text=None,
            use_random=False,
            verbose=False,
            max_text_tokens_per_segment=request.max_text_tokens_per_segment,
            **kwargs
        )
        
        # 检查文件是否生成成功
        if not os.path.exists(output_path):
            raise HTTPException(status_code=500, detail="音频生成失败")
        
        # 返回文件路径
        return JSONResponse({
            "success": True,
            "audio_path": output_path,
            "text": request.text
        })
        
    except Exception as e:
        print(f"生成语音时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成语音失败: {str(e)}")

if __name__ == "__main__":
    # 运行API服务
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )

