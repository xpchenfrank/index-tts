# IndexTTS API 使用说明

这是一个为 IndexTTS 项目封装的 REST API 服务，可以让其他项目方便地调用文本转语音功能。

## 功能特点

- 🚀 简单易用的 REST API 接口
- 🎯 自动使用指定的参考音频
- 📦 支持音频流和文件路径两种返回方式
- 🔧 可自定义生成参数
- 💪 支持批量处理

## 环境要求

- Python 3.8+
- 已配置好的 IndexTTS 环境
- FastAPI 和 Uvicorn

## 安装依赖

```bash
pip install fastapi uvicorn requests
```

## 快速开始

### 1. 启动 API 服务

```bash
python api.py
```

服务将在 `http://localhost:8000` 启动。

启动后可以访问以下地址查看 API 文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 2. 测试 API

运行客户端示例：

```bash
python api_client_example.py
```

## API 接口说明

### 1. 根路径 - GET `/`

获取 API 基本信息。

**响应示例：**
```json
{
  "message": "IndexTTS API服务正在运行",
  "version": "1.0.0",
  "endpoints": {
    "tts": "/tts (POST)",
    "health": "/health (GET)",
    "info": "/info (GET)"
  }
}
```

### 2. 健康检查 - GET `/health`

检查 API 服务状态。

**响应示例：**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "reference_audio": "./sampleAudios/我的音频.m4a"
}
```

### 3. 获取信息 - GET `/info`

获取模型和配置信息。

**响应示例：**
```json
{
  "model_version": "2.0",
  "device": "cuda:0",
  "reference_audio": "./sampleAudios/我的音频.m4a",
  "use_fp16": false
}
```

### 4. 文本转语音（流模式） - POST `/tts`

将文本转换为语音，返回音频文件流。

**请求参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| text | string | 是 | - | 要转换的文本 |
| max_text_tokens_per_segment | int | 否 | 120 | 分句最大Token数 |
| do_sample | bool | 否 | true | 是否进行采样 |
| top_p | float | 否 | 0.8 | Top-p 采样参数 |
| top_k | int | 否 | 30 | Top-k 采样参数 |
| temperature | float | 否 | 0.8 | 温度参数 |
| length_penalty | float | 否 | 0.0 | 长度惩罚 |
| num_beams | int | 否 | 3 | Beam search 数量 |
| repetition_penalty | float | 否 | 10.0 | 重复惩罚 |
| max_mel_tokens | int | 否 | 1500 | 最大 Mel Token 数 |

**请求示例：**
```json
{
  "text": "你好，欢迎使用IndexTTS语音合成服务。",
  "max_text_tokens_per_segment": 120,
  "temperature": 0.8
}
```

**响应：**
- Content-Type: `audio/wav`
- 返回 WAV 格式的音频流

**Python 调用示例：**
```python
import requests

response = requests.post(
    "http://localhost:8000/tts",
    json={"text": "你好，这是测试文本。"}
)

with open("output.wav", "wb") as f:
    f.write(response.content)
```

**cURL 调用示例：**
```bash
curl -X POST "http://localhost:8000/tts" \
  -H "Content-Type: application/json" \
  -d '{"text":"你好，这是测试文本。"}' \
  --output output.wav
```

### 5. 文本转语音（JSON模式） - POST `/tts_json`

将文本转换为语音，返回音频文件路径的 JSON。

**请求参数：** 与 `/tts` 相同

**响应示例：**
```json
{
  "success": true,
  "audio_path": "outputs/spk_1234567890.wav",
  "text": "你好，欢迎使用IndexTTS语音合成服务。"
}
```

**Python 调用示例：**
```python
import requests

response = requests.post(
    "http://localhost:8000/tts_json",
    json={"text": "你好，这是测试文本。"}
)

