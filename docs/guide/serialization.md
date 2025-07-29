# 序列化功能

Redis Toolkit 的核心優勢之一是智慧序列化系統，它能自動處理各種 Python 資料類型，讓您專注於業務邏輯而非資料轉換。

## 🎯 為什麼需要序列化？

Redis 原生只支援字串、列表、集合等簡單類型。當我們需要存儲 Python 的複雜物件時，必須進行序列化：

```python
# ❌ 原生 Redis 的限制
import redis
r = redis.Redis()

# 這會報錯！
user = {"name": "Alice", "age": 25}
r.set("user", user)  # TypeError: Invalid input type

# 😓 傳統做法：手動序列化
import json
r.set("user", json.dumps(user))
retrieved = json.loads(r.get("user"))  # 需要手動反序列化
```

```python
# ✅ Redis Toolkit 的解決方案
from redis_toolkit import RedisToolkit
toolkit = RedisToolkit()

# 自動處理！
user = {"name": "Alice", "age": 25}
toolkit.setter("user", user)
retrieved = toolkit.getter("user")  # 自動反序列化為 dict
```

## 🔐 安全第一：為什麼不用 Pickle？

許多 Redis 包裝器使用 Python 的 `pickle` 進行序列化，但這存在嚴重的安全風險：

::: danger 安全警告
Pickle 可以執行任意程式碼！反序列化不受信任的資料可能導致遠端程式碼執行 (RCE)。
:::

Redis Toolkit 採用 **JSON-based 序列化**，確保安全性：

```python
# 我們的序列化策略
# 1. 基本類型：使用 JSON
# 2. 二進位資料：Base64 編碼
# 3. NumPy 陣列：轉換為列表 + 元資料
# 4. 自定義物件：需要明確的序列化器
```

## 📊 支援的資料類型

### 基本類型

| Python 類型 | 範例 | 存儲格式 |
|------------|------|----------|
| str | `"Hello"` | 直接存儲 |
| int | `42` | JSON 數字 |
| float | `3.14` | JSON 數字 |
| bool | `True` | JSON 布林值 |
| None | `None` | JSON null |
| dict | `{"a": 1}` | JSON 物件 |
| list | `[1, 2, 3]` | JSON 陣列 |

### 進階類型

#### 二進位資料 (bytes)

```python
# 存儲二進位資料
binary_data = b"Binary \x00\x01\x02 data"
toolkit.setter("binary_key", binary_data)

# 自動識別並還原
retrieved = toolkit.getter("binary_key")
print(type(retrieved))  # <class 'bytes'>
print(retrieved == binary_data)  # True
```

#### NumPy 陣列

```python
import numpy as np

# 各種 NumPy 資料類型
int_array = np.array([1, 2, 3, 4, 5])
float_array = np.array([1.1, 2.2, 3.3], dtype=np.float32)
matrix = np.array([[1, 2], [3, 4]])

# 全部自動處理
toolkit.setter("int_array", int_array)
toolkit.setter("float_array", float_array)
toolkit.setter("matrix", matrix)

# 完整還原，包括 dtype
retrieved = toolkit.getter("float_array")
print(retrieved.dtype)  # float32
```

## 🔍 序列化內部機制

### 序列化流程

```python
# 簡化的序列化邏輯
def serialize_value(value):
    # 1. 檢查是否為 bytes
    if isinstance(value, bytes):
        return {
            "__type__": "bytes",
            "__value__": base64.b64encode(value).decode('utf-8')
        }
    
    # 2. 檢查是否為 NumPy 陣列
    if isinstance(value, np.ndarray):
        return {
            "__type__": "numpy",
            "__value__": value.tolist(),
            "__dtype__": str(value.dtype),
            "__shape__": value.shape
        }
    
    # 3. 其他類型使用 JSON
    return json.dumps(value, ensure_ascii=False)
```

### 反序列化流程

```python
# 簡化的反序列化邏輯
def deserialize_value(data):
    # 1. 嘗試 JSON 解析
    try:
        obj = json.loads(data)
        
        # 2. 檢查特殊類型標記
        if isinstance(obj, dict) and "__type__" in obj:
            if obj["__type__"] == "bytes":
                return base64.b64decode(obj["__value__"])
            elif obj["__type__"] == "numpy":
                array = np.array(obj["__value__"])
                return array.astype(obj["__dtype__"])
        
        return obj
    except:
        # 3. 無法解析則返回原始 bytes
        return data
```

## 🎨 處理複雜資料結構

### 巢狀結構

```python
# 複雜的巢狀資料
complex_data = {
    "user": {
        "id": 1001,
        "profile": {
            "name": "Alice",
            "avatar": b"PNG\x89\x50\x4E\x47",  # 二進位圖片資料
            "preferences": {
                "theme": "dark",
                "notifications": True
            }
        },
        "scores": np.array([95, 87, 92, 88, 90]),
        "metadata": {
            "created_at": "2024-01-01",
            "last_login": None
        }
    }
}

# 一行搞定！
toolkit.setter("user:1001:full", complex_data)

# 完整還原所有類型
retrieved = toolkit.getter("user:1001:full")
print(type(retrieved["user"]["profile"]["avatar"]))  # <class 'bytes'>
print(type(retrieved["user"]["scores"]))  # <class 'numpy.ndarray'>
```

