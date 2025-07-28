#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Redis Toolkit 發布訂閱範例

展示發布訂閱模式的各種使用場景
"""

import time
import threading
import json
from datetime import datetime
from redis_toolkit import RedisToolkit, RedisOptions


def basic_pubsub_example():
    """基本發布訂閱範例"""
    print("=== 基本發布訂閱範例 ===\n")
    
    received_messages = []
    
    def message_handler(channel: str, data):
        """訊息處理函數"""
        received_messages.append({
            "channel": channel,
            "data": data,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 收到訊息")
        print(f"  頻道: {channel}")
        print(f"  內容: {data}")
        print(f"  類型: {type(data).__name__}")
        print()
    
    # 創建訂閱者
    print("1. 創建訂閱者，監聽多個頻道")
    subscriber = RedisToolkit(
        channels=["news", "alerts", "updates"],
        message_handler=message_handler,
        options=RedisOptions(is_logger_info=False)
    )
    
    # 創建發布者
    publisher = RedisToolkit(options=RedisOptions(is_logger_info=False))
    
    # 等待訂閱者準備就緒
    time.sleep(0.5)
    
    # 發布不同類型的訊息
    print("2. 發布各種類型的訊息\n")
    
    messages = [
        ("news", {"title": "重要新聞", "content": "Redis Toolkit 發布新版本！"}),
        ("alerts", {"level": "warning", "message": "系統將在 10 分鐘後維護"}),
        ("updates", {"user_id": 123, "action": "login", "success": True}),
        ("news", "這是一個簡單的字串訊息"),
        ("alerts", ["清單訊息", "項目1", "項目2"]),
        ("updates", 42),  # 數字
        ("news", True),   # 布林值
    ]
    
    for channel, message in messages:
        publisher.publisher(channel, message)
        time.sleep(0.3)  # 稍微延遲以便觀察
    
    # 等待所有訊息處理完成
    time.sleep(1)
    
    print(f"3. 統計結果")
    print(f"   總共發送: {len(messages)} 條訊息")
    print(f"   總共接收: {len(received_messages)} 條訊息")
    print(f"   接收率: {len(received_messages)/len(messages)*100:.0f}%")
    
    # 清理資源
    subscriber.cleanup()
    publisher.cleanup()


def chat_room_example():
    """聊天室範例"""
    print("\n=== 聊天室範例 ===\n")
    
    chat_messages = []
    
    def chat_handler(channel: str, data):
        """聊天訊息處理"""
        chat_messages.append(data)
        
        # 格式化顯示
        timestamp = datetime.fromtimestamp(data["timestamp"]).strftime("%H:%M:%S")
        user = data["user"]
        message = data["message"]
        
        # 特殊訊息類型
        if data.get("type") == "join":
            print(f"[{timestamp}] 💚 {user} 加入聊天室")
        elif data.get("type") == "leave":
            print(f"[{timestamp}] 💔 {user} 離開聊天室")
        else:
            print(f"[{timestamp}] {user}: {message}")
    
    # 創建聊天室訂閱者
    chat_subscriber = RedisToolkit(
        channels=["chatroom:general"],
        message_handler=chat_handler,
        options=RedisOptions(is_logger_info=False)
    )
    
    # 模擬多個用戶
    users = ["Alice", "Bob", "Charlie"]
    publishers = {}
    
    for user in users:
        publishers[user] = RedisToolkit(options=RedisOptions(is_logger_info=False))
    
    time.sleep(0.5)
    
    print("聊天室：general")
    print("-" * 40)
    
    # 模擬聊天
    # Alice 加入
    publishers["Alice"].publisher("chatroom:general", {
        "type": "join",
        "user": "Alice",
        "timestamp": time.time()
    })
    time.sleep(0.5)
    
    # Bob 加入
    publishers["Bob"].publisher("chatroom:general", {
        "type": "join",
        "user": "Bob",
        "timestamp": time.time()
    })
    time.sleep(0.5)
    
    # 對話
    chat_flow = [
        ("Alice", "大家好！👋"),
        ("Bob", "Hi Alice! 今天過得如何？"),
        ("Alice", "很好！正在測試 Redis Toolkit 的 pub/sub 功能"),
        ("Charlie", None),  # Charlie 加入
        ("Charlie", "哇，我也在用這個！超方便的"),
        ("Bob", "確實，自動序列化省了很多工作"),
        ("Alice", "對啊，不用再手動 JSON.dumps 了 😄"),
    ]
    
    for user, message in chat_flow:
        if user == "Charlie" and message is None:
            # Charlie 加入
            publishers["Charlie"].publisher("chatroom:general", {
                "type": "join",
                "user": "Charlie",
                "timestamp": time.time()
            })
        else:
            # 發送聊天訊息
            publishers[user].publisher("chatroom:general", {
                "user": user,
                "message": message,
                "timestamp": time.time()
            })
        time.sleep(0.7)
    
    # Bob 離開
    publishers["Bob"].publisher("chatroom:general", {
        "type": "leave",
        "user": "Bob",
        "timestamp": time.time()
    })
    
    time.sleep(1)
    print("-" * 40)
    print(f"聊天記錄: {len(chat_messages)} 條訊息")
    
    # 清理
    chat_subscriber.cleanup()
    for pub in publishers.values():
        pub.cleanup()


def real_time_monitoring():
    """實時監控範例"""
    print("\n=== 實時監控範例 ===\n")
    
    metrics = {
        "cpu": [],
        "memory": [],
        "requests": []
    }
    
    def metrics_handler(channel: str, data):
        """處理監控指標"""
        metric_type = channel.split(":")[-1]
        if metric_type in metrics:
            metrics[metric_type].append(data)
        
        # 顯示即時數據
        if metric_type == "cpu":
            print(f"📊 CPU: {data['value']:.1f}% (主機: {data['host']})")
        elif metric_type == "memory":
            print(f"💾 記憶體: {data['used_gb']:.1f}GB / {data['total_gb']:.1f}GB")
        elif metric_type == "requests":
            print(f"🌐 請求: {data['count']} 次/秒 (平均回應: {data['avg_ms']:.0f}ms)")
    
    # 創建監控訂閱者
    monitor = RedisToolkit(
        channels=["metrics:cpu", "metrics:memory", "metrics:requests"],
        message_handler=metrics_handler,
        options=RedisOptions(is_logger_info=False)
    )
    
    # 創建指標發布者
    publisher = RedisToolkit(options=RedisOptions(is_logger_info=False))
    
    print("開始接收實時監控數據...\n")
    time.sleep(0.5)
    
    # 模擬發送監控數據
    import random
    
    for i in range(5):
        # CPU 指標
        publisher.publisher("metrics:cpu", {
            "host": "server-01",
            "value": 20 + random.random() * 60,
            "timestamp": time.time()
        })
        
        # 記憶體指標
        publisher.publisher("metrics:memory", {
            "host": "server-01",
            "used_gb": 4 + random.random() * 4,
            "total_gb": 16.0,
            "timestamp": time.time()
        })
        
        # 請求指標
        publisher.publisher("metrics:requests", {
            "count": random.randint(100, 500),
            "avg_ms": 50 + random.random() * 150,
            "timestamp": time.time()
        })
        
        time.sleep(1)
    
    # 顯示統計
    print("\n📈 監控統計摘要:")
    if metrics["cpu"]:
        avg_cpu = sum(m["value"] for m in metrics["cpu"]) / len(metrics["cpu"])
        print(f"   平均 CPU: {avg_cpu:.1f}%")
    
    if metrics["memory"]:
        avg_mem = sum(m["used_gb"] for m in metrics["memory"]) / len(metrics["memory"])
        print(f"   平均記憶體: {avg_mem:.1f}GB")
    
    if metrics["requests"]:
        avg_req = sum(m["count"] for m in metrics["requests"]) / len(metrics["requests"])
        print(f"   平均請求數: {avg_req:.0f} 次/秒")
    
    # 清理
    monitor.cleanup()
    publisher.cleanup()


def pattern_subscription():
    """模式訂閱範例（使用原生 Redis 功能）"""
    print("\n=== 模式訂閱範例 ===\n")
    
    # 注意：RedisToolkit 目前不直接支援模式訂閱，
    # 但可以透過 client 屬性使用原生功能
    
    toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
    
    # 使用原生 pubsub
    pubsub = toolkit.client.pubsub()
    
    # 訂閱模式
    patterns = ["user:*", "order:*", "system:*"]
    for pattern in patterns:
        pubsub.psubscribe(pattern)
    print(f"訂閱模式: {patterns}")
    
    # 創建發布者
    publisher = RedisToolkit(options=RedisOptions(is_logger_info=False))
    
    # 在另一個線程中處理訊息
    def pattern_listener():
        for message in pubsub.listen():
            if message['type'] == 'pmessage':
                channel = message['channel'].decode()
                pattern = message['pattern'].decode()
                
                # 反序列化數據
                from redis_toolkit.utils.serializers import deserialize_value
                try:
                    data = deserialize_value(message['data'])
                    print(f"📨 模式: {pattern} | 頻道: {channel}")
                    print(f"   資料: {data}")
                except:
                    pass
    
    # 啟動監聽線程
    listener_thread = threading.Thread(target=pattern_listener, daemon=True)
    listener_thread.start()
    
    time.sleep(0.5)
    print("\n發送符合模式的訊息:\n")
    
    # 發布符合模式的訊息
    test_messages = [
        ("user:login", {"user_id": 123, "action": "login"}),
        ("user:logout", {"user_id": 123, "action": "logout"}),
        ("order:created", {"order_id": "ORD-001", "amount": 99.99}),
        ("order:cancelled", {"order_id": "ORD-002", "reason": "缺貨"}),
        ("system:alert", {"level": "warning", "message": "高記憶體使用"}),
        ("other:message", {"note": "這個不會被接收"})  # 不符合模式
    ]
    
    for channel, data in test_messages:
        publisher.publisher(channel, data)
        time.sleep(0.5)
    
    # 等待處理完成
    time.sleep(1)
    
    # 清理
    pubsub.close()
    toolkit.cleanup()
    publisher.cleanup()


def error_handling_pubsub():
    """發布訂閱錯誤處理範例"""
    print("\n=== 發布訂閱錯誤處理 ===\n")
    
    error_count = 0
    success_count = 0
    
    def robust_handler(channel: str, data):
        """強健的訊息處理器"""
        global error_count, success_count
        
        try:
            # 模擬可能出錯的處理邏輯
            if isinstance(data, dict) and "error" in data:
                raise ValueError(f"模擬錯誤: {data['error']}")
            
            # 正常處理
            print(f"✅ 成功處理來自 {channel} 的訊息")
            success_count += 1
            
        except Exception as e:
            # 錯誤不會影響訂閱者繼續運行
            print(f"❌ 處理錯誤: {e}")
            error_count += 1
    
    # 創建訂閱者
    subscriber = RedisToolkit(
        channels=["test_channel"],
        message_handler=robust_handler,
        options=RedisOptions(is_logger_info=False)
    )
    
    publisher = RedisToolkit(options=RedisOptions(is_logger_info=False))
    
    time.sleep(0.5)
    
    # 發送各種訊息，包括會導致錯誤的
    test_messages = [
        {"status": "ok", "data": "正常訊息1"},
        {"error": "這會觸發錯誤"},
        {"status": "ok", "data": "正常訊息2"},
        {"error": "另一個錯誤"},
        {"status": "ok", "data": "正常訊息3"},
    ]
    
    print("發送測試訊息...\n")
    for msg in test_messages:
        publisher.publisher("test_channel", msg)
        time.sleep(0.3)
    
    time.sleep(1)
    
    print(f"\n處理統計:")
    print(f"  成功: {success_count}")
    print(f"  錯誤: {error_count}")
    print(f"  總計: {success_count + error_count}")
    print("\n💡 即使處理器出錯，訂閱者仍會繼續運行")
    
    # 清理
    subscriber.cleanup()
    publisher.cleanup()


def main():
    """主程式"""
    print("Redis Toolkit 發布訂閱範例")
    print("=" * 60)
    print()
    
    try:
        # 基本範例
        basic_pubsub_example()
        print("\n" + "=" * 60)
        
        # 聊天室
        chat_room_example()
        print("\n" + "=" * 60)
        
        # 實時監控
        real_time_monitoring()
        print("\n" + "=" * 60)
        
        # 模式訂閱
        pattern_subscription()
        print("\n" + "=" * 60)
        
        # 錯誤處理
        error_handling_pubsub()
        
        print("\n" + "=" * 60)
        print("✅ 所有發布訂閱範例執行完成！")
        print("\n💡 重點總結：")
        print("  - 自動序列化各種 Python 資料類型")
        print("  - 訂閱者在獨立線程中運行，不阻塞主程式")
        print("  - 支援多頻道訂閱")
        print("  - 錯誤處理不會中斷訂閱")
        print("  - 可透過 client 屬性使用原生功能（如模式訂閱）")
        
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()