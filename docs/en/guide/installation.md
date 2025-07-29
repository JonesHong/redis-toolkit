# Installation Guide

This guide will explain in detail how to install and configure Redis Toolkit in different environments.

## 📋 System Requirements

### Python Version
- Python >= 3.7
- Python 3.8 or higher recommended for best performance

### Redis Version
- Redis >= 4.0
- Redis 5.0 or higher recommended
- Supports Redis Cluster and Sentinel mode

### Operating Systems
- ✅ Linux (Ubuntu, CentOS, Debian, etc.)
- ✅ macOS
- ✅ Windows 10/11
- ✅ Docker containers

## 🎯 Quick Installation

### Basic Installation

The simplest installation method, includes core features:

```bash
pip install redis-toolkit
```

This will install:
- Redis Toolkit core features
- redis-py (Redis Python client)
- pretty-loguru (enhanced logging output)

### Advanced Installation Options

Choose different installation configurations based on your needs:

```bash
# Include image processing features (OpenCV)
pip install redis-toolkit[cv2]

# Include audio processing features
pip install redis-toolkit[audio]

# Include full audio support (with MP3)
pip install redis-toolkit[audio-full]

# Include all media processing features
pip install redis-toolkit[media]

# Install all optional features
pip install redis-toolkit[all]

# Development environment (includes testing tools)
pip install redis-toolkit[dev]
```

## 📦 Dependencies Explained

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| redis | >= 4.0.0 | Redis Python client |
| pretty-loguru | >= 1.1.3 | Enhanced logging features |

### Optional Dependencies

#### Image Processing
| Package | Version | Purpose |
|---------|---------|---------|
| opencv-python | >= 4.5.0 | Image encoding/decoding |
| numpy | >= 1.19.0 | Array operations |
| Pillow | >= 8.0.0 | Additional image format support |

#### Audio Processing
| Package | Version | Purpose |
|---------|---------|---------|
| numpy | >= 1.19.0 | Audio data processing |
| scipy | >= 1.7.0 | Signal processing |
| soundfile | >= 0.10.0 | Audio file I/O |

#### Development Tools
| Package | Version | Purpose |
|---------|---------|---------|
| pytest | >= 6.0 | Unit testing |
| black | >= 21.0 | Code formatting |
| mypy | >= 0.910 | Type checking |

## 🐳 Docker Installation

### Using Official Image

```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Redis Toolkit
RUN pip install redis-toolkit[all]

# Your application code
COPY . /app
WORKDIR /app

CMD ["python", "app.py"]
```

### Docker Compose Configuration

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  app:
    build: .
    depends_on:
      - redis
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    volumes:
      - .:/app

volumes:
  redis_data:
```

## 🔧 Virtual Environment Installation

### Using venv

```bash
# Create virtual environment
python -m venv redis_env

# Activate virtual environment
# Linux/macOS
source redis_env/bin/activate
# Windows
redis_env\Scripts\activate

# Install Redis Toolkit
pip install redis-toolkit[all]
```

### Using conda

```bash
# Create conda environment
conda create -n redis_env python=3.9

# Activate environment
conda activate redis_env

# Install Redis Toolkit
pip install redis-toolkit[all]
```

## 🛠️ Development Environment Setup

If you want to contribute or need the latest features:

```bash
# Clone repository
git clone https://github.com/JonesHong/redis-toolkit.git
cd redis-toolkit

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install development dependencies
pip install -e ".[dev,all]"

# Run tests
python tests/run_tests.py all
```

## ✅ Verify Installation

### Basic Verification

```python
# Verify installation
import redis_toolkit
print(redis_toolkit.__version__)

# Test basic functionality
from redis_toolkit import RedisToolkit
toolkit = RedisToolkit()
toolkit.setter("test", "Hello Redis Toolkit!")
print(toolkit.getter("test"))
```

### Check Optional Features

```python
# Check media processing features
try:
    from redis_toolkit.converters import encode_image
    print("✅ Image processing available")
except ImportError:
    print("❌ Image processing not installed")

try:
    from redis_toolkit.converters import encode_audio
    print("✅ Audio processing available")
except ImportError:
    print("❌ Audio processing not installed")
```

## 🔍 Common Issues

### 1. pip Installation Failure

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Use mirror source (for users in China)
pip install redis-toolkit -i https://pypi.douban.com/simple
```

### 2. OpenCV Installation Issues

```bash
# Linux systems may need extra dependencies
sudo apt-get update
sudo apt-get install python3-opencv

# Or use headless version
pip install opencv-python-headless
```

### 3. Compilation Errors on Windows

```bash
# Install Visual C++ Build Tools
# Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Or use pre-compiled wheels
pip install redis-toolkit --only-binary :all:
```

### 4. Redis Connection Issues

```python
# Check if Redis is running
import redis
try:
    r = redis.Redis(host='localhost', port=6379)
    r.ping()
    print("✅ Redis connection successful")
except redis.ConnectionError:
    print("❌ Cannot connect to Redis")
```

## 📚 Next Steps

After installation, you can:

- 📖 Read [Basic Usage](./basic-usage.md) to learn core features
- 🚀 Check [Quick Start](./getting-started.md) for example code
- ⚙️ Learn about [Configuration Options](./configuration.md) for customization

::: tip Tip
If you encounter any installation issues, please check our [Troubleshooting Guide](/en/reference/troubleshooting.html) or ask on [GitHub Issues](https://github.com/JonesHong/redis-toolkit/issues).
:::