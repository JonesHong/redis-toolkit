# Redis Toolkit

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
  <strong>🚀 具有智慧序列化和媒體處理功能的增強型 Redis 封裝工具</strong>
</p>

<p align="center">
  一個強大的 Redis 工具包，簡化多類型資料操作、發布/訂閱訊息傳遞和媒體檔案處理，並具有自動編碼/解碼功能。
</p>

---

## ✨ 功能特色

- 🎯 **智慧且安全的序列化**：自動處理 `dict`、`list`、`bool`、`bytes`、`int`、`float` 和 `numpy` 陣列，使用基於 JSON 的序列化（不使用 pickle！）
- 🔐 **安全優先**：不使用 pickle 序列化，避免遠端程式碼執行漏洞
- 🎵 **媒體處理**：內建圖片、音訊和視訊檔案的轉換器
- 📡 **簡化的發布/訂閱**：簡化的發布/訂閱功能，具有自動 JSON 序列化
- 🔧 **彈性配置**：支援自訂 Redis 客戶端和連線設定
- 🛡️ **韌性操作**：使用 `@with_retry` 裝飾器的內建重試機制
- 📦 **批次操作**：高效的 `batch_set` 和 `batch_get` 用於大量操作
- 🎨 **美化日誌**：使用 pretty-loguru 整合的增強日誌記錄
- 🔧 **彈性配置**：使用 Python dataclasses 的簡單配置

## 📦 安裝

### 基礎安裝
```bash
pip install redis-toolkit
```

### 包含媒體處理
```bash
# 圖片處理
pip install redis-toolkit[cv2]

# 音訊處理（基礎）
pip install redis-toolkit[audio]

# 音訊處理（含 MP3 支援）
pip install redis-toolkit[audio-full]

# 完整媒體支援
pip install redis-toolkit[all]
```

## 🚀 快速開始

### 基礎使用

```python
from redis_toolkit import RedisToolkit
from redis import Redis

# 方法 1：傳入現有的 Redis 實例
redis_client = Redis(host='localhost', port=6379, decode_responses=False)
toolkit = RedisToolkit(redis=redis_client)

# 方法 2：使用配置（含連線池）
from redis_toolkit import RedisConnectionConfig
config = RedisConnectionConfig(host='localhost', port=6379)
toolkit = RedisToolkit(config=config)

# 方法 3：使用預設值
toolkit = RedisToolkit()

# 儲存不同的資料類型
toolkit.setter("user", {"name": "Alice", "age": 25, "active": True})
toolkit.setter("scores", [95, 87, 92, 88])
toolkit.setter("flag", True)
toolkit.setter("binary_data", b"Hello, World!")

# 自動反序列化
user = toolkit.getter("user")      # {'name': 'Alice', 'age': 25, 'active': True}
scores = toolkit.getter("scores")  # [95, 87, 92, 88]
flag = toolkit.getter("flag")      # True (bool，而非字串)

# 存取底層 Redis 客戶端進行進階操作
raw_value = toolkit.client.get("user")  # 取得原始位元組
toolkit.client.expire("user", 3600)     # 設定 TTL
```

### 使用轉換器進行媒體處理

```python
from redis_toolkit import RedisToolkit
from redis_toolkit.converters import encode_image, decode_image
from redis_toolkit.converters import encode_audio, decode_audio
import cv2
import numpy as np

toolkit = RedisToolkit()

# 圖片處理
img = cv2.imread('photo.jpg')
img_bytes = encode_image(img, format='jpg', quality=90)
toolkit.setter('my_image', img_bytes)

# 擷取並解碼
retrieved_bytes = toolkit.getter('my_image')
decoded_img = decode_image(retrieved_bytes)

# 音訊處理
sample_rate = 44100
audio_data = np.sin(2 * np.pi * 440 * np.linspace(0, 1, sample_rate))
audio_bytes = encode_audio(audio_data, sample_rate=sample_rate)
toolkit.setter('my_audio', audio_bytes)

# 擷取並解碼
retrieved_audio = toolkit.getter('my_audio')
decoded_rate, decoded_audio = decode_audio(retrieved_audio)
```

### 發布/訂閱與媒體分享

