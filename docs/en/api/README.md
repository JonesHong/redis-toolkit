# API Reference

Welcome to the Redis Toolkit API Reference. Here you'll find detailed documentation for all public classes, methods, and functions.

## 📚 API Documentation Organization

<div class="api-categories">
  <div class="api-card">
    <h3>🔧 Core API</h3>
    <p>All methods of the RedisToolkit main class</p>
    <ul>
      <li>Initialization & Configuration</li>
      <li>Basic Operations</li>
      <li>Batch Operations</li>
      <li>Pub/Sub</li>
    </ul>
    <a href="./core.md" class="api-link">View Documentation →</a>
  </div>
  
  <div class="api-card">
    <h3>🎨 Converters API</h3>
    <p>Media processing converters</p>
    <ul>
      <li>Image Converters</li>
      <li>Audio Converters</li>
      <li>Video Converters</li>
      <li>Common Interfaces</li>
    </ul>
    <a href="./converters.md" class="api-link">View Documentation →</a>
  </div>
  
  <div class="api-card">
    <h3>⚙️ Configuration API</h3>
    <p>Configuration classes and options</p>
    <ul>
      <li>RedisConnectionConfig</li>
      <li>RedisOptions</li>
      <li>Default Configuration</li>
      <li>Validation Methods</li>
    </ul>
    <a href="./options.md" class="api-link">View Documentation →</a>
  </div>
  
  <div class="api-card">
    <h3>🛠️ Utility Functions</h3>
    <p>Utility and helper functions</p>
    <ul>
      <li>Serialization Functions</li>
      <li>Retry Decorators</li>
      <li>Validation Tools</li>
      <li>Exception Classes</li>
    </ul>
    <a href="./utilities.md" class="api-link">View Documentation →</a>
  </div>
</div>

## 🎯 Quick Navigation

### Most Used APIs

```python
# Core Classes
from redis_toolkit import RedisToolkit

# Configuration Classes
from redis_toolkit import RedisConnectionConfig, RedisOptions

# Converter Functions
from redis_toolkit.converters import (
    encode_image, decode_image,
    encode_audio, decode_audio,
    get_converter
)

# Utility Functions
from redis_toolkit.utils import serialize_value, deserialize_value
from redis_toolkit.utils import with_retry

# Exception Classes
from redis_toolkit.exceptions import (
    RedisToolkitError,
    SerializationError,
    ValidationError
)
```

### Quick Start Examples

```python
from redis_toolkit import RedisToolkit

# Create Instance
toolkit = RedisToolkit()

# Basic Operations
toolkit.set('key', {'data': 'value'})
value = toolkit.get('key')

# Batch Operations
toolkit.batch_set({
    'key1': 'value1',
    'key2': {'nested': 'data'}
})

# Pub/Sub
def handler(channel, message):
    print(f"Received: {message}")

subscriber = toolkit.subscribe('channel', handler=handler)
toolkit.publish('channel', 'Hello, Redis!')
```

## 📖 Usage Patterns

### Context Manager Pattern

```python
from redis_toolkit import RedisToolkit

# Automatic resource cleanup
with RedisToolkit() as toolkit:
    toolkit.set('temp', 'data')
    value = toolkit.get('temp')
```

### Custom Configuration

```python
from redis_toolkit import RedisToolkit, RedisConnectionConfig, RedisOptions

# Connection configuration
config = RedisConnectionConfig(
    host='redis.example.com',
    port=6379,
    password='secure_password'
)

# Behavior options
options = RedisOptions(
    log_level='INFO',
    use_connection_pool=True
)

# Create with custom config
toolkit = RedisToolkit(config=config, options=options)
```

### Error Handling

```python
from redis_toolkit.exceptions import SerializationError, ValidationError

try:
    toolkit.set('key', complex_object)
except SerializationError as e:
    print(f"Serialization failed: {e}")
except ValidationError as e:
    print(f"Validation failed: {e}")
```

## 📦 Optional Dependencies

Different features require different optional dependencies:

```bash
# Image processing
pip install redis-toolkit[image]

# Audio processing  
pip install redis-toolkit[audio]

# Full media support
pip install redis-toolkit[media]

# All features
pip install redis-toolkit[all]
```

## 🔍 Finding What You Need

1. **Basic Redis Operations** → [Core API](./core.md)
2. **Media Processing** → [Converters API](./converters.md)
3. **Configuration** → [Configuration API](./options.md)
4. **Error Handling** → [Utility Functions](./utilities.md)

## 📚 Additional Resources

- [Getting Started Guide](/en/guide/)
- [Advanced Features](/en/advanced/)
- [Examples](/en/examples/)
- [GitHub Repository](https://github.com/JonesHong/redis-toolkit)

<style>
.api-categories {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin: 2rem 0;
}

.api-card {
  background: #f7f7f7;
  border: 1px solid #e3e3e3;
  border-radius: 8px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.api-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

.api-card h3 {
  margin-top: 0;
  color: #dc382d;
}

.api-card ul {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

.api-link {
  display: inline-block;
  margin-top: 1rem;
  color: #dc382d;
  font-weight: bold;
  text-decoration: none;
}

.api-link:hover {
  text-decoration: underline;
}
</style>