# 基礎使用

本章將詳細介紹 Redis Toolkit 的核心功能，讓您掌握日常開發所需的各種操作。

## 🔧 初始化方式

Redis Toolkit 提供多種初始化方式，滿足不同場景需求：

### 1. 最簡單的方式

```python
from redis_toolkit import RedisToolkit

# 使用預設配置 (localhost:6379)
toolkit = RedisToolkit()
```

### 2. 自定義連接配置

```python
from redis_toolkit import RedisToolkit, RedisConnectionConfig

# 使用配置物件
config = RedisConnectionConfig(
    host='192.168.1.100',
    port=6380,
    db=1,
    password='your_password'
)
toolkit = RedisToolkit(config=config)
```

### 3. 使用現有 Redis 客戶端

```python
import redis
from redis_toolkit import RedisToolkit

# 如果您已經有 Redis 客戶端
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    decode_responses=False  # 重要：必須為 False
)
toolkit = RedisToolkit(redis=redis_client)
```

### 4. 進階選項配置

```python
from redis_toolkit import RedisToolkit, RedisOptions

options = RedisOptions(
    is_logger_info=True,        # 啟用日誌
    max_log_size=512,          # 日誌大小限制
    log_level="INFO",          # 日誌級別
    max_value_size=10*1024*1024  # 最大值大小 (10MB)
)

toolkit = RedisToolkit(options=options)
```

## 📝 基本操作

### 存儲資料 (setter)

```python
# 存儲各種資料類型
toolkit.setter("string_key", "Hello World")
toolkit.setter("number_key", 42)
toolkit.setter("float_key", 3.14159)
toolkit.setter("bool_key", True)
toolkit.setter("list_key", [1, 2, 3, 4, 5])
toolkit.setter("dict_key", {"name": "Alice", "age": 25})

# 設定過期時間
toolkit.setter("temp_key", "臨時資料", ex=60)  # 60秒後過期
toolkit.setter("temp_key2", "臨時資料", px=5000)  # 5000毫秒後過期
```

### 讀取資料 (getter)

```python
# 自動反序列化為原始類型
text = toolkit.getter("string_key")      # str
number = toolkit.getter("number_key")    # int
pi = toolkit.getter("float_key")         # float
flag = toolkit.getter("bool_key")        # bool
items = toolkit.getter("list_key")       # list
user = toolkit.getter("dict_key")        # dict

# 處理不存在的鍵
result = toolkit.getter("non_existent_key")  # 返回 None
```

### 刪除資料

```python
# 刪除單個鍵
toolkit.delete("unwanted_key")

# 刪除多個鍵
toolkit.client.delete("key1", "key2", "key3")

# 清空當前資料庫（謹慎使用！）
toolkit.client.flushdb()
```

### 檢查鍵是否存在

```python
# 使用 exists 方法
if toolkit.client.exists("user:1001"):
    user = toolkit.getter("user:1001")
    print(f"找到用戶: {user['name']}")
else:
    print("用戶不存在")
```

## 🎯 批次操作

處理大量資料時，批次操作可以顯著提升效能：

### 批次設定 (batch_set)

```python
# 準備批次資料
batch_data = {
    "user:1001": {"name": "Alice", "score": 95},
    "user:1002": {"name": "Bob", "score": 87},
    "user:1003": {"name": "Charlie", "score": 92},
    "user:1004": {"name": "David", "score": 88},
    "user:1005": {"name": "Eve", "score": 91}
}

# 一次性存儲
toolkit.batch_set(batch_data)
```

### 批次讀取 (batch_get)

```python
# 準備要讀取的鍵列表
keys = ["user:1001", "user:1002", "user:1003", "user:1004", "user:1005"]

# 批次讀取
results = toolkit.batch_get(keys)

# results 是一個字典
for key, value in results.items():
    if value:
        print(f"{key}: {value['name']} - 分數: {value['score']}")
```

## 🔄 資料類型處理

### 處理複雜巢狀結構

```python
# 複雜的巢狀資料
complex_data = {
    "company": "TechCorp",
    "employees": [
        {"id": 1, "name": "Alice", "skills": ["Python", "Redis"]},
        {"id": 2, "name": "Bob", "skills": ["Java", "MongoDB"]}
    ],
    "metadata": {
        "founded": 2020,
        "active": True,
        "revenue": 1000000.50
    }
}

toolkit.setter("company:techcorp", complex_data)
retrieved = toolkit.getter("company:techcorp")

# 完整保留結構和類型
print(retrieved["metadata"]["active"])  # True (布林值)
print(type(retrieved["metadata"]["revenue"]))  # <class 'float'>
```

### 處理二進位資料

```python
# 存儲二進位資料
binary_data = b"This is binary data \x00\x01\x02"
toolkit.setter("binary_key", binary_data)

# 讀取時自動識別
retrieved = toolkit.getter("binary_key")
print(type(retrieved))  # <class 'bytes'>
print(retrieved)  # b'This is binary data \x00\x01\x02'
```

### NumPy 陣列支援

