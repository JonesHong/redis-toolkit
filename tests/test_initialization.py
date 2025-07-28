#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
測試 RedisToolkit 的兩種初始化方式
"""

import pytest
from redis import Redis
from redis_toolkit import RedisToolkit, RedisConnectionConfig, RedisOptions


class TestInitialization:
    """測試不同的初始化方式"""
    
    def test_init_with_redis_instance(self):
        """測試使用 Redis 實例初始化"""
        # 創建 Redis 實例
        redis_client = Redis(host='localhost', port=6379, db=0, decode_responses=False)
        
        # 使用 Redis 實例創建 RedisToolkit
        toolkit = RedisToolkit(redis=redis_client)
        
        # 確認可以正常使用
        toolkit.setter("test_key", "test_value")
        assert toolkit.getter("test_key") == "test_value"
        
        # 確認 client 屬性返回相同的實例
        assert toolkit.client is redis_client
        
        # 清理
        toolkit.deleter("test_key")
        toolkit.cleanup()
    
    def test_init_with_config(self):
        """測試使用配置初始化"""
        # 創建配置
        config = RedisConnectionConfig(host='localhost', port=6379, db=0)
        
        # 使用配置創建 RedisToolkit
        toolkit = RedisToolkit(config=config)
        
        # 確認可以正常使用
        toolkit.setter("test_key", "test_value")
        assert toolkit.getter("test_key") == "test_value"
        
        # 確認 client 屬性可用
        assert toolkit.client is not None
        assert isinstance(toolkit.client, Redis)
        
        # 清理
        toolkit.deleter("test_key")
        toolkit.cleanup()
    
    def test_init_with_default(self):
        """測試使用預設值初始化"""
        # 使用預設值創建 RedisToolkit
        toolkit = RedisToolkit()
        
        # 確認可以正常使用
        toolkit.setter("test_key", "test_value")
        assert toolkit.getter("test_key") == "test_value"
        
        # 清理
        toolkit.deleter("test_key")
        toolkit.cleanup()
    
    def test_init_with_both_raises_error(self):
        """測試同時提供 redis 和 config 會拋出錯誤"""
        redis_client = Redis(host='localhost', port=6379)
        config = RedisConnectionConfig(host='localhost', port=6379)
        
        with pytest.raises(ValueError, match="不能同時提供 redis 和 config 參數"):
            RedisToolkit(redis=redis_client, config=config)
    
    def test_client_property_access(self):
        """測試 client 屬性的存取"""
        toolkit = RedisToolkit()
        
        # 使用 client 屬性執行原生 Redis 操作
        toolkit.client.set("raw_key", b"raw_value")
        assert toolkit.client.get("raw_key") == b"raw_value"
        
        # 設定過期時間
        toolkit.client.expire("raw_key", 10)
        ttl = toolkit.client.ttl("raw_key")
        assert ttl > 0 and ttl <= 10
        
        # 清理
        toolkit.client.delete("raw_key")
        toolkit.cleanup()
    
    def test_with_custom_options(self):
        """測試使用自定義選項"""
        options = RedisOptions(
            is_logger_info=False,
            use_connection_pool=False,
            max_value_size=1024
        )
        
        # 兩種方式都應該支援 options
        redis_client = Redis(host='localhost', port=6379)
        toolkit1 = RedisToolkit(redis=redis_client, options=options)
        
        config = RedisConnectionConfig()
        toolkit2 = RedisToolkit(config=config, options=options)
        
        # 檢查選項是否生效
        assert toolkit1.options.max_value_size == 1024
        assert toolkit2.options.max_value_size == 1024
        
        # 清理
        toolkit1.cleanup()
        toolkit2.cleanup()