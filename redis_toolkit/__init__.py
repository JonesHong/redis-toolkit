# -*- coding: utf-8 -*-
"""
Redis Toolkit - 增強版 Redis 工具包

支援多種資料類型的自動序列化、發布訂閱等功能
特別適用於處理字典資料和音視訊緩衝區資料
"""

from .core import RedisToolkit, RedisCore  # RedisCore 為向後相容別名
from .options import RedisOptions, RedisConnectionConfig, DEFAULT_OPTIONS
from .exceptions import RedisToolkitError, SerializationError
from .utils import simple_retry, serialize_value, deserialize_value

__version__ = "0.1.0"
__author__ = "Redis Toolkit Team"
__description__ = "增強版 Redis 工具包，支援多類型資料自動序列化"

# 公開的 API
__all__ = [
    # 核心類
    'RedisToolkit',
    'RedisCore',  # 向後相容
    
    # 配置類
    'RedisOptions',
    'RedisConnectionConfig',
    'DEFAULT_OPTIONS',
    
    # 例外類
    'RedisToolkitError',
    'SerializationError',
    
    # 工具函數
    'simple_retry',
    'serialize_value',
    'deserialize_value',
    
    # 版本資訊
    '__version__',
]