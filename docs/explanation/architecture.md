# Redis Toolkit 架構設計

本文檔深入探討 Redis Toolkit 的架構設計理念、核心組件和設計決策。

## 設計理念

Redis Toolkit 的設計遵循以下核心理念：

1. **簡單性**：提供簡潔直觀的 API，隱藏複雜性
2. **靈活性**：支援多種使用場景和配置選項
3. **性能**：優化常見操作，提供批次處理能力
4. **可擴展性**：允許自定義序列化器和轉換器
5. **健壯性**：完善的錯誤處理和重試機制

## 整體架構

```
┌─────────────────────────────────────────────────────────┐
│                    應用程序層                            │
├─────────────────────────────────────────────────────────┤
│                  Redis Toolkit API                       │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐ │
│  │ RedisToolkit│  │ Batch Ops    │  │ Pub/Sub        │ │
│  │    Core     │  │ Manager      │  │ Manager        │ │
│  └─────────────┘  └──────────────┘  └────────────────┘ │
├─────────────────────────────────────────────────────────┤
│                    序列化層                              │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐ │
│  │ JSON        │  │ Pickle       │  │ Custom         │ │
│  │ Serializer  │  │ Serializer   │  │ Serializers   │ │
│  └─────────────┘  └──────────────┘  └────────────────┘ │
├─────────────────────────────────────────────────────────┤
│                    轉換器層                              │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐ │
│  │ Image       │  │ Audio        │  │ Video          │ │
│  │ Converter   │  │ Converter    │  │ Converter      │ │
│  └─────────────┘  └──────────────┘  └────────────────┘ │
├─────────────────────────────────────────────────────────┤
│                    連接管理層                            │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐ │
│  │ Connection  │  │ Connection   │  │ Health         │ │
│  │ Pool        │  │ Config       │  │ Monitor        │ │
│  └─────────────┘  └──────────────┘  └────────────────┘ │
├─────────────────────────────────────────────────────────┤
│                  Redis 客戶端層                          │
│                    (redis-py)                            │
└─────────────────────────────────────────────────────────┘
```

## 核心組件

### 1. RedisToolkit Core

核心類負責協調所有操作：

```python
class RedisToolkit:
    def __init__(self, ...):
        self._setup_connection()
        self._setup_serialization()
        self._setup_pubsub()
        self._setup_monitoring()
```

**責任：**
- 管理 Redis 連接生命週期
- 協調序列化/反序列化
- 提供統一的 API 接口
- 處理錯誤和重試邏輯

### 2. 連接管理

#### 連接池架構

```python
class ConnectionPoolManager:
    """管理 Redis 連接池"""
    
    def __init__(self, config: RedisConnectionConfig):
        self.pool = self._create_pool(config)
        self.health_checker = HealthChecker(self.pool)
        
    def _create_pool(self, config):
        """創建優化的連接池"""
        return redis.ConnectionPool(
            host=config.host,
            port=config.port,
            max_connections=config.max_connections,
            # 其他配置...
        )
```

**設計決策：**
- 使用連接池減少連接開銷
- 實現健康檢查機制
- 支援自動重連和故障轉移

#### 連接狀態管理

```
┌─────────┐      ┌───────────┐      ┌─────────┐
│  Init   │ ───> │ Connected │ ───> │ Closed  │
└─────────┘      └───────────┘      └─────────┘
     │                  │                  ^
     │                  v                  │
     │           ┌───────────┐            │
     └─────────> │   Error   │ ───────────┘
                 └───────────┘
```

### 3. 序列化架構

#### 序列化策略模式

```python
class SerializationStrategy(ABC):
    @abstractmethod
    def serialize(self, data: Any) -> bytes:
        pass
    
    @abstractmethod
    def deserialize(self, data: bytes) -> Any:
        pass

class JSONStrategy(SerializationStrategy):
    def serialize(self, data: Any) -> bytes:
        return json.dumps(data).encode('utf-8')
    
    def deserialize(self, data: bytes) -> Any:
        return json.loads(data.decode('utf-8'))
```

**序列化流程：**

```
數據 → 類型檢查 → 選擇序列化器 → 序列化 → 壓縮（可選） → 存儲
```

#### 類型映射

| Python 類型 | 序列化方式 | 存儲格式 |
|------------|-----------|---------|
| dict, list | JSON | UTF-8 字符串 |
| numpy.ndarray | Pickle | 二進制 |
| 自定義對象 | 自定義序列化器 | 自定義格式 |
| bytes | 直接存儲 | 原始字節 |

### 4. 批次操作優化

#### 管道封裝

```python
class BatchOperationManager:
    def __init__(self, client: Redis):
        self.client = client
        
    def batch_set(self, data: Dict[str, Any]) -> List[bool]:
        """優化的批次設置"""
        pipe = self.client.pipeline(transaction=False)
        
        for key, value in data.items():
            serialized = self._serialize(value)
            pipe.set(key, serialized)
        
        results = pipe.execute()
        return results
```

**優化策略：**
- 使用非事務管道提升性能
- 自動分批處理大數據集
- 並行化序列化操作

### 5. 發布/訂閱系統

#### 異步消息處理

