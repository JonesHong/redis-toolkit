# 工具函數 API

Redis Toolkit 提供多種實用工具函數和異常類別。

## 序列化函數

### serialize_value()

```python
def serialize_value(
    value: Any,
    serializer: str = 'auto'
) -> bytes:
    """
    序列化值為二進制數據
    
    參數:
        value: 要序列化的值
        serializer: 序列化器類型 ('auto', 'json', 'pickle')
        
    返回:
        bytes: 序列化後的數據
        
    異常:
        SerializationError: 序列化失敗時
    """
```

### deserialize_value()

```python
def deserialize_value(
    data: bytes,
    default: Any = None
) -> Any:
    """
    反序列化二進制數據
    
    參數:
        data: 要反序列化的數據
        default: 反序列化失敗時的默認值
        
    返回:
        反序列化後的值
        
    異常:
        SerializationError: 反序列化失敗且未提供默認值時
    """
```

### 使用示例

```python
from redis_toolkit.utils import serialize_value, deserialize_value

# 自動選擇序列化器
data = {'name': 'Alice', 'age': 30}
serialized = serialize_value(data)  # 使用 JSON

# 指定序列化器
import numpy as np
array = np.array([1, 2, 3, 4, 5])
serialized = serialize_value(array, serializer='pickle')

# 反序列化
restored = deserialize_value(serialized)

# 使用默認值
restored = deserialize_value(b'invalid_data', default={})
```

## 重試裝飾器

### simple_retry()

```python
def simple_retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    簡單重試裝飾器
    
    參數:
        max_attempts: 最大重試次數
        delay: 初始延遲時間（秒）
        backoff: 延遲時間倍數
        exceptions: 要捕獲的異常類型
        
    使用:
        @simple_retry(max_attempts=3, delay=1.0)
        def unstable_operation():
            # 可能失敗的操作
            pass
    """
```

### with_retry()

```python
def with_retry(
    func: Callable,
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
) -> Any:
    """
    使用重試執行函數
    
    參數:
        func: 要執行的函數
        max_attempts: 最大重試次數
        delay: 初始延遲時間
        backoff: 延遲時間倍數
        exceptions: 要捕獲的異常類型
        
    返回:
        函數執行結果
    """
```

### 使用示例

```python
from redis_toolkit.utils import simple_retry, with_retry
import random

# 使用裝飾器
@simple_retry(max_attempts=3, delay=0.5)
def fetch_data():
    if random.random() < 0.7:
        raise ConnectionError("網絡錯誤")
    return "數據"

# 直接調用
result = fetch_data()

# 使用函數形式
def unstable_task():
    if random.random() < 0.5:
        raise ValueError("隨機錯誤")
    return "成功"

result = with_retry(
    unstable_task,
    max_attempts=5,
    delay=1.0,
    exceptions=(ValueError,)
)
```

## 驗證工具

### validate_key()

```python
def validate_key(key: str, max_length: int = 512) -> None:
    """
    驗證 Redis 鍵名
    
    參數:
        key: 要驗證的鍵名
        max_length: 最大長度
        
    異常:
        ValidationError: 鍵名無效時
    """
```

### validate_value_size()

```python
def validate_value_size(
    value: Any,
    max_size: int = 10 * 1024 * 1024
) -> None:
    """
    驗證值的大小
    
    參數:
        value: 要驗證的值
        max_size: 最大大小（字節）
        
    異常:
        ValidationError: 值太大時
    """
```

### 使用示例

```python
from redis_toolkit.utils import validate_key, validate_value_size

# 驗證鍵名
try:
    validate_key("user:123:profile")
    validate_key("a" * 1000)  # 太長
except ValidationError as e:
    print(f"鍵名無效: {e}")

# 驗證值大小
large_data = {"data": "x" * 1000000}
try:
    validate_value_size(large_data, max_size=500000)
except ValidationError as e:
    print(f"值太大: {e}")
```

## 連接池管理

### pool_manager

全域連接池管理器實例。

```python
from redis_toolkit import pool_manager

# 配置連接池
pool_manager.configure_pool(
    'default',
    host='localhost',
    port=6379,
    max_connections=50
)

# 獲取連接池
pool = pool_manager.get_pool('default')

# 清理連接池
pool_manager.cleanup_pool('default')

# 清理所有連接池
pool_manager.cleanup_all()
```

## 異常類別

### RedisToolkitError

所有 Redis Toolkit 異常的基類。

```python
class RedisToolkitError(Exception):
    """Redis Toolkit 基礎異常類"""
```

### SerializationError

序列化相關錯誤。

```python
class SerializationError(RedisToolkitError):
    """序列化錯誤"""
```

### ValidationError

驗證相關錯誤。

```python
class ValidationError(RedisToolkitError):
    """驗證錯誤"""
```

### ConnectionPoolError

連接池相關錯誤。

```python
class ConnectionPoolError(RedisToolkitError):
    """連接池錯誤"""
```

### SubscriberError

訂閱者相關錯誤。

```python
class SubscriberError(RedisToolkitError):
    """訂閱者錯誤"""
```

### 異常處理示例

```python
from redis_toolkit import RedisToolkit
from redis_toolkit.exceptions import (
    RedisToolkitError,
    SerializationError,
    ValidationError,
    ConnectionPoolError
)

toolkit = RedisToolkit()

try:
    # 可能出錯的操作
    toolkit.set('key', complex_object)
    
except SerializationError as e:
    print(f"無法序列化對象: {e}")
    
except ValidationError as e:
    print(f"驗證失敗: {e}")
    
except ConnectionPoolError as e:
    print(f"連接池錯誤: {e}")
    
except RedisToolkitError as e:
    print(f"Redis Toolkit 錯誤: {e}")
```

## 輔助函數

### get_redis_info()

獲取 Redis 服務器信息。

```python
def get_redis_info(client: Redis) -> Dict[str, Any]:
    """
    獲取 Redis 服務器信息
    
    參數:
        client: Redis 客戶端
        
    返回:
        服務器信息字典
    """
```

### format_bytes()

格式化字節大小。

```python
def format_bytes(size: int) -> str:
    """
    格式化字節大小為人類可讀格式
    
    參數:
        size: 字節大小
        
    返回:
        格式化的字符串（如 "1.5 MB"）
    """
```

### 使用示例

```python
from redis_toolkit.utils import get_redis_info, format_bytes

# 獲取服務器信息
info = get_redis_info(toolkit.client)
print(f"Redis 版本: {info['redis_version']}")
print(f"已用內存: {format_bytes(info['used_memory'])}")

# 格式化大小
size = 1536000  # 字節
print(format_bytes(size))  # "1.5 MB"
```

## 最佳實踐

1. **錯誤處理**：始終捕獲特定的異常類型
2. **重試策略**：合理設置重試次數和延遲
3. **驗證**：在存儲前驗證數據
4. **序列化**：選擇適合的序列化器
5. **連接池**：使用全域連接池管理器

## 相關文檔

- [核心 API](./core.md)
- [配置選項](./options.md)
- [錯誤處理指南](/advanced/error-handling.md)