# -*- coding: utf-8 -*-
"""
動態訂閱管理器的單元測試
"""

import time
import threading
import unittest
from unittest.mock import Mock, MagicMock, patch
from redis_toolkit.subscription_manager import SubscriptionManager, ChannelInfo


class TestSubscriptionManager(unittest.TestCase):
    """SubscriptionManager 單元測試"""
    
    def setUp(self):
        """測試前準備"""
        self.manager = SubscriptionManager(
            expire_minutes=0.1,  # 6秒過期（測試用）
            check_interval=1.0,  # 每秒檢查
            auto_cleanup=True
        )
    
    def tearDown(self):
        """測試後清理"""
        self.manager.cleanup()
    
    def test_initialization(self):
        """測試初始化"""
        self.assertEqual(self.manager.expire_minutes, 0.1)
        self.assertEqual(self.manager.check_interval, 1.0)
        self.assertTrue(self.manager.auto_cleanup)
        self.assertEqual(self.manager.max_expired_records, 100)
    
    def test_subscribe_dynamic(self):
        """測試動態訂閱"""
        callback = Mock()
        
        # 訂閱新頻道
        result = self.manager.subscribe_dynamic("test_channel", callback)
        self.assertTrue(result)
        
        # 檢查訂閱狀態
        stats = self.manager.get_statistics()
        self.assertEqual(stats["active_count"], 1)
        self.assertIn("test_channel", self.manager.channels)
        
        # 重複訂閱應返回 False
        result = self.manager.subscribe_dynamic("test_channel", callback)
        self.assertFalse(result)
    
    def test_unsubscribe(self):
        """測試取消訂閱"""
        callback = Mock()
        
        # 先訂閱
        self.manager.subscribe_dynamic("test_channel", callback)
        
        # 取消訂閱
        result = self.manager.unsubscribe("test_channel")
        self.assertTrue(result)
        
        # 檢查狀態
        self.assertNotIn("test_channel", self.manager.channels)
        
        # 取消不存在的訂閱
        result = self.manager.unsubscribe("non_existent")
        self.assertFalse(result)
    
    def test_update_activity(self):
        """測試活動更新"""
        callback = Mock()
        self.manager.subscribe_dynamic("test_channel", callback)
        
        # 記錄初始時間
        initial_time = self.manager.channels["test_channel"].last_activity
        
        # 等待一下
        time.sleep(0.1)
        
        # 更新活動
        self.manager.update_activity("test_channel")
        
        # 檢查時間已更新
        updated_time = self.manager.channels["test_channel"].last_activity
        self.assertGreater(updated_time, initial_time)
    
    def test_auto_expiration(self):
        """測試自動過期"""
        callback = Mock()
        self.manager.subscribe_dynamic("test_channel", callback)
        
        # 等待過期（6秒 + 檢查間隔）
        time.sleep(8)
        
        # 檢查是否已過期
        self.assertNotIn("test_channel", self.manager.channels)
        self.assertIn("test_channel", self.manager.expired_channels)
    
    def test_get_callback(self):
        """測試獲取回調函數"""
        callback = Mock()
        self.manager.subscribe_dynamic("test_channel", callback)
        
        # 獲取存在的回調
        retrieved = self.manager.get_callback("test_channel")
        self.assertEqual(retrieved, callback)
        
        # 獲取不存在的回調
        retrieved = self.manager.get_callback("non_existent")
        self.assertIsNone(retrieved)
    
    def test_get_expired_channels(self):
        """測試獲取過期頻道"""
        callback = Mock()
        
        # 訂閱並等待過期
        self.manager.subscribe_dynamic("test1", callback)
        time.sleep(8)
        
        # 獲取過期頻道
        expired = self.manager.get_expired_channels()
        self.assertIn("test1", expired)
        self.assertIn("expired_at", expired["test1"])
        self.assertIn("last_activity", expired["test1"])
    
    def test_resubscribe_channel(self):
        """測試重新訂閱"""
        callback = Mock()
        
        # 訂閱並等待過期
        self.manager.subscribe_dynamic("test_channel", callback)
        time.sleep(8)
        
        # 確認已過期
        self.assertIn("test_channel", self.manager.expired_channels)
        
        # 重新訂閱
        result = self.manager.resubscribe_channel("test_channel")
        self.assertTrue(result)
        
        # 檢查狀態
        self.assertIn("test_channel", self.manager.channels)
        self.assertNotIn("test_channel", self.manager.expired_channels)
    
    def test_max_expired_records(self):
        """測試過期記錄上限"""
        self.manager.max_expired_records = 3
        callback = Mock()
        
        # 創建多個過期頻道
        for i in range(5):
            channel = f"test_{i}"
            self.manager.subscribe_dynamic(channel, callback)
        
        # 等待全部過期
        time.sleep(8)
        
        # 檢查只保留最近的3個
        expired = self.manager.get_expired_channels()
        self.assertLessEqual(len(expired), 3)
    
    def test_cleanup(self):
        """測試清理"""
        callback = Mock()
        self.manager.subscribe_dynamic("test_channel", callback)
        
        # 清理
        self.manager.cleanup()
        
        # 檢查狀態
        self.assertFalse(self.manager._running)
        self.assertEqual(len(self.manager.channels), 0)
    
    def test_thread_safety(self):
        """測試線程安全"""
        results = []
        
        def subscribe_task(channel_id):
            callback = Mock()
            result = self.manager.subscribe_dynamic(f"channel_{channel_id}", callback)
            results.append(result)
        
        # 並發訂閱
        threads = []
        for i in range(10):
            t = threading.Thread(target=subscribe_task, args=(i,))
            threads.append(t)
            t.start()
        
        # 等待完成
        for t in threads:
            t.join()
        
        # 檢查結果
        self.assertEqual(sum(results), 10)  # 全部成功
        self.assertEqual(len(self.manager.channels), 10)
    
    def test_is_active(self):
        """測試活躍狀態檢查"""
        callback = Mock()
        self.manager.subscribe_dynamic("test_channel", callback)
        
        # 檢查活躍狀態
        self.assertTrue(self.manager.is_active("test_channel"))
        self.assertFalse(self.manager.is_active("non_existent"))
    
    def test_auto_cleanup_disabled(self):
        """測試禁用自動清理"""
        manager = SubscriptionManager(
            expire_minutes=0.1,
            check_interval=1.0,
            auto_cleanup=False
        )
        
        try:
            callback = Mock()
            manager.subscribe_dynamic("test_channel", callback)
            
            # 等待過期時間
            time.sleep(8)
            
            # 頻道應該仍然存在（因為沒有自動清理）
            self.assertIn("test_channel", manager.channels)
            self.assertEqual(len(manager.expired_channels), 0)
        finally:
            manager.cleanup()


if __name__ == "__main__":
    unittest.main()