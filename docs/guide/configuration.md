# 配置選項

Redis Toolkit 提供豐富的配置選項，讓您可以根據需求調整連線參數、效能設定、日誌行為等。本章將詳細介紹所有可用的配置選項。

## 🎯 配置概覽

Redis Toolkit 的配置分為兩個主要部分：

1. **RedisConnectionConfig** - 連線相關配置
2. **RedisOptions** - 工具包行為配置

```python
from redis_toolkit import RedisToolkit, RedisConnectionConfig, RedisOptions

# 連線配置
config = RedisConnectionConfig(
    host='localhost',
    port=6379,
    db=0
)

# 行為配置
options = RedisOptions(
    is_logger_info=True,
    max_log_size=256
)

# 使用配置
toolkit = RedisToolkit(config=config, options=options)
```

## 🔌 連線配置 (RedisConnectionConfig)

### 基本連線參數

```python
from redis_toolkit import RedisConnectionConfig

config = RedisConnectionConfig(
    # 基本連線
    host='localhost',          # Redis 主機地址
    port=6379,                # Redis 端口
    db=0,                     # 資料庫編號 (0-15)
    
    # 認證
    password='your_password',  # 密碼（可選）
    username='username',       # 用戶名（Redis 6.0+）
    
    # 編碼
    encoding='utf-8',         # 字符編碼
    decode_responses=False,   # 重要：必須為 False
)
```

::: warning 重要提示
`decode_responses` 必須設為 `False`，否則會影響序列化功能！
:::

### 進階連線選項

```python
config = RedisConnectionConfig(
    host='localhost',
    port=6379,
    
    # 連線保持
    socket_keepalive=True,           # 啟用 TCP keepalive
    socket_keepalive_options={       # Keepalive 選項
        'TCP_KEEPIDLE': 120,
        'TCP_KEEPINTVL': 30,
        'TCP_KEEPCNT': 3
    },
    
    # 超時設定
    connection_timeout=10,           # 連線超時（秒）
    socket_timeout=5,               # 操作超時（秒）
    
    # 重試機制
    retry_on_timeout=True,          # 超時重試
    retry_on_error=True,            # 錯誤重試
    
    # 健康檢查
    health_check_interval=30,       # 健康檢查間隔（秒）
)
```

### SSL/TLS 配置

```python
# 使用 SSL 連線
secure_config = RedisConnectionConfig(
    host='redis.example.com',
    port=6380,
    
    # SSL 設定
    ssl=True,                              # 啟用 SSL
    ssl_keyfile='/path/to/client-key.pem',    # 客戶端金鑰
    ssl_certfile='/path/to/client-cert.pem',  # 客戶端證書
    ssl_ca_certs='/path/to/ca-cert.pem',      # CA 證書
    ssl_cert_reqs='required',              # 證書要求等級
    ssl_check_hostname=True,               # 檢查主機名
)
```

### 連接池配置

```python
# 使用共享連接池以提升效能
config = RedisConnectionConfig(
    host='localhost',
    port=6379,
    
    # 連接池參數（當 use_connection_pool=True 時生效）
    max_connections=50,          # 最大連線數
    
    # 連接池會自動管理連線的創建和回收
)

# RedisOptions 中啟用連接池
options = RedisOptions(
    use_connection_pool=True     # 使用連接池
)
```

## ⚙️ 行為配置 (RedisOptions)

### 日誌配置

```python
from redis_toolkit import RedisOptions

options = RedisOptions(
    # 日誌控制
    is_logger_info=True,        # 啟用/停用日誌
    log_level="INFO",           # 日誌級別: DEBUG, INFO, WARNING, ERROR
    log_path="./logs",          # 日誌檔案路徑（None 表示只輸出到控制台）
    
    # 日誌內容控制
    max_log_size=256,           # 單條日誌最大字元數
)
```

### 訂閱者配置

```python
options = RedisOptions(
    # 訂閱者行為
    subscriber_retry_delay=5,    # 重連延遲（秒）
    subscriber_stop_timeout=5,   # 停止超時（秒）
)
```

### 資料驗證配置

