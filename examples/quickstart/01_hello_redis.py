#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis Toolkit 基礎使用範例
展示 95% 使用者會用到的核心功能
"""

import time
from redis_toolkit import RedisToolkit, RedisOptions


def basic_operations_example():
    """基本操作範例"""
    print("=== 基本操作範例 ===")
    
    # 建立工具包實例
    toolkit = RedisToolkit()
    
    # 測試各種資料類型的自動序列化
    print("1. 自動序列化不同資料類型...")
    test_data = {
        "字串": "你好，Redis Toolkit！",
        "整數": 42,
        "浮點數": 3.14159,
        "布林值_真": True,
        "布林值_假": False,
        "字典": {"使用者": "小明", "年齡": 25, "活躍": True},
        "列表": [1, "二", 3.0, True, None],
        "空值": None,
    }
    
    # 存儲資料
    for key, value in test_data.items():
        toolkit.setter(key, value)
        print(f"  ✓ 已存儲 {key}: {type(value).__name__}")
    
    print("\n2. 驗證資料完整性...")
    # 取得並驗證資料
    for key, expected_value in test_data.items():
        retrieved_value = toolkit.getter(key)
        is_correct = retrieved_value == expected_value
        print(f"  {'✓' if is_correct else '✗'} {key}: {is_correct}")
        
        if not is_correct:
            print(f"    期望: {expected_value}")
            print(f"    實際: {retrieved_value}")
    
    # 批次操作
    print("\n3. 批次操作...")
    batch_data = {
        f"用戶_{i}": {"id": i, "姓名": f"用戶{i}", "積分": i * 100}
        for i in range(1, 6)
    }
    
    toolkit.batch_set(batch_data)
    print(f"  ✓ 批次存儲了 {len(batch_data)} 筆資料")
    
    retrieved_batch = toolkit.batch_get(list(batch_data.keys()))
    all_correct = all(retrieved_batch[k] == v for k, v in batch_data.items())
    print(f"  {'✓' if all_correct else '✗'} 批次取得驗證: {all_correct}")
    
    # 健康檢查
    print(f"\n4. Redis 連線狀態: {'✓ 正常' if toolkit.health_check() else '✗ 異常'}")
    
    toolkit.cleanup()


def bytes_and_media_example():
    """位元組和媒體資料範例"""
    print("\n=== 位元組和媒體資料範例 ===")
    
    toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
    
    # 模擬音訊資料
    print("1. 模擬音訊緩衝區...")
    import random
    audio_data = bytes([random.randint(0, 255) for _ in range(1000)])
    
    toolkit.setter("音訊_緩衝區", audio_data)
    retrieved_audio = toolkit.getter("音訊_緩衝區")
    
    print(f"  音訊資料大小: {len(audio_data)} 位元組")
    print(f"  資料完整性: {'✓ 正確' if audio_data == retrieved_audio else '✗ 錯誤'}")
    print(f"  資料類型保持: {'✓ 正確' if type(audio_data) == type(retrieved_audio) else '✗ 錯誤'}")
    
    # 測試大型位元組資料
    print("\n2. 大型位元組資料測試...")
    large_data = "大型資料測試".encode("utf-8") * 10000  # 約 150KB
    
    start_time = time.time()
    toolkit.setter("大型_資料", large_data)
    store_time = time.time() - start_time
    
    start_time = time.time()
    retrieved_large = toolkit.getter("大型_資料")
    retrieve_time = time.time() - start_time
    
    print(f"  資料大小: {len(large_data)} 位元組")
    print(f"  存儲時間: {store_time:.3f} 秒")
    print(f"  取得時間: {retrieve_time:.3f} 秒")
    print(f"  資料完整性: {'✓ 正確' if large_data == retrieved_large else '✗ 錯誤'}")
    
    toolkit.cleanup()


def pubsub_example():
    """發布訂閱範例"""
    print("\n=== 發布訂閱範例 ===")
    
    received_messages = []
    
    def message_handler(channel: str, data):
        """訊息處理器"""
        received_messages.append((channel, data))
        print(f"  📨 收到訊息 - 頻道: {channel}")
        print(f"      資料類型: {type(data).__name__}")
        print(f"      內容: {data}")
    
    # 建立訂閱者
    subscriber = RedisToolkit(
        channels=["通知", "系統事件"],
        message_handler=message_handler,
        options=RedisOptions(is_logger_info=False)
    )
    
    # 建立發布者
    publisher = RedisToolkit(options=RedisOptions(is_logger_info=False))
    
    # 等待訂閱者啟動
    time.sleep(0.5)
    print("📡 開始發布不同類型的訊息...")
    
    # 發布各種類型的訊息
    test_messages = [
        ("通知", {"類型": "登入", "使用者": "小明", "時間": time.time()}),
        ("通知", "系統維護通知：今晚 23:00-24:00"),
        ("系統事件", {"事件": "用戶註冊", "用戶ID": 12345, "成功": True}),
        ("系統事件", [1, 2, 3, "測試列表"]),
        ("通知", True),  # 測試布林值
    ]
    
    for channel, message in test_messages:
        publisher.publisher(channel, message)
        time.sleep(0.3)  # 稍微延遲以便觀察
    
    # 等待訊息處理完成
    time.sleep(1)
    
    print(f"\n📊 總共收到 {len(received_messages)} 條訊息")
    
    # 清理資源
    subscriber.cleanup()
    publisher.cleanup()


def external_redis_example():
    """使用不同資料庫範例"""
    print("\n=== 使用不同資料庫範例 ===")
    
    # 使用不同的資料庫
    config = RedisConnectionConfig(db=1)
    
    # 建立 RedisToolkit
    toolkit = RedisToolkit(
        config=config,
        options=RedisOptions(is_logger_info=False)
    )
    
    # 使用 RedisToolkit 的增強功能
    enhanced_data = {
        "框架": "redis-toolkit",
        "版本": "0.1.3", 
        "特色": ["自動序列化", "發布訂閱", "音視訊友善"]
    }
    toolkit.setter("增強_資料", enhanced_data)
    
    # 同時使用原生 Redis 方法
    toolkit.client.lpush("原生_列表", "項目1", "項目2", "項目3")
    toolkit.client.expire("增強_資料", 3600)  # 設定過期時間
    
    # 驗證資料
    enhanced_result = toolkit.getter("增強_資料")
    list_length = toolkit.client.llen("原生_列表")
    ttl = toolkit.client.ttl("增強_資料")
    
    print(f"  增強資料: {enhanced_result}")
    print(f"  原生列表長度: {list_length}")
    print(f"  資料 TTL: {ttl} 秒")
    print("  ✓ 增強功能與原生方法完美配合")
    
    toolkit.cleanup()


def numpy_example():
    """Numpy 陣列範例（可選功能）"""
    print("\n=== Numpy 陣列範例（可選功能）===")
    
    try:
        import numpy as np
        
        toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
        
        # 測試不同類型的 numpy 陣列
        arrays = {
            "一維陣列": np.array([1, 2, 3, 4, 5]),
            "二維矩陣": np.array([[1, 2], [3, 4], [5, 6]]),
            "浮點陣列": np.array([1.1, 2.2, 3.3], dtype=np.float32),
            "布林陣列": np.array([True, False, True, False]),
        }
        
        print("  測試 Numpy 陣列序列化...")
        for name, array in arrays.items():
            toolkit.setter(f"numpy_{name}", array)
            retrieved = toolkit.getter(f"numpy_{name}")
            
            arrays_equal = np.array_equal(array, retrieved) if isinstance(retrieved, np.ndarray) else False
            types_equal = type(array) == type(retrieved)
            shapes_equal = array.shape == retrieved.shape if hasattr(retrieved, 'shape') else False
            
            print(f"    {name}:")
            print(f"      陣列相等: {'✓' if arrays_equal else '✗'}")
            print(f"      類型相等: {'✓' if types_equal else '✗'}")
            print(f"      形狀相等: {'✓' if shapes_equal else '✗'}")
        
        toolkit.cleanup()
        
    except ImportError:
        print("  ⚠️  Numpy 未安裝，跳過此範例")


def context_manager_example():
    """上下文管理器範例"""
    print("\n=== 上下文管理器範例 ===")
    
    # 使用 with 語句自動管理資源
    with RedisToolkit(options=RedisOptions(is_logger_info=False)) as toolkit:
        toolkit.setter("上下文_測試", {"訊息": "自動資源管理"})
        result = toolkit.getter("上下文_測試")
        print(f"  上下文中的資料: {result}")
        print("  ✓ 使用 with 語句，資源會自動清理")
    
    print("  ✓ 退出 with 區塊後，資源已自動清理")


if __name__ == "__main__":
    try:
        print("🚀 Redis Toolkit 功能展示")
        print("=" * 50)
        
        basic_operations_example()
        bytes_and_media_example() 
        pubsub_example()
        external_redis_example()
        numpy_example()
        context_manager_example()
        
        print("\n" + "=" * 50)
        print("🎉 所有範例執行完成！")
        print("\n💡 重點提醒:")
        print("  ✅ 自動處理 dict, list, bool, bytes 等資料類型")
        print("  ✅ 音視訊位元組資料零配置處理")
        print("  ✅ 發布訂閱訊息自動序列化") 
        print("  ✅ 完全相容 Redis 原生功能")
        print("  ✅ 簡單易用，開箱即用")
        
    except Exception as e:
        print(f"❌ 範例執行出錯: {e}")
        import traceback
        traceback.print_exc()