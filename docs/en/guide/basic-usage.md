# Basic Usage

This chapter will introduce the core features of Redis Toolkit in detail, helping you master various operations needed for daily development.

## 🔧 Initialization Methods

Redis Toolkit provides multiple initialization methods to meet different scenario requirements:

### 1. The Simplest Way

```python
from redis_toolkit import RedisToolkit

# Using default configuration (localhost:6379)
toolkit = RedisToolkit()
```

### 2. Custom Connection Configuration

```python
from redis_toolkit import RedisToolkit, RedisConnectionConfig

# Using configuration object
config = RedisConnectionConfig(
    host='192.168.1.100',
    port=6380,
    db=1,
    password='your_password'
)
toolkit = RedisToolkit(config=config)
```

### 3. Using Existing Redis Client

```python
import redis
from redis_toolkit import RedisToolkit

# If you already have a Redis client
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    decode_responses=False  # Important: must be False
)
toolkit = RedisToolkit(redis=redis_client)
```

### 4. Advanced Options Configuration

```python
from redis_toolkit import RedisToolkit, RedisOptions

options = RedisOptions(
    is_logger_info=True,        # Enable logging
    max_log_size=512,          # Log size limit
    log_level="INFO",          # Log level
    max_value_size=10*1024*1024  # Max value size (10MB)
)

toolkit = RedisToolkit(options=options)
```

## 📝 Basic Operations

### Storing Data (setter)

```python
# Store various data types
toolkit.setter("string_key", "Hello World")
toolkit.setter("number_key", 42)
toolkit.setter("float_key", 3.14159)
toolkit.setter("bool_key", True)
toolkit.setter("list_key", [1, 2, 3, 4, 5])
toolkit.setter("dict_key", {"name": "Alice", "age": 25})

# Set expiration time
toolkit.setter("temp_key", "temporary data", ex=60)  # Expires in 60 seconds
toolkit.setter("temp_key2", "temporary data", px=5000)  # Expires in 5000 milliseconds
```

### Reading Data (getter)

```python
# Automatically deserialize to original type
text = toolkit.getter("string_key")      # str
number = toolkit.getter("number_key")    # int
pi = toolkit.getter("float_key")         # float
flag = toolkit.getter("bool_key")        # bool
items = toolkit.getter("list_key")       # list
user = toolkit.getter("dict_key")        # dict

# Handle non-existent keys
result = toolkit.getter("non_existent_key")  # Returns None
```

### Deleting Data

```python
# Delete single key
toolkit.delete("unwanted_key")

# Delete multiple keys
toolkit.client.delete("key1", "key2", "key3")

# Clear current database (use with caution!)
toolkit.client.flushdb()
```

### Check if Key Exists

```python
# Using exists method
if toolkit.client.exists("user:1001"):
    user = toolkit.getter("user:1001")
    print(f"Found user: {user['name']}")
else:
    print("User does not exist")
```

## 🎯 Batch Operations

When dealing with large amounts of data, batch operations can significantly improve performance:

### Batch Set (batch_set)

```python
# Prepare batch data
batch_data = {
    "user:1001": {"name": "Alice", "score": 95},
    "user:1002": {"name": "Bob", "score": 87},
    "user:1003": {"name": "Charlie", "score": 92},
    "user:1004": {"name": "David", "score": 88},
    "user:1005": {"name": "Eve", "score": 91}
}

# Store all at once
toolkit.batch_set(batch_data)
```

### Batch Get (batch_get)

```python
# Prepare list of keys to read
keys = ["user:1001", "user:1002", "user:1003", "user:1004", "user:1005"]

# Batch read
results = toolkit.batch_get(keys)

# results is a dictionary
for key, value in results.items():
    if value:
        print(f"{key}: {value['name']} - Score: {value['score']}")
```

## 🔄 Data Type Handling

### Handle Complex Nested Structures

```python
# Complex nested data
complex_data = {
    "company": "TechCorp",
    "employees": [
        {"id": 1, "name": "Alice", "skills": ["Python", "Redis"]},
        {"id": 2, "name": "Bob", "skills": ["Java", "MongoDB"]}
    ],
    "metadata": {
        "founded": 2020,
        "active": True,
        "revenue": 1000000.50
    }
}

toolkit.setter("company:techcorp", complex_data)
retrieved = toolkit.getter("company:techcorp")

# Structure and types are fully preserved
print(retrieved["metadata"]["active"])  # True (boolean)
print(type(retrieved["metadata"]["revenue"]))  # <class 'float'>
```

### Handle Binary Data

```python
# Store binary data
binary_data = b"This is binary data \x00\x01\x02"
toolkit.setter("binary_key", binary_data)

# Automatically recognized when reading
retrieved = toolkit.getter("binary_key")
print(type(retrieved))  # <class 'bytes'>
print(retrieved)  # b'This is binary data \x00\x01\x02'
```

