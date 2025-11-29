# IndexTTS API 快速使用指南

## 🚀 快速开始（5分钟上手）

### 前提条件

确保你已经按照 IndexTTS 官方文档完成了基础环境配置：

```bash
# 如果还没有安装 uv 和创建环境，请先执行：
pip install uv
uv sync  # 创建虚拟环境并安装 IndexTTS 依赖
```

### 第一步：安装 API 依赖（在 UV 环境中）

```bash
# 激活 UV 虚拟环境
# Windows:
.venv\Scripts\activate

# Linux/Mac:
source .venv/bin/activate

# 安装 API 依赖
uv pip install fastapi uvicorn requests
```

### 第二步：准备参考音频

确保 `sampleAudios` 目录下有音频文件：

```
sampleAudios/
  └── 我的音频.m4a   ✓ 已存在
```

### 第三步：启动 API 服务

**方式1：使用启动脚本（推荐）**

Windows: 双击运行 `start_api.bat`  
Linux/Mac: 运行 `./start_api.sh`

**方式2：手动启动**

```bash
# 确保在 UV 虚拟环境中
uv run python api.py
```

**方式3：在已激活的环境中启动**

```bash
# 先激活环境
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 然后启动
python api.py
```

看到以下信息表示启动成功：
```
>> IndexTTS模型初始化完成！
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 第四步：测试 API

**方法1：运行测试脚本（在 UV 环境中）**
```bash
# 在 UV 环境中运行
uv run python test_api.py
```

**方法2：使用浏览器**

访问 http://localhost:8000/docs 查看交互式 API 文档

**方法3：使用 cURL**
```bash
curl -X POST "http://localhost:8000/tts" \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"你好，这是测试\"}" \
  --output test.wav
```

**方法4：Python 代码（任何环境都可以）**
```python
import requests

response = requests.post(
    "http://localhost:8000/tts",
    json={"text": "你好，世界！"}
)

with open("output.wav", "wb") as f:
    f.write(response.content)
```

> **注意**：API 服务器需要在 UV 环境中启动，但客户端调用可以在任何环境中进行（只要安装了 requests）

## 📝 API 使用示例

### 基本使用

```python
import requests

# 文本转语音
def tts(text):
    response = requests.post(
        "http://localhost:8000/tts",
        json={"text": text}
    )
    return response.content

# 使用
audio = tts("你好，欢迎使用IndexTTS")
with open("hello.wav", "wb") as f:
    f.write(audio)
```

### 自定义参数

```python
import requests

response = requests.post(
    "http://localhost:8000/tts",
    json={
        "text": "这是一段测试文本",
        "temperature": 0.9,          # 温度：影响多样性
        "max_text_tokens_per_segment": 100,  # 分句长度
        "top_p": 0.85,               # Top-p采样
    }
)

with open("output.wav", "wb") as f:
    f.write(response.content)
```

### 批量处理

```python
import requests

texts = [
    "第一段文本",
    "第二段文本", 
    "第三段文本"
]

for i, text in enumerate(texts):
    response = requests.post(
        "http://localhost:8000/tts",
        json={"text": text}
    )
    
    with open(f"output_{i+1}.wav", "wb") as f:
        f.write(response.content)
    print(f"已生成: output_{i+1}.wav")
```

## 🔧 常用配置

### 更换参考音频

1. 将新的音频文件（.wav/.mp3/.m4a）放入 `sampleAudios` 目录
2. 重启 API 服务

### 修改端口

编辑 `api.py` 文件最后一行：

```python
uvicorn.run(app, host="0.0.0.0", port=8000)  # 改为其他端口
```

### 启用 GPU 加速

编辑 `api.py` 的 `startup_event()` 函数：

```python
tts_model = IndexTTS2(
    model_dir=model_dir,
    cfg_path=cfg_path,
    use_fp16=True,  # 改为 True 启用 FP16
    use_cuda_kernel=True  # 改为 True 启用 CUDA 加速
)
```

## 📚 完整文档

详细的 API 文档请查看：
- **API_README.md** - 完整 API 文档
- **api_client_example.py** - 客户端示例代码
- **http://localhost:8000/docs** - 在线交互式文档（启动服务后访问）

## ❓ 常见问题

**Q: 启动时提示找不到模型？**
A: 确保已下载模型文件到 `checkpoints` 目录

**Q: 生成速度很慢？**  
A: 尝试启用 GPU 和 FP16 模式，或减小 `max_text_tokens_per_segment`

**Q: 如何在其他机器上调用？**
A: 修改 API 启动时的 `host` 为服务器IP，客户端使用 `http://服务器IP:8000`

**Q: 支持多个参考音频吗？**
A: 当前版本使用第一个找到的音频。如需切换，请替换 `sampleAudios` 中的文件

## 🎯 下一步

- 查看 `api_client_example.py` 了解更多使用示例
- 阅读 `API_README.md` 了解完整的 API 功能
- 访问 http://localhost:8000/docs 查看交互式文档

## 💡 提示

- 首次生成可能较慢（需要加载模型）
- 建议使用 GPU 以获得更好的性能
- 参考音频质量影响生成效果
- 可以通过参数调整生成质量和速度的平衡