result = response.json()
print(f"音频文件保存在: {result['audio_path']}")
```

## 配置说明

### 参考音频配置

API 会自动使用 `sampleAudios` 目录下的音频文件作为参考音频（音色来源）。

支持的音频格式：
- `.wav`
- `.mp3`
- `.m4a`

如果目录下有多个音频文件，会使用第一个找到的文件。

### 自定义参考音频

如果需要使用不同的参考音频，可以：

1. 将音频文件放入 `sampleAudios` 目录
2. 重启 API 服务

或者修改 `api.py` 中的 `reference_audio_path` 变量指向特定文件。

## 性能优化建议

1. **使用 GPU 加速**：在有 GPU 的环境下，模型会自动使用 CUDA 加速
2. **启用 FP16**：修改 `api.py` 中的 `use_fp16=True` 可以提升推理速度
3. **调整分句参数**：`max_text_tokens_per_segment` 参数影响生成速度和质量的平衡
4. **批量处理**：对于多个文本，建议复用同一个 API 连接

## 集成到其他项目

### Python 项目集成

```python
import requests

def generate_speech(text: str, output_file: str = "output.wav"):
    """调用 IndexTTS API 生成语音"""
    response = requests.post(
        "http://localhost:8000/tts",
        json={"text": text},
        timeout=60
    )
    
    if response.status_code == 200:
        with open(output_file, "wb") as f:
            f.write(response.content)
        return True
    else:
        print(f"生成失败: {response.text}")
        return False

# 使用示例
generate_speech("你好，世界！", "hello.wav")
```

### Node.js 项目集成

```javascript
const axios = require('axios');
const fs = require('fs');

async function generateSpeech(text, outputFile = 'output.wav') {
    try {
        const response = await axios.post('http://localhost:8000/tts', 
            { text: text },
            { responseType: 'arraybuffer' }
        );
        
        fs.writeFileSync(outputFile, response.data);
        console.log('语音生成成功:', outputFile);
        return true;
    } catch (error) {
        console.error('生成失败:', error.message);
        return false;
    }
}

// 使用示例
generateSpeech('你好，世界！', 'hello.wav');
```

### Java 项目集成

```java
import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;

public class TTSClient {
    public static void generateSpeech(String text, String outputFile) throws IOException {
        URL url = new URL("http://localhost:8000/tts");
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("POST");
        conn.setRequestProperty("Content-Type", "application/json");
        conn.setDoOutput(true);
        
        String jsonInput = String.format("{\"text\": \"%s\"}", text);
        
        try (OutputStream os = conn.getOutputStream()) {
            byte[] input = jsonInput.getBytes("utf-8");
            os.write(input, 0, input.length);
        }
        
        if (conn.getResponseCode() == 200) {
            try (InputStream is = conn.getInputStream();
                 FileOutputStream fos = new FileOutputStream(outputFile)) {
                byte[] buffer = new byte[8192];
                int bytesRead;
                while ((bytesRead = is.read(buffer)) != -1) {
                    fos.write(buffer, 0, bytesRead);
                }
            }
            System.out.println("语音生成成功: " + outputFile);
        }
    }
}
```

## 部署建议

### 开发环境

```bash
python api.py
```

### 生产环境

使用 Gunicorn 或其他 WSGI 服务器：

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动服务（4个工作进程）
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api:app --bind 0.0.0.0:8000
```

### Docker 部署

创建 `Dockerfile`：

```dockerfile
FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "api.py"]
```

构建并运行：

```bash
docker build -t indextts-api .
docker run -p 8000:8000 indextts-api
```

## 常见问题

### Q: API 启动时提示找不到模型文件？
A: 确保 `checkpoints` 目录下有完整的模型文件。参考项目 README 下载模型。

### Q: 生成语音很慢？
A: 尝试启用 GPU 加速和 FP16 模式，或者减小 `max_text_tokens_per_segment` 参数。

### Q: 如何更换参考音频？
A: 将新的音频文件放到 `sampleAudios` 目录，然后重启 API 服务。

### Q: 支持并发请求吗？
A: 支持，但注意 GPU 内存限制。建议根据硬件配置调整并发数。

### Q: 如何自定义端口？
A: 修改 `api.py` 中的 `uvicorn.run()` 参数，或通过环境变量配置。

## 技术支持

如有问题，请提交 Issue 或查看项目文档。

## 许可证

遵循主项目的许可证。

