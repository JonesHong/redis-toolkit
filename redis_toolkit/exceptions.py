# -*- coding: utf-8 -*-
"""
Redis Toolkit 自訂例外模組
"""

import redis


class RedisToolkitError(Exception):
    """
    Redis Toolkit 基礎例外類
    """
    pass


class SerializationError(RedisToolkitError):
    """
    資料序列化/反序列化錯誤
    """
    def __init__(self, message: str, original_data=None, original_exception=None):
        super().__init__(message)
        self.original_data = original_data
        self.original_exception = original_exception


class ValidationError(RedisToolkitError):
    """
    資料驗證錯誤，例如超過大小限制
    """
    pass


def wrap_redis_exceptions(func):
    """
    裝飾器：包裝 Redis 原生例外為 RedisToolkit 例外
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except redis.RedisError as e:
            raise RedisToolkitError(f"Redis 錯誤: {e}") from e
    return wrapper