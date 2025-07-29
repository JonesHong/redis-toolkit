# Serialization Features

One of Redis Toolkit's core advantages is its intelligent serialization system, which automatically handles various Python data types, allowing you to focus on business logic rather than data conversion.

## 🎯 Why Serialization?

Redis natively only supports simple types like strings, lists, and sets. When we need to store complex Python objects, serialization is required:

```python
# ❌ Native Redis limitations
import redis
r = redis.Redis()

# This will raise an error!
user = {"name": "Alice", "age": 25}
r.set("user", user)  # TypeError: Invalid input type

# 😓 Traditional approach: manual serialization
import json
r.set("user", json.dumps(user))
retrieved = json.loads(r.get("user"))  # Manual deserialization required
```

```python
# ✅ Redis Toolkit solution
from redis_toolkit import RedisToolkit
toolkit = RedisToolkit()

# Automatic handling!
user = {"name": "Alice", "age": 25}
toolkit.setter("user", user)
retrieved = toolkit.getter("user")  # Automatically deserialized to dict
```

## 🔐 Security First: Why Not Pickle?

Many Redis wrappers use Python's `pickle` for serialization, but this poses serious security risks:

::: danger Security Warning
Pickle can execute arbitrary code! Deserializing untrusted data may lead to Remote Code Execution (RCE).
:::

Redis Toolkit uses **JSON-based serialization** to ensure security:

```python
# Our serialization strategy
# 1. Basic types: Use JSON
# 2. Binary data: Base64 encoding
# 3. NumPy arrays: Convert to list + metadata
# 4. Custom objects: Require explicit serializers
```

## 📊 Supported Data Types

### Basic Types

| Python Type | Example | Storage Format |
|-------------|---------|----------------|
| str | `"Hello"` | Direct storage |
| int | `42` | JSON number |
| float | `3.14` | JSON number |
| bool | `True` | JSON boolean |
| None | `None` | JSON null |
| dict | `{"a": 1}` | JSON object |
| list | `[1, 2, 3]` | JSON array |

### Advanced Types

#### Binary Data (bytes)

```python
# Store binary data
binary_data = b"Binary \x00\x01\x02 data"
toolkit.setter("binary_key", binary_data)

# Automatically recognized and restored
retrieved = toolkit.getter("binary_key")
print(type(retrieved))  # <class 'bytes'>
print(retrieved == binary_data)  # True
```

#### NumPy Arrays

```python
import numpy as np

# Various NumPy data types
int_array = np.array([1, 2, 3, 4, 5])
float_array = np.array([1.1, 2.2, 3.3], dtype=np.float32)
matrix = np.array([[1, 2], [3, 4]])

# All handled automatically
toolkit.setter("int_array", int_array)
toolkit.setter("float_array", float_array)
toolkit.setter("matrix", matrix)

# Complete restoration, including dtype
retrieved = toolkit.getter("float_array")
print(retrieved.dtype)  # float32
```

## 🔍 Serialization Internals

### Serialization Flow

```python
# Simplified serialization logic
def serialize_value(value):
    # 1. Check if bytes
    if isinstance(value, bytes):
        return {
            "__type__": "bytes",
            "__value__": base64.b64encode(value).decode('utf-8')
        }
    
    # 2. Check if NumPy array
    if isinstance(value, np.ndarray):
        return {
            "__type__": "numpy",
            "__value__": value.tolist(),
            "__dtype__": str(value.dtype),
            "__shape__": value.shape
        }
    
    # 3. Other types use JSON
    return json.dumps(value, ensure_ascii=False)
```

### Deserialization Flow

```python
# Simplified deserialization logic
def deserialize_value(data):
    # 1. Try JSON parsing
    try:
        obj = json.loads(data)
        
        # 2. Check for special type markers
        if isinstance(obj, dict) and "__type__" in obj:
            if obj["__type__"] == "bytes":
                return base64.b64decode(obj["__value__"])
            elif obj["__type__"] == "numpy":
                array = np.array(obj["__value__"])
                return array.astype(obj["__dtype__"])
        
        return obj
    except:
        # 3. Return raw bytes if parsing fails
        return data
```

## 🎨 Handling Complex Data Structures

### Nested Structures

```python
# Complex nested data
complex_data = {
    "user": {
        "id": 1001,
        "profile": {
            "name": "Alice",
            "avatar": b"PNG\x89\x50\x4E\x47",  # Binary image data
            "preferences": {
                "theme": "dark",
                "notifications": True
            }
        },
        "scores": np.array([95, 87, 92, 88, 90]),
        "metadata": {
            "created_at": "2024-01-01",
            "last_login": None
        }
    }
}

# One line to handle it all!
toolkit.setter("user:1001:full", complex_data)

# Complete restoration of all types
retrieved = toolkit.getter("user:1001:full")
print(type(retrieved["user"]["profile"]["avatar"]))  # <class 'bytes'>
print(type(retrieved["user"]["scores"]))  # <class 'numpy.ndarray'>
```

