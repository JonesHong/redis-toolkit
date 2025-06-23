# Redis Toolkit  

![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)  
![Redis Version](https://img.shields.io/badge/redis-4.0+-red.svg)  
![License](https://img.shields.io/badge/license-MIT-green.svg)  

An enhanced Redis library that simplifies working with multiple data types, pub/sub, and buffering for audio/video.  

## ✨ Features

- 🚀 **Rich Data-type Support**  
  Automatic serialize/deserialize for `dict`, `list`, `bool`, `bytes` (Base64 JSON), `int`/`float`, and NumPy arrays :contentReference[oaicite:0]{index=0}  
- 🎵 **Media Buffering**  
  Optimized for audio/video byte buffers  
- 📡 **Smart Pub/Sub**  
  Easy publish/subscribe API with built-in JSON handling  
- 🔧 **Flexible Configuration**  
  Use your own `redis-py` client or built-in connection options  
- 🛡️ **Robustness**  
  Built-in retry decorator (with `ConnectionError` & `TimeoutError`) and health checks  
- 📦 **Bulk Operations**  
  Efficient `batch_set` / `batch_get`  
- 🔄 **Backward Compatible**  
  Alias `RedisCore` remains supported  

## 📦 Installation

```bash
pip install redis-toolkit
```

## 🚀 Quick Start

### Basic Usage

```python
from redis_toolkit import RedisToolkit

toolkit = RedisToolkit()

# Set various types
toolkit.setter("user", {"name": "Alice", "age": 30, "active": True})
toolkit.setter("scores", [95, 87, 92, 88])
toolkit.setter("flag", True)

# Get & automatically deserialize
user   = toolkit.getter("user")    # {'name': 'Alice', 'age': 30, 'active': True}
scores = toolkit.getter("scores")  # [95, 87, 92, 88]
flag   = toolkit.getter("flag")    # True

# Bulk operations
data    = {"a": 1, "b": [2, 3, 4], "c": "hello"}
toolkit.batch_set(data)
results = toolkit.batch_get(["a", "b", "c"])
```

### External Redis Client

```python
import redis
from redis_toolkit import RedisToolkit

custom = redis.Redis(host="localhost", port=6379, db=1)
toolkit = RedisToolkit(redis_client=custom)

# Use enhanced API alongside native commands
toolkit.setter("x", 123)
toolkit.client.lpush("list", "item1", "item2")
```

### Pub/Sub

```python
from redis_toolkit import RedisToolkit

def handler(channel, msg):
    print(f"[{channel}] ->", msg)

sub = RedisToolkit(channels=["news"], message_handler=handler)
pub = RedisToolkit()
pub.publisher("news", {"headline": "Hello Redis", "time": "2025-06-23T10:00:00Z"})
```

### Audio/Video Buffer

```python
import numpy as np
from redis_toolkit import RedisToolkit

audio = np.random.randn(44100).astype(np.float32)
toolkit = RedisToolkit()
toolkit.setter("audio_buf", audio.tobytes())

raw = toolkit.getter("audio_buf")
recovered = np.frombuffer(raw, np.float32)
assert np.array_equal(audio, recovered)
```

### Context Manager

```python
from redis_toolkit import RedisToolkit, RedisOptions

with RedisToolkit(options=RedisOptions(is_logger_info=False)) as tk:
    tk.setter("temp", {"x": 1})
    print(tk.getter("temp"))
# automatically calls cleanup()
```

## ⚙️ Configuration Options

```python
from redis_toolkit import RedisToolkit, RedisOptions, RedisConnectionConfig

config = RedisConnectionConfig(host="...", port=6379, db=2)
options = RedisOptions(
    is_logger_info=True,
    max_log_size=256,
    max_retries=5,
    retry_delay=1.5,
    connection_timeout=10
)

toolkit = RedisToolkit(config=config, options=options)
```

## 🔄 Migration from RedisCore

```diff
- from your_module import RedisCore
- redis_core = RedisCore(channels=…, message_handler=…)
+ from redis_toolkit import RedisToolkit
+ toolkit = RedisToolkit(channels=…, message_handler=…)
# (alias `RedisCore` still available)
```

## 📋 Requirements

* Python >= 3.7
* Redis >= 4.0
* redis-py >= 4.0

## 🤝 Contributing

1. Fork the repo
2. Create a branch (`git checkout -b feature/…`)
3. Commit changes (`git commit -m "…"`)
4. Push and open a PR

## 📄 License

MIT License — see [LICENSE](LICENSE)

## 📞 Support

* **Docs**: [https://redis-toolkit.readthedocs.io](https://redis-toolkit.readthedocs.io)
* **Issues**: [https://github.com/yourusername/redis-toolkit/issues](https://github.com/yourusername/redis-toolkit/issues)
* **Discussions**: [https://github.com/yourusername/redis-toolkit/discussions](https://github.com/yourusername/redis-toolkit/discussions)

