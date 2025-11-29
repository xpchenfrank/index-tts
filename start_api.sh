#!/bin/bash

echo "========================================"
echo "IndexTTS API 服务启动脚本 (UV 环境)"
echo "========================================"
echo

# 检查 UV
if ! command -v uv &> /dev/null; then
    echo "[错误] 未找到 uv，请先安装 uv"
    echo
    echo "安装方法:"
    echo "  pip install uv"
    echo "  或访问: https://github.com/astral-sh/uv"
    exit 1
fi

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "[错误] 未找到 .venv 虚拟环境"
    echo
    echo "请先运行以下命令创建环境:"
    echo "  uv sync"
    exit 1
fi

# 检查必要的目录
if [ ! -d "checkpoints" ]; then
    echo "[错误] checkpoints 目录不存在，请先下载模型文件"
    exit 1
fi

if [ ! -d "sampleAudios" ]; then
    echo "[警告] sampleAudios 目录不存在，正在创建..."
    mkdir -p sampleAudios
    echo "[提示] 请将参考音频文件放入 sampleAudios 目录"
    exit 1
fi

# 创建 outputs 目录
if [ ! -d "outputs" ]; then
    mkdir -p outputs
    echo "[信息] 已创建 outputs 目录"
fi

echo
echo "[信息] 正在激活 UV 虚拟环境..."
source .venv/bin/activate

# 检查并安装 API 依赖
echo "[信息] 检查 API 依赖..."
python -c "import fastapi" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[信息] 安装 API 依赖..."
    uv pip install fastapi uvicorn requests
fi

echo
echo "[信息] 正在启动 API 服务..."
echo "[信息] 服务地址: http://localhost:8000"
echo "[信息] API 文档: http://localhost:8000/docs"
echo
echo "按 Ctrl+C 可以停止服务"
echo "========================================"
echo

# 在 UV 环境中启动服务
uv run python api.py

