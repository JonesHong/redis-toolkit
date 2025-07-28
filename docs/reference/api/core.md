# 核心 API 參考

本文檔詳細介紹 Redis Toolkit 的核心 API。

## RedisToolkit 類

主要的工具類，提供所有 Redis 操作的高級接口。

### 構造函數

```python
RedisToolkit(
    redis: Optional[Redis] = None,
    config: Optional[RedisConnectionConfig] = None,
    options: Optional[RedisOptions] = None,
    channels: Optional[List[str]] = None,
    message_handler: Optional[Callable] = None
)
```

#### 參數

- **redis** (`Redis`, 可選): 現有的 Redis 客戶端實例
- **config** (`RedisConnectionConfig`, 可選): 連接配置
- **options** (`RedisOptions`, 可選): 工具選項
- **channels** (`List[str]`, 可選): 要訂閱的頻道列表
- **message_handler** (`Callable`, 可選): 消息處理函數

#### 示例

```python
# 使用默認配置
toolkit = RedisToolkit()

# 使用自定義配置
config = RedisConnectionConfig(host='redis.example.com', port=6379)
toolkit = RedisToolkit(config=config)

# 作為訂閱者
def handler(channel, data):
    print(f"收到 {channel}: {data}")

toolkit = RedisToolkit(
    channels=['events', 'notifications'],
    message_handler=handler
)
```

### 核心方法

#### setter

存儲數據到 Redis，自動序列化。

```python
setter(key: str, value: Any) -> bool
```

**參數:**
- **key** (`str`): Redis 鍵
- **value** (`Any`): 要存儲的值（支援任何可序列化的 Python 對象）

**返回:** `bool` - 操作是否成功

**示例:**
```python
toolkit.setter("user:123", {"name": "Alice", "age": 30})
toolkit.setter("scores", [95, 87, 92])
```

#### getter

從 Redis 獲取數據，自動反序列化。

```python
getter(key: str) -> Any
```

**參數:**
- **key** (`str`): Redis 鍵

**返回:** 存儲的值，如果鍵不存在則返回 `None`

**示例:**
```python
user = toolkit.getter("user:123")
if user:
    print(user['name'])
```

#### deleter

刪除 Redis 中的鍵。

```python
deleter(key: str) -> bool
```

**參數:**
- **key** (`str`): 要刪除的鍵

**返回:** `bool` - 是否成功刪除

**示例:**
```python
toolkit.deleter("user:123")
```

#### batch_set

批次設置多個鍵值對。

```python
batch_set(data: Dict[str, Any]) -> List[bool]
```

**參數:**
- **data** (`Dict[str, Any]`): 鍵值對字典

**返回:** `List[bool]` - 每個操作的成功狀態

**示例:**
```python
users = {
    "user:1": {"name": "Alice"},
    "user:2": {"name": "Bob"},
    "user:3": {"name": "Charlie"}
}
results = toolkit.batch_set(users)
```

#### batch_get

批次獲取多個鍵的值。

```python
batch_get(keys: List[str]) -> Dict[str, Any]
```

**參數:**
- **keys** (`List[str]`): 要獲取的鍵列表

**返回:** `Dict[str, Any]` - 鍵值對字典

**示例:**
```python
keys = ["user:1", "user:2", "user:3"]
users = toolkit.batch_get(keys)
for key, user in users.items():
    if user:
        print(f"{key}: {user['name']}")
```

#### publisher

發布消息到指定頻道。

```python
publisher(channel: str, data: Any) -> int
```

**參數:**
- **channel** (`str`): 頻道名稱
- **data** (`Any`): 要發布的數據

**返回:** `int` - 接收到消息的訂閱者數量

**示例:**
```python
toolkit.publisher("events", {
    "type": "user_login",
    "user_id": 123,
    "timestamp": time.time()
})
```

### 工具方法

#### health_check

檢查 Redis 連接健康狀態。

