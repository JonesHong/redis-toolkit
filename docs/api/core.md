# 核心 API - RedisToolkit

`RedisToolkit` 是 Redis Toolkit 的核心類別，提供所有主要功能的統一介面。

## 類別概覽

```python
class RedisToolkit:
    """增強版 Redis 客戶端，支援自動序列化和發布訂閱功能"""
    
    def __init__(
        self,
        config: Optional[RedisConnectionConfig] = None,
        options: Optional[RedisOptions] = None,
        client: Optional[Redis] = None
    ):
        """初始化 RedisToolkit"""
```

## 初始化參數

### config: RedisConnectionConfig
Redis 連接配置對象

### options: RedisOptions  
工具包行為配置選項

### client: Redis
預先建立的 Redis 客戶端實例（可選）

## 基本操作方法

### set()
設置鍵值對，自動序列化值

```python
def set(
    self,
    key: str,
    value: Any,
    expire: Optional[int] = None,
    nx: bool = False,
    xx: bool = False,
    keepttl: bool = False
) -> bool:
    """
    設置鍵值對
    
    參數:
        key: 鍵名
        value: 值（任意類型，自動序列化）
        expire: 過期時間（秒）
        nx: 僅當鍵不存在時設置
        xx: 僅當鍵存在時設置
        keepttl: 保留原有的 TTL
        
    返回:
        bool: 是否設置成功
    """
```

### get()
獲取值，自動反序列化

```python
def get(self, key: str, default: Any = None) -> Any:
    """
    獲取值
    
    參數:
        key: 鍵名
        default: 默認值
        
    返回:
        反序列化後的值
    """
```

### delete()
刪除鍵

```python
def delete(self, *keys: str) -> int:
    """
    刪除一個或多個鍵
    
    參數:
        *keys: 要刪除的鍵名
        
    返回:
        成功刪除的鍵數量
    """
```

### exists()
檢查鍵是否存在

```python
def exists(self, *keys: str) -> int:
    """
    檢查鍵是否存在
    
    參數:
        *keys: 要檢查的鍵名
        
    返回:
        存在的鍵數量
    """
```

## 批次操作

### batch_set()
批次設置多個鍵值對

```python
def batch_set(
    self,
    mapping: Dict[str, Any],
    expire: Optional[int] = None
) -> Dict[str, bool]:
    """
    批次設置鍵值對
    
    參數:
        mapping: 鍵值對字典
        expire: 統一的過期時間
        
    返回:
        設置結果字典
    """
```

### batch_get()
批次獲取多個值

```python
def batch_get(
    self,
    keys: List[str],
    default: Any = None
) -> Dict[str, Any]:
    """
    批次獲取值
    
    參數:
        keys: 鍵名列表
        default: 默認值
        
    返回:
        鍵值對字典
    """
```

### batch_delete()
批次刪除多個鍵

```python
def batch_delete(self, keys: List[str]) -> Dict[str, bool]:
    """
    批次刪除鍵
    
    參數:
        keys: 要刪除的鍵名列表
        
    返回:
        刪除結果字典
    """
```

## 發布訂閱

### publish()
發布消息

```python
def publish(self, channel: str, message: Any) -> int:
    """
    發布消息到頻道
    
    參數:
        channel: 頻道名稱
        message: 消息內容（自動序列化）
        
    返回:
        接收到消息的訂閱者數量
    """
```

### subscribe()
訂閱頻道

```python
def subscribe(
    self,
    *channels: str,
    handler: Optional[Callable] = None,
    error_handler: Optional[Callable] = None,
    daemon: bool = True
) -> 'Subscriber':
    """
    訂閱頻道
    
    參數:
        *channels: 要訂閱的頻道
        handler: 消息處理函數
        error_handler: 錯誤處理函數
        daemon: 是否為守護線程
        
    返回:
        Subscriber 實例
    """
```

### psubscribe()
模式訂閱

```python
def psubscribe(
    self,
    *patterns: str,
    handler: Optional[Callable] = None,
    error_handler: Optional[Callable] = None,
    daemon: bool = True
) -> 'Subscriber':
    """
    使用模式訂閱頻道
    
    參數:
        *patterns: 頻道模式
        handler: 消息處理函數
        error_handler: 錯誤處理函數
        daemon: 是否為守護線程
        
    返回:
        Subscriber 實例
    """
```

## 其他方法

### expire()
設置鍵的過期時間

```python
def expire(self, key: str, seconds: int) -> bool:
    """設置過期時間（秒）"""
```

### ttl()
獲取鍵的剩餘生存時間

```python
def ttl(self, key: str) -> int:
    """獲取 TTL（秒）"""
```

### keys()
查找符合模式的鍵

```python
def keys(self, pattern: str = "*") -> List[str]:
    """查找符合模式的鍵"""
```

### cleanup()
清理資源

```python
def cleanup(self) -> None:
    """清理資源，關閉連接"""
```

## 使用示例

### 基本使用

```python
from redis_toolkit import RedisToolkit

# 創建實例
toolkit = RedisToolkit()

# 設置值
toolkit.set('user:1', {'name': 'Alice', 'age': 30})

# 獲取值
user = toolkit.get('user:1')
print(user)  # {'name': 'Alice', 'age': 30}

# 批次操作
users = {
    'user:2': {'name': 'Bob', 'age': 25},
    'user:3': {'name': 'Charlie', 'age': 35}
}
toolkit.batch_set(users)

# 批次獲取
result = toolkit.batch_get(['user:1', 'user:2', 'user:3'])
```

### 發布訂閱

```python
# 訂閱頻道
def message_handler(channel, message):
    print(f"收到消息: {channel} -> {message}")

subscriber = toolkit.subscribe(
    'notifications',
    handler=message_handler
)

# 發布消息
toolkit.publish('notifications', {
    'type': 'alert',
    'message': '系統更新完成'
})

# 停止訂閱
subscriber.stop()
```

### 使用上下文管理器

```python
from redis_toolkit import RedisToolkit

with RedisToolkit() as toolkit:
    toolkit.set('temp_key', 'temp_value')
    value = toolkit.get('temp_key')
# 自動清理資源
```

## 注意事項

1. **自動序列化**：所有值都會自動序列化，支援 JSON、pickle 等格式
2. **線程安全**：使用連接池時，操作是線程安全的
3. **資源管理**：記得調用 `cleanup()` 或使用上下文管理器
4. **錯誤處理**：所有方法都包含適當的錯誤處理和日誌記錄

## 相關文檔

- [配置選項](./options.md)
- [轉換器 API](./converters.md)
- [工具函數](./utilities.md)