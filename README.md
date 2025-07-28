
<h1 align="center">Redis Toolkit</h1>

<p align="center">
  <img src="https://raw.githubusercontent.com/JonesHong/redis-toolkit/main/assets/images/logo.png" alt="Redis Toolkit Logo" width="200"/>
</p>

<p align="center">
  <a href="https://pypi.org/project/redis-toolkit/">
    <img alt="PyPI version" src="https://img.shields.io/pypi/v/redis-toolkit.svg">
  </a>
  <a href="https://pypi.org/project/redis-toolkit/">
    <img alt="Python versions" src="https://img.shields.io/pypi/pyversions/redis-toolkit.svg">
  </a>
  <a href="https://github.com/JonesHong/redis-toolkit/blob/main/LICENSE">
    <img alt="License" src="https://img.shields.io/github/license/JonesHong/redis-toolkit.svg">
  </a>
  <a href="https://deepwiki.com/JonesHong/redis-toolkit"><img src="https://deepwiki.com/badge.svg" alt="Ask DeepWiki"></a>
</p>


<p align="center">
  <strong>🚀 Enhanced Redis wrapper with intelligent serialization and media processing</strong>
</p>

<p align="center">
  A powerful Redis toolkit that simplifies multi-type data operations, pub/sub messaging, and media file processing with automatic encoding/decoding capabilities.
</p>

---

## ✨ Features

- 🎯 **Smart & Secure Serialization**: Automatic handling of `dict`, `list`, `bool`, `bytes`, `int`, `float`, and `numpy` arrays using JSON-based serialization (no pickle!)
- 🔐 **Security First**: No pickle serialization means no remote code execution vulnerabilities
- 🎵 **Media Processing**: Built-in converters for images, audio, and video files
- 📡 **Pub/Sub Made Easy**: Simplified publish/subscribe with automatic JSON serialization
- 🔧 **Flexible Configuration**: Support for custom Redis clients and connection settings
- 🛡️ **Resilient Operations**: Built-in retry mechanisms with `@with_retry` decorator
- 📦 **Batch Operations**: Efficient `batch_set` and `batch_get` for bulk operations
- 🎨 **Pretty Logging**: Enhanced logging with pretty-loguru integration
- 🔧 **Flexible Configuration**: Simple configuration with Python dataclasses

## 📦 Installation

### Basic Installation
```bash
pip install redis-toolkit
```

### With Media Processing
```bash
# For image processing
pip install redis-toolkit[cv2]

# For audio processing (basic)
pip install redis-toolkit[audio]

# For audio processing (with MP3 support)
pip install redis-toolkit[audio-full]

# For complete media support
pip install redis-toolkit[all]
```

## 🚀 Quick Start

### Basic Usage

```python
from redis_toolkit import RedisToolkit
from redis import Redis

# Method 1: Pass existing Redis instance
redis_client = Redis(host='localhost', port=6379, decode_responses=False)
toolkit = RedisToolkit(redis=redis_client)

# Method 2: Use configuration (with connection pooling)
from redis_toolkit import RedisConnectionConfig
config = RedisConnectionConfig(host='localhost', port=6379)
toolkit = RedisToolkit(config=config)

# Method 3: Use defaults
toolkit = RedisToolkit()

# Store different data types
toolkit.setter("user", {"name": "Alice", "age": 25, "active": True})
toolkit.setter("scores", [95, 87, 92, 88])
toolkit.setter("flag", True)
toolkit.setter("binary_data", b"Hello, World!")

# Automatic deserialization
user = toolkit.getter("user")      # {'name': 'Alice', 'age': 25, 'active': True}
scores = toolkit.getter("scores")  # [95, 87, 92, 88]
flag = toolkit.getter("flag")      # True (bool, not string)

# Access the underlying Redis client for advanced operations
raw_value = toolkit.client.get("user")  # Get raw bytes
toolkit.client.expire("user", 3600)     # Set TTL
```

### Media Processing with Converters

