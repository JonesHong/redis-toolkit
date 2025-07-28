# 序列化深入解析

本文檔深入探討 Redis Toolkit 的序列化機制、支援的數據類型、性能特性和最佳實踐。

## 序列化概述

序列化是將 Python 對象轉換為可以存儲在 Redis 中的字節串的過程。Redis Toolkit 提供了智能的自動序列化機制。

### 為什麼需要序列化？

Redis 原生只支援字符串、列表、集合、有序集合和哈希等基本數據類型。要存儲 Python 的複雜對象（如字典、自定義類實例等），必須先將其序列化。

```python
# Redis 原生方式
import redis
import json

r = redis.Redis()
data = {"name": "Alice", "scores": [95, 87, 92]}
r.set("user:1", json.dumps(data))  # 手動序列化
retrieved = json.loads(r.get("user:1"))  # 手動反序列化

# Redis Toolkit 方式
from redis_toolkit import RedisToolkit

toolkit = RedisToolkit()
toolkit.setter("user:1", data)  # 自動序列化
retrieved = toolkit.getter("user:1")  # 自動反序列化
```

## 序列化策略

### 1. 類型檢測流程

```
輸入數據
   │
   ├─> 是 bytes？ ────────> 直接存儲
   │
   ├─> 是基本類型？ ──────> JSON 序列化
   │   (dict, list, str, int, float, bool, None)
   │
   ├─> 是 NumPy 數組？ ────> Pickle 序列化
   │
   ├─> 是 Pandas 對象？ ───> Pickle 序列化
   │
   └─> 其他類型 ─────────> 嘗試 JSON → 失敗則 Pickle
```

### 2. JSON 序列化

**優先使用 JSON 的原因：**

1. **人類可讀**：便於調試和監控
2. **跨語言兼容**：其他語言也能讀取
3. **安全**：不會執行任意代碼
4. **緊湊**：對於簡單數據結構很高效

**支援的類型：**
- `dict`：轉換為 JSON 對象
- `list`, `tuple`：轉換為 JSON 數組
- `str`：直接作為 JSON 字符串
- `int`, `float`：轉換為 JSON 數字
- `bool`：轉換為 JSON 布爾值
- `None`：轉換為 JSON null

**限制：**
```python
# 這些類型無法用 JSON 序列化
from datetime import datetime
from decimal import Decimal

# 錯誤示例
toolkit.setter("date", datetime.now())  # 將使用 Pickle
toolkit.setter("price", Decimal("19.99"))  # 將使用 Pickle

# 正確做法
toolkit.setter("date", datetime.now().isoformat())  # 轉為字符串
toolkit.setter("price", float(Decimal("19.99")))  # 轉為浮點數
```

### 3. Pickle 序列化

**使用 Pickle 的場景：**

1. **NumPy 數組**：保持數組結構和數據類型
2. **Pandas DataFrame**：完整保存數據和元信息
3. **自定義類**：保存對象狀態
4. **複雜數據結構**：嵌套的特殊類型

**安全警告：**
```python
# ⚠️ 警告：Pickle 可以執行任意代碼
# 永遠不要反序列化不信任的數據！

# 安全模式（未來功能）
toolkit = RedisToolkit(options=RedisOptions(
    safe_mode=True,  # 禁用 Pickle
    allowed_types=['dict', 'list', 'str', 'int', 'float']
))
```

### 4. 自定義序列化器

#### 實現自定義序列化器

```python
import msgpack
from typing import Any

class MsgPackSerializer:
    """MessagePack 序列化器 - 更快更緊湊"""
    
    @staticmethod
    def serialize(obj: Any) -> bytes:
        return msgpack.packb(obj, use_bin_type=True)
    
    @staticmethod
    def deserialize(data: bytes) -> Any:
        return msgpack.unpackb(data, raw=False)

# 使用自定義序列化器
options = RedisOptions(
    custom_serializer=MsgPackSerializer.serialize,
    custom_deserializer=MsgPackSerializer.deserialize
)
toolkit = RedisToolkit(options=options)
```

#### 類型特定序列化器

```python
from datetime import datetime
import json

class DateTimeSerializer:
    """處理 datetime 對象的序列化器"""
    
    @staticmethod
    def serialize(obj: Any) -> bytes:
        def json_encoder(o):
            if isinstance(o, datetime):
                return {'__datetime__': o.isoformat()}
            raise TypeError(f"Object of type {type(o)} is not JSON serializable")
        
        return json.dumps(obj, default=json_encoder).encode('utf-8')
    
    @staticmethod
    def deserialize(data: bytes) -> Any:
        def json_decoder(d):
            if '__datetime__' in d:
                return datetime.fromisoformat(d['__datetime__'])
            return d
        
        return json.loads(data.decode('utf-8'), object_hook=json_decoder)
```

## 性能特性

### 1. 序列化性能比較