```python
health_check() -> bool
```

**返回:** `bool` - 連接是否健康

**示例:**
```python
if toolkit.health_check():
    print("Redis 連接正常")
else:
    print("Redis 連接異常")
```

#### cleanup

清理資源，關閉連接。

```python
cleanup() -> None
```

**示例:**
```python
toolkit.cleanup()
```

### 屬性

#### client

獲取底層的 Redis 客戶端實例。

```python
@property
client() -> Redis
```

**示例:**
```python
# 使用原生 Redis 命令
toolkit.client.zadd("leaderboard", {"alice": 100})
toolkit.client.expire("temp-key", 300)
```

#### config

獲取當前的連接配置。

```python
@property
config() -> RedisConnectionConfig
```

#### options

獲取當前的選項配置。

```python
@property
options() -> RedisOptions
```

## RedisConnectionConfig 類

Redis 連接配置類。

### 構造函數

```python
RedisConnectionConfig(
    host: str = 'localhost',
    port: int = 6379,
    db: int = 0,
    password: Optional[str] = None,
    socket_timeout: Optional[float] = None,
    socket_connect_timeout: Optional[float] = None,
    socket_keepalive: Optional[bool] = None,
    socket_keepalive_options: Optional[Dict] = None,
    connection_pool: Optional[Any] = None,
    unix_socket_path: Optional[str] = None,
    encoding: str = 'utf-8',
    encoding_errors: str = 'strict',
    charset: Optional[str] = None,
    errors: Optional[str] = None,
    decode_responses: bool = True,
    retry_on_timeout: bool = False,
    retry_on_error: Optional[List] = None,
    ssl: bool = False,
    ssl_keyfile: Optional[str] = None,
    ssl_certfile: Optional[str] = None,
    ssl_cert_reqs: str = 'required',
    ssl_ca_certs: Optional[str] = None,
    ssl_ca_path: Optional[str] = None,
    ssl_ca_data: Optional[str] = None,
    ssl_check_hostname: bool = False,
    ssl_password: Optional[str] = None,
    ssl_validate_ocsp: bool = False,
    ssl_validate_ocsp_stapled: bool = False,
    ssl_ocsp_context: Optional[Any] = None,
    ssl_ocsp_expected_cert: Optional[Any] = None,
    max_connections: Optional[int] = None,
    single_connection_client: bool = False,
    health_check_interval: int = 0,
    client_name: Optional[str] = None,
    username: Optional[str] = None,
    retry: Optional[Any] = None,
    redis_connect_func: Optional[Any] = None,
    credential_provider: Optional[Any] = None,
    connection_timeout: float = 10.0,
    max_idle_time: Optional[int] = None,
    idle_check_interval: Optional[int] = None
)
```

### 常用配置示例

#### 基本連接

```python
config = RedisConnectionConfig(
    host='localhost',
    port=6379,
    db=0
)
```

#### 密碼認證

```python
config = RedisConnectionConfig(
    host='redis.example.com',
    port=6379,
    password='secret-password'
)
```

#### SSL/TLS 連接

```python
config = RedisConnectionConfig(
    host='secure-redis.example.com',
    port=6380,
    ssl=True,
    ssl_cert_reqs='required',
    ssl_ca_certs='/path/to/ca.pem'
)
```

#### 連接池配置

```python
config = RedisConnectionConfig(
    host='localhost',
    port=6379,
    max_connections=100,
    socket_keepalive=True,
    socket_keepalive_options={
        1: 1,  # TCP_KEEPIDLE
        2: 1,  # TCP_KEEPINTVL
        3: 3,  # TCP_KEEPCNT
    }
)
```

### 方法

#### validate

驗證配置的有效性。

```python
validate() -> None
```

**拋出:** `ValueError` - 如果配置無效

**示例:**
```python
try:
    config.validate()
    print("配置有效")
except ValueError as e:
    print(f"配置錯誤: {e}")
```

