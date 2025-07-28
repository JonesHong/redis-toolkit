# 配置 API 參考

本文檔詳細介紹 Redis Toolkit 的配置選項和環境變量。

## 配置優先級

Redis Toolkit 使用以下優先級順序來決定配置：

1. 直接傳入的參數（最高優先級）
2. 環境變量
3. 配置文件
4. 默認值（最低優先級）

## 環境變量

### 連接配置

| 環境變量 | 描述 | 默認值 |
|---------|-----|--------|
| `REDIS_HOST` | Redis 服務器主機 | `localhost` |
| `REDIS_PORT` | Redis 服務器端口 | `6379` |
| `REDIS_PASSWORD` | Redis 密碼 | `None` |
| `REDIS_DB` | Redis 數據庫索引 | `0` |
| `REDIS_USERNAME` | Redis 用戶名（Redis 6.0+） | `None` |
| `REDIS_SSL` | 是否使用 SSL | `false` |
| `REDIS_SSL_CERT_PATH` | SSL 證書路徑 | `None` |
| `REDIS_SSL_KEY_PATH` | SSL 密鑰路徑 | `None` |
| `REDIS_SSL_CA_PATH` | SSL CA 證書路徑 | `None` |

### 連接池配置

| 環境變量 | 描述 | 默認值 |
|---------|-----|--------|
| `REDIS_MAX_CONNECTIONS` | 最大連接數 | `50` |
| `REDIS_SOCKET_TIMEOUT` | Socket 超時（秒） | `None` |
| `REDIS_SOCKET_CONNECT_TIMEOUT` | 連接超時（秒） | `None` |
| `REDIS_SOCKET_KEEPALIVE` | 啟用 TCP keepalive | `false` |
| `REDIS_CONNECTION_POOL_CLASS` | 自定義連接池類 | `None` |

### Redis Toolkit 選項

| 環境變量 | 描述 | 默認值 |
|---------|-----|--------|
| `REDIS_TOOLKIT_LOG_LEVEL` | 日誌級別 | `INFO` |
| `REDIS_TOOLKIT_ENABLE_METRICS` | 啟用指標收集 | `false` |
| `REDIS_TOOLKIT_KEY_PREFIX` | 全局鍵前綴 | `""` |
| `REDIS_TOOLKIT_DEFAULT_EXPIRY` | 默認過期時間（秒） | `None` |
| `REDIS_TOOLKIT_MAX_VALUE_SIZE` | 最大值大小（字節） | `536870912` |
| `REDIS_TOOLKIT_COMPRESSION_THRESHOLD` | 壓縮閾值（字節） | `1024` |

### 使用環境變量示例

```bash
# 設置環境變量
export REDIS_HOST=redis.example.com
export REDIS_PORT=6380
export REDIS_PASSWORD=secret
export REDIS_TOOLKIT_LOG_LEVEL=DEBUG

# 運行應用
python app.py
```

在代碼中：

```python
# 自動從環境變量讀取配置
toolkit = RedisToolkit()  # 將使用環境變量中的設置
```

## 配置文件

### YAML 配置

創建 `redis-toolkit.yml`:

```yaml
redis:
  host: redis.example.com
  port: 6379
  password: secret
  db: 0
  ssl:
    enabled: true
    cert_path: /path/to/cert.pem
    key_path: /path/to/key.pem
    ca_path: /path/to/ca.pem

connection_pool:
  max_connections: 100
  socket_timeout: 5.0
  socket_keepalive: true

toolkit:
  log_level: INFO
  enable_metrics: true
  key_prefix: "myapp:"
  compression:
    enabled: true
    threshold: 512
  validation:
    enabled: true
    max_key_length: 256
    max_value_size: 104857600  # 100MB
```

### JSON 配置

創建 `redis-toolkit.json`:

```json
{
  "redis": {
    "host": "redis.example.com",
    "port": 6379,
    "password": "secret",
    "db": 0
  },
  "connection_pool": {
    "max_connections": 100,
    "socket_timeout": 5.0
  },
  "toolkit": {
    "log_level": "INFO",
    "enable_metrics": true,
    "key_prefix": "myapp:"
  }
}
```

### 加載配置文件

```python
from redis_toolkit import RedisToolkit, load_config

# 從 YAML 文件加載
config = load_config('redis-toolkit.yml')
toolkit = RedisToolkit(config=config)

# 從 JSON 文件加載
config = load_config('redis-toolkit.json')
toolkit = RedisToolkit(config=config)
```