```python
options = RedisOptions(
    # 資料大小限制
    max_value_size=10*1024*1024,   # 最大值大小（10MB）
    max_key_length=512,            # 最大鍵長度
    
    # 驗證控制
    enable_validation=True,        # 啟用輸入驗證
)
```

### 效能配置

```python
options = RedisOptions(
    # 連接池
    use_connection_pool=True,      # 使用共享連接池
    max_connections=None,          # 最大連線數（None 表示無限制）
)
```

## 🎨 配置範例

### 開發環境配置

```python
# 開發環境：詳細日誌、寬鬆限制
dev_config = RedisConnectionConfig(
    host='localhost',
    port=6379,
    connection_timeout=30,
    retry_on_error=True
)

dev_options = RedisOptions(
    is_logger_info=True,
    log_level="DEBUG",
    max_log_size=1024,
    enable_validation=True,
    subscriber_retry_delay=2
)

dev_toolkit = RedisToolkit(config=dev_config, options=dev_options)
```

### 生產環境配置

```python
# 生產環境：效能優先、嚴格驗證
prod_config = RedisConnectionConfig(
    host='redis-cluster.prod',
    port=6379,
    password=os.environ.get('REDIS_PASSWORD'),
    ssl=True,
    ssl_ca_certs='/etc/ssl/redis-ca.pem',
    connection_timeout=5,
    socket_timeout=3,
    health_check_interval=60
)

prod_options = RedisOptions(
    is_logger_info=True,
    log_level="WARNING",        # 只記錄警告和錯誤
    log_path="/var/log/app",    # 寫入日誌檔案
    max_value_size=5*1024*1024, # 5MB 限制
    use_connection_pool=True,
    max_connections=100,
    enable_validation=True
)

prod_toolkit = RedisToolkit(config=prod_config, options=prod_options)
```

### 測試環境配置

```python
# 測試環境：快速失敗、詳細錯誤
test_config = RedisConnectionConfig(
    host='localhost',
    port=6379,
    connection_timeout=1,       # 快速超時
    retry_on_timeout=False,     # 不重試
    retry_on_error=False
)

test_options = RedisOptions(
    is_logger_info=False,       # 測試時關閉日誌
    enable_validation=True,     # 嚴格驗證
    max_value_size=1024*1024    # 1MB 限制
)

test_toolkit = RedisToolkit(config=test_config, options=test_options)
```

## 🔧 動態配置

### 配置驗證

```python
# 配置物件支援驗證
config = RedisConnectionConfig(
    host='localhost',
    port=6379,
    ssl=True,
    ssl_certfile='/path/to/cert.pem'
)

try:
    config.validate()  # 驗證配置
except ValueError as e:
    print(f"配置錯誤: {e}")
```

### 配置合併

```python
# 從環境變數載入配置
import os

def load_config_from_env():
    config = RedisConnectionConfig(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', '6379')),
        password=os.getenv('REDIS_PASSWORD'),
        db=int(os.getenv('REDIS_DB', '0'))
    )
    
    options = RedisOptions(
        is_logger_info=os.getenv('DEBUG', 'false').lower() == 'true',
        log_level=os.getenv('LOG_LEVEL', 'INFO'),
        use_connection_pool=os.getenv('USE_POOL', 'true').lower() == 'true'
    )
    
    return config, options

# 使用環境配置
config, options = load_config_from_env()
toolkit = RedisToolkit(config=config, options=options)
```

### 配置檔案

```python
# 從 YAML 載入配置
import yaml

def load_config_from_file(config_file):
    with open(config_file, 'r') as f:
        data = yaml.safe_load(f)
    
    # 連線配置
    conn_data = data.get('connection', {})
    config = RedisConnectionConfig(**conn_data)
    
    # 選項配置
    opts_data = data.get('options', {})
    options = RedisOptions(**opts_data)
    
    return config, options

# config.yaml 範例:
"""
connection:
  host: localhost
  port: 6379
  password: ${REDIS_PASSWORD}
  db: 0
  ssl: true
  ssl_ca_certs: /etc/ssl/redis-ca.pem

options:
  is_logger_info: true
  log_level: INFO
  log_path: /var/log/redis-toolkit
  use_connection_pool: true
  max_connections: 50
"""
```

