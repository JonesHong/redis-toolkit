# -*- coding: utf-8 -*-
"""
Redis Toolkit 序列化模組 (改進版)
提供多種資料類型的自動序列化與反序列化，
改進了對嵌套在字典中的 bytes 資料的處理
"""
import json
import base64
import pickle
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


def serialize_value(value: Any) -> Union[bytes, int]:
    """
    將 Python 值序列化為 Redis 可存放的 bytes 或 int。
    改進版本，支援嵌套在字典中的 bytes 資料。
    """
    # None 特殊
    if value is None:
        return b'__NONE__'

    # bool -> raw bytes '0'/'1'
    if isinstance(value, bool):
        return int(value)

    # bytes/bytearray -> 用 Base64 包成 JSON wrapper
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
        except (TypeError, ValueError):
            pass

    # 容器型別 (dict, list, tuple) -> JSON wrapper (使用支援 bytes 的編碼器)
    if isinstance(value, (dict, list, tuple)):
        try:
            return json.dumps(
                {'__type__': type(value).__name__, '__data__': value},
                ensure_ascii=False,
                cls=BytesAwareJSONEncoder
            ).encode('utf-8')
        except (TypeError, ValueError) as e:
            raise SerializationError(
                "JSON 序列化失敗",
                original_data=value,
                original_exception=e
            )

    # NumPy 陣列特例
    try:
        import numpy as np  # noqa: F401
        if isinstance(value, np.ndarray):
            try:
                return pickle.dumps({'__type__': 'numpy', '__data__': value})
            except Exception as e:
                raise SerializationError(
                    "NumPy pickle 序列化失敗",
                    original_data=value,
                    original_exception=e
                )
    except ImportError:
        pass

    # 其他物件 -> pickle wrapper
    try:
        return pickle.dumps({'__type__': 'pickle', '__data__': value})
    except Exception as e:
        raise SerializationError(
            "Pickle 序列化失敗",
            original_data=value,
            original_exception=e
        )


def deserialize_value(data: Union[bytes, bytearray, int]) -> Any:
    """
    將 Redis 取回的資料反序列化回 Python 值。
    改進版本，支援嵌套在字典中的 bytes 資料。
    """
    # None 標記
    if data == b'__NONE__':
        return None

    # raw bytes '0'/'1' -> bool
    if isinstance(data, (bytes, bytearray)) and data in (b'0', b'1'):
        return bool(int(data))

    # 純 int (bool special-case) -> bool，其餘非 bytes 原樣回傳
    if not isinstance(data, (bytes, bytearray)):
        if isinstance(data, int) and data in (0, 1):
            return bool(data)
        return data

    # 嘗試以 UTF-8 解碼 bytes
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError:
        # 非 UTF-8, 走 pickle 還原
        return _try_pickle_load(data)

    # 嘗試 JSON loads
    try:
        obj = json.loads(text)
    except (json.JSONDecodeError, TypeError, ValueError):
        # JSON parse 失敗, 走 pickle 還原
        return _try_pickle_load(data)

    # JSON 解析成功，檢查 wrapper
    if isinstance(obj, dict) and '__type__' in obj:
        t = obj['__type__']
        d = obj['__data__']

        if t == 'bytes':
            return base64.b64decode(d.encode('ascii'))
        if t == 'int':
            # 0/1 視為布林
            if d in (0, 1):
                return bool(d)
            return int(d)
        if t == 'float':
            return float(d)
        if t == 'str':
            return str(d)
        if t in ('list', 'dict', 'tuple'):
            # 遞歸解碼嵌套的 bytes 資料
            decoded_data = _decode_bytes_in_object(d)
            if t == 'tuple':
                return tuple(decoded_data)
            return decoded_data
        if t == 'numpy':
            return d
        if t == 'pickle':
            return d
        # 未知 type, 回傳 __data__
        return d

    # 非 wrapper dict, 但可能包含嵌套的 bytes, 遞歸解碼
    return _decode_bytes_in_object(obj)


def _try_pickle_load(data: bytes) -> Any:
    """
    嘗試 pickle.loads，還原 numpy / pickle wrapper，
    失敗則嘗試 decode utf-8 或回傳 raw bytes
    """
    try:
        obj = pickle.loads(data)
        if isinstance(obj, dict) and '__type__' in obj:
            if obj['__type__'] in ('numpy', 'pickle'):
                return obj['__data__']
        return obj
    except Exception:
        try:
            return data.decode('utf-8')
        except UnicodeDecodeError:
            return data


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