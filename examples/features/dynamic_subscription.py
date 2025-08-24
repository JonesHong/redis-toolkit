#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
動態訂閱管理範例
展示如何使用動態訂閱、自動過期、續訂等功能
"""

import time
import threading
import json
from datetime import datetime
from redis_toolkit import RedisToolkit, RedisOptions


def news_handler(channel: str, data: dict):
    """新聞頻道處理器"""
    print(f"📰 新聞更新 [{channel}]: {data.get('title', 'N/A')}")
    print(f"   內容: {data.get('content', '')[:50]}...")


def alert_handler(channel: str, data: dict):
    """警報頻道處理器"""
    level = data.get('level', 'INFO')
    icon = {'CRITICAL': '🚨', 'WARNING': '⚠️', 'INFO': 'ℹ️'}.get(level, '📢')
    print(f"{icon} 警報 [{channel}]: {data.get('message', 'N/A')}")


def stock_handler(channel: str, data: dict):
    """股票頻道處理器"""
    symbol = data.get('symbol', 'N/A')
    price = data.get('price', 0)
    change = data.get('change', 0)
    arrow = '📈' if change > 0 else '📉' if change < 0 else '➡️'
    print(f"{arrow} 股票 [{symbol}]: ${price:.2f} ({change:+.2f}%)")


def demo_basic_dynamic_subscription():
    """基本動態訂閱示範"""
    print("\n" + "="*60)
    print("📡 基本動態訂閱示範")
    print("="*60)
    
    # 創建 RedisToolkit 實例
    toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
    
    try:
        # 動態訂閱不同頻道
        print("\n1️⃣ 動態訂閱頻道...")
        toolkit.subscribe_dynamic("news_channel", news_handler)
        toolkit.subscribe_dynamic("alert_channel", alert_handler)
        toolkit.subscribe_dynamic("stock_channel", stock_handler)
        
        # 發布測試訊息
        print("\n2️⃣ 發布測試訊息...")
        
        # 發布者（可以是另一個實例）
        publisher = RedisToolkit()
        
        # 發送不同類型的訊息
        publisher.publisher("news_channel", {
            "title": "Redis Toolkit 發布新版本",
            "content": "新增動態訂閱管理功能，支援自動過期和續訂機制...",
            "timestamp": datetime.now().isoformat()
        })
        
        publisher.publisher("alert_channel", {
            "level": "WARNING",
            "message": "系統記憶體使用率超過 80%",
            "timestamp": datetime.now().isoformat()
        })
        
        publisher.publisher("stock_channel", {
            "symbol": "AAPL",
            "price": 189.25,
            "change": 2.35,
            "timestamp": datetime.now().isoformat()
        })
        
        # 等待訊息處理
        time.sleep(2)
        
        # 查看訂閱統計
        print("\n3️⃣ 訂閱統計資訊:")
        stats = toolkit.get_subscription_stats()
        print(f"   活躍頻道數: {stats.get('active_count', 0)}")
        print(f"   總訊息數: {stats.get('total_messages', 0)}")
        
        # 動態取消訂閱
        print("\n4️⃣ 取消訂閱 alert_channel...")
        toolkit.unsubscribe_dynamic("alert_channel")
        
        # 再次查看統計
        stats = toolkit.get_subscription_stats()
        print(f"   剩餘活躍頻道: {stats.get('active_channels', [])}")
        
    finally:
        toolkit.cleanup()
        publisher.cleanup()


def demo_auto_expire():
    """自動過期機制示範"""
    print("\n" + "="*60)
    print("⏱️ 自動過期機制示範")
    print("="*60)
    
    # 創建配置為快速過期的實例（測試用）
    toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
    
    # 修改過期時間為 10 秒（測試用）
    if toolkit.subscription_manager:
        toolkit.subscription_manager.expire_minutes = 10/60  # 10秒
        toolkit.subscription_manager.check_interval = 2.0     # 2秒檢查一次
    
    try:
        # 訂閱頻道
        print("\n1️⃣ 訂閱測試頻道...")
        toolkit.subscribe_dynamic("test_expire", lambda ch, d: print(f"收到: {d}"))
        
        # 發送初始訊息
        publisher = RedisToolkit()
        publisher.publisher("test_expire", {"msg": "保持活躍"})
        time.sleep(1)
        
        print("\n2️⃣ 等待頻道過期（10秒無活動）...")
        print("   ", end="", flush=True)
        
        for i in range(12):
            time.sleep(1)
            print(".", end="", flush=True)
            
            # 每5秒檢查一次狀態
            if i % 5 == 4:
                stats = toolkit.get_subscription_stats()
                active = stats.get('active_count', 0)
                expired_count = stats.get('expired_count', 0)
                print(f"\n   狀態: 活躍={active}, 過期={expired_count}", end="", flush=True)
        
        print("\n\n3️⃣ 檢查過期頻道...")
        expired = toolkit.get_expired_channels()
        for channel, info in expired.items():
            print(f"   過期頻道: {channel}")
            print(f"   最後活動: {info['last_activity']}")
            print(f"   訊息數: {info['message_count']}")
        
        # 續訂過期頻道
        if expired:
            print("\n4️⃣ 續訂過期頻道...")
            for channel in expired:
                success = toolkit.resubscribe_channel(channel)
                print(f"   續訂 {channel}: {'成功' if success else '失敗'}")
            
            # 發送訊息確認續訂
            publisher.publisher("test_expire", {"msg": "續訂後的訊息"})
            time.sleep(1)
        
    finally:
        toolkit.cleanup()
        publisher.cleanup()


def demo_concurrent_subscriptions():
    """並發訂閱示範"""
    print("\n" + "="*60)
    print("🔄 並發訂閱示範")
    print("="*60)
    
    toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
    publisher = RedisToolkit()
    
    # 訊息計數器
    message_counts = {}
    lock = threading.Lock()
    
    def create_handler(topic):
        """創建特定主題的處理器"""
        def handler(channel, data):
            with lock:
                if topic not in message_counts:
                    message_counts[topic] = 0
                message_counts[topic] += 1
                count = message_counts[topic]
            print(f"   [{topic}] 訊息 #{count}: {data.get('value', 'N/A')}")
        return handler
    
    try:
        print("\n1️⃣ 動態訂閱多個主題...")
        topics = ["topic_A", "topic_B", "topic_C", "topic_D", "topic_E"]
        
        for topic in topics:
            channel = f"concurrent_{topic}"
            toolkit.subscribe_dynamic(channel, create_handler(topic))
            print(f"   已訂閱: {channel}")
        
        print("\n2️⃣ 並發發送訊息...")
        
        def publisher_worker(topic, count):
            """發布者工作執行緒"""
            channel = f"concurrent_{topic}"
            for i in range(count):
                publisher.publisher(channel, {
                    "topic": topic,
                    "value": f"Message {i+1}",
                    "timestamp": time.time()
                })
                time.sleep(0.1)
        
        # 啟動多個發布者執行緒
        threads = []
        for topic in topics:
            thread = threading.Thread(
                target=publisher_worker,
                args=(topic, 3),  # 每個主題發3條訊息
                name=f"Publisher-{topic}"
            )
            threads.append(thread)
            thread.start()
        
        # 等待所有發布者完成
        for thread in threads:
            thread.join()
        
        # 等待訊息處理
        time.sleep(2)
        
        print("\n3️⃣ 統計結果:")
        total = sum(message_counts.values())
        print(f"   總訊息數: {total}")
        for topic, count in sorted(message_counts.items()):
            print(f"   {topic}: {count} 條訊息")
        
        # 查看詳細統計
        stats = toolkit.get_subscription_stats()
        print(f"\n4️⃣ 訂閱管理器統計:")
        print(f"   活躍頻道: {stats.get('active_count', 0)}")
        print(f"   總訂閱數: {stats.get('total_subscribed', 0)}")
        print(f"   處理訊息數: {stats.get('total_messages', 0)}")
        
    finally:
        toolkit.cleanup()
        publisher.cleanup()


def demo_selective_subscription():
    """選擇性訂閱示範"""
    print("\n" + "="*60)
    print("🎯 選擇性訂閱示範")
    print("="*60)
    
    toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
    publisher = RedisToolkit()
    
    # 不同優先級的處理器
    def high_priority_handler(channel, data):
        print(f"🔴 高優先級 [{channel}]: {data}")
    
    def normal_priority_handler(channel, data):
        print(f"🟡 一般優先級 [{channel}]: {data}")
    
    def low_priority_handler(channel, data):
        print(f"🟢 低優先級 [{channel}]: {data}")
    
    try:
        print("\n1️⃣ 根據條件動態訂閱...")
        
        # 模擬根據系統負載決定訂閱策略
        system_load = 0.3  # 假設系統負載 30%
        
        if system_load < 0.5:
            print("   系統負載低，訂閱所有頻道")
            toolkit.subscribe_dynamic("priority_high", high_priority_handler)
            toolkit.subscribe_dynamic("priority_normal", normal_priority_handler)
            toolkit.subscribe_dynamic("priority_low", low_priority_handler)
        elif system_load < 0.8:
            print("   系統負載中等，只訂閱高優先級和一般優先級")
            toolkit.subscribe_dynamic("priority_high", high_priority_handler)
            toolkit.subscribe_dynamic("priority_normal", normal_priority_handler)
        else:
            print("   系統負載高，只訂閱高優先級")
            toolkit.subscribe_dynamic("priority_high", high_priority_handler)
        
        print("\n2️⃣ 發送不同優先級的訊息...")
        publisher.publisher("priority_high", {"alert": "系統錯誤", "level": "critical"})
        publisher.publisher("priority_normal", {"info": "使用者登入", "user": "alice"})
        publisher.publisher("priority_low", {"debug": "快取更新", "keys": 42})
        
        time.sleep(2)
        
        print("\n3️⃣ 動態調整訂閱...")
        
        # 模擬系統負載增加
        system_load = 0.9
        print(f"   系統負載增加到 {system_load*100:.0f}%")
        
        # 取消低優先級訂閱
        if "priority_low" in [ch for ch in toolkit.get_subscription_stats().get('active_channels', [])]:
            toolkit.unsubscribe_dynamic("priority_low")
            print("   已取消低優先級訂閱")
        
        if "priority_normal" in [ch for ch in toolkit.get_subscription_stats().get('active_channels', [])]:
            toolkit.unsubscribe_dynamic("priority_normal")
            print("   已取消一般優先級訂閱")
        
        # 測試訊息
        print("\n4️⃣ 再次發送訊息（只有高優先級會處理）...")
        publisher.publisher("priority_high", {"alert": "記憶體不足", "level": "warning"})
        publisher.publisher("priority_normal", {"info": "定時任務", "task": "backup"})
        publisher.publisher("priority_low", {"debug": "GC執行", "freed": "124MB"})
        
        time.sleep(2)
        
    finally:
        toolkit.cleanup()
        publisher.cleanup()


def main():
    """主程式"""
    print("\n" + "🚀 Redis Toolkit 動態訂閱管理示範 🚀".center(60))
    
    demos = [
        ("基本動態訂閱", demo_basic_dynamic_subscription),
        ("自動過期機制", demo_auto_expire),
        ("並發訂閱", demo_concurrent_subscriptions),
        ("選擇性訂閱", demo_selective_subscription),
    ]
    
    print("\n請選擇示範項目:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")
    print(f"  {len(demos)+1}. 執行所有示範")
    print(f"  0. 結束")
    
    while True:
        try:
            choice = input("\n請輸入選項 (0-{}): ".format(len(demos)+1))
            choice = int(choice)
            
            if choice == 0:
                print("再見！")
                break
            elif 1 <= choice <= len(demos):
                demos[choice-1][1]()
            elif choice == len(demos) + 1:
                for name, demo_func in demos:
                    demo_func()
                    time.sleep(1)
            else:
                print("無效選項，請重新輸入")
        except KeyboardInterrupt:
            print("\n\n中斷執行")
            break
        except Exception as e:
            print(f"錯誤: {e}")
    
    print("\n" + "="*60)
    print("示範結束")


if __name__ == "__main__":
    main()