#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試輸入驗證機制
"""

import pytest
from redis_toolkit import RedisToolkit, RedisOptions, ValidationError


class TestInputValidation:
    """測試輸入驗證功能"""
    
    def test_normal_operations(self):
        """測試正常操作不受影響"""
        toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
        
        # 正常的鍵值對
        toolkit.setter("normal_key", "normal value")
        assert toolkit.getter("normal_key") == "normal value"
        
        # 正常的批次操作
        batch_data = {"key1": "value1", "key2": "value2"}
        toolkit.batch_set(batch_data)
        result = toolkit.batch_get(["key1", "key2"])
        assert result == batch_data
        
        # 清理
        toolkit.deleter("normal_key")
        toolkit.deleter("key1")
        toolkit.deleter("key2")
    
    def test_key_length_validation(self):
        """測試鍵名長度驗證"""
        toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
        
        # 超長鍵名
        long_key = "k" * 1000
        with pytest.raises(ValidationError) as exc_info:
            toolkit.setter(long_key, "value")
        assert "鍵名長度" in str(exc_info.value)
        assert "超過限制" in str(exc_info.value)
    
    def test_value_size_validation(self):
        """測試值大小驗證"""
        toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
        
        # 超大值
        large_value = "x" * (11 * 1024 * 1024)  # 11MB
        with pytest.raises(ValidationError) as exc_info:
            toolkit.setter("large_key", large_value)
        assert "資料大小" in str(exc_info.value)
        assert "超過限制" in str(exc_info.value)
    
    def test_batch_single_value_validation(self):
        """測試批次操作中單一值的驗證"""
        toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
        
        # 批次操作中有超大值
        batch_data = {
            "key1": "normal value",
            "key2": "x" * (11 * 1024 * 1024)  # 11MB
        }
        with pytest.raises(ValidationError) as exc_info:
            toolkit.batch_set(batch_data)
        assert "批次操作中資料大小" in str(exc_info.value)
        assert "key2" in str(exc_info.value)
    
    def test_batch_total_size_validation(self):
        """測試批次操作總大小驗證"""
        toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
        
        # 11 個接近 10MB 的值，總共超過 100MB 限制
        batch_data = {f"key_{i}": "x" * (10 * 1024 * 1024 - 100) for i in range(11)}
        with pytest.raises(ValidationError) as exc_info:
            toolkit.batch_set(batch_data)
        assert "批次操作總大小" in str(exc_info.value)
    
    def test_disable_validation(self):
        """測試關閉驗證"""
        toolkit = RedisToolkit(
            options=RedisOptions(is_logger_info=False, enable_validation=False)
        )
        
        # 關閉驗證後可以儲存超大資料
        long_key = "k" * 1000
        large_value = "x" * (11 * 1024 * 1024)
        
        toolkit.setter(long_key, large_value)
        # 驗證可以取回值
        result = toolkit.getter(long_key)
        assert result == large_value
        
        # 清理
        toolkit.deleter(long_key)
    
    def test_custom_limits(self):
        """測試自訂限制"""
        custom_options = RedisOptions(
            is_logger_info=False,
            max_value_size=1024,  # 1KB
            max_key_length=10     # 10 字元
        )
        toolkit = RedisToolkit(options=custom_options)
        
        # 測試自訂鍵名限制
        with pytest.raises(ValidationError):
            toolkit.setter("this_is_too_long", "value")
        
        # 測試自訂值大小限制
        with pytest.raises(ValidationError):
            toolkit.setter("key", "x" * 2000)  # 2KB
        
        # 正常情況
        toolkit.setter("short", "x" * 500)  # 500 bytes
        assert toolkit.getter("short") == "x" * 500
        
        # 清理
        toolkit.deleter("short")