```python
import time
import json
import pickle
import msgpack
from redis_toolkit.utils import benchmark_serializers

def benchmark_serializers(data, iterations=10000):
    """基準測試不同的序列化方法"""
    
    results = {}
    
    # JSON
    start = time.time()
    for _ in range(iterations):
        json_bytes = json.dumps(data).encode('utf-8')
        json.loads(json_bytes.decode('utf-8'))
    results['json'] = time.time() - start
    
    # Pickle
    start = time.time()
    for _ in range(iterations):
        pickle_bytes = pickle.dumps(data)
        pickle.loads(pickle_bytes)
    results['pickle'] = time.time() - start
    
    # MessagePack
    start = time.time()
    for _ in range(iterations):
        msgpack_bytes = msgpack.packb(data)
        msgpack.unpackb(msgpack_bytes)
    results['msgpack'] = time.time() - start
    
    return results

# 測試數據
test_data = {
    'users': [{'id': i, 'name': f'User{i}'} for i in range(100)],
    'scores': list(range(1000)),
    'metadata': {'version': '1.0', 'timestamp': time.time()}
}

results = benchmark_serializers(test_data)
for method, duration in results.items():
    print(f"{method}: {duration:.3f}秒")
```

### 2. 大小比較

```python
def compare_sizes(data):
    """比較不同序列化方法的輸出大小"""
    
    json_size = len(json.dumps(data).encode('utf-8'))
    pickle_size = len(pickle.dumps(data))
    msgpack_size = len(msgpack.packb(data))
    
    print(f"JSON: {json_size:,} bytes")
    print(f"Pickle: {pickle_size:,} bytes")
    print(f"MessagePack: {msgpack_size:,} bytes")
    
    # 計算相對大小
    base = json_size
    print(f"\n相對於 JSON:")
    print(f"Pickle: {pickle_size/base:.2f}x")
    print(f"MessagePack: {msgpack_size/base:.2f}x")
```

### 3. 性能優化技巧

#### 預序列化

```python
class CachedSerializer:
    """帶緩存的序列化器"""
    
    def __init__(self, cache_size=1000):
        self._cache = {}
        self._cache_order = []
        self.cache_size = cache_size
    
    def serialize(self, obj: Any) -> bytes:
        # 為可哈希對象創建緩存鍵
        cache_key = self._make_cache_key(obj)
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # 序列化並緩存
        serialized = json.dumps(obj).encode('utf-8')
        self._add_to_cache(cache_key, serialized)
        
        return serialized
    
    def _make_cache_key(self, obj):
        if isinstance(obj, (str, int, float, bool, type(None))):
            return ('simple', obj)
        elif isinstance(obj, (list, tuple)):
            return ('sequence', tuple(obj))
        elif isinstance(obj, dict):
            return ('dict', tuple(sorted(obj.items())))
        else:
            return None  # 不可緩存
```

#### 批次序列化

```python
def batch_serialize(items: List[Any]) -> List[bytes]:
    """並行序列化多個項目"""
    from concurrent.futures import ThreadPoolExecutor
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        return list(executor.map(
            lambda x: json.dumps(x).encode('utf-8'), 
            items
        ))
```

## 特殊數據類型處理

### 1. NumPy 數組

```python
import numpy as np
from redis_toolkit.converters import encode_numpy, decode_numpy

# 創建 NumPy 數組
arr = np.random.rand(100, 100)

# 方式 1：使用 Pickle（默認）
toolkit.setter("array:1", arr)
retrieved = toolkit.getter("array:1")

# 方式 2：自定義編碼（更高效）
encoded = encode_numpy(arr)
toolkit.setter("array:2", encoded)
retrieved = decode_numpy(toolkit.getter("array:2"))
```

### 2. Pandas DataFrame

```python
import pandas as pd

# 創建 DataFrame
df = pd.DataFrame({
    'A': range(1000),
    'B': np.random.rand(1000),
    'C': ['category'] * 1000
})

# 直接存儲（使用 Pickle）
toolkit.setter("dataframe:1", df)

# 優化存儲（轉換格式）
toolkit.setter("dataframe:2", df.to_dict('records'))  # JSON 友好
toolkit.setter("dataframe:3", df.to_parquet())  # 二進制，更緊湊
```

### 3. 日期時間

```python
from datetime import datetime, date, timedelta

# 問題：datetime 不是 JSON 可序列化的
now = datetime.now()

# 解決方案 1：轉換為字符串
toolkit.setter("time:1", now.isoformat())
retrieved = datetime.fromisoformat(toolkit.getter("time:1"))

# 解決方案 2：轉換為時間戳
toolkit.setter("time:2", now.timestamp())
retrieved = datetime.fromtimestamp(toolkit.getter("time:2"))

# 解決方案 3：使用自定義序列化器（見上文）
```

## 壓縮集成

### 1. 自動壓縮

