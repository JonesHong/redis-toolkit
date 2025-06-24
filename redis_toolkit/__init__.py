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

__version__ = "0.1.2"
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

# 可選轉換器功能 - 延遲載入，避免強制依賴
def _try_import_converters():
    """嘗試匯入轉換器功能，失敗時靜默忽略"""
    try:
        # 只匯入便利函數，保持簡單
        from .converters import encode_image, decode_image
        globals()['encode_image'] = encode_image
        globals()['decode_image'] = decode_image
        __all__.extend(['encode_image', 'decode_image'])
    except ImportError:
        pass  # 圖片轉換器不可用
    
    try:
        from .converters import encode_audio, decode_audio
        globals()['encode_audio'] = encode_audio
        globals()['decode_audio'] = decode_audio
        __all__.extend(['encode_audio', 'decode_audio'])
    except ImportError:
        pass  # 音頻轉換器不可用

# 自動載入可用的轉換器
_try_import_converters()