### 列表中的混合類型

```python
# 混合類型列表
mixed_list = [
    "text",
    42,
    3.14,
    True,
    None,
    {"nested": "dict"},
    [1, 2, 3],
    b"binary",
    np.array([1, 2, 3])
]

toolkit.setter("mixed_list", mixed_list)
retrieved = toolkit.getter("mixed_list")

# 每個元素都保持原始類型
for i, item in enumerate(retrieved):
    print(f"Index {i}: {type(item)} = {item}")
```

## 🚀 效能考量

### 序列化效能比較

```python
import time
import pickle
import json

data = {"users": [{"id": i, "name": f"User{i}"} for i in range(1000)]}

# JSON 序列化
start = time.time()
json_data = json.dumps(data)
json_time = time.time() - start

# Pickle 序列化
start = time.time()
pickle_data = pickle.dumps(data)
pickle_time = time.time() - start

print(f"JSON: {json_time:.4f}s, 大小: {len(json_data)} bytes")
print(f"Pickle: {pickle_time:.4f}s, 大小: {len(pickle_data)} bytes")

# 結果：JSON 通常較大但更安全，適合網路傳輸
```

### 優化建議

1. **大型資料壓縮**
   ```python
   import gzip
   
   # 對大型資料進行壓縮
   large_data = {"huge": "data" * 10000}
   
   # 手動壓縮
   compressed = gzip.compress(
       json.dumps(large_data).encode('utf-8')
   )
   toolkit.setter("compressed_data", compressed)
   ```

2. **避免過度巢狀**
   ```python
   # ❌ 避免過深的巢狀
   deeply_nested = {"a": {"b": {"c": {"d": {"e": "value"}}}}}
   
   # ✅ 扁平化結構
   flat_structure = {
       "a_b_c_d_e": "value"
   }
   ```

3. **批次操作**
   ```python
   # 使用批次操作減少序列化開銷
   batch_data = {
       f"key:{i}": {"id": i, "data": f"value{i}"}
       for i in range(1000)
   }
   toolkit.batch_set(batch_data)  # 比逐個設定快很多
   ```

## 🛠️ 自定義序列化

### 處理不支援的類型

```python
from datetime import datetime
import json

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# 使用自定義編碼器
data = {
    "created": datetime.now(),
    "user": "Alice"
}

# 手動序列化
serialized = json.dumps(data, cls=DateTimeEncoder)
toolkit.client.set("custom_data", serialized)
```

### 建立包裝器類別

```python
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class User:
    id: int
    name: str
    created_at: datetime
    
    def to_dict(self):
        """轉換為可序列化的字典"""
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        """從字典還原"""
        return cls(
            id=data["id"],
            name=data["name"],
            created_at=datetime.fromisoformat(data["created_at"])
        )

# 使用範例
user = User(id=1, name="Alice", created_at=datetime.now())
toolkit.setter("user:1", user.to_dict())

# 還原
data = toolkit.getter("user:1")
restored_user = User.from_dict(data)
```

## 🔍 除錯序列化問題

### 檢查序列化結果

```python
from redis_toolkit.utils import serialize_value

# 檢查資料如何被序列化
test_data = {
    "text": "Hello",
    "number": 42,
    "binary": b"bytes",
    "array": np.array([1, 2, 3])
}

serialized = serialize_value(test_data)
print("序列化結果:")
print(serialized)
print(f"大小: {len(serialized)} bytes")
```

### 處理序列化錯誤

```python
from redis_toolkit.exceptions import SerializationError

# 自定義類別（無法直接序列化）
class CustomClass:
    def __init__(self, value):
        self.value = value

try:
    toolkit.setter("custom", CustomClass(42))
except SerializationError as e:
    print(f"序列化失敗: {e}")
    # 改為存儲可序列化的表示
    toolkit.setter("custom", {"value": 42})
```

## 📚 最佳實踐

1. **保持資料結構簡單**
   - 優先使用原生 Python 類型
   - 避免存儲類別實例，改用字典

2. **注意資料大小**
   - Redis 單個值的大小限制為 512MB
   - 大型資料考慮分片或壓縮

3. **版本相容性**
   - 序列化格式可能隨版本變化
   - 重要資料考慮版本標記

4. **安全考量**
   - 永遠不要反序列化不受信任的資料
   - 定期審查存儲的資料類型

## 🎯 下一步

了解了序列化機制後，您可以：

- 學習[發布訂閱](./pubsub.md)功能，了解如何傳遞序列化的訊息
- 查看[配置選項](./configuration.md)，自定義序列化行為
- 探索[媒體處理](/advanced/media-processing.md)，了解二進位資料的進階應用

::: tip 小結
Redis Toolkit 的序列化系統讓您無需關心底層細節，專注於應用邏輯。記住：安全第一，簡單至上！
:::