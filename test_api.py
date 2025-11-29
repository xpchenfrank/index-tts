"""
快速测试 IndexTTS API 服务

这个脚本用于快速验证 API 服务是否正常工作
"""

import requests
import time
import sys

API_URL = "http://localhost:8000"

def test_connection():
    """测试连接"""
    print("1. 测试连接...")
    try:
        response = requests.get(f"{API_URL}/", timeout=5)
        if response.status_code == 200:
            print("   ✓ 连接成功")
            return True
        else:
            print(f"   ✗ 连接失败: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ✗ 无法连接到服务，请确保 API 服务正在运行")
        print("   提示: 运行 'python api.py' 启动服务")
        return False
    except Exception as e:
        print(f"   ✗ 错误: {e}")
        return False

def test_health():
    """测试健康检查"""
    print("\n2. 测试健康检查...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ 服务健康")
            print(f"   - 状态: {data.get('status')}")
            print(f"   - 模型已加载: {data.get('model_loaded')}")
            print(f"   - 参考音频: {data.get('reference_audio')}")
            return True
        else:
            print(f"   ✗ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ 错误: {e}")
        return False

def test_info():
    """测试信息接口"""
    print("\n3. 测试信息接口...")
    try:
        response = requests.get(f"{API_URL}/info", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ 获取信息成功")
            print(f"   - 模型版本: {data.get('model_version')}")
            print(f"   - 设备: {data.get('device')}")
            print(f"   - FP16: {data.get('use_fp16')}")
            return True
        else:
            print(f"   ✗ 获取信息失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ 错误: {e}")
        return False

def test_tts():
    """测试文本转语音"""
    print("\n4. 测试文本转语音...")
    test_text = "你好，这是一个测试。"
    output_file = "test_output.wav"
    
    try:
        print(f"   生成文本: {test_text}")
        start_time = time.time()
        
        response = requests.post(
            f"{API_URL}/tts",
            json={"text": test_text},
            timeout=120  # TTS 可能需要较长时间
        )
        
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            # 保存音频文件
            with open(output_file, "wb") as f:
                f.write(response.content)
            
            file_size = len(response.content)
            print(f"   ✓ 生成成功")
            print(f"   - 耗时: {elapsed_time:.2f} 秒")
            print(f"   - 文件大小: {file_size / 1024:.2f} KB")
            print(f"   - 保存位置: {output_file}")
            return True
        else:
            print(f"   ✗ 生成失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("   ✗ 请求超时，生成时间过长")
        return False
    except Exception as e:
        print(f"   ✗ 错误: {e}")
        return False

def main():
    print("=" * 60)
    print("IndexTTS API 快速测试")
    print("=" * 60)
    
    # 运行所有测试
    results = []
    
    results.append(("连接测试", test_connection()))
    if not results[-1][1]:
        print("\n" + "=" * 60)
        print("测试中断: 无法连接到服务")
        print("=" * 60)
        sys.exit(1)
    
    results.append(("健康检查", test_health()))
    results.append(("信息接口", test_info()))
    results.append(("TTS 功能", test_tts()))
    
    # 输出总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name:15s}: {status}")
    
    print("-" * 60)
    print(f"总计: {success_count}/{total_count} 通过")
    print("=" * 60)
    
    if success_count == total_count:
        print("\n🎉 所有测试通过！API 服务运行正常。")
        sys.exit(0)
    else:
        print("\n⚠️  部分测试失败，请检查错误信息。")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)

