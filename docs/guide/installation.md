# 安裝指南

本指南將詳細說明如何在不同環境下安裝和配置 Redis Toolkit。

## 📋 系統需求

### Python 版本
- Python >= 3.7
- 建議使用 Python 3.8 或更高版本以獲得最佳效能

### Redis 版本
- Redis >= 4.0
- 建議使用 Redis 5.0 或更高版本
- 支援 Redis 集群和哨兵模式

### 作業系統
- ✅ Linux (Ubuntu, CentOS, Debian 等)
- ✅ macOS
- ✅ Windows 10/11
- ✅ Docker 容器

## 🎯 快速安裝

### 基礎安裝

最簡單的安裝方式，包含核心功能：

```bash
pip install redis-toolkit
```

這將安裝：
- Redis Toolkit 核心功能
- redis-py (Redis Python 客戶端)
- pretty-loguru (美化日誌輸出)

### 進階安裝選項

根據您的需求選擇不同的安裝配置：

```bash
# 包含圖片處理功能 (OpenCV)
pip install redis-toolkit[cv2]

# 包含音頻處理功能
pip install redis-toolkit[audio]

# 包含完整音頻支援 (含 MP3)
pip install redis-toolkit[audio-full]

# 包含所有媒體處理功能
pip install redis-toolkit[media]

# 安裝所有可選功能
pip install redis-toolkit[all]

# 開發環境 (包含測試工具)
pip install redis-toolkit[dev]
```

## 📦 依賴套件說明

### 核心依賴

| 套件 | 版本 | 用途 |
|-----|------|-----|
| redis | >= 4.0.0 | Redis Python 客戶端 |
| pretty-loguru | >= 1.1.3 | 增強的日誌功能 |

### 可選依賴

#### 圖片處理
| 套件 | 版本 | 用途 |
|-----|------|-----|
| opencv-python | >= 4.5.0 | 圖片編解碼 |
| numpy | >= 1.19.0 | 陣列操作 |
| Pillow | >= 8.0.0 | 額外圖片格式支援 |

#### 音頻處理
| 套件 | 版本 | 用途 |
|-----|------|-----|
| numpy | >= 1.19.0 | 音頻數據處理 |
| scipy | >= 1.7.0 | 信號處理 |
| soundfile | >= 0.10.0 | 音頻檔案讀寫 |

#### 開發工具
| 套件 | 版本 | 用途 |
|-----|------|-----|
| pytest | >= 6.0 | 單元測試 |
| black | >= 21.0 | 程式碼格式化 |
| mypy | >= 0.910 | 類型檢查 |

## 🐳 Docker 安裝

### 使用官方映像檔

```dockerfile
FROM python:3.9-slim

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 安裝 Redis Toolkit
RUN pip install redis-toolkit[all]

# 您的應用程式碼
COPY . /app
WORKDIR /app

CMD ["python", "app.py"]
```

### Docker Compose 配置

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

## 🔧 虛擬環境安裝

### 使用 venv

```bash
# 創建虛擬環境
python -m venv redis_env

# 啟動虛擬環境
# Linux/macOS
source redis_env/bin/activate
# Windows
redis_env\Scripts\activate

# 安裝 Redis Toolkit
pip install redis-toolkit[all]
```

### 使用 conda

```bash
# 創建 conda 環境
conda create -n redis_env python=3.9

# 啟動環境
conda activate redis_env

# 安裝 Redis Toolkit
pip install redis-toolkit[all]
```

## 🛠️ 開發環境設置

如果您想要參與開發或需要最新功能：

```bash
# 克隆儲存庫
git clone https://github.com/JonesHong/redis-toolkit.git
cd redis-toolkit

# 創建虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 安裝開發依賴
pip install -e ".[dev,all]"

# 運行測試
python tests/run_tests.py all
```

## ✅ 驗證安裝

### 基本驗證

```python
# 驗證安裝
import redis_toolkit
print(redis_toolkit.__version__)

# 測試基本功能
from redis_toolkit import RedisToolkit
toolkit = RedisToolkit()
toolkit.setter("test", "Hello Redis Toolkit!")
print(toolkit.getter("test"))
```

### 檢查可選功能

```python
# 檢查媒體處理功能
try:
    from redis_toolkit.converters import encode_image
    print("✅ 圖片處理功能可用")
except ImportError:
    print("❌ 圖片處理功能未安裝")

try:
    from redis_toolkit.converters import encode_audio
    print("✅ 音頻處理功能可用")
except ImportError:
    print("❌ 音頻處理功能未安裝")
```

## 🔍 常見問題

### 1. pip 安裝失敗

```bash
# 升級 pip
python -m pip install --upgrade pip

# 使用國內鏡像源（中國大陸用戶）
pip install redis-toolkit -i https://pypi.douban.com/simple
```

### 2. OpenCV 安裝問題

```bash
# Linux 系統可能需要額外依賴
sudo apt-get update
sudo apt-get install python3-opencv

# 或使用 headless 版本
pip install opencv-python-headless
```

### 3. Windows 上的編譯錯誤

```bash
# 安裝 Visual C++ Build Tools
# 下載地址: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# 或使用預編譯的 wheel
pip install redis-toolkit --only-binary :all:
```

### 4. Redis 連接問題

```python
# 檢查 Redis 是否運行
import redis
try:
    r = redis.Redis(host='localhost', port=6379)
    r.ping()
    print("✅ Redis 連接正常")
except redis.ConnectionError:
    print("❌ 無法連接到 Redis")
```

## 📚 下一步

安裝完成後，您可以：

- 📖 閱讀[基礎使用](./basic-usage.md)學習核心功能
- 🚀 查看[快速開始](./getting-started.md)的範例程式碼
- ⚙️ 了解[配置選項](./configuration.md)進行客製化設置

::: tip 提示
如果遇到任何安裝問題，請查看我們的[疑難排解指南](/reference/troubleshooting.html)或在 [GitHub Issues](https://github.com/JonesHong/redis-toolkit/issues) 上提問。
:::