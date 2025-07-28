#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis Toolkit 核心功能測試
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch
from redis_toolkit import RedisToolkit, RedisOptions, RedisConnectionConfig, SerializationError


class TestRedisToolkitBasic:
    """基本功能測試"""
    
    def setup_method(self):
        """每個測試方法執行前的設定"""
        self.toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
    
    def teardown_method(self):
        """每個測試方法執行後的清理"""
        if hasattr(self, 'toolkit'):
            self.toolkit.cleanup()
    
    def test_basic_string_operations(self):
        """測試基本字串操作"""
        # 設定和取得字串
        self.toolkit.setter("test_string", "你好世界")
        result = self.toolkit.getter("test_string")
        assert result == "你好世界"
        
        # 測試空字串
        self.toolkit.setter("empty_string", "")
        result = self.toolkit.getter("empty_string")
        assert result == ""
        
        # 測試包含特殊字符的字串
        special_string = "測試 🚀 特殊字符 & symbols!@#$%"
        self.toolkit.setter("special_string", special_string)
        result = self.toolkit.getter("special_string")
        assert result == special_string
    
    def test_boolean_operations(self):
        """測試布林值操作"""
        # 測試 True
        self.toolkit.setter("bool_true", True)
        result = self.toolkit.getter("bool_true")
        assert result is True
        assert isinstance(result, bool)
        
        # 測試 False
        self.toolkit.setter("bool_false", False)
        result = self.toolkit.getter("bool_false")
        assert result is False
        assert isinstance(result, bool)
    
    def test_numeric_operations(self):
        """測試數值操作"""
        # 整數
        self.toolkit.setter("int_value", 42)
        result = self.toolkit.getter("int_value")
        assert result == 42
        assert isinstance(result, int)
        
        # 浮點數
        self.toolkit.setter("float_value", 3.14159)
        result = self.toolkit.getter("float_value")
        assert result == 3.14159
        assert isinstance(result, float)
        
        # 負數
        self.toolkit.setter("negative", -100)
        result = self.toolkit.getter("negative")
        assert result == -100
        
        # 零
        self.toolkit.setter("zero", 0)
        result = self.toolkit.getter("zero")
        assert result == 0
    
    def test_dict_operations(self):
        """測試字典操作"""
        test_dict = {
            "name": "小明",
            "age": 25,
            "active": True,
            "score": 95.5,
            "items": [1, 2, 3],
            "metadata": {"type": "user", "level": 2}
        }
        
        self.toolkit.setter("test_dict", test_dict)
        result = self.toolkit.getter("test_dict")
        assert result == test_dict
        assert isinstance(result, dict)
    
    def test_list_operations(self):
        """測試列表操作"""
        test_list = [1, "二", 3.0, True, None, {"nested": "dict"}, [1, 2]]
        
        self.toolkit.setter("test_list", test_list)
        result = self.toolkit.getter("test_list")
        assert result == test_list
        assert isinstance(result, list)
    
    def test_bytes_operations(self):
        """測試位元組操作"""
        test_bytes = b"Hello, \x00\x01\x02 binary data!"
        
        self.toolkit.setter("test_bytes", test_bytes)
        result = self.toolkit.getter("test_bytes")
        assert result == test_bytes
        assert isinstance(result, bytes)
    
    def test_none_value(self):
        """測試 None 值"""
        self.toolkit.setter("test_none", None)
        result = self.toolkit.getter("test_none")
        assert result is None
    
    def test_nonexistent_key(self):
        """測試不存在的鍵"""
        result = self.toolkit.getter("nonexistent_key")
        assert result is None
    
    def test_delete_operations(self):
        """測試刪除操作"""
        # 設定一個值
        self.toolkit.setter("to_delete", "待刪除的值")
        assert self.toolkit.getter("to_delete") == "待刪除的值"
        
        # 刪除
        success = self.toolkit.deleter("to_delete")
        assert success is True
        
        # 確認已刪除
        assert self.toolkit.getter("to_delete") is None
        
        # 刪除不存在的鍵
        success = self.toolkit.deleter("nonexistent")
        assert success is False


class TestRedisToolkitBatch:
    """批次操作測試"""
    
    def setup_method(self):
        self.toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
    
    def teardown_method(self):
        self.toolkit.cleanup()
    
    def test_batch_set_get(self):
        """測試批次設定和取得"""
        test_data = {
            "user_1": {"name": "Alice", "age": 30},
            "user_2": {"name": "Bob", "age": 25},
            "user_3": {"name": "Charlie", "age": 35},
            "config": {"debug": True, "version": "1.0"},
            "numbers": [1, 2, 3, 4, 5]
        }
        
        # 批次設定
        self.toolkit.batch_set(test_data)
        
        # 批次取得
        keys = list(test_data.keys())
        results = self.toolkit.batch_get(keys)
        
        # 驗證結果
        assert len(results) == len(test_data)
        for key, expected_value in test_data.items():
            assert results[key] == expected_value
    
    def test_batch_get_partial(self):
        """測試部分存在的鍵的批次取得"""
        # 設定部分資料
        self.toolkit.setter("exists_1", "value_1")
        self.toolkit.setter("exists_3", "value_3")
        
        # 批次取得（包含不存在的鍵）
        keys = ["exists_1", "not_exists_2", "exists_3", "not_exists_4"]
        results = self.toolkit.batch_get(keys)
        
        # 驗證結果
        assert results["exists_1"] == "value_1"
        assert results["not_exists_2"] is None
        assert results["exists_3"] == "value_3"
        assert results["not_exists_4"] is None
    
    def test_empty_batch_operations(self):
        """測試空批次操作"""
        # 空批次設定
        self.toolkit.batch_set({})
        
        # 空批次取得
        results = self.toolkit.batch_get([])
        assert results == {}