#### to_dict

將配置轉換為字典。

```python
to_dict() -> Dict[str, Any]
```

**返回:** 配置的字典表示

**示例:**
```python
config_dict = config.to_dict()
print(config_dict['host'])
```

## RedisOptions 類

Redis Toolkit 的選項配置。

### 構造函數

```python
RedisOptions(
    enable_json_encoder: bool = True,
    use_connection_pool: bool = True,
    enable_compression: bool = False,
    compression_threshold: int = 1024,
    max_connections: int = 50,
    retry_max_attempts: int = 3,
    retry_base_delay: float = 0.1,
    retry_max_delay: float = 10.0,
    operation_timeout: Optional[float] = None,
    enable_pipeline_autobatch: bool = False,
    pipeline_autobatch_size: int = 100,
    is_logger_info: bool = True,
    log_level: str = "INFO",
    max_log_size: int = 1024,
    enable_metrics: bool = False,
    metrics_interval: int = 60,
    enable_key_prefix: bool = False,
    key_prefix: str = "",
    enable_key_expiry: bool = False,
    default_key_expiry: int = 3600,
    max_value_size: int = 512 * 1024 * 1024,  # 512MB
    max_key_length: int = 512,
    enable_validation: bool = True,
    custom_serializer: Optional[Any] = None,
    custom_deserializer: Optional[Any] = None
)
```

### 常用選項示例

#### 啟用壓縮

```python
options = RedisOptions(
    enable_compression=True,
    compression_threshold=512  # 壓縮大於 512 bytes 的值
)
```

#### 自定義序列化

```python
import msgpack

options = RedisOptions(
    custom_serializer=msgpack.packb,
    custom_deserializer=msgpack.unpackb
)
```

#### 調試模式

```python
options = RedisOptions(
    is_logger_info=True,
    log_level="DEBUG",
    enable_metrics=True
)
```

#### 鍵前綴和過期

```python
options = RedisOptions(
    enable_key_prefix=True,
    key_prefix="myapp:",
    enable_key_expiry=True,
    default_key_expiry=86400  # 24 小時
)
```

## 異常類

### RedisToolkitError

所有 Redis Toolkit 異常的基類。

```python
class RedisToolkitError(Exception):
    pass
```

### ValidationError

數據驗證失敗時拋出。

```python
class ValidationError(RedisToolkitError):
    pass
```

**示例:**
```python
try:
    toolkit.setter("x" * 1000, "value")  # 鍵太長
except ValidationError as e:
    print(f"驗證失敗: {e}")
```

### SerializationError

序列化或反序列化失敗時拋出。

```python
class SerializationError(RedisToolkitError):
    pass
```

**示例:**
```python
try:
    toolkit.setter("key", complex_object)
except SerializationError as e:
    print(f"序列化失敗: {e}")
```

### ConnectionError

連接問題時拋出。

```python
class ConnectionError(RedisToolkitError):
    pass
```

## 上下文管理器

RedisToolkit 支援上下文管理器協議：

```python
with RedisToolkit() as toolkit:
    toolkit.setter("key", "value")
    value = toolkit.getter("key")
# 自動調用 cleanup()
```

## 線程安全

RedisToolkit 是線程安全的，可以在多線程環境中共享實例：

```python
import threading

toolkit = RedisToolkit()

def worker(thread_id):
    for i in range(100):
        toolkit.setter(f"thread:{thread_id}:item:{i}", {"value": i})

threads = []
for i in range(10):
    t = threading.Thread(target=worker, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
```

## 性能考量

1. **連接池**: 默認啟用，確保高效的連接復用
2. **批次操作**: 使用 `batch_set` 和 `batch_get` 以獲得更好的性能
3. **管道**: 通過 `toolkit.client.pipeline()` 使用管道來組合操作
4. **序列化**: 考慮使用自定義序列化器以提升性能