```python
options = RedisOptions(
    enable_compression=True,
    compression_threshold=1024  # 壓縮大於 1KB 的值
)

toolkit = RedisToolkit(options=options)

# 大數據自動壓縮
large_data = {"data": "x" * 10000}
toolkit.setter("compressed:1", large_data)  # 自動壓縮
```

### 2. 壓縮策略

```python
import zlib
import lz4.frame
import brotli

class CompressionStrategy:
    """可配置的壓縮策略"""
    
    def __init__(self, algorithm='zlib', level=6):
        self.algorithm = algorithm
        self.level = level
    
    def compress(self, data: bytes) -> bytes:
        if self.algorithm == 'zlib':
            return zlib.compress(data, level=self.level)
        elif self.algorithm == 'lz4':
            return lz4.frame.compress(data)
        elif self.algorithm == 'brotli':
            return brotli.compress(data, quality=self.level)
        else:
            raise ValueError(f"Unknown algorithm: {self.algorithm}")
    
    def decompress(self, data: bytes) -> bytes:
        if self.algorithm == 'zlib':
            return zlib.decompress(data)
        elif self.algorithm == 'lz4':
            return lz4.frame.decompress(data)
        elif self.algorithm == 'brotli':
            return brotli.decompress(data)
```

## 最佳實踐

### 1. 選擇正確的序列化格式

```python
def choose_serializer(data_type, requirements):
    """根據需求選擇序列化器"""
    
    if requirements.get('human_readable'):
        return 'json'
    
    if requirements.get('cross_language'):
        return 'json' if data_type in ['dict', 'list'] else 'msgpack'
    
    if requirements.get('performance'):
        return 'msgpack'
    
    if requirements.get('complex_types'):
        return 'pickle'
    
    return 'json'  # 默認
```

### 2. 處理大數據

```python
class ChunkedStorage:
    """分塊存儲大數據"""
    
    def __init__(self, toolkit, chunk_size=1024*1024):  # 1MB chunks
        self.toolkit = toolkit
        self.chunk_size = chunk_size
    
    def store_large(self, key: str, data: bytes):
        """分塊存儲大數據"""
        chunks = []
        
        for i in range(0, len(data), self.chunk_size):
            chunk = data[i:i+self.chunk_size]
            chunk_key = f"{key}:chunk:{i//self.chunk_size}"
            self.toolkit.setter(chunk_key, chunk)
            chunks.append(chunk_key)
        
        # 存儲元信息
        self.toolkit.setter(f"{key}:meta", {
            'chunks': chunks,
            'total_size': len(data),
            'chunk_size': self.chunk_size
        })
    
    def retrieve_large(self, key: str) -> bytes:
        """檢索分塊數據"""
        meta = self.toolkit.getter(f"{key}:meta")
        if not meta:
            return None
        
        # 獲取所有塊
        chunks = self.toolkit.batch_get(meta['chunks'])
        
        # 組合數據
        return b''.join(chunks[key] for key in meta['chunks'])
```

### 3. 版本控制

```python
class VersionedSerializer:
    """支援版本控制的序列化器"""
    
    VERSION = 2
    
    @classmethod
    def serialize(cls, obj: Any) -> bytes:
        """添加版本信息"""
        versioned = {
            '_version': cls.VERSION,
            '_type': type(obj).__name__,
            'data': obj
        }
        return json.dumps(versioned).encode('utf-8')
    
    @classmethod
    def deserialize(cls, data: bytes) -> Any:
        """處理不同版本"""
        versioned = json.loads(data.decode('utf-8'))
        
        version = versioned.get('_version', 1)
        
        if version == 1:
            # 舊版本遷移
            return cls._migrate_v1(versioned)
        elif version == 2:
            return versioned['data']
        else:
            raise ValueError(f"Unknown version: {version}")
```

## 故障排除

### 1. 序列化錯誤

```python
# 常見錯誤和解決方案

# 錯誤：Object of type 'set' is not JSON serializable
# 解決：轉換為列表
toolkit.setter("myset", list(my_set))

# 錯誤：Circular reference detected
# 解決：打破循環引用或使用自定義序列化
obj.parent = None  # 移除循環引用

# 錯誤：Maximum recursion depth exceeded
# 解決：簡化數據結構或增加遞歸限制
import sys
sys.setrecursionlimit(10000)
```

### 2. 性能問題

```python
# 診斷序列化性能
import cProfile

def profile_serialization():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # 你的序列化代碼
    for _ in range(1000):
        toolkit.setter(f"key:{_}", large_object)
    
    profiler.disable()
    profiler.print_stats(sort='cumulative')
```

## 總結

Redis Toolkit 的序列化系統設計為：

1. **智能**：自動選擇最適合的序列化方法
2. **靈活**：支援自定義序列化器
3. **安全**：默認使用安全的 JSON 格式
4. **高效**：優化常見用例的性能

通過理解這些序列化機制，您可以更好地使用 Redis Toolkit，並在需要時進行優化。