```python
from redis_toolkit import RedisToolkit
from redis_toolkit.converters import encode_image, decode_image
from redis_toolkit.converters import encode_audio, decode_audio
import cv2
import numpy as np

toolkit = RedisToolkit()

# Image processing
img = cv2.imread('photo.jpg')
img_bytes = encode_image(img, format='jpg', quality=90)
toolkit.setter('my_image', img_bytes)

# Retrieve and decode
retrieved_bytes = toolkit.getter('my_image')
decoded_img = decode_image(retrieved_bytes)

# Audio processing
sample_rate = 44100
audio_data = np.sin(2 * np.pi * 440 * np.linspace(0, 1, sample_rate))
audio_bytes = encode_audio(audio_data, sample_rate=sample_rate)
toolkit.setter('my_audio', audio_bytes)

# Retrieve and decode
retrieved_audio = toolkit.getter('my_audio')
decoded_rate, decoded_audio = decode_audio(retrieved_audio)
```

### Pub/Sub with Media Sharing

```python
from redis_toolkit import RedisToolkit
from redis_toolkit.converters import encode_image
import base64

# Setup subscriber
def message_handler(channel, data):
    if data.get('type') == 'image':
        # Decode base64 image data
        img_bytes = base64.b64decode(data['image_data'])
        img = decode_image(img_bytes)
        print(f"Received image: {img.shape}")

subscriber = RedisToolkit(
    channels=["media_channel"],
    message_handler=message_handler
)

# Setup publisher
publisher = RedisToolkit()

# Send image through pub/sub
img_bytes = encode_image(your_image_array, format='jpg', quality=80)
img_base64 = base64.b64encode(img_bytes).decode('utf-8')

message = {
    'type': 'image',
    'user': 'Alice',
    'image_data': img_base64,
    'timestamp': time.time()
}

publisher.publisher("media_channel", message)
```

### Advanced Configuration

```python
from redis_toolkit import RedisToolkit, RedisOptions, RedisConnectionConfig

# Custom Redis connection
config = RedisConnectionConfig(
    host="localhost",
    port=6379,
    db=1,
    password="your_password"
)

# Custom options
options = RedisOptions(
    is_logger_info=True,
    max_log_size=512,
    subscriber_retry_delay=10,
    log_level="INFO",  # Support for pretty-loguru
    log_path="./logs"  # Optional file logging
)

# Method 1: With configuration
toolkit = RedisToolkit(config=config, options=options)

# Method 2: With existing Redis client
import redis
pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
redis_client = redis.Redis(connection_pool=pool)
toolkit = RedisToolkit(redis=redis_client, options=options)

# Access the underlying Redis client
print(f"Redis server info: {toolkit.client.info()['redis_version']}")
```


### Batch Operations

```python
# Batch set
data = {
    "user:1": {"name": "Alice", "score": 95},
    "user:2": {"name": "Bob", "score": 87},
    "user:3": {"name": "Charlie", "score": 92}
}
toolkit.batch_set(data)

# Batch get
keys = ["user:1", "user:2", "user:3"]
results = toolkit.batch_get(keys)
```

### Context Manager

```python
with RedisToolkit() as toolkit:
    toolkit.setter("temp_data", {"session": "12345"})
    data = toolkit.getter("temp_data")
    # Automatic cleanup on exit
```

## 🎨 Media Converters

### Image Converter

```python
from redis_toolkit.converters import get_converter

# Create image converter with custom settings
img_converter = get_converter('image', format='png', quality=95)

# Encode image
encoded = img_converter.encode(image_array)

# Decode image
decoded = img_converter.decode(encoded)

# Resize image
resized = img_converter.resize(image_array, width=800, height=600)

# Get image info
info = img_converter.get_info(encoded_bytes)
```

### Audio Converter

```python
from redis_toolkit.converters import get_converter

# Create audio converter
audio_converter = get_converter('audio', sample_rate=44100, format='wav')

# Encode from file
encoded = audio_converter.encode_from_file('song.mp3')

# Encode from array
encoded = audio_converter.encode((sample_rate, audio_array))

# Decode audio
sample_rate, audio_array = audio_converter.decode(encoded)

# Normalize audio
normalized = audio_converter.normalize(audio_array, target_level=0.8)

# Get file info
info = audio_converter.get_file_info('song.mp3')
```

### Video Converter