### NumPy Array Support

```python
import numpy as np

# Store NumPy array
array = np.array([1, 2, 3, 4, 5], dtype=np.float32)
toolkit.setter("numpy_array", array)

# Read and restore
retrieved = toolkit.getter("numpy_array")
print(type(retrieved))  # <class 'numpy.ndarray'>
print(retrieved.dtype)  # float32
```

## 🛡️ Error Handling

### Using Exception Handling

```python
from redis_toolkit.exceptions import RedisToolkitError, SerializationError

try:
    # Attempt operation
    toolkit.setter("key", some_data)
except SerializationError as e:
    print(f"Serialization error: {e}")
except RedisToolkitError as e:
    print(f"Redis Toolkit error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Using Retry Decorator

```python
from redis_toolkit.utils import with_retry

@with_retry(max_attempts=3, delay=1.0)
def reliable_operation():
    # Operation that might fail
    return toolkit.getter("important_key")

# Automatically retry up to 3 times
result = reliable_operation()
```

## 🔐 Advanced Techniques

### Using Pipeline

```python
# Use pipeline to batch execute commands
pipe = toolkit.client.pipeline()

# Queue multiple commands
for i in range(100):
    pipe.set(f"key:{i}", f"value:{i}")

# Execute all commands at once
pipe.execute()
```

### Using Context Manager

```python
# Automatic resource management
with RedisToolkit() as toolkit:
    toolkit.setter("temp_data", {"session": "12345"})
    data = toolkit.getter("temp_data")
    # Resources cleaned up automatically on exit
```

### Direct Access to Redis Client

```python
# When you need to use native Redis commands
toolkit.client.zadd("leaderboard", {"Alice": 100, "Bob": 90})
toolkit.client.zrange("leaderboard", 0, -1, desc=True, withscores=True)

# Use other Redis features
toolkit.client.expire("temp_key", 3600)
toolkit.client.ttl("temp_key")
```

## 📊 Practical Examples

### Cache System

```python
class CacheSystem:
    def __init__(self, default_ttl=3600):
        self.toolkit = RedisToolkit()
        self.default_ttl = default_ttl
    
    def get_or_set(self, key, fetch_func, ttl=None):
        """Get from cache or set new value"""
        # Try to get from cache
        cached = self.toolkit.getter(key)
        if cached is not None:
            return cached
        
        # Cache miss, execute fetch function
        value = fetch_func()
        
        # Store in cache
        self.toolkit.setter(key, value, ex=ttl or self.default_ttl)
        return value

# Usage example
cache = CacheSystem()

def expensive_calculation():
    print("Performing expensive calculation...")
    return sum(range(1000000))

# First call executes calculation
result = cache.get_or_set("calc_result", expensive_calculation)

# Subsequent calls return from cache
result = cache.get_or_set("calc_result", expensive_calculation)
```

### Counter System

```python
class CounterSystem:
    def __init__(self):
        self.toolkit = RedisToolkit()
    
    def increment(self, counter_name, amount=1):
        """Increment counter"""
        key = f"counter:{counter_name}"
        return self.toolkit.client.incr(key, amount)
    
    def get_count(self, counter_name):
        """Get current count"""
        key = f"counter:{counter_name}"
        count = self.toolkit.client.get(key)
        return int(count) if count else 0
    
    def reset(self, counter_name):
        """Reset counter"""
        key = f"counter:{counter_name}"
        self.toolkit.client.delete(key)

# Usage example
counter = CounterSystem()

# Page view counting
counter.increment("page_views")
counter.increment("page_views")
views = counter.get_count("page_views")
print(f"Page views: {views}")
```

## 🎯 Best Practices

1. **Key Naming Convention**
   ```python
   # Use colons to separate namespaces
   "user:1001"          # User data
   "session:abc123"     # Session data
   "cache:api:users"    # API cache
   ```

2. **Set Appropriate Expiration Times**
   ```python
   # Session data - shorter expiration
   toolkit.setter("session:123", session_data, ex=1800)  # 30 minutes
   
   # Cache data - medium expiration
   toolkit.setter("cache:users", users_list, ex=3600)  # 1 hour
   ```

3. **Handle Large Data**
   ```python
   # Compress large data
   import gzip
   
   large_data = {"huge": "data" * 1000}
   compressed = gzip.compress(json.dumps(large_data).encode())
   toolkit.setter("compressed_data", compressed)
   ```

## 📚 Next Steps

Now that you've mastered the basic operations, you can continue learning:

- [Serialization Features](./serialization.md) - Deep dive into data type handling
- [Pub/Sub](./pubsub.md) - Learn about messaging mechanisms
- [Advanced Batch Operations](/en/advanced/batch-operations.md) - Handle large-scale data

::: tip Practice Suggestion
Try implementing a simple task queue or leaderboard system using Redis Toolkit. This will help you better understand these features.
:::