## 🎯 配置最佳實踐

### 1. 環境分離

```python
class ConfigManager:
    @staticmethod
    def get_config(env='development'):
        configs = {
            'development': {
                'config': RedisConnectionConfig(host='localhost'),
                'options': RedisOptions(log_level='DEBUG')
            },
            'staging': {
                'config': RedisConnectionConfig(
                    host='redis-staging.internal',
                    ssl=True
                ),
                'options': RedisOptions(log_level='INFO')
            },
            'production': {
                'config': RedisConnectionConfig(
                    host='redis-prod.internal',
                    ssl=True,
                    password=os.environ['REDIS_PASSWORD']
                ),
                'options': RedisOptions(
                    log_level='WARNING',
                    use_connection_pool=True
                )
            }
        }
        
        return configs.get(env, configs['development'])

# 使用
env = os.getenv('APP_ENV', 'development')
config_dict = ConfigManager.get_config(env)
toolkit = RedisToolkit(**config_dict)
```

### 2. 連線池管理

```python
# 全域連線池配置
from redis_toolkit import pool_manager

# 配置共享連線池
pool_manager.configure_pool(
    'default',
    host='localhost',
    port=6379,
    max_connections=50
)

# 多個 RedisToolkit 實例共享同一連線池
toolkit1 = RedisToolkit()  # 使用預設池
toolkit2 = RedisToolkit()  # 共享相同連線池
```

### 3. 配置熱更新

```python
class DynamicConfig:
    def __init__(self):
        self._config = None
        self._options = None
        self._toolkit = None
        self.reload()
    
    def reload(self):
        """重新載入配置"""
        # 從配置源載入新配置
        self._config = self._load_connection_config()
        self._options = self._load_options()
        
        # 重建 toolkit
        if self._toolkit:
            self._toolkit.cleanup()
        
        self._toolkit = RedisToolkit(
            config=self._config,
            options=self._options
        )
    
    @property
    def toolkit(self):
        return self._toolkit
    
    def _load_connection_config(self):
        # 從檔案、環境變數或配置中心載入
        return RedisConnectionConfig(...)
    
    def _load_options(self):
        # 載入選項配置
        return RedisOptions(...)
```

### 4. 配置監控

```python
def monitor_config(toolkit):
    """監控配置狀態"""
    config = toolkit._config
    options = toolkit.options
    
    # 記錄當前配置
    logger.info(f"Redis 連線: {config.host}:{config.port}")
    logger.info(f"使用 SSL: {config.ssl}")
    logger.info(f"連接池: {options.use_connection_pool}")
    logger.info(f"最大連線數: {options.max_connections}")
    
    # 檢查連線健康
    try:
        toolkit.client.ping()
        logger.info("Redis 連線正常")
    except Exception as e:
        logger.error(f"Redis 連線異常: {e}")
```

## 📊 效能調優建議

1. **連接池優化**
   ```python
   # 高並發場景
   options = RedisOptions(
       use_connection_pool=True,
       max_connections=200    # 根據並發量調整
   )
   ```

2. **超時設定**
   ```python
   # 快速失敗
   config = RedisConnectionConfig(
       connection_timeout=3,  # 連線超時
       socket_timeout=2      # 操作超時
   )
   ```

3. **日誌優化**
   ```python
   # 生產環境減少日誌
   options = RedisOptions(
       log_level="ERROR",    # 只記錄錯誤
       max_log_size=128     # 限制日誌大小
   )
   ```

## 📚 下一步

了解配置選項後，您可以：

- 探索[進階功能](/advanced/)，學習媒體處理和批次操作
- 查看[效能優化](/advanced/performance.md)，調優您的配置
- 閱讀[錯誤處理](/advanced/error-handling.md)，建立穩定的應用

::: tip 小結
合理的配置是高效應用的基礎。根據環境需求調整配置，定期檢查和優化，讓 Redis Toolkit 發揮最佳效能！
:::