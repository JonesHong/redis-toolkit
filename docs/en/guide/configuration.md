# Configuration Options

Redis Toolkit provides rich configuration options that allow you to adjust connection parameters, performance settings, logging behavior, and more based on your needs. This chapter will detail all available configuration options.

## 🎯 Configuration Overview

Redis Toolkit configuration is divided into two main parts:

1. **RedisConnectionConfig** - Connection-related configuration
2. **RedisOptions** - Toolkit behavior configuration

```python
from redis_toolkit import RedisToolkit, RedisConnectionConfig, RedisOptions

# Connection configuration
config = RedisConnectionConfig(
    host='localhost',
    port=6379,
    db=0
)

# Behavior configuration
options = RedisOptions(
    is_logger_info=True,
    max_log_size=256
)

# Use configuration
toolkit = RedisToolkit(config=config, options=options)
```

## 🔌 Connection Configuration (RedisConnectionConfig)

### Basic Connection Parameters

```python
from redis_toolkit import RedisConnectionConfig

config = RedisConnectionConfig(
    # Basic connection
    host='localhost',          # Redis host address
    port=6379,                # Redis port
    db=0,                     # Database number (0-15)
    
    # Authentication
    password='your_password',  # Password (optional)
    username='username',       # Username (Redis 6.0+)
    
    # Encoding
    encoding='utf-8',         # Character encoding
    decode_responses=False,   # Important: Must be False
)
```

::: warning Important
`decode_responses` must be set to `False`, otherwise it will affect serialization functionality!
:::

### Advanced Connection Options

```python
config = RedisConnectionConfig(
    host='localhost',
    port=6379,
    
    # Connection keep-alive
    socket_keepalive=True,           # Enable TCP keepalive
    socket_keepalive_options={       # Keepalive options
        'TCP_KEEPIDLE': 120,
        'TCP_KEEPINTVL': 30,
        'TCP_KEEPCNT': 3
    },
    
    # Timeout settings
    connection_timeout=10,           # Connection timeout (seconds)
    socket_timeout=5,               # Operation timeout (seconds)
    
    # Retry mechanism
    retry_on_timeout=True,          # Retry on timeout
    retry_on_error=True,            # Retry on error
    
    # Health check
    health_check_interval=30,       # Health check interval (seconds)
)
```

### SSL/TLS Configuration

```python
# Using SSL connection
secure_config = RedisConnectionConfig(
    host='redis.example.com',
    port=6380,
    
    # SSL settings
    ssl=True,                              # Enable SSL
    ssl_keyfile='/path/to/client-key.pem',    # Client key
    ssl_certfile='/path/to/client-cert.pem',  # Client certificate
    ssl_ca_certs='/path/to/ca-cert.pem',      # CA certificate
    ssl_cert_reqs='required',              # Certificate requirement level
    ssl_check_hostname=True,               # Check hostname
)
```

### Connection Pool Configuration

```python
# Use shared connection pool for better performance
config = RedisConnectionConfig(
    host='localhost',
    port=6379,
    
    # Connection pool parameters (effective when use_connection_pool=True)
    max_connections=50,          # Maximum connections
    
    # Connection pool automatically manages connection creation and recycling
)

# Enable connection pool in RedisOptions
options = RedisOptions(
    use_connection_pool=True     # Use connection pool
)
```

## ⚙️ Behavior Configuration (RedisOptions)

### Logging Configuration

```python
from redis_toolkit import RedisOptions

options = RedisOptions(
    # Log control
    is_logger_info=True,        # Enable/disable logging
    log_level="INFO",           # Log level: DEBUG, INFO, WARNING, ERROR
    log_path="./logs",          # Log file path (None means console only)
    
    # Log content control
    max_log_size=256,           # Maximum characters per log entry
)
```

### Subscriber Configuration

```python
options = RedisOptions(
    # Subscriber behavior
    subscriber_retry_delay=5,    # Reconnection delay (seconds)
    subscriber_stop_timeout=5,   # Stop timeout (seconds)
)
```

### Data Validation Configuration

```python
options = RedisOptions(
    # Data size limits
    max_value_size=10*1024*1024,   # Maximum value size (10MB)
    max_key_length=512,            # Maximum key length
    
    # Validation control
    enable_validation=True,        # Enable input validation
)
```

### Performance Configuration

```python
options = RedisOptions(
    # Connection pool
    use_connection_pool=True,      # Use shared connection pool
    max_connections=None,          # Maximum connections (None means unlimited)
)
```

## 🎨 Configuration Examples

### Development Environment Configuration

```python
# Development environment: Detailed logs, relaxed limits
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

### Production Environment Configuration

```python
# Production environment: Performance first, strict validation
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
    log_level="WARNING",        # Only log warnings and errors
    log_path="/var/log/app",    # Write to log file
    max_value_size=5*1024*1024, # 5MB limit
    use_connection_pool=True,
    max_connections=100,
    enable_validation=True
)