```python
class PubSubManager:
    def __init__(self, toolkit: RedisToolkit):
        self.toolkit = toolkit
        self.subscriptions = {}
        self.thread_pool = ThreadPoolExecutor(max_workers=10)
        
    def subscribe(self, channel: str, handler: Callable):
        """訂閱頻道並異步處理消息"""
        pubsub = self.toolkit.client.pubsub()
        pubsub.subscribe(channel)
        
        def message_loop():
            for message in pubsub.listen():
                if message['type'] == 'message':
                    data = self._deserialize(message['data'])
                    self.thread_pool.submit(handler, channel, data)
        
        thread = Thread(target=message_loop, daemon=True)
        thread.start()
        self.subscriptions[channel] = (pubsub, thread)
```

**設計特點：**
- 非阻塞消息處理
- 自動序列化/反序列化
- 線程池管理

## 設計模式

### 1. 單例模式（可選）

```python
class SingletonRedisToolkit:
    _instance = None
    _lock = Lock()
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance
```

### 2. 工廠模式

```python
class ToolkitFactory:
    @staticmethod
    def create(toolkit_type: str) -> RedisToolkit:
        if toolkit_type == "basic":
            return RedisToolkit()
        elif toolkit_type == "cached":
            return CachedRedisToolkit()
        elif toolkit_type == "cluster":
            return ClusterRedisToolkit()
```

### 3. 裝飾器模式

```python
def with_retry(max_attempts: int = 3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except RedisError as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(2 ** attempt)
        return wrapper
    return decorator
```

## 性能考量

### 1. 連接復用

```
請求 1 ─┐
請求 2 ─┼─> 連接池 ─> Redis 服務器
請求 3 ─┘
```

通過連接池避免頻繁創建/銷毀連接。

### 2. 批次處理

```
單次操作: [請求] → [響應] → [請求] → [響應] ... (N 次往返)
批次操作: [批次請求] → [批次響應] (1 次往返)
```

減少網絡往返次數，提升吞吐量。

### 3. 序列化優化

- 使用快速序列化庫（如 msgpack）
- 實現序列化緩存
- 延遲反序列化

## 擴展性設計

### 1. 插件架構

```python
class PluginManager:
    def __init__(self):
        self.plugins = {}
        
    def register(self, name: str, plugin: Plugin):
        self.plugins[name] = plugin
        
    def execute(self, name: str, *args, **kwargs):
        if name in self.plugins:
            return self.plugins[name].execute(*args, **kwargs)
```

### 2. 自定義序列化器

```python
class CustomSerializer:
    def __init__(self, toolkit: RedisToolkit):
        toolkit.register_serializer('custom', self)
        
    def can_handle(self, obj: Any) -> bool:
        return isinstance(obj, MyCustomClass)
        
    def serialize(self, obj: MyCustomClass) -> bytes:
        # 自定義序列化邏輯
        pass
        
    def deserialize(self, data: bytes) -> MyCustomClass:
        # 自定義反序列化邏輯
        pass
```

### 3. 中間件支援

```python
class Middleware:
    def before_set(self, key: str, value: Any) -> Tuple[str, Any]:
        # 修改鍵或值
        return key, value
        
    def after_get(self, key: str, value: Any) -> Any:
        # 處理獲取的值
        return value
```

## 錯誤處理策略

### 1. 分層錯誤處理

```
應用層錯誤 ─> ValidationError
    │
序列化錯誤 ─> SerializationError
    │
連接錯誤 ──> ConnectionError
    │
Redis 錯誤 ─> RedisError
```

### 2. 重試機制

```python
class RetryStrategy:
    def __init__(self, max_attempts: int, base_delay: float):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        
    def execute(self, operation: Callable) -> Any:
        for attempt in range(self.max_attempts):
            try:
                return operation()
            except TransientError as e:
                if attempt == self.max_attempts - 1:
                    raise
                delay = self.calculate_delay(attempt)
                time.sleep(delay)
    
    def calculate_delay(self, attempt: int) -> float:
        # 指數退避
        return self.base_delay * (2 ** attempt)
```

## 安全性考量

### 1. 輸入驗證

```python
class Validator:
    @staticmethod
    def validate_key(key: str) -> None:
        if not key or len(key) > 512:
            raise ValidationError("Invalid key")
        if any(char in key for char in ['\n', '\r', ' ']):
            raise ValidationError("Key contains invalid characters")
    
    @staticmethod
    def validate_value_size(value: Any, max_size: int) -> None:
        size = len(str(value).encode('utf-8'))
        if size > max_size:
            raise ValidationError(f"Value too large: {size} bytes")
```

### 2. 連接安全

- 支援 SSL/TLS 加密連接
- 密碼認證
- ACL 支援（Redis 6.0+）

## 未來展望

### 計劃中的功能

1. **Redis Cluster 支援**
   - 自動分片
   - 故障轉移
   - 讀寫分離

2. **異步支援**
   - 基於 aioredis 的異步版本
   - 協程友好的 API

3. **更多序列化格式**
   - Protocol Buffers
   - MessagePack
   - Avro

4. **高級功能**
   - 分佈式鎖
   - 限流器
   - 緩存策略

### 架構演進

```
當前: 單機 Redis
  │
  v
階段 1: Redis Sentinel（高可用）
  │
  v
階段 2: Redis Cluster（分片）
  │
  v
階段 3: 多區域部署（全球化）
```

## 總結

Redis Toolkit 的架構設計注重簡單性和擴展性的平衡。通過分層架構、設計模式的應用和性能優化，我們提供了一個既易用又強大的 Redis 操作工具包。未來將繼續演進，支援更多的使用場景和部署模式。