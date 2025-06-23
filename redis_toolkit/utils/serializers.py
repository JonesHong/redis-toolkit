# -*- coding: utf-8 -*-
"""
Redis Toolkit 序列化模組
提供多種資料類型的自動序列化與反序列化，
支援:
  - None          <-> None
  - bool          <-> raw bytes '0'/'1' -> bool
  - bytes         <-> JSON(Base64) wrapper
  - str/int/float <-> JSON wrapper
  - dict/list/tuple <-> JSON wrapper
  - np.ndarray    <-> pickle wrapper
  - 其他物件      <-> pickle wrapper
"""
import json
import base64
import pickle
from typing import Any, Union

from ..exceptions import SerializationError


def serialize_value(value: Any) -> Union[bytes, int]:
    """
    將 Python 值序列化為 Redis 可存放的 bytes 或 int。
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

    # 容器型別 (dict, list, tuple) -> JSON wrapper
    if isinstance(value, (dict, list, tuple)):
        try:
            return json.dumps(
                {'__type__': type(value).__name__, '__data__': value},
                ensure_ascii=False
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
            return d
        if t == 'numpy':
            return d
        if t == 'pickle':
            return d
        # 未知 type, 回傳 __data__
        return d

    # 非 wrapper dict, 回傳 JSON 解析後的 obj
    return obj


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
