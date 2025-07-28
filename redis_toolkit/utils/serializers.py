# -*- coding: utf-8 -*-
"""
Redis Toolkit 序列化模組 (安全版)
提供多種資料類型的自動序列化與反序列化，
完全移除 pickle 以確保安全性
"""
import json
import base64
from typing import Any, Union

from ..exceptions import SerializationError


class BytesAwareJSONEncoder(json.JSONEncoder):
    """支援 bytes 的 JSON 編碼器"""
    
    def default(self, obj):
        if isinstance(obj, bytes):
            return {
                '__type__': 'bytes',
                '__data__': base64.b64encode(obj).decode('ascii')
            }
        elif isinstance(obj, bytearray):
            return {
                '__type__': 'bytearray', 
                '__data__': base64.b64encode(obj).decode('ascii')
            }
        return super().default(obj)


def _decode_bytes_in_object(obj):
    """遞歸解碼物件中的 bytes 資料"""
    if isinstance(obj, dict):
        if obj.get('__type__') == 'bytes' and '__data__' in obj:
            return base64.b64decode(obj['__data__'].encode('ascii'))
        elif obj.get('__type__') == 'bytearray' and '__data__' in obj:
            return bytearray(base64.b64decode(obj['__data__'].encode('ascii')))
        else:
            return {key: _decode_bytes_in_object(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_decode_bytes_in_object(item) for item in obj]
    else:
        return obj


def serialize_numpy_array(value) -> bytes:
    """安全地序列化 NumPy 陣列"""
    try:
        import numpy as np
        if not isinstance(value, np.ndarray):
            raise ValueError("不是 NumPy 陣列")
        
        # 轉換為安全的 JSON 格式
        return json.dumps({
            '__type__': 'numpy',
            '__dtype__': str(value.dtype),
            '__shape__': value.shape,
            '__data__': value.tolist()  # 轉為 Python list
        }, ensure_ascii=False).encode('utf-8')
    except ImportError:
        raise SerializationError("NumPy 未安裝")
    except Exception as e:
        raise SerializationError(
            f"NumPy 陣列序列化失敗: {e}",
            original_data=value,
            original_exception=e
        )


def deserialize_numpy_array(obj: dict):
    """安全地反序列化 NumPy 陣列"""
    try:
        import numpy as np
        return np.array(
            obj['__data__'], 
            dtype=obj['__dtype__']
        ).reshape(obj['__shape__'])
    except ImportError:
        raise SerializationError("NumPy 未安裝")
    except Exception as e:
        raise SerializationError(
            f"NumPy 陣列反序列化失敗: {e}",
            original_exception=e
        )


def serialize_value(value: Any) -> Union[bytes, int]:
    """
    將 Python 值序列化為 Redis 可存放的 bytes 或 int。
    安全版本，不使用 pickle。
    
    支援的類型：
    - None
    - bool
    - int, float
    - str
    - bytes, bytearray
    - dict, list, tuple
    - numpy.ndarray (如果安裝了 NumPy)
    """
    # None 特殊標記
    if value is None:
        return b'__NONE__'

    # bool -> JSON with type marker
    if isinstance(value, bool):
        return json.dumps(
            {'__type__': 'bool', '__data__': value},
            ensure_ascii=False
        ).encode('utf-8')

    # bytes/bytearray -> Base64 編碼的 JSON
    if isinstance(value, (bytes, bytearray)):
        encoded = base64.b64encode(value).decode('ascii')
        return json.dumps(
            {'__type__': 'bytes', '__data__': encoded},
            ensure_ascii=False
        ).encode('utf-8')

    # 基本型別 (str, int, float) -> JSON wrapper
    if isinstance(value, (str, int, float)):
        try:
            return json.dumps(
                {'__type__': type(value).__name__, '__data__': value},
                ensure_ascii=False
            ).encode('utf-8')
        except (TypeError, ValueError) as e:
            raise SerializationError(
                f"無法序列化 {type(value).__name__} 類型",
                original_data=value,
                original_exception=e
            )

    # 容器型別 (dict, list, tuple) -> JSON wrapper
    if isinstance(value, (dict, list, tuple)):
        try:
            return json.dumps(
                {'__type__': type(value).__name__, '__data__': value},
                ensure_ascii=False,
                cls=BytesAwareJSONEncoder
            ).encode('utf-8')
        except (TypeError, ValueError) as e:
            raise SerializationError(
                f"無法序列化 {type(value).__name__} 類型",
                original_data=value,
                original_exception=e
            )

    # NumPy 陣列特殊處理（安全版本）
    try:
        import numpy as np
        if isinstance(value, np.ndarray):
            return serialize_numpy_array(value)
    except ImportError:
        pass

    # 不支援的類型
    raise SerializationError(
        f"不支援的資料類型: {type(value).__name__}。\n"
        f"支援的類型: None, bool, int, float, str, bytes, bytearray, dict, list, tuple, numpy.ndarray"
    )


def deserialize_value(data: Union[bytes, bytearray, int]) -> Any:
    """
    將 Redis 取回的資料反序列化回 Python 值。
    安全版本，不使用 pickle。
    """
    # None 標記
    if data == b'__NONE__':
        return None

    # int 0/1 -> bool
    if isinstance(data, int) and data in (0, 1):
        return bool(data)
    
    # 非 bytes 類型直接返回
    if not isinstance(data, (bytes, bytearray)):
        return data

    # 嘗試 UTF-8 解碼
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError:
        # 無法解碼，返回原始 bytes
        return bytes(data)

    # 嘗試 JSON 解析
    try:
        obj = json.loads(text)
    except (json.JSONDecodeError, TypeError, ValueError):
        # 不是 JSON，返回解碼後的字串
        return text

    # 處理特殊的 wrapper 格式
    if isinstance(obj, dict) and '__type__' in obj:
        t = obj['__type__']
        d = obj.get('__data__')

        if t == 'bytes':
            return base64.b64decode(d.encode('ascii'))
        elif t == 'bytearray':
            return bytearray(base64.b64decode(d.encode('ascii')))
        elif t == 'bool':
            return bool(d)
        elif t == 'int':
            # 0/1 視為布林
            if d in (0, 1):
                return bool(d)
            return int(d)
        elif t == 'float':
            return float(d)
        elif t == 'str':
            return str(d)
        elif t in ('list', 'dict', 'tuple'):
            # 遞歸解碼嵌套的 bytes 資料
            decoded_data = _decode_bytes_in_object(d)
            if t == 'tuple':
                return tuple(decoded_data)
            return decoded_data
        elif t == 'numpy':
            # 安全的 NumPy 反序列化
            return deserialize_numpy_array(obj)
        else:
            # 未知類型，返回原始數據
            return d

    # 非 wrapper dict，但可能包含嵌套的 bytes，遞歸解碼
    return _decode_bytes_in_object(obj)


# 便利函數用於測試
def test_serialize_deserialize(value):
    """測試序列化和反序列化的往返"""
    try:
        serialized = serialize_value(value)
        deserialized = deserialize_value(serialized)
        return deserialized
    except Exception as e:
        print(f"序列化測試失敗: {e}")
        return None