```python
from redis_toolkit.converters import get_converter

# Create video converter
video_converter = get_converter('video')

# Encode video file
encoded = video_converter.encode('movie.mp4')

# Save video bytes to file
video_converter.save_video_bytes(encoded, 'output.mp4')

# Get video info
info = video_converter.get_video_info('movie.mp4')

# Extract frames
frames = video_converter.extract_frames('movie.mp4', max_frames=10)
```

## 🎯 Use Cases

### Real-time Image Sharing
Perfect for applications that need to share images instantly across different services or users.

### Audio/Video Streaming
Handle audio and video buffers efficiently with automatic encoding/decoding.

### Multi-media Chat Applications
Build chat applications that support text, images, audio, and video messages.

### Data Analytics Dashboards
Share real-time charts and visualizations between different components.

### IoT Data Processing
Handle sensor data, images from cameras, and audio from microphones.

## ⚙️ Configuration Options

### Redis Connection Config
```python
RedisConnectionConfig(
    host='localhost',
    port=6379,
    db=0,
    password=None,
    username=None,
    encoding='utf-8',
    decode_responses=False,     # Always False for proper serialization
    socket_keepalive=True,
    socket_keepalive_options=None,
    connection_timeout=None,    # Connection timeout in seconds
    socket_timeout=None,        # Socket operation timeout in seconds
    retry_on_timeout=False,     # Retry on timeout
    retry_on_error=True,        # Retry on error
    health_check_interval=30,   # Health check interval in seconds
    ssl=False,                  # Use SSL/TLS
    ssl_keyfile=None,          # SSL key file path
    ssl_certfile=None,         # SSL certificate file path
    ssl_ca_certs=None,         # SSL CA certificates file path
    ssl_cert_reqs='required'   # SSL certificate requirement level
)
```

### Redis Options
```python
RedisOptions(
    is_logger_info=True,           # Enable logging
    max_log_size=256,              # Max log entry size
    subscriber_retry_delay=5,      # Subscriber reconnection delay
    subscriber_stop_timeout=5,     # Subscriber stop timeout
    log_level="INFO",              # Log level (DEBUG, INFO, WARNING, ERROR)
    log_path=None,                 # Log file path (None for console only)
    max_value_size=10*1024*1024,   # Max value size in bytes (10MB)
    max_key_length=512,            # Max key length
    enable_validation=True,        # Enable validation
    use_connection_pool=True,      # Use shared connection pool
    max_connections=None           # Max connections (None for unlimited)
)
```

### Configuration Validation

Both `RedisOptions` and `RedisConnectionConfig` support validation:

```python
# Validate configuration before use
options = RedisOptions(log_level="DEBUG")
options.validate()  # Raises ValueError if invalid

config = RedisConnectionConfig(port=6379, ssl=True)
config.validate()  # Raises ValueError if invalid

# RedisToolkit automatically validates options on initialization
toolkit = RedisToolkit(config=config, options=options)
```

## 📋 Requirements

- Python >= 3.7
- Redis >= 4.0
- redis-py >= 4.0

### Optional Dependencies
- **OpenCV**: For image and video processing (`pip install opencv-python`)
- **NumPy**: For array operations (`pip install numpy`)
- **SciPy**: For audio processing (`pip install scipy`)
- **SoundFile**: For advanced audio formats (`pip install soundfile`)
- **Pillow**: For additional image formats (`pip install Pillow`)

## 🧪 Testing

```bash
# Install development dependencies
pip install redis-toolkit[dev]

# Run tests
pytest

# Run with coverage
pytest --cov=redis_toolkit

# Run specific test categories
pytest -m "not slow"  # Skip slow tests
pytest -m integration  # Run integration tests only
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact & Support

- **Documentation**: [https://redis-toolkit.readthedocs.io](https://redis-toolkit.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/JonesHong/redis-toolkit/issues)
- **Discussions**: [GitHub Discussions](https://github.com/JonesHong/redis-toolkit/discussions)
- **PyPI**: [https://pypi.org/project/redis-toolkit/](https://pypi.org/project/redis-toolkit/)

## 🌟 Showcase

**Used by these awesome projects:**
- Add your project here by opening a PR!

---

<p align="center">
  Made with ❤️ by the Redis Toolkit Team
</p>