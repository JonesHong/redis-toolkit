#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
動態訂閱管理器配置示範
展示多種配置和修改 SubscriptionManager 的方式
"""

import time
from redis_toolkit import RedisToolkit, RedisOptions
from redis_toolkit.subscription_manager import SubscriptionManager


def demo_config_via_options():
    """透過 RedisOptions 配置"""
    print("\n" + "="*60)
    print("📋 方式1: 透過 RedisOptions 配置")
    print("="*60)
    
    # 創建自訂配置
    options = RedisOptions(
        is_logger_info=False,
        # 動態訂閱相關配置
        enable_dynamic_subscription=True,
        subscription_expire_minutes=2.0,     # 2分鐘過期
        subscription_check_interval=10.0,    # 每10秒檢查
        subscription_auto_cleanup=True,
        subscription_max_expired=50          # 最多保留50個過期記錄
    )
    
    toolkit = RedisToolkit(options=options)
    
    # 檢查配置
    if toolkit.subscription_manager:
        print(f"✅ 管理器已創建")
        print(f"   過期時間: {toolkit.subscription_manager.expire_minutes} 分鐘")
        print(f"   檢查間隔: {toolkit.subscription_manager.check_interval} 秒")
        print(f"   自動清理: {toolkit.subscription_manager.auto_cleanup}")
    
    toolkit.cleanup()


def demo_replace_manager():
    """動態替換管理器"""
    print("\n" + "="*60)
    print("🔄 方式2: 動態替換管理器")
    print("="*60)
    
    # 使用預設配置創建
    toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
    
    print("1️⃣ 初始配置:")
    if toolkit.subscription_manager:
        print(f"   過期時間: {toolkit.subscription_manager.expire_minutes} 分鐘")
        print(f"   檢查間隔: {toolkit.subscription_manager.check_interval} 秒")
    
    # 創建新的管理器
    print("\n2️⃣ 替換為新的管理器...")
    new_manager = SubscriptionManager(
        expire_minutes=1.0,   # 1分鐘過期
        check_interval=5.0,   # 每5秒檢查
        auto_cleanup=False    # 不自動清理
    )
    
    # 替換管理器
    toolkit.set_subscription_manager(new_manager)
    
    print("3️⃣ 新配置:")
    print(f"   過期時間: {toolkit.subscription_manager.expire_minutes} 分鐘")
    print(f"   檢查間隔: {toolkit.subscription_manager.check_interval} 秒")
    print(f"   自動清理: {toolkit.subscription_manager.auto_cleanup}")
    
    toolkit.cleanup()


def demo_disable_manager():
    """停用動態訂閱管理器"""
    print("\n" + "="*60)
    print("❌ 方式3: 停用動態訂閱管理器")
    print("="*60)
    
    # 方式A: 初始化時停用
    print("1️⃣ 初始化時停用:")
    options = RedisOptions(
        is_logger_info=False,
        enable_dynamic_subscription=False  # 停用
    )
    toolkit_a = RedisToolkit(options=options)
    print(f"   管理器狀態: {toolkit_a.subscription_manager is None}")
    
    # 方式B: 運行時停用
    print("\n2️⃣ 運行時停用:")
    toolkit_b = RedisToolkit(options=RedisOptions(is_logger_info=False))
    print(f"   停用前: {toolkit_b.subscription_manager is not None}")
    
    toolkit_b.set_subscription_manager(None)
    print(f"   停用後: {toolkit_b.subscription_manager is None}")
    
    toolkit_a.cleanup()
    toolkit_b.cleanup()


def demo_runtime_modification():
    """運行時修改配置"""
    print("\n" + "="*60)
    print("⚙️ 方式4: 運行時直接修改屬性")
    print("="*60)
    
    toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
    
    print("1️⃣ 初始配置:")
    manager = toolkit.subscription_manager
    if manager:
        print(f"   過期時間: {manager.expire_minutes} 分鐘")
        print(f"   檢查間隔: {manager.check_interval} 秒")
    
    print("\n2️⃣ 直接修改屬性...")
    # 直接修改現有管理器的屬性
    manager.expire_minutes = 10.0  # 改為10分鐘
    manager.check_interval = 60.0  # 改為60秒
    
    print("3️⃣ 修改後:")
    print(f"   過期時間: {manager.expire_minutes} 分鐘")
    print(f"   檢查間隔: {manager.check_interval} 秒")
    
    # 測試訂閱
    def test_handler(channel, data):
        print(f"   收到訊息: {data}")
    
    toolkit.subscribe_dynamic("test_channel", test_handler)
    
    stats = toolkit.get_subscription_stats()
    print(f"\n4️⃣ 訂閱統計:")
    print(f"   活躍頻道: {stats.get('active_count', 0)}")
    print(f"   過期設定: {stats.get('expire_minutes', 0)} 分鐘")
    
    toolkit.cleanup()


def demo_multiple_instances():
    """多實例不同配置"""
    print("\n" + "="*60)
    print("🎯 方式5: 多實例使用不同配置")
    print("="*60)
    
    # 短期訂閱實例（快速過期）
    short_term_options = RedisOptions(
        is_logger_info=False,
        subscription_expire_minutes=1.0,
        subscription_check_interval=5.0
    )
    short_term = RedisToolkit(options=short_term_options)
    
    # 長期訂閱實例（慢速過期）
    long_term_options = RedisOptions(
        is_logger_info=False,
        subscription_expire_minutes=60.0,  # 1小時
        subscription_check_interval=300.0  # 5分鐘檢查
    )
    long_term = RedisToolkit(options=long_term_options)
    
    print("短期訂閱實例:")
    print(f"  過期: {short_term.subscription_manager.expire_minutes} 分鐘")
    print(f"  檢查: {short_term.subscription_manager.check_interval} 秒")
    
    print("\n長期訂閱實例:")
    print(f"  過期: {long_term.subscription_manager.expire_minutes} 分鐘")
    print(f"  檢查: {long_term.subscription_manager.check_interval} 秒")
    
    # 根據需求選擇使用哪個實例
    def use_appropriate_instance(priority):
        if priority == "high":
            return long_term  # 重要訊息用長期訂閱
        else:
            return short_term  # 一般訊息用短期訂閱
    
    # 示範使用
    important_toolkit = use_appropriate_instance("high")
    important_toolkit.subscribe_dynamic("critical_alerts", lambda c, d: None)
    
    normal_toolkit = use_appropriate_instance("low")
    normal_toolkit.subscribe_dynamic("info_updates", lambda c, d: None)
    
    print("\n訂閱分配:")
    print(f"  critical_alerts → 長期實例 (60分鐘過期)")
    print(f"  info_updates → 短期實例 (1分鐘過期)")
    
    short_term.cleanup()
    long_term.cleanup()


def main():
    """主程式"""
    print("\n" + "🔧 動態訂閱管理器配置示範 🔧".center(60))
    
    demos = [
        ("透過 RedisOptions 配置", demo_config_via_options),
        ("動態替換管理器", demo_replace_manager),
        ("停用動態訂閱管理器", demo_disable_manager),
        ("運行時修改配置", demo_runtime_modification),
        ("多實例不同配置", demo_multiple_instances),
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


if __name__ == "__main__":
    main()