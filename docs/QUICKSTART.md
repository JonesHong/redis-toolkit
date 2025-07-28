# Redis Toolkit Quick Start Guide

Get up and running with Redis Toolkit in minutes!

## Installation

### Basic Installation

```bash
pip install redis-toolkit
```

### With Media Processing Support

```bash
# For image processing
pip install redis-toolkit[cv2]

# For audio processing
pip install redis-toolkit[audio]

# For all features
pip install redis-toolkit[all]
```

## Basic Usage

### 1. Simple Key-Value Operations

```python
from redis_toolkit import RedisToolkit

# Create toolkit instance
toolkit = RedisToolkit()

# Store data - automatic serialization
toolkit.setter("user:1", {"name": "Alice", "age": 25, "active": True})
toolkit.setter("scores", [95, 87, 92, 88])
toolkit.setter("config", {"debug": False, "timeout": 30})

# Retrieve data - automatic deserialization
user = toolkit.getter("user:1")      # Returns dict
scores = toolkit.getter("scores")    # Returns list
config = toolkit.getter("config")    # Returns dict

# Delete data
toolkit.deleter("user:1")
```

### 2. Connection Options

#### Option 1: Use Default Connection

```python
# Connects to localhost:6379, db=0
toolkit = RedisToolkit()
```

#### Option 2: Pass Existing Redis Client

```python
from redis import Redis

# Create your own Redis client
redis_client = Redis(
    host='redis-server.example.com',
    port=6379,
    password='your-password'
)

# Pass it to RedisToolkit
toolkit = RedisToolkit(redis=redis_client)
```

#### Option 3: Use Configuration

```python
from redis_toolkit import RedisToolkit, RedisConnectionConfig

# Create configuration
config = RedisConnectionConfig(
    host='redis-server.example.com',
    port=6379,
    password='your-password',
    db=1,
    connection_timeout=5.0,
    socket_timeout=10.0
)

# Create toolkit with configuration
toolkit = RedisToolkit(config=config)
```

### 3. Batch Operations

Process multiple items efficiently:

```python
# Batch set multiple items
users = {
    "user:1": {"name": "Alice", "score": 95},
    "user:2": {"name": "Bob", "score": 87},
    "user:3": {"name": "Charlie", "score": 92}
}
toolkit.batch_set(users)

# Batch get multiple items
keys = ["user:1", "user:2", "user:3"]
results = toolkit.batch_get(keys)
```

### 4. Pub/Sub Messaging

#### Publisher

```python
from redis_toolkit import RedisToolkit

# Create publisher
publisher = RedisToolkit()

# Publish messages
publisher.publisher("notifications", {
    "type": "user_login",
    "user_id": 123,
    "timestamp": time.time()
})

publisher.publisher("events", {
    "action": "purchase",
    "item_id": "ABC123",
    "amount": 99.99
})
```

#### Subscriber

```python
from redis_toolkit import RedisToolkit

# Define message handler
def handle_message(channel, data):
    print(f"Received on {channel}: {data}")
    
    if channel == "notifications":
        if data["type"] == "user_login":
            print(f"User {data['user_id']} logged in")
    
    elif channel == "events":
        if data["action"] == "purchase":
            print(f"Purchase: {data['item_id']} for ${data['amount']}")

# Create subscriber
subscriber = RedisToolkit(
    channels=["notifications", "events"],
    message_handler=handle_message
)

# Keep the program running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    subscriber.cleanup()
```

## Common Use Cases

### 1. Session Storage

```python
# Store user session
session_data = {
    "user_id": 123,
    "username": "alice",
    "roles": ["user", "admin"],
    "login_time": time.time()
}
toolkit.setter(f"session:{session_id}", session_data)

# Retrieve session
session = toolkit.getter(f"session:{session_id}")
```

### 2. Caching API Responses

```python
import json
import requests

def get_user_data(user_id):
    # Check cache first
    cache_key = f"api:user:{user_id}"
    cached = toolkit.getter(cache_key)
    
    if cached:
        return cached
    
    # Fetch from API
    response = requests.get(f"https://api.example.com/users/{user_id}")
    data = response.json()
    
    # Cache for 1 hour using native Redis client
    toolkit.setter(cache_key, data)
    toolkit.client.expire(cache_key, 3600)
    
    return data
```

### 3. Task Queue