## 程序化配置

### 完整配置示例

```python
from redis_toolkit import (
    RedisToolkit, 
    RedisConnectionConfig, 
    RedisOptions
)

# 連接配置
connection_config = RedisConnectionConfig(
    # 基本連接
    host='redis.example.com',
    port=6379,
    password='secret',
    db=1,
    
    # 超時設置
    socket_timeout=5.0,
    socket_connect_timeout=3.0,
    connection_timeout=10.0,
    
    # 連接池
    max_connections=100,
    socket_keepalive=True,
    socket_keepalive_options={
        1: 1,  # TCP_KEEPIDLE
        2: 1,  # TCP_KEEPINTVL
        3: 3,  # TCP_KEEPCNT
    },
    
    # SSL/TLS
    ssl=True,
    ssl_cert_reqs='required',
    ssl_ca_certs='/path/to/ca.pem',
    ssl_certfile='/path/to/cert.pem',
    ssl_keyfile='/path/to/key.pem',
    
    # 高級選項
    health_check_interval=30,
    client_name='my-app',
    retry_on_timeout=True,
    retry_on_error=['ECONNRESET', 'EPIPE']
)

# 工具選項
toolkit_options = RedisOptions(
    # 序列化
    enable_json_encoder=True,
    custom_serializer=None,
    custom_deserializer=None,
    
    # 壓縮
    enable_compression=True,
    compression_threshold=1024,  # 1KB
    
    # 連接管理
    use_connection_pool=True,
    max_connections=100,
    
    # 重試策略
    retry_max_attempts=3,
    retry_base_delay=0.1,
    retry_max_delay=10.0,
    
    # 超時
    operation_timeout=30.0,
    
    # 管道
    enable_pipeline_autobatch=True,
    pipeline_autobatch_size=100,
    
    # 日誌
    is_logger_info=True,
    log_level="INFO",
    max_log_size=1024,
    
    # 指標
    enable_metrics=True,
    metrics_interval=60,
    
    # 鍵管理
    enable_key_prefix=True,
    key_prefix="myapp:",
    enable_key_expiry=True,
    default_key_expiry=3600,  # 1 小時
    
    # 驗證
    enable_validation=True,
    max_value_size=512 * 1024 * 1024,  # 512MB
    max_key_length=512
)

# 創建 toolkit
toolkit = RedisToolkit(
    config=connection_config,
    options=toolkit_options
)
```

## 配置驗證

### 自動驗證

```python
# 配置會在創建時自動驗證
try:
    config = RedisConnectionConfig(port=70000)  # 無效端口
except ValueError as e:
    print(f"配置錯誤: {e}")
```

### 手動驗證

```python
config = RedisConnectionConfig(host='redis.example.com')

# 驗證配置
try:
    config.validate()
    print("配置有效")
except ValueError as e:
    print(f"配置無效: {e}")

# 測試連接
toolkit = RedisToolkit(config=config)
if toolkit.health_check():
    print("連接成功")
else:
    print("連接失敗")
```

## 動態配置

### 運行時更新配置

```python
class DynamicRedisToolkit:
    def __init__(self):
        self._toolkit = None
        self._config = None
        
    def update_config(self, new_config):
        """動態更新配置"""
        # 驗證新配置
        new_config.validate()
        
        # 創建新的 toolkit
        old_toolkit = self._toolkit
        self._toolkit = RedisToolkit(config=new_config)
        self._config = new_config
        
        # 清理舊連接
        if old_toolkit:
            old_toolkit.cleanup()
    
    @property
    def toolkit(self):
        if not self._toolkit:
            raise RuntimeError("Toolkit 未初始化")
        return self._toolkit
```

### 配置熱重載

```python
import signal
import yaml

class ConfigReloader:
    def __init__(self, config_path):
        self.config_path = config_path
        self.toolkit = None
        self.reload_config()
        
        # 註冊信號處理器
        signal.signal(signal.SIGHUP, self._handle_reload)
    
    def reload_config(self):
        """重新加載配置"""
        with open(self.config_path) as f:
            config_data = yaml.safe_load(f)
        
        config = RedisConnectionConfig(**config_data['redis'])
        options = RedisOptions(**config_data['toolkit'])
        
        # 創建新的 toolkit
        old_toolkit = self.toolkit
        self.toolkit = RedisToolkit(config=config, options=options)
        
        # 清理舊的
        if old_toolkit:
            old_toolkit.cleanup()
        
        print(f"配置已重新加載: {self.config_path}")
    
    def _handle_reload(self, signum, frame):
        """處理重載信號"""
        self.reload_config()
```

