# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Redis Toolkit is a Python library that provides enhanced Redis functionality with automatic serialization, pub/sub support, and media processing capabilities. The codebase is written primarily in Traditional Chinese (繁體中文) comments and documentation.

## Key Architecture

### Core Components

1. **RedisToolkit** (`redis_toolkit/core.py`): Main interface for Redis operations
   - Automatic serialization/deserialization of Python types (dict, list, bool, bytes, numpy arrays)
   - Pub/Sub with automatic JSON handling
   - Connection pool management
   - Batch operations support

2. **Converters** (`redis_toolkit/converters/`): Media processing modules
   - Image converter: OpenCV-based image encoding/decoding
   - Audio converter: SciPy/SoundFile-based audio processing
   - Video converter: OpenCV-based video handling

3. **Serialization** (`redis_toolkit/utils/serializers.py`): JSON-based secure serialization
   - No pickle usage (security-first design)
   - Custom handling for bytes, numpy arrays, and complex types

## Development Commands

### Testing

```bash
# Run basic tests (core functionality)
python tests/run_tests.py basic

# Run all tests
python tests/run_tests.py all

# Run converter/media tests
python tests/run_tests.py converters
python tests/run_tests.py media

# Run with coverage
python tests/run_tests.py coverage

# Run specific test file
pytest tests/unit/test_core.py -v

# Run tests without slow tests
pytest -m "not slow"
```

### Linting and Formatting

```bash
# Format code with black
black redis_toolkit tests

# Check with flake8
flake8 redis_toolkit tests

# Type checking with mypy
mypy redis_toolkit
```

### Building and Distribution

```bash
# Build package
python -m build

# Install in development mode
pip install -e .

# Install with media dependencies
pip install -e ".[cv2,audio]"
pip install -e ".[all]"  # All optional dependencies
```

## Testing Requirements

- Redis server must be running on localhost:6379 for integration tests
- Optional dependencies (opencv-python, numpy, scipy) needed for converter tests
- Use `--skip-redis-check` flag to run tests without Redis

## Code Conventions

1. **Language**: Comments and docstrings are in Traditional Chinese (繁體中文)
2. **Error Handling**: Use custom exceptions from `redis_toolkit.exceptions`
3. **Logging**: Uses pretty-loguru for enhanced logging
4. **Serialization**: Always use the secure JSON-based serializers, never pickle
5. **Type Hints**: Comprehensive type hints throughout the codebase

## Key Design Decisions

1. **No Pickle Serialization**: For security, all serialization uses JSON with custom encoders
2. **Connection Pool Management**: Shared pools via `pool_manager` for efficiency
3. **Retry Mechanisms**: Built-in retry decorators for resilient operations
4. **Flexible Configuration**: Support both Redis instance passing and config-based initialization

## Common Development Tasks

### Adding a New Converter

1. Create converter class in `redis_toolkit/converters/`
2. Implement `encode()` and `decode()` methods
3. Register in `converters/__init__.py`
4. Add tests in `tests/unit/test_converters.py`

### Working with Redis Operations

- Use `@with_retry` decorator for operations that might fail
- Always validate input with the validation utilities
- Log operations appropriately based on `options.is_logger_info`

### Running Examples

```bash
# Basic examples
python examples/quickstart/01_hello_redis.py

# Media processing examples
python examples/real-world/media_processing/complete_example.py
```

## Important Notes

- The project uses dataclasses for configuration (`RedisOptions`, `RedisConnectionConfig`)
- Media converters are optional and depend on external libraries
- Always check for optional dependencies before using converters
- The codebase follows a modular design with clear separation of concerns