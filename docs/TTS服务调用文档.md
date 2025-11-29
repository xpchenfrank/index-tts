# TTS服务调用文档

## 服务地址

```
http://localhost:8000
```

## 核心接口：文本转语音

### 接口地址
```
POST http://localhost:8000/tts
```

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| text | string | ✓ | 要转换的中文文本 |
| reference_audio | string | ✗ | 参考音频文件名（不填则使用默认） |

### 返回

直接返回 WAV 格式的音频流，Content-Type: `audio/wav`

## 调用示例

### Python

```python
import requests

# 最简单的调用
response = requests.post(
    "http://localhost:8000/tts",
    json={"text": "你好，这是测试"}
)

# 保存音频文件
with open("output.wav", "wb") as f:
    f.write(response.content)

# 播放音频（需要安装 pygame 或其他播放库）
import pygame
pygame.mixer.init()
pygame.mixer.music.load("output.wav")
pygame.mixer.music.play()
```

### Java

```java
import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;

public class TTSClient {
    public static byte[] textToSpeech(String text) throws IOException {
        URL url = new URL("http://localhost:8000/tts");
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("POST");
        conn.setRequestProperty("Content-Type", "application/json");
        conn.setDoOutput(true);
        
        // 发送请求
        String jsonInput = String.format("{\"text\": \"%s\"}", text);
        try (OutputStream os = conn.getOutputStream()) {
            byte[] input = jsonInput.getBytes("utf-8");
            os.write(input, 0, input.length);
        }
        
        // 读取音频流
        if (conn.getResponseCode() == 200) {
            ByteArrayOutputStream baos = new ByteArrayOutputStream();
            try (InputStream is = conn.getInputStream()) {
                byte[] buffer = new byte[8192];
                int bytesRead;
                while ((bytesRead = is.read(buffer)) != -1) {
                    baos.write(buffer, 0, bytesRead);
                }
            }
            return baos.toByteArray();
        }
        
        throw new IOException("TTS 请求失败: " + conn.getResponseCode());
    }
    
    // 使用示例
    public static void main(String[] args) throws IOException {
        byte[] audioData = textToSpeech("你好世界");
        
        // 保存到文件
        try (FileOutputStream fos = new FileOutputStream("output.wav")) {
            fos.write(audioData);
        }
    }
}
```

### Node.js

```javascript
const axios = require('axios');
const fs = require('fs');

async function textToSpeech(text) {
    const response = await axios.post(
        'http://localhost:8000/tts',
        { text: text },
        { responseType: 'arraybuffer' }
    );
    
    return response.data;
}

// 使用示例
async function main() {
    const audioData = await textToSpeech('你好世界');
    
    // 保存到文件
    fs.writeFileSync('output.wav', audioData);
    
    console.log('音频已保存到 output.wav');
}

main();
```

### C#

```csharp
using System;
using System.IO;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;

public class TTSClient
{
    private static readonly HttpClient client = new HttpClient();
    
    public static async Task<byte[]> TextToSpeechAsync(string text)
    {
        var json = $"{{\"text\": \"{text}\"}}";
        var content = new StringContent(json, Encoding.UTF8, "application/json");
        
        var response = await client.PostAsync(
            "http://localhost:8000/tts", 
            content
        );
        
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadAsByteArrayAsync();
    }
    
    // 使用示例
    public static async Task Main()
    {
        byte[] audioData = await TextToSpeechAsync("你好世界");
        
        // 保存到文件
        File.WriteAllBytes("output.wav", audioData);
        Console.WriteLine("音频已保存到 output.wav");
    }
}
```

### Go

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "io"
    "net/http"
    "os"
)

type TTSRequest struct {
    Text string `json:"text"`
}

func textToSpeech(text string) ([]byte, error) {
    reqData := TTSRequest{Text: text}
    jsonData, _ := json.Marshal(reqData)
    
    resp, err := http.Post(
        "http://localhost:8000/tts",
        "application/json",
        bytes.NewBuffer(jsonData),
    )
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()
    
    return io.ReadAll(resp.Body)
}