```python
from redis_toolkit import RedisToolkit
from redis_toolkit.converters import encode_image
import base64

# 設定訂閱者
def message_handler(channel, data):
    if data.get('type') == 'image':
        # 解碼 base64 圖片資料
        img_bytes = base64.b64decode(data['image_data'])
        img = decode_image(img_bytes)
        print(f"接收到圖片：{img.shape}")

subscriber = RedisToolkit(
    channels=["media_channel"],
    message_handler=message_handler
)

# 設定發布者
publisher = RedisToolkit()

# 透過發布/訂閱傳送圖片
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

### 進階配置

```python
from redis_toolkit import RedisToolkit, RedisOptions, RedisConnectionConfig

# 自訂 Redis 連線
config = RedisConnectionConfig(
    host="localhost",
    port=6379,
    db=1,
    password="your_password"
)

# 自訂選項
options = RedisOptions(
    is_logger_info=True,
    max_log_size=512,
    subscriber_retry_delay=10,
    log_level="INFO",  # 支援 pretty-loguru
    log_path="./logs"  # 可選的檔案日誌記錄
)

# 方法 1：使用配置
toolkit = RedisToolkit(config=config, options=options)

# 方法 2：使用現有的 Redis 客戶端
import redis
pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
redis_client = redis.Redis(connection_pool=pool)
toolkit = RedisToolkit(redis=redis_client, options=options)

# 存取底層 Redis 客戶端
print(f"Redis 伺服器資訊：{toolkit.client.info()['redis_version']}")
```

### 批次操作

```python
# 批次設定
data = {
    "user:1": {"name": "Alice", "score": 95},
    "user:2": {"name": "Bob", "score": 87},
    "user:3": {"name": "Charlie", "score": 92}
}
toolkit.batch_set(data)

# 批次取得
keys = ["user:1", "user:2", "user:3"]
results = toolkit.batch_get(keys)
```

### 上下文管理器

```python
with RedisToolkit() as toolkit:
    toolkit.setter("temp_data", {"session": "12345"})
    data = toolkit.getter("temp_data")
    # 退出時自動清理
```

## 🎨 媒體轉換器

### 圖片轉換器

```python
from redis_toolkit.converters import get_converter

# 建立具有自訂設定的圖片轉換器
img_converter = get_converter('image', format='png', quality=95)

# 編碼圖片
encoded = img_converter.encode(image_array)

# 解碼圖片
decoded = img_converter.decode(encoded)

# 調整圖片大小
resized = img_converter.resize(image_array, width=800, height=600)

# 取得圖片資訊
info = img_converter.get_info(encoded_bytes)
```

### 音訊轉換器

```python
from redis_toolkit.converters import get_converter

# 建立音訊轉換器
audio_converter = get_converter('audio', sample_rate=44100, format='wav')

# 從檔案編碼
encoded = audio_converter.encode_from_file('song.mp3')

# 從陣列編碼
encoded = audio_converter.encode((sample_rate, audio_array))

# 解碼音訊
sample_rate, audio_array = audio_converter.decode(encoded)

# 正規化音訊
normalized = audio_converter.normalize(audio_array, target_level=0.8)

# 取得檔案資訊
info = audio_converter.get_file_info('song.mp3')
```

### 視訊轉換器

```python
from redis_toolkit.converters import get_converter

# 建立視訊轉換器
video_converter = get_converter('video')

# 編碼視訊檔案
encoded = video_converter.encode('movie.mp4')

# 將視訊位元組儲存到檔案
video_converter.save_video_bytes(encoded, 'output.mp4')

# 取得視訊資訊
info = video_converter.get_video_info('movie.mp4')

