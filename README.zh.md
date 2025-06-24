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
  <strong>🚀 增強型 Redis 包裝器，具備智能序列化和媒體處理功能</strong>
</p>

<p align="center">
  一個強大的 Redis 工具包，簡化多種資料類型操作、發布訂閱訊息傳遞，以及具備自動編解碼功能的媒體檔案處理。
</p>

---

## ✨ 功能特色

- 🎯 **智能序列化**：自動處理 `dict`、`list`、`bool`、`bytes`、`int`、`float` 和 `numpy` 陣列
- 🎵 **媒體處理**：內建圖片、音頻和視頻檔案轉換器
- 📡 **簡化發布訂閱**：具備自動 JSON 序列化的簡易發布訂閱功能
- 🔧 **彈性配置**：支援自訂 Redis 客戶端和連線設定
- 🛡️ **穩定操作**：內建重試機制和健康檢查
- 📦 **批次操作**：高效的 `batch_set` 和 `batch_get` 批量操作

## 📦 安裝

### 基本安裝
```bash
pip install redis-toolkit
```

### 媒體處理功能
```bash
# 圖片處理
pip install redis-toolkit[cv2]

# 音頻處理（基礎）
pip install redis-toolkit[audio]

# 音頻處理（支援 MP3）
pip install redis-toolkit[audio-full]

# 完整媒體支援
pip install redis-toolkit[all]
```

## 🚀 快速開始

### 基本使用

```python
from redis_toolkit import RedisToolkit

# 初始化工具包
toolkit = RedisToolkit()

# 存儲不同資料類型
toolkit.setter("user", {"name": "Alice", "age": 25, "active": True})
toolkit.setter("scores", [95, 87, 92, 88])
toolkit.setter("flag", True)
toolkit.setter("binary_data", b"Hello, World!")

# 自動反序列化
user = toolkit.getter("user")      # {'name': 'Alice', 'age': 25, 'active': True}
scores = toolkit.getter("scores")  # [95, 87, 92, 88]
flag = toolkit.getter("flag")      # True (布林值，非字串)
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

# 取得並解碼
retrieved_bytes = toolkit.getter('my_image')
decoded_img = decode_image(retrieved_bytes)

# 音頻處理
sample_rate = 44100
audio_data = np.sin(2 * np.pi * 440 * np.linspace(0, 1, sample_rate))
audio_bytes = encode_audio(audio_data, sample_rate=sample_rate)
toolkit.setter('my_audio', audio_bytes)

# 取得並解碼
retrieved_audio = toolkit.getter('my_audio')
decoded_rate, decoded_audio = decode_audio(retrieved_audio)
```

### 發布訂閱與媒體分享

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
        print(f"收到圖片: {img.shape}")

subscriber = RedisToolkit(
    channels=["media_channel"],
    message_handler=message_handler
)

# 設定發布者
publisher = RedisToolkit()

# 透過發布訂閱傳送圖片
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
    subscriber_retry_delay=10
)

toolkit = RedisToolkit(config=config, options=options)
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
    # 離開時自動清理
```

## 🎨 媒體轉換器

### 圖片轉換器

```python
from redis_toolkit.converters import get_converter

# 建立自訂設定的圖片轉換器
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

### 音頻轉換器

```python
from redis_toolkit.converters import get_converter

# 建立音頻轉換器
audio_converter = get_converter('audio', sample_rate=44100, format='wav')

# 從檔案編碼
encoded = audio_converter.encode_from_file('song.mp3')

# 從陣列編碼
encoded = audio_converter.encode((sample_rate, audio_array))

# 解碼音頻
sample_rate, audio_array = audio_converter.decode(encoded)

# 正規化音頻
normalized = audio_converter.normalize(audio_array, target_level=0.8)

# 取得檔案資訊
info = audio_converter.get_file_info('song.mp3')
```

### 視頻轉換器

```python
from redis_toolkit.converters import get_converter

# 建立視頻轉換器
video_converter = get_converter('video')

# 編碼視頻檔案
encoded = video_converter.encode('movie.mp4')

# 將視頻位元組儲存為檔案
video_converter.save_video_bytes(encoded, 'output.mp4')

# 取得視頻資訊
info = video_converter.get_video_info('movie.mp4')

# 提取幀畫面
frames = video_converter.extract_frames('movie.mp4', max_frames=10)
```

## 🎯 使用場景

### 即時圖片分享
適合需要在不同服務或使用者之間即時分享圖片的應用程式。

### 音頻/視頻串流
透過自動編解碼功能有效處理音頻和視頻緩衝區。

### 多媒體聊天應用
建構支援文字、圖片、音頻和視頻訊息的聊天應用程式。

### 資料分析儀表板
在不同元件之間分享即時圖表和視覺化資料。

### 物聯網資料處理
處理感測器資料、攝影機圖像和麥克風音頻。

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
    decode_responses=False,
    socket_keepalive=True
)
```

### Redis 選項
```python
RedisOptions(
    is_logger_info=True,           # 啟用日誌記錄
    max_log_size=256,              # 最大日誌條目大小
    subscriber_retry_delay=5,      # 訂閱者重連延遲
    subscriber_stop_timeout=5      # 訂閱者停止逾時
)
```

## 📋 系統需求

- Python >= 3.7
- Redis >= 4.0
- redis-py >= 4.0

### 可選依賴
- **OpenCV**: 用於圖片和視頻處理 (`pip install opencv-python`)
- **NumPy**: 用於陣列操作 (`pip install numpy`)
- **SciPy**: 用於音頻處理 (`pip install scipy`)
- **SoundFile**: 用於進階音頻格式 (`pip install soundfile`)
- **Pillow**: 用於額外圖片格式 (`pip install Pillow`)

## 🧪 測試

```bash
# 安裝開發依賴
pip install redis-toolkit[dev]

# 執行測試
pytest

# 執行包含涵蓋率的測試
pytest --cov=redis_toolkit

# 執行特定測試類別
pytest -m "not slow"  # 跳過慢速測試
pytest -m integration  # 僅執行整合測試
```

## 🤝 貢獻

我們歡迎貢獻！請參閱我們的[貢獻指南](CONTRIBUTING.md)了解詳情。

1. Fork 此專案
2. 建立功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的變更 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request

## 📄 授權

此專案採用 MIT 授權 - 詳情請參閱 [LICENSE](LICENSE) 檔案。

## 📞 聯絡與支援

- **文件**: [https://redis-toolkit.readthedocs.io](https://redis-toolkit.readthedocs.io)
- **問題回報**: [GitHub Issues](https://github.com/JonesHong/redis-toolkit/issues)
- **討論**: [GitHub Discussions](https://github.com/JonesHong/redis-toolkit/discussions)
- **PyPI**: [https://pypi.org/project/redis-toolkit/](https://pypi.org/project/redis-toolkit/)

## 🌟 專案展示

**被這些優秀專案使用：**
- 在此新增您的專案，歡迎開啟 PR！

---

<p align="center">
  由 Redis Toolkit 團隊用 ❤️ 製作
</p>