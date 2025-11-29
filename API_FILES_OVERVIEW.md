# IndexTTS API 文件说明

本文档说明 API 服务相关文件的用途和使用方法。

## 📁 文件清单

### 核心文件

| 文件名 | 类型 | 说明 |
|--------|------|------|
| `api.py` | Python | **API 服务主文件**，包含所有接口实现 |
| `requirements_api.txt` | 文本 | API 服务所需的 Python 依赖包 |
| `sampleAudios/` | 目录 | 存放参考音频的文件夹 |

### 启动脚本

| 文件名 | 平台 | 说明 |
|--------|------|------|
| `start_api.bat` | Windows | Windows 系统的一键启动脚本 |
| `start_api.sh` | Linux/Mac | Linux/Mac 系统的一键启动脚本 |

### 测试工具

| 文件名 | 类型 | 说明 |
|--------|------|------|
| `check_environment.py` | Python | 环境检查工具，验证所有依赖和配置 |
| `test_api.py` | Python | 命令行测试脚本，用于快速验证 API 功能 |
| `test_page.html` | HTML | 网页测试界面，可在浏览器中直接测试 |

### 示例和文档

| 文件名 | 类型 | 说明 |
|--------|------|------|
| `api_client_example.py` | Python | 客户端调用示例，演示如何使用 API |
| `QUICKSTART.md` | 文档 | 快速入门指南（5分钟上手） |
| `API_README.md` | 文档 | 完整的 API 使用文档 |
| `API_FILES_OVERVIEW.md` | 文档 | 本文件，文件说明总览 |
| `API使用说明.txt` | 文本 | 简明使用说明（纯文本格式） |
| `关于环境和服务的说明.md` | 文档 | 解释 UV 环境和服务架构 |

## 🚀 使用流程

### 新用户推荐流程

```
1. ⚠️ 重要：阅读"关于环境和服务的说明.md"（理解架构）
   ↓
2. 运行 check_environment.py 检查环境（在 UV 环境中）
   ↓
3. 阅读 QUICKSTART.md（快速入门）
   ↓
4. 运行 start_api.bat（Windows）或 start_api.sh（Linux/Mac）
   ↓
5. 运行 test_api.py 验证服务
   ↓
6. 打开 test_page.html 在浏览器中测试
   ↓
7. 参考 api_client_example.py 集成到自己的项目
```

### 开发者推荐流程

```
1. 阅读 API_README.md（完整文档）
   ↓
2. 直接运行 python api.py 启动服务
   ↓
3. 访问 http://localhost:8000/docs 查看 Swagger 文档
   ↓
4. 根据需要修改 api.py 配置
   ↓
5. 参考示例代码集成到项目中
```

## 📋 详细说明

### api.py

这是 API 服务的核心文件，提供以下接口：

- `GET /` - 根路径，返回 API 基本信息
- `GET /health` - 健康检查接口
- `GET /info` - 获取模型信息
- `POST /tts` - 文本转语音（返回音频流）
- `POST /tts_json` - 文本转语音（返回 JSON，包含文件路径）

**启动方式：**
```bash
python api.py
```

**配置项：**
- 端口：默认 8000，可在文件末尾修改
- 模型目录：默认 `./checkpoints`
- 参考音频目录：默认 `./sampleAudios`
- GPU 设置：`use_fp16`、`use_cuda_kernel` 等

### requirements_api.txt

列出了运行 API 服务所需的额外依赖包（不包括 IndexTTS 主项目依赖）。

**安装方式：**
```bash
pip install -r requirements_api.txt
```

主要依赖：
- `fastapi` - Web 框架
- `uvicorn` - ASGI 服务器
- `requests` - HTTP 客户端

### start_api.bat / start_api.sh

一键启动脚本，会自动：
1. 检查 Python 环境
2. 检查必要的目录和文件
3. 安装缺失的依赖
4. 启动 API 服务

**Windows 使用：**
- 双击 `start_api.bat`
- 或在命令行运行：`start_api.bat`

**Linux/Mac 使用：**
```bash
chmod +x start_api.sh
./start_api.sh
```

### test_api.py

命令行测试脚本，会自动执行以下测试：
1. 连接测试
2. 健康检查
3. 信息接口
4. TTS 功能测试

**使用方式：**
```bash
python test_api.py
```

测试成功会生成 `test_output.wav` 文件。

### test_page.html

网页版测试界面，功能：
- 可视化界面
- 实时状态显示
- 在线试听生成的语音
- 内置示例文本
- 支持 Ctrl+Enter 快捷键

**使用方式：**
1. 启动 API 服务
2. 用浏览器打开 `test_page.html`
3. 输入文本，点击"生成语音"

**注意：** 需要启用浏览器的自动播放权限。

