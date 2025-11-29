"""
环境检查脚本

检查 IndexTTS API 运行环境是否正确配置
"""

import sys
import os
from pathlib import Path

def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def check_python_version():
    """检查 Python 版本"""
    print_section("Python 版本检查")
    version = sys.version_info
    print(f"Python 版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 10:
        print("✅ Python 版本符合要求 (>= 3.10)")
        return True
    else:
        print("❌ Python 版本不符合要求，需要 Python 3.10+")
        return False

def check_virtual_env():
    """检查是否在虚拟环境中"""
    print_section("虚拟环境检查")
    
    # 检查是否在虚拟环境中
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if in_venv:
        print(f"✅ 运行在虚拟环境中")
        print(f"   环境路径: {sys.prefix}")
        
        # 检查是否是项目的 .venv
        if '.venv' in sys.prefix or 'indextts' in sys.prefix.lower():
            print("✅ 看起来是 IndexTTS 的虚拟环境")
            return True
        else:
            print("⚠️  不确定是否是 IndexTTS 的虚拟环境")
            return True
    else:
        print("❌ 未在虚拟环境中运行")
        print("   建议: 激活 .venv 环境后再运行")
        print("   Windows: .venv\\Scripts\\activate")
        print("   Linux/Mac: source .venv/bin/activate")
        return False

def check_directories():
    """检查必要的目录"""
    print_section("目录检查")
    
    required_dirs = {
        'checkpoints': '模型文件目录',
        'sampleAudios': '参考音频目录',
        '.venv': 'UV 虚拟环境'
    }
    
    all_exist = True
    for dir_name, description in required_dirs.items():
        if os.path.exists(dir_name):
            print(f"✅ {description} ({dir_name})")
        else:
            print(f"❌ {description} ({dir_name}) - 不存在")
            all_exist = False
    
    return all_exist

def check_model_files():
    """检查模型文件"""
    print_section("模型文件检查")
    
    required_files = [
        'checkpoints/config.yaml',
        'checkpoints/gpt.pth',
        'checkpoints/s2mel.pth',
        'checkpoints/bpe.model',
        'checkpoints/wav2vec2bert_stats.pt'
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            print(f"✅ {file_path} ({size_mb:.1f} MB)")
        else:
            print(f"❌ {file_path} - 不存在")
            all_exist = False
    
    return all_exist

def check_reference_audio():
    """检查参考音频"""
    print_section("参考音频检查")
    
    if not os.path.exists('sampleAudios'):
        print("❌ sampleAudios 目录不存在")
        return False
    
    audio_files = []
    for ext in ['*.wav', '*.mp3', '*.m4a']:
        audio_files.extend(Path('sampleAudios').glob(ext))
    
    if audio_files:
        print(f"✅ 找到 {len(audio_files)} 个音频文件:")
        for f in audio_files:
            size_kb = f.stat().st_size / 1024
            print(f"   - {f.name} ({size_kb:.1f} KB)")
        return True
    else:
        print("❌ 未找到音频文件")
        print("   支持格式: .wav, .mp3, .m4a")
        return False

def check_dependencies():
    """检查 Python 依赖"""
    print_section("Python 依赖检查")
    
    core_deps = {
        'torch': 'PyTorch',
        'torchaudio': 'TorchAudio',
        'transformers': 'Transformers',
        'omegaconf': 'OmegaConf',
        'librosa': 'Librosa'
    }
    
    api_deps = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'requests': 'Requests'
    }
    
    print("\n核心依赖 (IndexTTS):")
    core_ok = True
    for module, name in core_deps.items():
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name} - 未安装")
            core_ok = False
    
    print("\nAPI 依赖:")
    api_ok = True
    for module, name in api_deps.items():
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ⚠️  {name} - 未安装（运行 API 需要）")
            api_ok = False
    
    if not api_ok:
        print("\n安装 API 依赖: uv pip install fastapi uvicorn requests")
    
    return core_ok

def check_gpu():
    """检查 GPU 可用性"""
    print_section("GPU 检查")
    
    try:
        import torch
        
        if torch.cuda.is_available():
            print(f"✅ CUDA 可用")
            print(f"   CUDA 版本: {torch.version.cuda}")
            print(f"   GPU 数量: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                print(f"   GPU {i}: {torch.cuda.get_device_name(i)}")
            return True
        else:
            print("⚠️  CUDA 不可用，将使用 CPU（速度较慢）")
            return False
    except ImportError:
        print("❌ 无法导入 PyTorch，跳过 GPU 检查")
        return False

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("  IndexTTS API 环境检查工具")
    print("=" * 60)
    print(f"\n当前工作目录: {os.getcwd()}")
    print(f"Python 可执行文件: {sys.executable}")
    
    results = {
        'Python 版本': check_python_version(),
        '虚拟环境': check_virtual_env(),
        '目录结构': check_directories(),
        '模型文件': check_model_files(),
        '参考音频': check_reference_audio(),
        'Python 依赖': check_dependencies(),
        'GPU 支持': check_gpu()
    }
    
    # 总结
    print_section("检查总结")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {name}")
    
    print("\n" + "-" * 60)
    print(f"通过: {passed}/{total}")
    print("-" * 60)
    
    if passed == total:
        print("\n🎉 所有检查通过！环境配置正确。")
        print("\n下一步:")
        print("  1. 启动 API: uv run python api.py")
        print("  2. 或运行: start_api.bat (Windows) / ./start_api.sh (Linux/Mac)")
        return 0
    else:
        print("\n⚠️  部分检查未通过，请根据上述提示修复问题。")
        print("\n常见问题:")
        print("  1. 如果虚拟环境未激活:")
        print("     Windows: .venv\\Scripts\\activate")
        print("     Linux/Mac: source .venv/bin/activate")
        print("  2. 如果缺少依赖:")
        print("     uv sync")
        print("  3. 如果缺少模型文件:")
        print("     参考 README.md 下载模型")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n检查被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n检查过程中出错: {e}")
        sys.exit(1)

