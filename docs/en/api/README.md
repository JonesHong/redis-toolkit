# API Reference

Welcome to the Redis Toolkit API reference documentation. Here you'll find detailed information about all public classes, methods, and functions.

## 📚 API Documentation Organization

<div class="api-categories">
  <div class="api-card">
    <h3>🔧 Core API</h3>
    <p>All methods of the RedisToolkit main class</p>
    <ul>
      <li>Initialization & Configuration</li>
      <li>Basic Operation Methods</li>
      <li>Batch Operations</li>
      <li>Publish/Subscribe</li>
    </ul>
    <a href="./core.html" class="api-link">View Documentation →</a>
  </div>
  
  <div class="api-card">
    <h3>🎨 Converters API</h3>
    <p>Media processing related converters</p>
    <ul>
      <li>Image Converter</li>
      <li>Audio Converter</li>
      <li>Video Converter</li>
      <li>Common Interface</li>
    </ul>
    <a href="./converters.html" class="api-link">View Documentation →</a>
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
    <a href="./options.html" class="api-link">View Documentation →</a>
  </div>
  
  <div class="api-card">
    <h3>🛠️ Utility Functions</h3>
    <p>Utilities and helper functions</p>
    <ul>
      <li>Serialization Functions</li>
      <li>Retry Decorators</li>
      <li>Validation Tools</li>
      <li>Exception Classes</li>
    </ul>
    <a href="./utilities.html" class="api-link">View Documentation →</a>
  </div>
</div>

## 🎯 Quick Navigation

### Most Commonly Used APIs

```python
# Core classes
from redis_toolkit import RedisToolkit

# Configuration classes
from redis_toolkit import RedisConnectionConfig, RedisOptions

# Converter functions
from redis_toolkit.converters import (
    encode_image, decode_image,
    encode_audio, decode_audio,
    get_converter
)

# Utility functions
from redis_toolkit.utils import serialize_value, deserialize_value
from redis_toolkit.utils import with_retry

# Exception classes
from redis_toolkit.exceptions import (
    RedisToolkitError,
    SerializationError,
    ValidationError
)
```

## 📖 API Usage Examples

### Basic Initialization

```python
# Method 1: Using default configuration
toolkit = RedisToolkit()

# Method 2: Custom configuration
config = RedisConnectionConfig(host='localhost', port=6379)
options = RedisOptions(is_logger_info=True)
toolkit = RedisToolkit(config=config, options=options)

# Method 3: Using existing Redis client
import redis
client = redis.Redis()
toolkit = RedisToolkit(redis=client)
```

### Common Operations

```python
# Store and retrieve data
toolkit.setter("key", {"data": "value"})
data = toolkit.getter("key")

# Batch operations
batch_data = {"key1": "value1", "key2": "value2"}
toolkit.batch_set(batch_data)
results = toolkit.batch_get(["key1", "key2"])

# Publish/Subscribe
toolkit.publisher("channel", {"message": "Hello"})
```

### Media Processing

```python
# Image processing
img_bytes = encode_image(image_array, format='jpg')
decoded_img = decode_image(img_bytes)

# Using converters
converter = get_converter('image')
resized = converter.resize(image_array, width=800)
```

## 🔍 API Design Principles

### 1. Simple and Intuitive

Our API design follows the "simplicity first" principle:

```python
# ✅ Simple and clear
toolkit.setter("key", value)
toolkit.getter("key")

# ❌ Overly complex
toolkit.storage.persistence.set_with_options("key", value, options={...})
```

### 2. Consistency

All APIs maintain consistent naming and behavior patterns:

- `setter` / `getter` - Basic access
- `batch_set` / `batch_get` - Batch operations
- `encode_*` / `decode_*` - Encoding/Decoding

### 3. Error Handling

Unified exception system for easy error handling:

```python
try:
    toolkit.setter("key", problematic_value)
except SerializationError:
    # Handle serialization errors
except ValidationError:
    # Handle validation errors
except RedisToolkitError:
    # Handle other errors
```

## 📊 API Versioning and Compatibility

### Versioning Strategy

We follow Semantic Versioning:

- **Major version**: Incompatible API changes
- **Minor version**: Backwards-compatible functionality additions
- **Patch version**: Backwards-compatible bug fixes

### Deprecation Policy

When an API needs to be deprecated:

1. Mark as `@deprecated` in documentation
2. Issue deprecation warnings
3. Maintain for at least two minor versions
4. Provide migration guides

```python
# Deprecation example
@deprecated("Use toolkit.setter instead")
def set_value(key, value):
    warnings.warn("set_value is deprecated, use setter", DeprecationWarning)
    return toolkit.setter(key, value)
```

## 🎯 API Best Practices

### 1. Use Type Hints

```python
from typing import Dict, Any, Optional

def process_data(
    key: str,
    data: Dict[str, Any],
    ttl: Optional[int] = None
) -> bool:
    """Process and store data"""
    return toolkit.setter(key, data, ex=ttl)
```

### 2. Parameter Validation

```python
# Use configuration class validation
config = RedisConnectionConfig(port=6379)
config.validate()  # Ensure configuration is valid

# Custom validation
if not isinstance(data, (dict, list)):
    raise ValidationError("Data must be dict or list")
```

### 3. Resource Management

```python
# Using context manager
with RedisToolkit() as toolkit:
    toolkit.setter("key", "value")
    # Automatic resource cleanup

# Manual cleanup
toolkit = RedisToolkit()
try:
    # Use toolkit
finally:
    toolkit.cleanup()
```

## 📚 Deep Dive

Choose the appropriate API documentation based on your needs:

<div class="api-nav">
  <a href="./core.html" class="nav-item">
    <span class="icon">🔧</span>
    <span>Core API</span>
  </a>
  <a href="./converters.html" class="nav-item">
    <span class="icon">🎨</span>
    <span>Converters API</span>
  </a>
  <a href="./options.html" class="nav-item">
    <span class="icon">⚙️</span>
    <span>Configuration API</span>
  </a>
  <a href="./utilities.html" class="nav-item">
    <span class="icon">🛠️</span>
    <span>Utility Functions</span>
  </a>
</div>

::: tip Tips
- Use your IDE's auto-completion to explore the API
- Check the source code for implementation details
- Refer to example code to learn best practices
:::

<style>
.api-categories {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin: 2rem 0;
}

.api-card {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1.5rem;
  transition: all 0.2s;
}

.api-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border-color: #dc382d;
}

.api-card h3 {
  color: #dc382d;
  margin-top: 0;
  margin-bottom: 0.5rem;
}

.api-card p {
  color: #666;
  margin-bottom: 1rem;
}

.api-card ul {
  margin: 0 0 1rem 0;
  padding-left: 1.2rem;
  color: #555;
  font-size: 0.9rem;
}

.api-link {
  display: inline-block;
  color: #dc382d;
  text-decoration: none;
  font-weight: 500;
  transition: transform 0.2s;
}

.api-link:hover {
  transform: translateX(3px);
}

.api-nav {
  display: flex;
  gap: 1rem;
  margin: 2rem 0;
  flex-wrap: wrap;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.8rem 1.5rem;
  background: #dc382d;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  transition: all 0.2s;
}

.nav-item:hover {
  background: #e85d52;
  transform: translateY(-2px);
}

.nav-item .icon {
  font-size: 1.2rem;
}
</style>