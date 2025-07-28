#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis Toolkit 效能測試範例
測試各種操作的效能表現
"""

import time
import statistics
from redis_toolkit import RedisToolkit, RedisOptions


def benchmark_operation(operation_name: str, operation_func, iterations: int = 1000):
    """效能測試輔助函數"""
    print(f"\n📊 測試 {operation_name} ({iterations} 次操作)")
    
    times = []
    for i in range(iterations):
        start_time = time.perf_counter()
        operation_func(i)
        end_time = time.perf_counter()
        times.append(end_time - start_time)
    
    total_time = sum(times)
    avg_time = statistics.mean(times)
    min_time = min(times)
    max_time = max(times)
    ops_per_second = iterations / total_time
    
    print(f"  總時間: {total_time:.3f} 秒")
    print(f"  平均時間: {avg_time*1000:.3f} 毫秒/操作")
    print(f"  最快: {min_time*1000:.3f} 毫秒")
    print(f"  最慢: {max_time*1000:.3f} 毫秒")
    print(f"  吞吐量: {ops_per_second:.0f} 操作/秒")
    
    return total_time, ops_per_second


def test_basic_operations():
    """測試基本操作效能"""
    print("=== 基本操作效能測試 ===")
    
    toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
    
    # 測試字串操作
    def string_set_operation(i):
        toolkit.setter(f"string_{i}", f"測試字串_{i}")
    
    def string_get_operation(i):
        toolkit.getter(f"string_{i}")
    
    # 測試字典操作
    def dict_set_operation(i):
        toolkit.setter(f"dict_{i}", {"id": i, "名稱": f"項目_{i}", "值": i * 10})
    
    def dict_get_operation(i):
        toolkit.getter(f"dict_{i}")
    
    # 執行測試
    benchmark_operation("字串設定", string_set_operation)
    benchmark_operation("字串取得", string_get_operation)
    benchmark_operation("字典設定", dict_set_operation)
    benchmark_operation("字典取得", dict_get_operation)
    
    toolkit.cleanup()


def test_batch_operations():
    """測試批次操作效能"""
    print("\n=== 批次操作效能測試 ===")
    
    toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
    
    # 準備測試資料
    batch_sizes = [10, 50, 100, 500]
    
    for batch_size in batch_sizes:
        print(f"\n📦 批次大小: {batch_size}")
        
        # 準備批次資料
        batch_data = {
            f"batch_key_{i}": {"索引": i, "資料": f"批次資料_{i}"}
            for i in range(batch_size)
        }
        
        # 測試批次設定
        start_time = time.perf_counter()
        toolkit.batch_set(batch_data)
        batch_set_time = time.perf_counter() - start_time
        
        # 測試批次取得
        keys = list(batch_data.keys())
        start_time = time.perf_counter()
        result = toolkit.batch_get(keys)
        batch_get_time = time.perf_counter() - start_time
        
        # 測試個別操作（用於比較）
        start_time = time.perf_counter()
        for key, value in batch_data.items():
            toolkit.setter(f"individual_{key}", value)
        individual_set_time = time.perf_counter() - start_time
        
        individual_keys = [f"individual_{key}" for key in keys]
        start_time = time.perf_counter()
        for key in individual_keys:
            toolkit.getter(key)
        individual_get_time = time.perf_counter() - start_time
        
        # 顯示結果
        print(f"  批次設定: {batch_set_time:.3f} 秒 ({batch_size/batch_set_time:.0f} 操作/秒)")
        print(f"  個別設定: {individual_set_time:.3f} 秒 ({batch_size/individual_set_time:.0f} 操作/秒)")
        print(f"  效能提升: {individual_set_time/batch_set_time:.1f}x")
        
        print(f"  批次取得: {batch_get_time:.3f} 秒 ({batch_size/batch_get_time:.0f} 操作/秒)")
        print(f"  個別取得: {individual_get_time:.3f} 秒 ({batch_size/individual_get_time:.0f} 操作/秒)")
        print(f"  效能提升: {individual_get_time/batch_get_time:.1f}x")
    
    toolkit.cleanup()


def test_data_size_impact():
    """測試資料大小對效能的影響"""
    print("\n=== 資料大小效能測試 ===")
    
    toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
    
    # 測試不同大小的資料
    data_sizes = [
        ("小型", "x" * 100),                    # 100 位元組
        ("中型", "x" * 1000),                   # 1KB
        ("大型", "x" * 10000),                  # 10KB
        ("超大型", "x" * 100000),               # 100KB
    ]
    
    for size_name, data in data_sizes:
        print(f"\n📏 {size_name}資料 ({len(data)} 位元組)")
        
        # 測試設定
        start_time = time.perf_counter()
        for i in range(100):
            toolkit.setter(f"{size_name}_data_{i}", data)
        set_time = time.perf_counter() - start_time
        
        # 測試取得
        start_time = time.perf_counter()
        for i in range(100):
            toolkit.getter(f"{size_name}_data_{i}")
        get_time = time.perf_counter() - start_time
        
        # 計算吞吐量
        data_throughput_set = (len(data) * 100) / set_time / 1024 / 1024  # MB/s
        data_throughput_get = (len(data) * 100) / get_time / 1024 / 1024  # MB/s
        
        print(f"  設定: {set_time:.3f} 秒 ({100/set_time:.0f} 操作/秒, {data_throughput_set:.1f} MB/s)")
        print(f"  取得: {get_time:.3f} 秒 ({100/get_time:.0f} 操作/秒, {data_throughput_get:.1f} MB/s)")
    
    toolkit.cleanup()


def test_pubsub_performance():
    """測試發布訂閱效能"""
    print("\n=== 發布訂閱效能測試 ===")
    
    received_count = [0]  # 使用列表以便在內部函數中修改
    
    def message_handler(channel: str, data):
        received_count[0] += 1
    
    # 建立訂閱者
    subscriber = RedisToolkit(
        channels=["效能測試"],
        message_handler=message_handler,
        options=RedisOptions(is_logger_info=False)
    )
    
    # 建立發布者
    publisher = RedisToolkit(options=RedisOptions(is_logger_info=False))
    
    # 等待訂閱者啟動
    time.sleep(0.5)
    
    # 測試發布效能
    message_counts = [100, 500, 1000]
    
    for msg_count in message_counts:
        print(f"\n📤 發布 {msg_count} 條訊息")
        
        received_count[0] = 0
        test_message = {"測試": True, "編號": 0, "資料": "效能測試訊息"}
        
        start_time = time.perf_counter()
        for i in range(msg_count):
            test_message["編號"] = i
            publisher.publisher("效能測試", test_message)
        publish_time = time.perf_counter() - start_time
        
        # 等待訊息處理完成
        time.sleep(2)
        
        publish_rate = msg_count / publish_time
        receive_rate = received_count[0] / 2.0  # 除以等待時間
        
        print(f"  發布速率: {publish_rate:.0f} 訊息/秒")
        print(f"  接收速率: {receive_rate:.0f} 訊息/秒")
        print(f"  訊息完整性: {received_count[0]}/{msg_count} ({received_count[0]/msg_count*100:.1f}%)")
    
    # 清理
    subscriber.cleanup()
    publisher.cleanup()


def test_retry_performance():
    """測試效能"""
    print("\n=== 效能測試 ===")
    
    # 測試第一個實例
    toolkit_with_retry = RedisToolkit(
        options=RedisOptions(is_logger_info=False)
    )
    
    # 測試第二個實例
    toolkit_without_retry = RedisToolkit(
        options=RedisOptions(is_logger_info=False)
    )
    
    test_iterations = 1000
    test_data = {"測試": "重試機制效能", "值": 12345}
    
    # 測試啟用重試的效能
    start_time = time.perf_counter()
    for i in range(test_iterations):
        toolkit_with_retry.setter(f"retry_test_{i}", test_data)
    with_retry_time = time.perf_counter() - start_time
    
    # 測試不啟用重試的效能
    start_time = time.perf_counter()
    for i in range(test_iterations):
        toolkit_without_retry.setter(f"no_retry_test_{i}", test_data)
    without_retry_time = time.perf_counter() - start_time
    
    print(f"📈 重試機制效能對比 ({test_iterations} 次操作)")
    print(f"  啟用重試: {with_retry_time:.3f} 秒 ({test_iterations/with_retry_time:.0f} 操作/秒)")
    print(f"  不啟用重試: {without_retry_time:.3f} 秒 ({test_iterations/without_retry_time:.0f} 操作/秒)")
    print(f"  效能差異: {with_retry_time/without_retry_time:.1f}x")
    
    toolkit_with_retry.cleanup()
    toolkit_without_retry.cleanup()


if __name__ == "__main__":
    try:
        print("🏃‍♂️ Redis Toolkit 效能測試")
        print("=" * 50)
        
        test_basic_operations()
        test_batch_operations()
        test_data_size_impact()
        test_pubsub_performance()
        test_retry_performance()
        
        print("\n" + "=" * 50)
        print("🏁 效能測試完成！")
        
        print("\n💡 效能優化建議:")
        print("  ✅ 使用批次操作處理大量資料")
        print("  ✅ 根據資料大小選擇合適的操作方式")
        print("  ✅ 在穩定環境中可考慮關閉重試機制")
        print("  ✅ 發布訂閱適合即時訊息傳遞")
        
    except Exception as e:
        print(f"❌ 效能測試出錯: {e}")
        import traceback
        traceback.print_exc()