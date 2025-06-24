#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis Toolkit 測試配置
"""

import pytest
import redis
import time
import logging
from redis_toolkit import RedisToolkit, RedisOptions

# 設定測試日誌
logging.basicConfig(level=logging.WARNING)


@pytest.fixture(scope="session")
def redis_available():
    """檢查 Redis 是否可用"""
    try:
        client = redis.Redis(host='localhost', port=6379, db=0)
        client.ping()
        return True
    except (redis.ConnectionError, redis.TimeoutError):
        return False


@pytest.fixture
def redis_client():
    """提供 Redis 客戶端實例"""
    client = redis.Redis(host='localhost', port=6379, db=15, decode_responses=False)  # 使用測試專用 DB
    yield client
    # 清理測試資料
    try:
        client.flushdb()
    except:
        pass


@pytest.fixture
def toolkit():
    """提供 RedisToolkit 實例"""
    instance = RedisToolkit(
        options=RedisOptions(is_logger_info=False)
    )
    yield instance
    instance.cleanup()


@pytest.fixture
def toolkit_with_custom_db():
    """提供使用自訂資料庫的 RedisToolkit 實例"""
    from redis_toolkit import RedisConnectionConfig
    
    config = RedisConnectionConfig(host='localhost', port=6379, db=14)
    instance = RedisToolkit(
        config=config,
        options=RedisOptions(is_logger_info=False)
    )
    yield instance
    instance.cleanup()
    
    # 清理測試資料
    try:
        instance.client.flushdb()
    except:
        pass


@pytest.fixture
def sample_data():
    """提供測試用的樣本資料"""
    return {
        "string_data": "測試字串資料",
        "dict_data": {
            "name": "測試用戶",
            "age": 25,
            "active": True,
            "score": 95.5,
            "tags": ["tag1", "tag2"],
            "metadata": {"type": "test", "version": "1.0"}
        },
        "list_data": [1, "二", 3.0, True, None, {"nested": "value"}],
        "bytes_data": b"binary test data \x00\x01\x02",
        "bool_true": True,
        "bool_false": False,
        "number_int": 42,
        "number_float": 3.14159,
        "empty_dict": {},
        "empty_list": [],
        "none_value": None,
    }


@pytest.fixture
def pubsub_setup():
    """設定發布訂閱測試環境"""
    received_messages = []
    
    def message_handler(channel: str, data):
        received_messages.append((channel, data, time.time()))
    
    subscriber = RedisToolkit(
        channels=["test_channel_1", "test_channel_2"],
        message_handler=message_handler,
        options=RedisOptions(is_logger_info=False)
    )
    
    publisher = RedisToolkit(
        options=RedisOptions(is_logger_info=False)
    )
    
    # 等待訂閱者啟動
    time.sleep(0.5)
    
    yield {
        'subscriber': subscriber,
        'publisher': publisher,
        'received_messages': received_messages,
        'message_handler': message_handler
    }
    
    # 清理
    subscriber.cleanup()
    publisher.cleanup()


def pytest_configure(config):
    """Pytest 配置"""
    config.addinivalue_line(
        "markers", "slow: 標記為慢速測試"
    )
    config.addinivalue_line(
        "markers", "integration: 標記為整合測試"
    )
    config.addinivalue_line(
        "markers", "requires_redis: 標記為需要 Redis 的測試"
    )


def pytest_collection_modifyitems(config, items):
    """修改測試項目收集"""
    redis_marker = pytest.mark.requires_redis
    
    for item in items:
        # 為需要 Redis 的測試添加標記
        if "redis" in item.name.lower() or "toolkit" in item.name.lower():
            item.add_marker(redis_marker)


@pytest.fixture
def performance_timer():
    """效能測試計時器"""
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.perf_counter()
        
        def stop(self):
            self.end_time = time.perf_counter()
        
        @property
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
    
    return Timer()


@pytest.fixture
def large_data():
    """提供大型測試資料"""
    return {
        "large_string": "x" * 10000,  # 10KB 字串
        "large_dict": {f"key_{i}": f"value_{i}" for i in range(1000)},  # 1000 個鍵值對
        "large_list": list(range(1000)),  # 1000 個元素的列表
        "large_bytes": b"binary_data" * 1000,  # 約 11KB 的位元組資料
    }


# 測試跳過條件
skip_if_no_redis = pytest.mark.skipif(
    not pytest.importorskip("redis"),
    reason="Redis 未安裝"
)

skip_if_no_numpy = pytest.mark.skipif(
    not pytest.importorskip("numpy", minversion="1.19"),
    reason="Numpy 未安裝或版本過舊"
)


class RedisTestHelper:
    """Redis 測試輔助類"""
    
    @staticmethod
    def wait_for_subscriber(timeout=2.0):
        """等待訂閱者啟動"""
        time.sleep(min(timeout, 2.0))
    
    @staticmethod
    def cleanup_redis_keys(client, pattern="*"):
        """清理 Redis 鍵"""
        try:
            keys = client.keys(pattern)
            if keys:
                client.delete(*keys)
        except:
            pass
    
    @staticmethod
    def verify_data_integrity(original, retrieved):
        """驗證資料完整性"""
        return original == retrieved and type(original) == type(retrieved)


@pytest.fixture
def redis_helper():
    """提供 Redis 測試輔助工具"""
    return RedisTestHelper()