### Mixed Types in Lists

```python
# Mixed type list
mixed_list = [
    "text",
    42,
    3.14,
    True,
    None,
    {"nested": "dict"},
    [1, 2, 3],
    b"binary",
    np.array([1, 2, 3])
]

toolkit.setter("mixed_list", mixed_list)
retrieved = toolkit.getter("mixed_list")

# Each element maintains its original type
for i, item in enumerate(retrieved):
    print(f"Index {i}: {type(item)} = {item}")
```

## 🚀 Performance Considerations

### Serialization Performance Comparison

```python
import time
import pickle
import json

data = {"users": [{"id": i, "name": f"User{i}"} for i in range(1000)]}

# JSON serialization
start = time.time()
json_data = json.dumps(data)
json_time = time.time() - start

# Pickle serialization
start = time.time()
pickle_data = pickle.dumps(data)
pickle_time = time.time() - start

print(f"JSON: {json_time:.4f}s, Size: {len(json_data)} bytes")
print(f"Pickle: {pickle_time:.4f}s, Size: {len(pickle_data)} bytes")

# Result: JSON is usually larger but safer and suitable for network transmission
```

### Optimization Tips

1. **Compress Large Data**
   ```python
   import gzip
   
   # Compress large data
   large_data = {"huge": "data" * 10000}
   
   # Manual compression
   compressed = gzip.compress(
       json.dumps(large_data).encode('utf-8')
   )
   toolkit.setter("compressed_data", compressed)
   ```

2. **Avoid Deep Nesting**
   ```python
   # ❌ Avoid deeply nested structures
   deeply_nested = {"a": {"b": {"c": {"d": {"e": "value"}}}}}
   
   # ✅ Flattened structure
   flat_structure = {
       "a_b_c_d_e": "value"
   }
   ```

3. **Batch Operations**
   ```python
   # Use batch operations to reduce serialization overhead
   batch_data = {
       f"key:{i}": {"id": i, "data": f"value{i}"}
       for i in range(1000)
   }
   toolkit.batch_set(batch_data)  # Much faster than setting individually
   ```

## 🛠️ Custom Serialization

### Handling Unsupported Types

```python
from datetime import datetime
import json

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Use custom encoder
data = {
    "created": datetime.now(),
    "user": "Alice"
}

# Manual serialization
serialized = json.dumps(data, cls=DateTimeEncoder)
toolkit.client.set("custom_data", serialized)
```

### Creating Wrapper Classes

```python
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class User:
    id: int
    name: str
    created_at: datetime
    
    def to_dict(self):
        """Convert to serializable dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        """Restore from dictionary"""
        return cls(
            id=data["id"],
            name=data["name"],
            created_at=datetime.fromisoformat(data["created_at"])
        )

# Usage example
user = User(id=1, name="Alice", created_at=datetime.now())
toolkit.setter("user:1", user.to_dict())

# Restore
data = toolkit.getter("user:1")
restored_user = User.from_dict(data)
```

## 🔍 Debugging Serialization Issues

### Inspecting Serialization Results

```python
from redis_toolkit.utils import serialize_value

# Check how data is serialized
test_data = {
    "text": "Hello",
    "number": 42,
    "binary": b"bytes",
    "array": np.array([1, 2, 3])
}

serialized = serialize_value(test_data)
print("Serialization result:")
print(serialized)
print(f"Size: {len(serialized)} bytes")
```

### Handling Serialization Errors

```python
from redis_toolkit.exceptions import SerializationError

# Custom class (cannot serialize directly)
class CustomClass:
    def __init__(self, value):
        self.value = value

try:
    toolkit.setter("custom", CustomClass(42))
except SerializationError as e:
    print(f"Serialization failed: {e}")
    # Store a serializable representation instead
    toolkit.setter("custom", {"value": 42})
```

## 📚 Best Practices

1. **Keep Data Structures Simple**
   - Prioritize native Python types
   - Avoid storing class instances, use dictionaries instead

2. **Watch Data Size**
   - Redis single value size limit is 512MB
   - Consider sharding or compression for large data

3. **Version Compatibility**
   - Serialization format may change between versions
   - Consider version tagging for important data

4. **Security Considerations**
   - Never deserialize untrusted data
   - Regularly audit stored data types

## 🎯 Next Steps

After understanding the serialization mechanism, you can:

- Learn about [Publish/Subscribe](./pubsub.md) to understand how to pass serialized messages
- Check [Configuration Options](./configuration.md) to customize serialization behavior
- Explore [Media Processing](/en/advanced/media-processing.md) for advanced binary data applications

::: tip Summary
Redis Toolkit's serialization system lets you ignore low-level details and focus on application logic. Remember: Security first, simplicity supreme!
:::