func main() {
    audioData, err := textToSpeech("你好世界")
    if err != nil {
        panic(err)
    }
    
    // 保存到文件
    os.WriteFile("output.wav", audioData, 0644)
    fmt.Println("音频已保存到 output.wav")
}
```

## 高级功能

### 1. 查看可用的参考音频

```bash
GET http://localhost:8000/audios
```

返回：
```json
{
  "total": 1,
  "audios": [
    {
      "filename": "我的音频.m4a",
      "path": "sampleAudios/我的音频.m4a",
      "size_kb": 746.5,
      "is_current": true
    }
  ]
}
```

### 2. 使用指定的参考音频

```python
import requests

response = requests.post(
    "http://localhost:8000/tts",
    json={
        "text": "你好世界",
        "reference_audio": "我的音频.m4a"  # 指定音频文件名
    }
)
```

### 3. 切换默认参考音频

```python
import requests

# 切换到另一个音频
response = requests.post(
    "http://localhost:8000/audios/switch?filename=另一个音频.wav"
)

print(response.json())
# {"success": true, "current_reference_audio": "...", "message": "已切换到: 另一个音频.wav"}
```

## 音频消费方式

### 方式1：保存为文件

```python
import requests

response = requests.post(
    "http://localhost:8000/tts",
    json={"text": "你好"}
)

with open("speech.wav", "wb") as f:
    f.write(response.content)
```

### 方式2：直接播放（Python）

```python
import requests
import io
import pygame

response = requests.post(
    "http://localhost:8000/tts",
    json={"text": "你好"}
)

# 从内存播放
audio_stream = io.BytesIO(response.content)
pygame.mixer.init()
pygame.mixer.music.load(audio_stream)
pygame.mixer.music.play()
```

### 方式3：流式处理

```python
import requests

response = requests.post(
    "http://localhost:8000/tts",
    json={"text": "你好"},
    stream=True
)

# 边下载边处理
with open("speech.wav", "wb") as f:
    for chunk in response.iter_content(chunk_size=8192):
        if chunk:
            f.write(chunk)
```

### 方式4：Base64 编码传输

```python
import requests
import base64

response = requests.post(
    "http://localhost:8000/tts",
    json={"text": "你好"}
)

# 编码为 Base64
audio_base64 = base64.b64encode(response.content).decode('utf-8')

# 可以存入数据库或通过 JSON 传输
# ...

# 解码使用
audio_data = base64.b64decode(audio_base64)
with open("speech.wav", "wb") as f:
    f.write(audio_data)
```

## 错误处理

### HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误（如文本为空） |
| 503 | 服务未就绪（模型未加载） |
| 500 | 服务器内部错误 |

### 错误响应示例

```python
import requests

response = requests.post(
    "http://localhost:8000/tts",
    json={"text": ""}  # 空文本
)

if response.status_code != 200:
    error = response.json()
    print(f"错误: {error['detail']}")
```

## 性能建议

1. **复用连接**：使用连接池，避免每次请求都建立新连接

```python
import requests

# 创建 Session 复用连接
session = requests.Session()

# 多次调用
for text in texts:
    response = session.post(
        "http://localhost:8000/tts",
        json={"text": text}
    )
    # 处理音频...
```

2. **批量处理**：如果有多个文本，依次调用即可，服务端会自动管理资源

3. **超时设置**：TTS 生成可能需要时间，建议设置较长的超时

```python
response = requests.post(
    "http://localhost:8000/tts",
    json={"text": "很长的文本..."},
    timeout=60  # 60秒超时
)
```

## 常见问题

**Q: 支持哪些语言？**  
A: 主要支持中文，也支持中英混合

**Q: 音频格式是什么？**  
A: WAV 格式，采样率 24kHz，单声道

**Q: 文本长度有限制吗？**  
A: 建议单次请求不超过 200 个字，过长可能导致生成时间过长

**Q: 如何更换说话人音色？**  
A: 将不同的参考音频放入 `sampleAudios` 目录，然后使用 `reference_audio` 参数指定

**Q: 服务挂了怎么办？**  
A: 先检查服务是否在运行，然后查看日志排查错误

## 测试接口

### 健康检查
```
GET http://localhost:8000/health
```

返回服务状态和当前配置

### 查看 API 文档
```
http://localhost:8000/docs
```

打开浏览器访问此地址，可以看到完整的交互式 API 文档