## 配置最佳實踐

### 1. 生產環境配置

```python
# production.py
REDIS_CONFIG = RedisConnectionConfig(
    host=os.getenv('REDIS_HOST', 'redis.prod.example.com'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    password=os.getenv('REDIS_PASSWORD'),
    
    # 生產環境優化
    max_connections=200,
    socket_keepalive=True,
    health_check_interval=30,
    
    # SSL/TLS
    ssl=True,
    ssl_cert_reqs='required',
    ssl_ca_certs='/etc/ssl/certs/redis-ca.pem'
)

TOOLKIT_OPTIONS = RedisOptions(
    # 性能優化
    use_connection_pool=True,
    enable_compression=True,
    compression_threshold=2048,
    
    # 監控
    enable_metrics=True,
    metrics_interval=60,
    
    # 日誌
    log_level="WARNING",
    
    # 安全
    enable_validation=True,
    max_value_size=100 * 1024 * 1024  # 100MB
)
```

### 2. 開發環境配置

```python
# development.py
REDIS_CONFIG = RedisConnectionConfig(
    host='localhost',
    port=6379,
    db=15  # 使用獨立的數據庫
)

TOOLKIT_OPTIONS = RedisOptions(
    # 調試
    log_level="DEBUG",
    is_logger_info=True,
    
    # 開發便利性
    enable_key_prefix=True,
    key_prefix="dev:",
    
    # 較小的限制
    max_connections=10
)
```

### 3. 測試環境配置

```python
# test.py
REDIS_CONFIG = RedisConnectionConfig(
    host='localhost',
    port=6379,
    db=9  # 測試專用數據庫
)

TOOLKIT_OPTIONS = RedisOptions(
    # 測試優化
    log_level="ERROR",
    enable_metrics=False,
    
    # 快速失敗
    retry_max_attempts=1,
    operation_timeout=5.0,
    
    # 測試隔離
    enable_key_prefix=True,
    key_prefix=f"test:{uuid.uuid4()}:"
)
```

## 配置架構

### 使用配置類

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class AppConfig:
    """應用配置"""
    redis: RedisConnectionConfig
    toolkit: RedisOptions
    app_name: str
    environment: str
    
    @classmethod
    def from_env(cls, env: str = 'development'):
        """從環境創建配置"""
        if env == 'production':
            from .production import REDIS_CONFIG, TOOLKIT_OPTIONS
        elif env == 'development':
            from .development import REDIS_CONFIG, TOOLKIT_OPTIONS
        else:
            from .test import REDIS_CONFIG, TOOLKIT_OPTIONS
        
        return cls(
            redis=REDIS_CONFIG,
            toolkit=TOOLKIT_OPTIONS,
            app_name=os.getenv('APP_NAME', 'redis-toolkit-app'),
            environment=env
        )
```

### 配置工廠

```python
class ToolkitFactory:
    """Redis Toolkit 工廠"""
    
    @staticmethod
    def create(env: str = None) -> RedisToolkit:
        """根據環境創建 toolkit"""
        if env is None:
            env = os.getenv('APP_ENV', 'development')
        
        config = AppConfig.from_env(env)
        
        return RedisToolkit(
            config=config.redis,
            options=config.toolkit
        )
```

## 故障排除

### 常見配置問題

1. **連接超時**
   ```python
   config = RedisConnectionConfig(
       socket_connect_timeout=10.0,  # 增加連接超時
       socket_timeout=30.0,          # 增加操作超時
       retry_on_timeout=True         # 啟用超時重試
   )
   ```

2. **SSL 證書錯誤**
   ```python
   config = RedisConnectionConfig(
       ssl=True,
       ssl_check_hostname=False,     # 禁用主機名檢查（僅開發環境）
       ssl_cert_reqs='optional'      # 可選證書驗證
   )
   ```

3. **連接池耗盡**
   ```python
   options = RedisOptions(
       max_connections=200,           # 增加最大連接數
       enable_metrics=True            # 啟用監控
   )
   ```

### 配置調試

```python
# 啟用詳細日誌
import logging

logging.basicConfig(level=logging.DEBUG)

options = RedisOptions(
    log_level="DEBUG",
    is_logger_info=True
)

toolkit = RedisToolkit(options=options)

# 打印當前配置
print(f"連接配置: {toolkit.config.to_dict()}")
print(f"選項配置: {vars(toolkit.options)}")
```