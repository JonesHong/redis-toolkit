# 配置 API

Redis Toolkit 提供兩個主要的配置類：`RedisConnectionConfig` 和 `RedisOptions`。

## RedisConnectionConfig

Redis 連接配置類，用於設置連接參數。

### 類定義

```python
@dataclass
class RedisConnectionConfig:
    """Redis 連接配置"""
    
    # 基本連接參數
    host: str = 'localhost'
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    username: Optional[str] = None
    
    # 編碼設置
    encoding: str = 'utf-8'
    decode_responses: bool = False  # 必須為 False
    
    # 連接池參數
    max_connections: Optional[int] = None
    
    # 超時設置
    connection_timeout: Optional[float] = None
    socket_timeout: Optional[float] = None
    socket_connect_timeout: Optional[float] = None
    
    # 重試設置
    retry_on_timeout: bool = False
    retry_on_error: bool = False
    
    # SSL/TLS 設置
    ssl: bool = False
    ssl_keyfile: Optional[str] = None
    ssl_certfile: Optional[str] = None
    ssl_cert_reqs: str = 'required'
    ssl_ca_certs: Optional[str] = None
    ssl_check_hostname: bool = True
    
    # 健康檢查
    health_check_interval: int = 0
    
    # Socket 選項
    socket_keepalive: bool = False
    socket_keepalive_options: Optional[Dict[str, int]] = None
```

### 使用示例

```python
from redis_toolkit import RedisConnectionConfig

# 基本配置
config = RedisConnectionConfig(
    host='localhost',
    port=6379,
    db=0
)

# 帶密碼的配置
secure_config = RedisConnectionConfig(
    host='redis.example.com',
    port=6379,
    password='your_password',
    username='your_username'  # Redis 6.0+
)

# SSL 配置
ssl_config = RedisConnectionConfig(
    host='redis.example.com',
    port=6380,
    ssl=True,
    ssl_cert_reqs='required',
    ssl_ca_certs='/path/to/ca-cert.pem'
)

# 高級配置
advanced_config = RedisConnectionConfig(
    host='redis.example.com',
    port=6379,
    password='your_password',
    max_connections=100,
    connection_timeout=10,
    socket_timeout=5,
    retry_on_timeout=True,
    health_check_interval=30,
    socket_keepalive=True,
    socket_keepalive_options={
        'TCP_KEEPIDLE': 120,
        'TCP_KEEPINTVL': 30,
        'TCP_KEEPCNT': 3
    }
)
```

### 配置驗證

```python
config = RedisConnectionConfig(
    host='redis.example.com',
    ssl=True,
    ssl_certfile='/path/to/cert.pem'
)

# 驗證配置
try:
    config.validate()
except ValueError as e:
    print(f"配置錯誤: {e}")
```

## RedisOptions

Redis Toolkit 行為配置類，控制工具包的運行方式。

### 類定義

```python
@dataclass
class RedisOptions:
    """Redis Toolkit 選項配置"""
    
    # 日誌設置
    is_logger_info: bool = True
    log_level: str = "INFO"
    log_path: Optional[str] = None
    max_log_size: int = 256
    
    # 訂閱者設置
    subscriber_retry_delay: float = 5.0
    subscriber_stop_timeout: float = 5.0
    
    # 連接池設置
    use_connection_pool: bool = True
    max_connections: Optional[int] = None
    
    # 數據驗證
    enable_validation: bool = True
    max_value_size: int = 10 * 1024 * 1024  # 10MB
    max_key_length: int = 512
    
    # 序列化設置
    default_serializer: str = 'auto'  # 'json', 'pickle', 'auto'
    pickle_protocol: int = 4
```

### 使用示例

