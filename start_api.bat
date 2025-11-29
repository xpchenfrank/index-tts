@echo off
chcp 65001 >nul
echo ========================================
echo IndexTTS API 服务启动脚本 (UV 环境)
echo ========================================
echo.

:: 检查 UV
where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 uv，请先安装 uv
    echo.
    echo 安装方法:
    echo   pip install uv
    echo   或访问: https://github.com/astral-sh/uv
    pause
    exit /b 1
)

:: 检查虚拟环境
if not exist ".venv" (
    echo [错误] 未找到 .venv 虚拟环境
    echo.
    echo 请先运行以下命令创建环境:
    echo   uv sync
    pause
    exit /b 1
)

:: 检查必要的目录
if not exist "checkpoints" (
    echo [错误] checkpoints 目录不存在，请先下载模型文件
    pause
    exit /b 1
)

if not exist "sampleAudios" (
    echo [警告] sampleAudios 目录不存在，正在创建...
    mkdir sampleAudios
    echo [提示] 请将参考音频文件放入 sampleAudios 目录
    pause
    exit /b 1
)

:: 创建 outputs 目录
if not exist "outputs" (
    mkdir outputs
    echo [信息] 已创建 outputs 目录
)

echo.
echo [信息] 正在激活 UV 虚拟环境...
call .venv\Scripts\activate.bat

:: 检查并安装 API 依赖
echo [信息] 检查 API 依赖...
python -c "import fastapi" 2>nul
if %errorlevel% neq 0 (
    echo [信息] 安装 API 依赖...
    uv pip install fastapi uvicorn requests
)

echo.
echo [信息] 正在启动 API 服务...
echo [信息] 服务地址: http://localhost:8000
echo [信息] API 文档: http://localhost:8000/docs
echo.
echo 按 Ctrl+C 可以停止服务
echo ========================================
echo.

:: 在 UV 环境中启动服务
uv run python api.py

pause