```python
# Producer
def add_task(task_data):
    task_id = str(uuid.uuid4())
    toolkit.setter(f"task:{task_id}", {
        "id": task_id,
        "data": task_data,
        "status": "pending",
        "created_at": time.time()
    })
    toolkit.publisher("task_queue", {"task_id": task_id})

# Consumer
def task_handler(channel, data):
    task_id = data["task_id"]
    task = toolkit.getter(f"task:{task_id}")
    
    if task:
        # Process task
        process_task(task)
        
        # Update status
        task["status"] = "completed"
        toolkit.setter(f"task:{task_id}", task)
```

### 4. Real-time Metrics

```python
# Increment counter
def track_page_view(page):
    key = f"metrics:pageviews:{page}:{datetime.now().strftime('%Y-%m-%d')}"
    current = toolkit.getter(key) or 0
    toolkit.setter(key, current + 1)

# Get metrics
def get_page_views(page, date):
    key = f"metrics:pageviews:{page}:{date}"
    return toolkit.getter(key) or 0
```

## Media Processing

### Image Processing

```python
from redis_toolkit.converters import encode_image, decode_image
import cv2

# Read and store image
img = cv2.imread('photo.jpg')
img_bytes = encode_image(img, format='jpg', quality=85)
toolkit.setter('user:avatar:123', img_bytes)

# Retrieve and decode
stored_bytes = toolkit.getter('user:avatar:123')
restored_img = decode_image(stored_bytes)
```

### Audio Processing

```python
from redis_toolkit.converters import encode_audio, decode_audio
import numpy as np

# Generate audio
sample_rate = 44100
duration = 2  # seconds
frequency = 440  # Hz (A4 note)
t = np.linspace(0, duration, int(sample_rate * duration))
audio_data = np.sin(2 * np.pi * frequency * t)

# Store audio
audio_bytes = encode_audio(audio_data, sample_rate=sample_rate)
toolkit.setter('audio:tone:a4', audio_bytes)

# Retrieve audio
stored_bytes = toolkit.getter('audio:tone:a4')
rate, audio = decode_audio(stored_bytes)
```

## Configuration Tips

### Custom Options

```python
from redis_toolkit import RedisOptions

options = RedisOptions(
    # Logging
    is_logger_info=True,
    log_level="DEBUG",
    max_log_size=512,
    
    # Security
    max_value_size=50 * 1024 * 1024,  # 50MB limit
    max_key_length=256,
    enable_validation=True,
    
    # Performance
    use_connection_pool=True,
    max_connections=50
)

toolkit = RedisToolkit(options=options)
```

### SSL/TLS Connection

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

## Error Handling

```python
from redis_toolkit.exceptions import (
    ValidationError,
    SerializationError,
    RedisToolkitError
)

try:
    # Validation error example
    toolkit.setter("x" * 1000, "value")  # Key too long
    
except ValidationError as e:
    print(f"Validation failed: {e}")
    
except SerializationError as e:
    print(f"Cannot serialize data: {e}")
    
except RedisToolkitError as e:
    print(f"Redis error: {e}")
```

## Best Practices

1. **Use Context Managers**: Ensures proper cleanup

```python
with RedisToolkit() as toolkit:
    toolkit.setter("key", "value")
    # Automatic cleanup on exit
```

2. **Validate Configuration**: Check before using

```python
config = RedisConnectionConfig(port=6379)
config.validate()  # Raises ValueError if invalid
```

3. **Handle Missing Keys**: Check for None

```python
value = toolkit.getter("maybe-missing-key")
if value is None:
    # Handle missing key
    value = default_value
```

4. **Use Batch Operations**: More efficient for multiple items

```python
# Instead of multiple setter calls
for key, value in items.items():
    toolkit.setter(key, value)

# Use batch_set
toolkit.batch_set(items)
```

5. **Access Native Redis**: For advanced operations

```python
# Use native Redis commands when needed
toolkit.client.zadd("leaderboard", {"alice": 100, "bob": 95})
toolkit.client.expire("temporary-key", 300)
```

## Troubleshooting

### Check Dependencies

```python
from redis_toolkit.converters import check_dependencies

# Check all converter dependencies
check_dependencies()
```

### Connection Issues

```python
# Check connection health
if not toolkit.health_check():
    print("Redis connection is not healthy")
```

### Debug Logging

```python
# Enable debug logging
options = RedisOptions(log_level="DEBUG")
toolkit = RedisToolkit(options=options)
```

## Next Steps

- Read the full [API Documentation](API.md)
- Explore [example scripts](../examples/)
- Check the [changelog](CHANGELOG.md) for updates
- Report issues on [GitHub](https://github.com/JonesHong/redis-toolkit/issues)