```python
from redis_toolkit import RedisOptions

# 基本選項
options = RedisOptions(
    is_logger_info=True,
    log_level="INFO"
)

# 開發環境選項
dev_options = RedisOptions(
    is_logger_info=True,
    log_level="DEBUG",
    max_log_size=1024,
    enable_validation=True,
    subscriber_retry_delay=2.0
)

# 生產環境選項
prod_options = RedisOptions(
    is_logger_info=True,
    log_level="WARNING",
    log_path="/var/log/app",
    use_connection_pool=True,
    max_connections=200,
    enable_validation=True,
    max_value_size=5 * 1024 * 1024  # 5MB
)

# 自定義序列化選項
custom_options = RedisOptions(
    default_serializer='pickle',
    pickle_protocol=5,  # Python 3.8+
    enable_validation=False  # 禁用驗證以提高性能
)
```

## DEFAULT_OPTIONS

預設的配置實例，可以直接使用或作為基礎進行修改。

```python
from redis_toolkit import DEFAULT_OPTIONS

# 使用預設選項
toolkit = RedisToolkit(options=DEFAULT_OPTIONS)

# 基於預設選項修改
import copy
custom_options = copy.deepcopy(DEFAULT_OPTIONS)
custom_options.log_level = "ERROR"
custom_options.max_connections = 100
```

## 配置組合使用

```python
from redis_toolkit import (
    RedisToolkit,
    RedisConnectionConfig,
    RedisOptions
)

# 創建配置
config = RedisConnectionConfig(
    host='redis.example.com',
    port=6379,
    password='secure_password',
    ssl=True
)

options = RedisOptions(
    log_level="INFO",
    use_connection_pool=True,
    max_connections=50
)

# 使用配置創建 RedisToolkit
toolkit = RedisToolkit(
    config=config,
    options=options
)
```

## 環境變數支援

您可以從環境變數載入配置：

```python
import os
from redis_toolkit import RedisConnectionConfig, RedisOptions

def load_config_from_env():
    """從環境變數載入配置"""
    config = RedisConnectionConfig(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', '6379')),
        password=os.getenv('REDIS_PASSWORD'),
        db=int(os.getenv('REDIS_DB', '0')),
        ssl=os.getenv('REDIS_SSL', 'false').lower() == 'true'
    )
    
    options = RedisOptions(
        is_logger_info=os.getenv('DEBUG', 'false').lower() == 'true',
        log_level=os.getenv('LOG_LEVEL', 'INFO'),
        use_connection_pool=os.getenv('USE_POOL', 'true').lower() == 'true',
        max_connections=int(os.getenv('MAX_CONNECTIONS', '50'))
    )
    
    return config, options

# 使用環境配置
config, options = load_config_from_env()
toolkit = RedisToolkit(config=config, options=options)
```

## 配置檔案支援

支援從 YAML 或 JSON 載入配置：

```python
import yaml
import json
from redis_toolkit import RedisConnectionConfig, RedisOptions

def load_config_from_yaml(file_path):
    """從 YAML 檔案載入配置"""
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)
    
    config = RedisConnectionConfig(**data.get('connection', {}))
    options = RedisOptions(**data.get('options', {}))
    
    return config, options

def load_config_from_json(file_path):
    """從 JSON 檔案載入配置"""
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    config = RedisConnectionConfig(**data.get('connection', {}))
    options = RedisOptions(**data.get('options', {}))
    
    return config, options
```

### YAML 配置範例

```yaml
# config.yaml
connection:
  host: redis.example.com
  port: 6379
  password: ${REDIS_PASSWORD}
  db: 0
  ssl: true
  ssl_ca_certs: /etc/ssl/redis-ca.pem
  max_connections: 100

options:
  is_logger_info: true
  log_level: INFO
  log_path: /var/log/redis-toolkit
  use_connection_pool: true
  max_connections: 100
  enable_validation: true
  max_value_size: 5242880  # 5MB
```

## 配置最佳實踐

1. **環境分離**：為不同環境使用不同的配置
2. **安全性**：不要在代碼中硬編碼密碼
3. **連接池**：生產環境始終使用連接池
4. **日誌級別**：生產環境使用 WARNING 或 ERROR
5. **驗證**：開發環境啟用完整驗證，生產環境可適當放寬
6. **超時設置**：根據網絡條件調整超時值

## 相關文檔

- [核心 API](./core.md)
- [配置指南](/guide/configuration.md)
- [效能優化](/advanced/performance.md)