prod_toolkit = RedisToolkit(config=prod_config, options=prod_options)
```

### Test Environment Configuration

```python
# Test environment: Fast failure, detailed errors
test_config = RedisConnectionConfig(
    host='localhost',
    port=6379,
    connection_timeout=1,       # Fast timeout
    retry_on_timeout=False,     # No retry
    retry_on_error=False
)

test_options = RedisOptions(
    is_logger_info=False,       # Disable logs during testing
    enable_validation=True,     # Strict validation
    max_value_size=1024*1024    # 1MB limit
)

test_toolkit = RedisToolkit(config=test_config, options=test_options)
```

## 🔧 Dynamic Configuration

### Configuration Validation

```python
# Configuration objects support validation
config = RedisConnectionConfig(
    host='localhost',
    port=6379,
    ssl=True,
    ssl_certfile='/path/to/cert.pem'
)

try:
    config.validate()  # Validate configuration
except ValueError as e:
    print(f"Configuration error: {e}")
```

### Configuration Merging

```python
# Load configuration from environment variables
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

# Use environment configuration
config, options = load_config_from_env()
toolkit = RedisToolkit(config=config, options=options)
```

### Configuration Files

```python
# Load configuration from YAML
import yaml

def load_config_from_file(config_file):
    with open(config_file, 'r') as f:
        data = yaml.safe_load(f)
    
    # Connection configuration
    conn_data = data.get('connection', {})
    config = RedisConnectionConfig(**conn_data)
    
    # Options configuration
    opts_data = data.get('options', {})
    options = RedisOptions(**opts_data)
    
    return config, options

# config.yaml example:
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

## 🎯 Configuration Best Practices

### 1. Environment Separation

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

# Usage
env = os.getenv('APP_ENV', 'development')
config_dict = ConfigManager.get_config(env)
toolkit = RedisToolkit(**config_dict)
```

### 2. Connection Pool Management

```python
# Global connection pool configuration
from redis_toolkit import pool_manager

# Configure shared connection pool
pool_manager.configure_pool(
    'default',
    host='localhost',
    port=6379,
    max_connections=50
)

# Multiple RedisToolkit instances share the same connection pool
toolkit1 = RedisToolkit()  # Use default pool
toolkit2 = RedisToolkit()  # Share same connection pool
```

### 3. Configuration Hot Reload

```python
class DynamicConfig:
    def __init__(self):
        self._config = None
        self._options = None
        self._toolkit = None
        self.reload()
    
    def reload(self):
        """Reload configuration"""
        # Load new configuration from source
        self._config = self._load_connection_config()
        self._options = self._load_options()
        
        # Rebuild toolkit
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
        # Load from file, environment variables or configuration center
        return RedisConnectionConfig(...)
    
    def _load_options(self):
        # Load options configuration
        return RedisOptions(...)
```

### 4. Configuration Monitoring

```python
def monitor_config(toolkit):
    """Monitor configuration status"""
    config = toolkit._config
    options = toolkit.options
    
    # Log current configuration
    logger.info(f"Redis connection: {config.host}:{config.port}")
    logger.info(f"Using SSL: {config.ssl}")
    logger.info(f"Connection pool: {options.use_connection_pool}")
    logger.info(f"Max connections: {options.max_connections}")
    
    # Check connection health
    try:
        toolkit.client.ping()
        logger.info("Redis connection healthy")
    except Exception as e:
        logger.error(f"Redis connection error: {e}")
```

## 📊 Performance Tuning Recommendations

1. **Connection Pool Optimization**
   ```python
   # High concurrency scenario
   options = RedisOptions(
       use_connection_pool=True,
       max_connections=200    # Adjust based on concurrency
   )
   ```

2. **Timeout Settings**
   ```python
   # Fast failure
   config = RedisConnectionConfig(
       connection_timeout=3,  # Connection timeout
       socket_timeout=2      # Operation timeout
   )
   ```

3. **Logging Optimization**
   ```python
   # Reduce logs in production
   options = RedisOptions(
       log_level="ERROR",    # Only log errors
       max_log_size=128     # Limit log size
   )
   ```

## 📚 Next Steps

After understanding configuration options, you can:

- Explore [Advanced Features](/en/advanced/) to learn about media processing and batch operations
- Check out [Performance Optimization](/en/advanced/performance.md) to tune your configuration
- Read [Error Handling](/en/advanced/error-handling.md) to build stable applications

::: tip Summary
Proper configuration is the foundation of efficient applications. Adjust configuration based on environmental needs, regularly check and optimize, and let Redis Toolkit perform at its best!
:::