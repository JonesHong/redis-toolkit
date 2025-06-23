#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis Toolkit 測試執行腳本
提供多種測試執行選項
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
        client = redis.Redis(host='localhost', port=51201, db=0)
        client.ping()
        print("✅ Redis 連線正常")
        return True
    except (redis.ConnectionError, redis.TimeoutError) as e:
        print(f"❌ Redis 連線失敗: {e}")
        print("💡 請確保 Redis 服務正在執行：")
        print("   - Windows: redis-server.exe")
        print("   - Linux/Mac: redis-server")
        return False


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
        "tests/test_core.py",
        "tests/test_serializers.py",
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
    # 這裡可以執行效能測試範例
    try:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        
        print("執行效能測試範例...")
        subprocess.run([sys.executable, "examples/performance_test.py"], check=True)
        return True
    except subprocess.CalledProcessError:
        print("❌ 效能測試執行失敗")
        return False


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


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="Redis Toolkit 測試執行器")
    parser.add_argument(
        "test_type",
        nargs="?",
        default="basic",
        choices=["basic", "all", "quick", "integration", "performance", "coverage", "stress"],
        help="測試類型 (預設: basic)"
    )
    parser.add_argument(
        "--skip-redis-check",
        action="store_true",
        help="跳過 Redis 連線檢查"
    )
    
    args = parser.parse_args()
    
    print("🧪 Redis Toolkit 測試執行器")
    print("=" * 50)
    
    # 檢查 Redis 連線（除非跳過）
    if not args.skip_redis_check and args.test_type in ["basic", "all", "integration", "stress"]:
        if not check_redis_connection():
            print("\n💡 如果您只想測試序列化功能，可以執行：")
            print("   python run_tests.py quick --skip-redis-check")
            sys.exit(1)
    
    # 執行對應的測試
    test_functions = {
        "basic": run_basic_tests,
        "all": run_all_tests,
        "quick": run_quick_tests,
        "integration": run_integration_tests,
        "performance": run_performance_tests,
        "coverage": run_coverage_tests,
        "stress": run_stress_tests,
    }
    
    success = test_functions[args.test_type]()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 測試執行完成！")
    else:
        print("❌ 測試執行失敗！")
        sys.exit(1)


if __name__ == "__main__":
    main()