```python
import numpy as np

# 存儲 NumPy 陣列
array = np.array([1, 2, 3, 4, 5], dtype=np.float32)
toolkit.setter("numpy_array", array)

# 讀取並還原
retrieved = toolkit.getter("numpy_array")
print(type(retrieved))  # <class 'numpy.ndarray'>
print(retrieved.dtype)  # float32
```

## 🛡️ 錯誤處理

### 使用異常處理

```python
from redis_toolkit.exceptions import RedisToolkitError, SerializationError

try:
    # 嘗試操作
    toolkit.setter("key", some_data)
except SerializationError as e:
    print(f"序列化錯誤: {e}")
except RedisToolkitError as e:
    print(f"Redis Toolkit 錯誤: {e}")
except Exception as e:
    print(f"未預期的錯誤: {e}")
```

### 使用重試裝飾器

```python
from redis_toolkit.utils import with_retry

@with_retry(max_attempts=3, delay=1.0)
def reliable_operation():
    # 可能失敗的操作
    return toolkit.getter("important_key")

# 自動重試最多 3 次
result = reliable_operation()
```

## 🔐 進階技巧

### 使用管線 (Pipeline)

```python
# 使用管線批次執行命令
pipe = toolkit.client.pipeline()

# 排隊多個命令
for i in range(100):
    pipe.set(f"key:{i}", f"value:{i}")

# 一次執行所有命令
pipe.execute()
```

### 使用 Context Manager

```python
# 自動資源管理
with RedisToolkit() as toolkit:
    toolkit.setter("temp_data", {"session": "12345"})
    data = toolkit.getter("temp_data")
    # 離開時自動清理資源
```

### 直接訪問 Redis 客戶端

```python
# 需要使用原生 Redis 命令時
toolkit.client.zadd("leaderboard", {"Alice": 100, "Bob": 90})
toolkit.client.zrange("leaderboard", 0, -1, desc=True, withscores=True)

# 使用 Redis 的其他功能
toolkit.client.expire("temp_key", 3600)
toolkit.client.ttl("temp_key")
```

## 📊 實用範例

### 快取系統

```python
class CacheSystem:
    def __init__(self, default_ttl=3600):
        self.toolkit = RedisToolkit()
        self.default_ttl = default_ttl
    
    def get_or_set(self, key, fetch_func, ttl=None):
        """獲取快取或設定新值"""
        # 嘗試從快取獲取
        cached = self.toolkit.getter(key)
        if cached is not None:
            return cached
        
        # 快取未命中，執行獲取函數
        value = fetch_func()
        
        # 存入快取
        self.toolkit.setter(key, value, ex=ttl or self.default_ttl)
        return value

# 使用範例
cache = CacheSystem()

def expensive_calculation():
    print("執行昂貴的計算...")
    return sum(range(1000000))

# 第一次呼叫會執行計算
result = cache.get_or_set("calc_result", expensive_calculation)

# 後續呼叫直接從快取返回
result = cache.get_or_set("calc_result", expensive_calculation)
```

### 計數器系統

```python
class CounterSystem:
    def __init__(self):
        self.toolkit = RedisToolkit()
    
    def increment(self, counter_name, amount=1):
        """增加計數器"""
        key = f"counter:{counter_name}"
        return self.toolkit.client.incr(key, amount)
    
    def get_count(self, counter_name):
        """獲取當前計數"""
        key = f"counter:{counter_name}"
        count = self.toolkit.client.get(key)
        return int(count) if count else 0
    
    def reset(self, counter_name):
        """重置計數器"""
        key = f"counter:{counter_name}"
        self.toolkit.client.delete(key)

# 使用範例
counter = CounterSystem()

# 頁面瀏覽計數
counter.increment("page_views")
counter.increment("page_views")
views = counter.get_count("page_views")
print(f"頁面瀏覽次數: {views}")
```

## 🎯 最佳實踐

1. **鍵命名規範**
   ```python
   # 使用冒號分隔命名空間
   "user:1001"          # 用戶資料
   "session:abc123"     # 會話資料
   "cache:api:users"    # API 快取
   ```

2. **設定適當的過期時間**
   ```python
   # 會話資料 - 較短過期時間
   toolkit.setter("session:123", session_data, ex=1800)  # 30分鐘
   
   # 快取資料 - 中等過期時間
   toolkit.setter("cache:users", users_list, ex=3600)  # 1小時
   ```

3. **處理大型資料**
   ```python
   # 壓縮大型資料
   import gzip
   
   large_data = {"huge": "data" * 1000}
   compressed = gzip.compress(json.dumps(large_data).encode())
   toolkit.setter("compressed_data", compressed)
   ```

## 📚 下一步學習

現在您已經掌握了基礎操作，可以繼續學習：

- [序列化功能](./serialization.md) - 深入了解資料類型處理
- [發布訂閱](./pubsub.md) - 學習訊息傳遞機制
- [批次操作進階](/advanced/batch-operations.md) - 處理大規模資料

::: tip 練習建議
嘗試使用 Redis Toolkit 實現一個簡單的任務隊列或排行榜系統，這將幫助您更好地理解這些功能。
:::