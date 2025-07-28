# Redis Toolkit API Reference

Complete API documentation for Redis Toolkit.

## Table of Contents

- [RedisToolkit](#redistoolkit)
- [Configuration Classes](#configuration-classes)
- [Converters](#converters)
- [Exceptions](#exceptions)
- [Utilities](#utilities)

## RedisToolkit

The main class for interacting with Redis.

### Class: `RedisToolkit`

```python
class RedisToolkit(
    redis: Optional[Redis] = None,
    config: Optional[RedisConnectionConfig] = None,
    channels: Optional[List[str]] = None,
    message_handler: Optional[Callable[[str, Any], None]] = None,
    options: Optional[RedisOptions] = None,
)
```

#### Parameters

- **redis** (`Optional[Redis]`): Existing Redis client instance. Mutually exclusive with `config`.
- **config** (`Optional[RedisConnectionConfig]`): Redis connection configuration. Mutually exclusive with `redis`.
- **channels** (`Optional[List[str]]`): List of channels to subscribe to.
- **message_handler** (`Optional[Callable[[str, Any], None]]`): Function to handle received messages.
- **options** (`Optional[RedisOptions]`): Toolkit behavior options.

#### Properties

##### `client`

```python
@property
def client(self) -> Redis
```

Returns the underlying Redis client for direct access to Redis commands.

#### Methods

##### `setter`

```python
def setter(
    self,
    name: str,
    value: Any,
    options: Optional[RedisOptions] = None
) -> None
```

Sets a key-value pair in Redis with automatic serialization.

**Parameters:**
- **name** (`str`): The key name.
- **value** (`Any`): The value to store (supports dict, list, bool, bytes, int, float, str, numpy arrays).
- **options** (`Optional[RedisOptions]`): Override default options.

**Raises:**
- `ValidationError`: If key/value validation fails.
- `SerializationError`: If serialization fails.
- `RedisToolkitError`: If Redis operation fails.

**Example:**
```python
toolkit.setter("user:1", {"name": "Alice", "age": 25})
toolkit.setter("scores", [95, 87, 92])
toolkit.setter("active", True)
```

##### `getter`

```python
def getter(
    self,
    name: str,
    options: Optional[RedisOptions] = None
) -> Any
```

Gets a value from Redis with automatic deserialization.

**Parameters:**
- **name** (`str`): The key name.
- **options** (`Optional[RedisOptions]`): Override default options.

**Returns:**
- `Any`: The deserialized value, or `None` if key doesn't exist.

**Raises:**
- `SerializationError`: If deserialization fails.

**Example:**
```python
user = toolkit.getter("user:1")  # Returns: {"name": "Alice", "age": 25}
scores = toolkit.getter("scores")  # Returns: [95, 87, 92]
```

##### `deleter`

```python
def deleter(self, name: str) -> bool
```

Deletes a key from Redis.

**Parameters:**
- **name** (`str`): The key name.

**Returns:**
- `bool`: True if key was deleted, False if key didn't exist.

**Example:**
```python
deleted = toolkit.deleter("user:1")
```

##### `batch_set`

```python
def batch_set(
    self,
    mapping: Dict[str, Any],
    options: Optional[RedisOptions] = None
) -> None
```

Sets multiple key-value pairs in a single pipeline operation.

**Parameters:**
- **mapping** (`Dict[str, Any]`): Dictionary of key-value pairs.
- **options** (`Optional[RedisOptions]`): Override default options.

**Raises:**
- `ValidationError`: If validation fails.
- `SerializationError`: If serialization fails.
- `RedisToolkitError`: If Redis operation fails.

**Example:**
```python
toolkit.batch_set({
    "user:1": {"name": "Alice", "age": 25},
    "user:2": {"name": "Bob", "age": 30},
    "user:3": {"name": "Charlie", "age": 35}
})
```

##### `batch_get`

```python
def batch_get(
    self,
    names: List[str],
    options: Optional[RedisOptions] = None
) -> Dict[str, Any]
```

Gets multiple values in a single operation.

**Parameters:**
- **names** (`List[str]`): List of key names.
- **options** (`Optional[RedisOptions]`): Override default options.

**Returns:**
- `Dict[str, Any]`: Dictionary mapping keys to values (None for non-existent keys).

**Example:**
```python
results = toolkit.batch_get(["user:1", "user:2", "user:3"])
# Returns: {"user:1": {...}, "user:2": {...}, "user:3": None}
```

##### `publisher`

```python
def publisher(
    self,
    channel: str,
    data: Any,
    options: Optional[RedisOptions] = None
) -> None
```

Publishes a message to a channel.

**Parameters:**
- **channel** (`str`): Channel name.
- **data** (`Any`): Data to publish (automatically serialized).
- **options** (`Optional[RedisOptions]`): Override default options.

**Raises:**
- `SerializationError`: If serialization fails.

**Example:**
```python
toolkit.publisher("notifications", {
    "type": "user_login",
    "user_id": 123,
    "timestamp": time.time()
})
```

##### `health_check`

```python
def health_check(self) -> bool
```

Checks if Redis connection is healthy.

**Returns:**
- `bool`: True if connection is healthy, False otherwise.

##### `stop_subscriber`

```python
def stop_subscriber(self) -> None
```

Stops the subscriber thread safely.

##### `cleanup`

```python
def cleanup(self) -> None
```

Cleans up resources (stops subscriber, closes connections).

## Configuration Classes

### Class: `RedisOptions`

Configuration options for RedisToolkit behavior.

```python
@dataclass
class RedisOptions:
    # Logging
    is_logger_info: bool = True
    max_log_size: int = 256
    log_level: str = "INFO"
    log_path: Optional[str] = None
    
    # Subscriber
    subscriber_retry_delay: int = 5
    subscriber_stop_timeout: int = 5
    
    # Security
    max_value_size: int = 10 * 1024 * 1024
    max_key_length: int = 512
    enable_validation: bool = True
    
    # Connection Pool
    use_connection_pool: bool = True
    max_connections: Optional[int] = None
```

#### Methods

##### `validate`

```python
def validate(self) -> None
```

Validates the configuration options.

**Raises:**
- `ValueError`: If any option is invalid.

### Class: `RedisConnectionConfig`

Redis connection configuration.

```python
@dataclass
class RedisConnectionConfig:
    host: str = 'localhost'
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    username: Optional[str] = None
    encoding: str = 'utf-8'
    socket_keepalive: bool = True
    socket_keepalive_options: Optional[dict] = None
    connection_timeout: Optional[float] = None
    socket_timeout: Optional[float] = None
    retry_on_timeout: bool = False
    retry_on_error: bool = True
    health_check_interval: int = 30
    ssl: bool = False
    ssl_keyfile: Optional[str] = None
    ssl_certfile: Optional[str] = None
    ssl_ca_certs: Optional[str] = None
    ssl_cert_reqs: str = 'required'
```

#### Methods

##### `validate`

```python
def validate(self) -> None
```

Validates the connection configuration.

**Raises:**
- `ValueError`: If any configuration is invalid.

##### `to_redis_kwargs`

```python
def to_redis_kwargs(self) -> dict
```

Converts configuration to Redis client constructor arguments.

## Converters

### Image Converter

```python
from redis_toolkit.converters import get_converter, encode_image, decode_image

# Using converter class
converter = get_converter('image', format='jpg', quality=90)
encoded = converter.encode(image_array)
decoded = converter.decode(encoded)

# Using convenience functions
encoded = encode_image(image_array, format='jpg', quality=90)
decoded = decode_image(encoded)
```

#### Methods

- **encode(image_array)**: Encodes numpy array to bytes
- **decode(image_bytes)**: Decodes bytes to numpy array
- **resize(image_array, width, height)**: Resizes image
- **get_info(image_bytes)**: Gets image metadata

### Audio Converter

```python
from redis_toolkit.converters import get_converter, encode_audio, decode_audio

# Using converter class
converter = get_converter('audio', sample_rate=44100, format='wav')
encoded = converter.encode((sample_rate, audio_array))
sample_rate, decoded = converter.decode(encoded)

# Using convenience functions
encoded = encode_audio(audio_array, sample_rate=44100)
sample_rate, decoded = decode_audio(encoded)
```

#### Methods

- **encode(audio_tuple)**: Encodes (sample_rate, array) to bytes
- **decode(audio_bytes)**: Decodes bytes to (sample_rate, array)
- **encode_from_file(file_path)**: Loads and encodes audio file
- **normalize(audio_array, target_level)**: Normalizes audio level
- **get_file_info(file_path)**: Gets audio file metadata

### Video Converter

```python
from redis_toolkit.converters import get_converter, encode_video, decode_video

# Using converter class
converter = get_converter('video')
encoded = converter.encode('video.mp4')
decoded = converter.decode(encoded)

# Using convenience functions
encoded = encode_video('video.mp4')
decoded = decode_video(encoded)
```

#### Methods

- **encode(video_path)**: Reads video file to bytes
- **decode(video_bytes)**: Returns video bytes (passthrough)
- **save_video_bytes(video_bytes, output_path)**: Saves bytes to file
- **get_video_info(video_path)**: Gets video metadata
- **extract_frames(video_path, max_frames)**: Extracts video frames

## Exceptions

### `RedisToolkitError`

Base exception for all Redis Toolkit errors.

```python
class RedisToolkitError(Exception):
    """Base exception for Redis Toolkit"""
```

### `SerializationError`

Raised when serialization/deserialization fails.

```python
class SerializationError(RedisToolkitError):
    def __init__(
        self,
        message: str,
        original_data: Any = None,
        original_exception: Optional[Exception] = None
    )
```

### `ValidationError`

Raised when validation fails.

```python
class ValidationError(RedisToolkitError):
    """Raised when validation fails"""
```

### `ConverterNotAvailableError`

Raised when a converter is not available due to missing dependencies.

```python
class ConverterNotAvailableError(Exception):
    def __init__(
        self,
        converter_name: str,
        reason: str,
        available_converters: List[str]
    )
```

## Utilities

### Retry Decorators

#### `@simple_retry`

Basic retry decorator with exponential backoff.

```python
from redis_toolkit.utils.retry import simple_retry

@simple_retry(max_retries=3, base_delay=1.0)
def unstable_operation():
    # Your code here
    pass
```

#### `@with_retry`

Advanced retry decorator with more options.

```python
from redis_toolkit.utils.retry import with_retry

@with_retry(
    max_attempts=5,
    delay=0.5,
    backoff_factor=2,
    exceptions=(ConnectionError, TimeoutError),
    on_retry=lambda e, attempt: print(f"Retry {attempt}: {e}")
)
def network_operation():
    # Your code here
    pass
```

### Serialization Functions

```python
from redis_toolkit.utils.serializers import serialize_value, deserialize_value

# Serialize any supported type
serialized = serialize_value({"key": "value"})

# Deserialize back
original = deserialize_value(serialized)
```

## Context Manager Usage

RedisToolkit supports context manager protocol for automatic cleanup:

```python
with RedisToolkit() as toolkit:
    toolkit.setter("key", "value")
    value = toolkit.getter("key")
    # Automatic cleanup on exit
```

## Thread Safety

- RedisToolkit instances are thread-safe for all operations
- The connection pool manager is a thread-safe singleton
- Subscriber runs in a separate daemon thread

## Performance Tips

1. Use batch operations for multiple keys
2. Enable connection pooling (default)
3. Configure appropriate timeouts
4. Use SSL only when necessary
5. Set reasonable max_value_size limits

## Error Handling

All methods follow these error handling patterns:

1. **Validation errors** → `ValidationError`
2. **Serialization errors** → `SerializationError`
3. **Redis errors** → `RedisToolkitError`
4. **Missing dependencies** → `ConverterNotAvailableError`

Example:

```python
try:
    toolkit.setter("key", large_data)
except ValidationError as e:
    print(f"Validation failed: {e}")
except SerializationError as e:
    print(f"Serialization failed: {e}")
    print(f"Original data type: {type(e.original_data)}")
except RedisToolkitError as e:
    print(f"Redis operation failed: {e}")
```