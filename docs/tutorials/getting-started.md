# 快速開始

本教程將帶您快速了解如何使用 Redis Toolkit。

## 安裝

### 基本安裝

```bash
pip install redis-toolkit
```

### 包含媒體處理支援

```bash
# 圖片處理支援
pip install redis-toolkit[cv2]

# 音頻處理支援
pip install redis-toolkit[audio]

# 完整功能
pip install redis-toolkit[all]
```

## 基本使用

### 1. 簡單的鍵值操作

```python
from redis_toolkit import RedisToolkit

# 創建 toolkit 實例
toolkit = RedisToolkit()

# 存儲數據 - 自動序列化
toolkit.setter("user:1", {"name": "Alice", "age": 25, "active": True})
toolkit.setter("scores", [95, 87, 92, 88])
toolkit.setter("config", {"debug": False, "timeout": 30})

# 讀取數據 - 自動反序列化
user = toolkit.getter("user:1")      # 返回字典
scores = toolkit.getter("scores")    # 返回列表
config = toolkit.getter("config")    # 返回字典

# 刪除數據
toolkit.deleter("user:1")
```

### 2. 連接選項

#### 選項 1：使用默認連接

```python
# 連接到 localhost:6379, db=0
toolkit = RedisToolkit()
```

#### 選項 2：傳入現有的 Redis 客戶端

```python
from redis import Redis

# 創建您自己的 Redis 客戶端
redis_client = Redis(
    host='redis-server.example.com',
    port=6379,
    password='your-password'
)

# 傳給 RedisToolkit
toolkit = RedisToolkit(redis=redis_client)
```

#### 選項 3：使用配置

```python
from redis_toolkit import RedisToolkit, RedisConnectionConfig

# 創建配置
config = RedisConnectionConfig(
    host='redis-server.example.com',
    port=6379,
    password='your-password',
    db=1,
    connection_timeout=5.0,
    socket_timeout=10.0
)

# 使用配置創建 toolkit
toolkit = RedisToolkit(config=config)
```

## 進階配置

### 自定義選項

```python
from redis_toolkit import RedisOptions

options = RedisOptions(
    # 日誌
    is_logger_info=True,
    log_level="DEBUG",
    max_log_size=512,
    
    # 安全性
    max_value_size=50 * 1024 * 1024,  # 50MB 限制
    max_key_length=256,
    enable_validation=True,
    
    # 性能
    use_connection_pool=True,
    max_connections=50
)

toolkit = RedisToolkit(options=options)
```

### SSL/TLS 連接

```python
config = RedisConnectionConfig(
    host='secure-redis.example.com',
    port=6380,
    ssl=True,
    ssl_cert_reqs='required',
    ssl_ca_certs='/path/to/ca.pem'
)

toolkit = RedisToolkit(config=config)
```

## 下一步

完成本教程後，您可以：

- 學習[第一個 Redis 應用教程](/tutorials/first-redis-app)
- 查看[批次操作指南](/how-to/batch-operations)
- 探索[API 參考文檔](/reference/api/core)