# 擷取畫格
frames = video_converter.extract_frames('movie.mp4', max_frames=10)
```

## 🎯 使用案例

### 即時圖片分享
適用於需要在不同服務或使用者之間即時分享圖片的應用程式。

### 音訊/視訊串流
使用自動編碼/解碼功能高效處理音訊和視訊緩衝區。

### 多媒體聊天應用程式
建立支援文字、圖片、音訊和視訊訊息的聊天應用程式。

### 資料分析儀表板
在不同元件之間分享即時圖表和視覺化。

### 物聯網資料處理
處理感測器資料、來自攝影機的圖片和來自麥克風的音訊。

## ⚙️ 配置選項

### Redis 連線配置
```python
RedisConnectionConfig(
    host='localhost',
    port=6379,
    db=0,
    password=None,
    username=None,
    encoding='utf-8',
    decode_responses=False,     # 始終為 False 以確保正確序列化
    socket_keepalive=True,
    socket_keepalive_options=None,
    connection_timeout=None,    # 連線逾時（秒）
    socket_timeout=None,        # Socket 操作逾時（秒）
    retry_on_timeout=False,     # 逾時時重試
    retry_on_error=True,        # 錯誤時重試
    health_check_interval=30,   # 健康檢查間隔（秒）
    ssl=False,                  # 使用 SSL/TLS
    ssl_keyfile=None,          # SSL 金鑰檔案路徑
    ssl_certfile=None,         # SSL 憑證檔案路徑
    ssl_ca_certs=None,         # SSL CA 憑證檔案路徑
    ssl_cert_reqs='required'   # SSL 憑證需求等級
)
```

### Redis 選項
```python
RedisOptions(
    is_logger_info=True,           # 啟用日誌記錄
    max_log_size=256,              # 最大日誌項目大小
    subscriber_retry_delay=5,      # 訂閱者重新連線延遲
    subscriber_stop_timeout=5,     # 訂閱者停止逾時
    log_level="INFO",              # 日誌等級（DEBUG、INFO、WARNING、ERROR）
    log_path=None,                 # 日誌檔案路徑（None 表示僅輸出到控制台）
    max_value_size=10*1024*1024,   # 最大值大小（位元組，10MB）
    max_key_length=512,            # 最大金鑰長度
    enable_validation=True,        # 啟用驗證
    use_connection_pool=True,      # 使用共享連線池
    max_connections=None           # 最大連線數（None 表示無限制）
)
```

### 配置驗證

`RedisOptions` 和 `RedisConnectionConfig` 都支援驗證：

```python
# 使用前驗證配置
options = RedisOptions(log_level="DEBUG")
options.validate()  # 如果無效會引發 ValueError

config = RedisConnectionConfig(port=6379, ssl=True)
config.validate()  # 如果無效會引發 ValueError

# RedisToolkit 在初始化時自動驗證選項
toolkit = RedisToolkit(config=config, options=options)
```

## 📋 需求

- Python >= 3.7
- Redis >= 4.0
- redis-py >= 4.0

### 可選相依套件
- **OpenCV**：用於圖片和視訊處理（`pip install opencv-python`）
- **NumPy**：用於陣列操作（`pip install numpy`）
- **SciPy**：用於音訊處理（`pip install scipy`）
- **SoundFile**：用於進階音訊格式（`pip install soundfile`）
- **Pillow**：用於額外的圖片格式（`pip install Pillow`）

## 🧪 測試

```bash
# 安裝開發相依套件
pip install redis-toolkit[dev]

# 執行測試
pytest

# 執行並顯示覆蓋率
pytest --cov=redis_toolkit

# 執行特定測試類別
pytest -m "not slow"  # 跳過慢速測試
pytest -m integration  # 僅執行整合測試
```

## 🤝 貢獻

歡迎貢獻！請參閱我們的[貢獻指南](CONTRIBUTING.md)了解詳情。

1. Fork 專案
2. 建立功能分支（`git checkout -b feature/amazing-feature`）
3. 提交您的更改（`git commit -m 'Add amazing feature'`）
4. 推送到分支（`git push origin feature/amazing-feature`）
5. 開啟 Pull Request

## 📄 授權

本專案採用 MIT 授權 - 詳情請參閱 [LICENSE](LICENSE) 檔案。

## 📞 聯絡與支援

- **文件**：[https://redis-toolkit.readthedocs.io](https://redis-toolkit.readthedocs.io)
- **問題**：[GitHub Issues](https://github.com/JonesHong/redis-toolkit/issues)
- **討論**：[GitHub Discussions](https://github.com/JonesHong/redis-toolkit/discussions)
- **PyPI**：[https://pypi.org/project/redis-toolkit/](https://pypi.org/project/redis-toolkit/)

## 🌟 展示

**被這些優秀專案使用：**
- 透過開啟 PR 來新增您的專案！

---

<p align="center">
  由 Redis Toolkit 團隊用 ❤️ 製作
</p>