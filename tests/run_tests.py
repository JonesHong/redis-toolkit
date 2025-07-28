#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis Toolkit 測試執行腳本
提供多種測試執行選項，包括新增的轉換器測試
"""

import subprocess
import sys
import argparse
import redis
import time


def check_redis_connection():
    """檢查 Redis 連線"""
    print("🔍 檢查 Redis 連線...")
    try:
        client = redis.Redis(host='localhost', port=6379, db=0)
        client.ping()
        print("✅ Redis 連線正常")
        return True
    except (redis.ConnectionError, redis.TimeoutError) as e:
        print(f"❌ Redis 連線失敗: {e}")
        print("💡 請確保 Redis 服務正在執行：")
        print("   - Windows: redis-server.exe")
        print("   - Linux/Mac: redis-server")
        return False


def check_optional_dependencies():
    """檢查可選依賴"""
    dependencies = {
        'opencv-python': '圖片轉換器',
        'numpy': 'Numpy 陣列支援',
        'scipy': '音頻轉換器',
        'soundfile': '音頻檔案支援',
    }
    
    print("🔍 檢查可選依賴...")
    available = {}
    
    for package, description in dependencies.items():
        try:
            if package == 'opencv-python':
                import cv2
                available[package] = f"✅ {description} (OpenCV {cv2.__version__})"
            elif package == 'numpy':
                import numpy as np
                available[package] = f"✅ {description} (NumPy {np.__version__})"
            elif package == 'scipy':
                import scipy
                available[package] = f"✅ {description} (SciPy {scipy.__version__})"
            elif package == 'soundfile':
                import soundfile as sf
                available[package] = f"✅ {description}"
        except ImportError:
            available[package] = f"⚠️ {description} (未安裝)"
    
    for package, status in available.items():
        print(f"   {status}")
    
    return available


def run_pytest(test_args):
    """執行 pytest"""
    cmd = ["python", "-m", "pytest"] + test_args
    print(f"🚀 執行指令: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode == 0
    except FileNotFoundError:
        print("❌ pytest 未安裝，請執行: pip install pytest")
        return False


def run_basic_tests():
    """執行基本測試"""
    print("🧪 執行基本功能測試...")
    args = [
        "tests/unit/test_core.py",
        "tests/unit/test_serializers.py",
        "-v",
        "--tb=short"
    ]
    return run_pytest(args)


def run_converter_tests():
    """執行轉換器測試"""
    print("🧪 執行轉換器功能測試...")
    args = [
        "tests/unit/test_converters.py",
        "-v",
        "--tb=short"
    ]
    return run_pytest(args)


def run_converter_integration_tests():
    """執行轉換器整合測試"""
    print("🧪 執行轉換器整合測試...")
    args = [
        "tests/integration/test_converters_integration.py",
        "-v",
        "--tb=short"
    ]
    return run_pytest(args)


def run_all_tests():
    """執行所有測試"""
    print("🧪 執行完整測試套件...")
    args = [
        "tests/",
        "-v",
        "--tb=short",
        "--durations=10"  # 顯示最慢的 10 個測試
    ]
    return run_pytest(args)


def run_quick_tests():
    """執行快速測試（跳過慢速測試）"""
    print("⚡ 執行快速測試...")
    args = [
        "tests/",
        "-v",
        "-m", "not slow",
        "--tb=line"
    ]
    return run_pytest(args)


def run_integration_tests():
    """執行整合測試"""
    print("🔗 執行整合測試...")
    args = [
        "tests/",
        "-v",
        "-m", "integration",
        "--tb=short"
    ]
    return run_pytest(args)


def run_performance_tests():
    """執行效能測試"""
    print("📊 執行效能測試...")
    args = [
        "tests/",
        "-v",
        "-m", "slow",
        "--tb=short"
    ]
    return run_pytest(args)


def run_media_tests():
    """執行媒體相關測試"""
    print("🎥 執行媒體處理測試...")
    args = [
        "tests/unit/test_converters.py",
        "tests/integration/test_converters_integration.py",
        "-v",
        "--tb=short"
    ]
    return run_pytest(args)


def run_coverage_tests():
    """執行覆蓋率測試"""
    print("📈 執行測試覆蓋率分析...")
    
    # 檢查是否安裝 pytest-cov
    try:
        import pytest_cov
    except ImportError:
        print("❌ pytest-cov 未安裝，請執行: pip install pytest-cov")
        return False
    
    args = [
        "tests/",
        "--cov=redis_toolkit",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-branch",
        "-v"
    ]
    
    success = run_pytest(args)
    if success:
        print("\n📊 覆蓋率報告已生成在 htmlcov/ 目錄")
        print("💡 開啟 htmlcov/index.html 查看詳細報告")
    
    return success


def run_stress_tests():
    """執行壓力測試"""
    print("💪 執行壓力測試...")
    
    try:
        from redis_toolkit import RedisToolkit, RedisOptions
        import threading
        import time
        
        print("測試多執行緒併發操作...")
        
        def worker(worker_id, operations=100):
            toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
            for i in range(operations):
                key = f"stress_test_{worker_id}_{i}"
                data = {"worker": worker_id, "operation": i, "timestamp": time.time()}
                toolkit.setter(key, data)
                retrieved = toolkit.getter(key)
                assert retrieved == data
            toolkit.cleanup()
            print(f"  Worker {worker_id} 完成 {operations} 次操作")
        
        # 啟動多個執行緒
        threads = []
        start_time = time.time()
        
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i, 50))
            threads.append(thread)
            thread.start()
        
        # 等待所有執行緒完成
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        print(f"✅ 壓力測試完成，耗時 {end_time - start_time:.2f} 秒")
        return True
        
    except Exception as e:
        print(f"❌ 壓力測試失敗: {e}")
        return False


def run_example_tests():
    """執行範例程式測試"""
    print("📋 執行範例程式測試...")
    
    try:
        print("執行媒體範例程式...")
        result = subprocess.run([
            sys.executable, "examples/real-world/media_processing/complete_example.py", "--test-mode"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ 媒體範例程式執行成功")
            return True
        else:
            print(f"❌ 媒體範例程式執行失敗: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ 範例程式執行超時")
        return False
    except FileNotFoundError:
        print("⚠️ 範例程式檔案未找到，跳過測試")
        return True
    except Exception as e:
        print(f"❌ 範例程式測試失敗: {e}")
        return False


def run_dependency_specific_tests():
    """執行依賴特定測試"""
    print("🎯 執行依賴特定測試...")
    
    dependencies = check_optional_dependencies()
    test_args = ["tests/", "-v", "--tb=short"]
    
    # 根據可用依賴調整測試
    skip_marks = []
    
    if "✅" not in dependencies.get('opencv-python', ''):
        skip_marks.append("not (test_image or TestImage)")
        print("⏭️ 跳過圖片相關測試 (OpenCV 未安裝)")
    
    if "✅" not in dependencies.get('numpy', ''):
        skip_marks.append("not numpy")
        print("⏭️ 跳過 NumPy 相關測試")
    
    if "✅" not in dependencies.get('scipy', ''):
        skip_marks.append("not (test_audio or TestAudio)")
        print("⏭️ 跳過音頻相關測試 (SciPy 未安裝)")
    
    if skip_marks:
        test_args.extend(["-m", " and ".join(skip_marks)])
    
    return run_pytest(test_args)


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="Redis Toolkit 測試執行器")
    parser.add_argument(
        "test_type",
        nargs="?",
        default="basic",
        choices=[
            "basic", "all", "quick", "integration", "performance", 
            "coverage", "stress", "converters", "converter-integration",
            "media", "examples", "dependency-specific"
        ],
        help="測試類型 (預設: basic)"
    )
    parser.add_argument(
        "--skip-redis-check",
        action="store_true",
        help="跳過 Redis 連線檢查"
    )
    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="檢查依賴後退出"
    )
    
    args = parser.parse_args()
    
    print("🧪 Redis Toolkit 測試執行器")
    print("=" * 50)
    
    # 只檢查依賴
    if args.check_deps:
        check_optional_dependencies()
        return
    
    # 檢查 Redis 連線（除非跳過）
    redis_tests = [
        "basic", "all", "integration", "stress", 
        "converter-integration", "media", "examples"
    ]
    
    if not args.skip_redis_check and args.test_type in redis_tests:
        if not check_redis_connection():
            print("\n💡 如果您只想測試序列化功能，可以執行：")
            print("   python run_tests.py quick --skip-redis-check")
            print("💡 或測試轉換器功能：")
            print("   python run_tests.py converters --skip-redis-check")
            sys.exit(1)
    
    # 檢查可選依賴
    if args.test_type in ["converters", "converter-integration", "media", "all"]:
        print()
        check_optional_dependencies()
        print()
    
    # 執行對應的測試
    test_functions = {
        "basic": run_basic_tests,
        "all": run_all_tests,
        "quick": run_quick_tests,
        "integration": run_integration_tests,
        "performance": run_performance_tests,
        "coverage": run_coverage_tests,
        "stress": run_stress_tests,
        "converters": run_converter_tests,
        "converter-integration": run_converter_integration_tests,
        "media": run_media_tests,
        "examples": run_example_tests,
        "dependency-specific": run_dependency_specific_tests,
    }
    
    success = test_functions[args.test_type]()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 測試執行完成！")
        
        # 提供後續建議
        if args.test_type == "basic":
            print("\n💡 下一步建議:")
            print("   python run_tests.py converters     # 測試轉換器功能")
            print("   python run_tests.py media          # 測試媒體處理")
            print("   python run_tests.py all            # 執行完整測試")
        elif args.test_type == "converters":
            print("\n💡 下一步建議:")
            print("   python run_tests.py converter-integration  # 測試整合功能")
            print("   python run_tests.py examples               # 執行範例程式")
    else:
        print("❌ 測試執行失敗！")
        
        # 提供除錯建議
        print("\n🔧 除錯建議:")
        if args.test_type in ["converters", "media"]:
            print("   1. 檢查依賴: python run_tests.py --check-deps")
            print("   2. 安裝轉換器依賴: pip install redis-toolkit[cv2,audio]")
            print("   3. 執行基本測試: python run_tests.py basic")
        else:
            print("   1. 檢查 Redis 連線")
            print("   2. 檢查依賴安裝")
            print("   3. 查看詳細錯誤訊息")
        
        sys.exit(1)


if __name__ == "__main__":
    main()