### api_client_example.py

完整的客户端示例代码，展示：
- 如何检查服务健康状态
- 如何调用 TTS 接口（流模式）
- 如何调用 TTS 接口（JSON 模式）
- 如何批量生成语音

**使用方式：**
```bash
python api_client_example.py
```

可以直接复制其中的函数到自己的项目中使用。

### QUICKSTART.md

快速入门指南，适合：
- 第一次使用的用户
- 需要快速集成的开发者
- 不想看长篇文档的用户

内容包括：
- 5分钟快速上手流程
- 基本使用示例
- 常用配置说明
- 常见问题解答

### API_README.md

完整的 API 文档，包含：
- 详细的接口说明
- 完整的参数列表
- 多语言调用示例（Python、Node.js、Java）
- 性能优化建议
- 部署方案
- 故障排除

适合需要深入了解 API 的开发者。

## 🎯 使用场景

### 场景1：快速测试

```bash
# 1. 启动服务
python api.py

# 2. 新开一个终端，运行测试
python test_api.py

# 或打开网页测试
# 用浏览器打开 test_page.html
```

### 场景2：Python 项目集成

```python
# 参考 api_client_example.py
import requests

def my_tts(text):
    response = requests.post(
        "http://localhost:8000/tts",
        json={"text": text}
    )
    return response.content

# 使用
audio = my_tts("你好，世界")
with open("output.wav", "wb") as f:
    f.write(audio)
```

### 场景3：其他语言项目集成

参考 `API_README.md` 中的多语言示例：
- Node.js 示例
- Java 示例
- 或使用任何支持 HTTP 的语言

### 场景4：远程调用

```python
# 如果 API 部署在其他机器上
API_URL = "http://192.168.1.100:8000"  # 改为实际 IP

response = requests.post(
    f"{API_URL}/tts",
    json={"text": "测试文本"}
)
```

## 🔧 自定义配置

### 更换参考音频

```bash
# 将新的音频文件放入 sampleAudios 目录
cp your_audio.wav sampleAudios/

# 重启 API 服务
```

API 会自动使用第一个找到的音频文件。

### 修改端口

编辑 `api.py`，找到最后一行：

```python
uvicorn.run(app, host="0.0.0.0", port=8000)
```

改为：

```python
uvicorn.run(app, host="0.0.0.0", port=8888)  # 使用 8888 端口
```

### 启用 GPU 加速

编辑 `api.py`，找到 `startup_event()` 函数：

```python
tts_model = IndexTTS2(
    model_dir=model_dir,
    cfg_path=cfg_path,
    use_fp16=True,  # 启用 FP16
    use_cuda_kernel=True  # 启用 CUDA 加速
)
```

## 📊 文件依赖关系

```
api.py (核心)
  ├─ 依赖: requirements_api.txt
  ├─ 依赖: checkpoints/ (模型文件)
  └─ 依赖: sampleAudios/ (参考音频)

启动脚本
  ├─ start_api.bat
  └─ start_api.sh
       └─ 调用: api.py

测试工具
  ├─ test_api.py
  │    └─ 调用: api.py (HTTP)
  └─ test_page.html
       └─ 调用: api.py (HTTP)

示例代码
  └─ api_client_example.py
       └─ 调用: api.py (HTTP)

文档
  ├─ QUICKSTART.md (入门)
  ├─ API_README.md (完整文档)
  └─ API_FILES_OVERVIEW.md (本文件)
```

## ❓ 常见问题

**Q: 应该先看哪个文件？**  
A: 新用户看 `QUICKSTART.md`，开发者看 `API_README.md`

**Q: 如何验证 API 是否正常工作？**  
A: 运行 `test_api.py` 或打开 `test_page.html`

**Q: 如何集成到我的项目？**  
A: 参考 `api_client_example.py` 中的示例代码

**Q: 可以修改这些文件吗？**  
A: 可以！所有文件都可以根据需要修改

**Q: 生产环境如何部署？**  
A: 参考 `API_README.md` 的"部署建议"章节

## 📞 获取帮助

1. 查看 `API_README.md` 的"常见问题"章节
2. 运行 `test_api.py` 诊断问题
3. 查看 API 日志输出
4. 访问 http://localhost:8000/docs 查看接口文档

## 🎉 快速开始

最简单的使用方式：

```bash
# 1. 启动服务（三选一）
python api.py                # 直接启动
start_api.bat               # Windows 一键启动
./start_api.sh              # Linux/Mac 一键启动

# 2. 测试服务（三选一）
python test_api.py          # 命令行测试
python api_client_example.py  # 示例代码
# 或打开 test_page.html      # 网页测试

# 3. 查看文档
# 浏览器访问 http://localhost:8000/docs
```

就是这么简单！🚀

