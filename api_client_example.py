"""
IndexTTS API 客户端示例

展示如何调用IndexTTS API服务
"""

import requests
import json

# API服务地址
API_BASE_URL = "http://localhost:8000"

def check_health():
    """检查API服务健康状态"""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✓ API服务运行正常")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            return True
        else:
            print("✗ API服务异常")
            return False
    except Exception as e:
        print(f"✗ 无法连接到API服务: {e}")
        return False

def get_api_info():
    """获取API信息"""
    try:
        response = requests.get(f"{API_BASE_URL}/info")
        if response.status_code == 200:
            print("\nAPI信息:")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"获取API信息失败: {e}")

def text_to_speech_stream(text, output_file="output.wav"):
    """
    调用TTS API，将文本转换为语音并保存为文件
    
    Args:
        text: 要转换的文本
        output_file: 输出音频文件路径
    """
    try:
        # 准备请求数据
        data = {
            "text": text,
            "max_text_tokens_per_segment": 120,
            "temperature": 0.8,
            "top_p": 0.8,
            "top_k": 30
        }
        
        print(f"\n正在生成语音: {text[:50]}...")
        
        # 发送POST请求
        response = requests.post(
            f"{API_BASE_URL}/tts",
            json=data,
            stream=True
        )
        
        if response.status_code == 200:
            # 保存音频文件
            with open(output_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print(f"✓ 语音生成成功，已保存到: {output_file}")
            return True
        else:
            print(f"✗ 生成失败: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False

def text_to_speech_json(text):
    """
    调用TTS API（JSON模式），返回音频文件路径
    
    Args:
        text: 要转换的文本
    """
    try:
        # 准备请求数据
        data = {
            "text": text,
            "max_text_tokens_per_segment": 120
        }
        
        print(f"\n正在生成语音(JSON模式): {text[:50]}...")
        
        # 发送POST请求
        response = requests.post(
            f"{API_BASE_URL}/tts_json",
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 语音生成成功")
            print(f"  音频路径: {result['audio_path']}")
            return result
        else:
            print(f"✗ 生成失败: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return None

def batch_generate(texts, output_dir="outputs"):
    """
    批量生成语音
    
    Args:
        texts: 文本列表
        output_dir: 输出目录
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n开始批量生成 {len(texts)} 条语音...")
    
    success_count = 0
    for i, text in enumerate(texts):
        output_file = os.path.join(output_dir, f"batch_{i+1}.wav")
        if text_to_speech_stream(text, output_file):
            success_count += 1
    
    print(f"\n批量生成完成: {success_count}/{len(texts)} 成功")

if __name__ == "__main__":
    print("=" * 60)
    print("IndexTTS API 客户端示例")
    print("=" * 60)
    
    # 1. 检查服务健康状态
    if not check_health():
        print("\n请先启动API服务: python api.py")
        exit(1)
    
    # 2. 获取API信息
    get_api_info()
    
    # 3. 单个文本转语音（流模式）
    print("\n" + "=" * 60)
    print("示例1: 单个文本转语音（流模式）")
    print("=" * 60)
    text_to_speech_stream(
        "你好，欢迎使用IndexTTS语音合成服务。这是一个测试示例。",
        "example_output1.wav"
    )
    
    # 4. 单个文本转语音（JSON模式）
    print("\n" + "=" * 60)
    print("示例2: 单个文本转语音（JSON模式）")
    print("=" * 60)
    text_to_speech_json("这是第二个测试示例，使用JSON模式返回结果。")
    
    # 5. 批量生成（可选，注释掉避免生成太多文件）
    # print("\n" + "=" * 60)
    # print("示例3: 批量生成")
    # print("=" * 60)
    # texts = [
    #     "这是第一条测试文本。",
    #     "这是第二条测试文本。",
    #     "这是第三条测试文本。"
    # ]
    # batch_generate(texts, "batch_outputs")
    
    print("\n" + "=" * 60)
    print("示例运行完成！")
    print("=" * 60)