class TestRedisToolkitPubSub:
    """發布訂閱測試"""
    
    def test_basic_pubsub(self):
        """測試基本發布訂閱"""
        received_messages = []
        
        def message_handler(channel: str, data):
            received_messages.append((channel, data))
        
        # 建立訂閱者
        subscriber = RedisToolkit(
            channels=["test_channel"],
            message_handler=message_handler,
            options=RedisOptions(is_logger_info=False)
        )
        
        # 建立發布者
        publisher = RedisToolkit(options=RedisOptions(is_logger_info=False))
        
        # 等待訂閱者啟動
        time.sleep(0.5)
        
        # 發布訊息
        test_messages = [
            {"type": "login", "user": "test_user"},
            "simple string message",
            [1, 2, 3, 4],
            True,
            42
        ]
        
        for msg in test_messages:
            publisher.publisher("test_channel", msg)
        
        # 等待訊息處理
        time.sleep(1)
        
        # 驗證接收到的訊息
        assert len(received_messages) == len(test_messages)
        for i, (channel, data) in enumerate(received_messages):
            assert channel == "test_channel"
            assert data == test_messages[i]
        
        # 清理
        subscriber.cleanup()
        publisher.cleanup()
    
    def test_multiple_channels(self):
        """測試多頻道訂閱"""
        received_messages = []
        
        def message_handler(channel: str, data):
            received_messages.append((channel, data))
        
        # 訂閱多個頻道
        subscriber = RedisToolkit(
            channels=["channel_1", "channel_2", "channel_3"],
            message_handler=message_handler,
            options=RedisOptions(is_logger_info=False)
        )
        
        publisher = RedisToolkit(options=RedisOptions(is_logger_info=False))
        
        time.sleep(0.5)
        
        # 向不同頻道發布訊息
        publisher.publisher("channel_1", "message_1")
        publisher.publisher("channel_2", "message_2")
        publisher.publisher("channel_3", "message_3")
        
        time.sleep(1)
        
        # 驗證
        assert len(received_messages) == 3
        channels = [msg[0] for msg in received_messages]
        assert "channel_1" in channels
        assert "channel_2" in channels
        assert "channel_3" in channels
        
        subscriber.cleanup()
        publisher.cleanup()


class TestRedisToolkitConfig:
    """配置測試"""
    
    def test_custom_options(self):
        """測試自訂選項"""
        custom_options = RedisOptions(
            is_logger_info=False,
            max_log_size=128,
            subscriber_retry_delay=10,
            subscriber_stop_timeout=3
        )
        
        toolkit = RedisToolkit(options=custom_options)
        
        assert toolkit.options.is_logger_info is False
        assert toolkit.options.max_log_size == 128
        assert toolkit.options.subscriber_retry_delay == 10
        assert toolkit.options.subscriber_stop_timeout == 3
        
        toolkit.cleanup()
    


class TestRedisToolkitContextManager:
    """上下文管理器測試"""
    
    def test_context_manager(self):
        """測試上下文管理器"""
        with RedisToolkit(options=RedisOptions(is_logger_info=False)) as toolkit:
            toolkit.setter("context_test", "上下文測試")
            result = toolkit.getter("context_test")
            assert result == "上下文測試"
        
        # 退出上下文後應該自動清理（無法直接測試，但不應該出錯）


class TestRedisToolkitHealthCheck:
    """健康檢查測試"""
    
    def test_health_check_success(self):
        """測試健康檢查成功"""
        toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
        
        # 假設 Redis 正常運行
        health = toolkit.health_check()
        assert health is True
        
        toolkit.cleanup()
    
    @patch('redis.Redis.ping')
    def test_health_check_failure(self, mock_ping):
        """測試健康檢查失敗"""
        mock_ping.side_effect = Exception("連線失敗")
        
        toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
        
        health = toolkit.health_check()
        assert health is False
        
        toolkit.cleanup()


class TestRedisToolkitErrors:
    """錯誤處理測試"""
    
    def test_serialization_error(self):
        """測試序列化錯誤"""
        toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
        
        # 測試無法序列化的物件
        class UnserializableObject:
            def __init__(self):
                self.func = lambda x: x  # 函數無法序列化
        
        unserializable = UnserializableObject()
        
        with pytest.raises(SerializationError):
            toolkit.setter("unserializable", unserializable)
        
        toolkit.cleanup()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])