# 轉換器 API 參考

本文檔詳細介紹 Redis Toolkit 的媒體轉換器 API。

## 概述

Redis Toolkit 提供專門的轉換器來處理不同類型的媒體數據：

- **圖片轉換器**: 處理圖片的編碼和解碼
- **音頻轉換器**: 處理音頻數據的序列化
- **視頻轉換器**: 處理視頻幀的存儲

## 圖片轉換器

### encode_image

將圖片編碼為字節串。

```python
encode_image(
    image: np.ndarray,
    format: str = 'jpg',
    quality: int = 95
) -> bytes
```

#### 參數

- **image** (`np.ndarray`): OpenCV 格式的圖片數組
- **format** (`str`, 可選): 圖片格式 ('jpg', 'png', 'webp')，默認為 'jpg'
- **quality** (`int`, 可選): 壓縮質量 (1-100)，僅對 JPEG 和 WebP 有效，默認為 95

#### 返回

`bytes`: 編碼後的圖片字節串

#### 示例

```python
import cv2
from redis_toolkit.converters import encode_image

# 讀取圖片
img = cv2.imread('photo.jpg')

# JPEG 編碼（有損壓縮）
jpg_bytes = encode_image(img, format='jpg', quality=90)

# PNG 編碼（無損壓縮）
png_bytes = encode_image(img, format='png')

# WebP 編碼（更好的壓縮率）
webp_bytes = encode_image(img, format='webp', quality=85)
```

### decode_image

將字節串解碼為圖片。

```python
decode_image(data: bytes) -> np.ndarray
```

#### 參數

- **data** (`bytes`): 編碼的圖片字節串

#### 返回

`np.ndarray`: OpenCV 格式的圖片數組

#### 示例

```python
from redis_toolkit.converters import decode_image

# 從字節串解碼圖片
image_bytes = toolkit.getter('image:123')
img = decode_image(image_bytes)

# 顯示或保存圖片
cv2.imshow('Decoded Image', img)
cv2.imwrite('decoded.jpg', img)
```

### ImageConverter 類

圖片轉換器類，提供更多控制選項。

```python
class ImageConverter:
    def __init__(self, default_format: str = 'jpg', default_quality: int = 95):
        pass
        
    def encode(self, image: np.ndarray, **kwargs) -> bytes:
        pass
        
    def decode(self, data: bytes) -> np.ndarray:
        pass
```

#### 示例

```python
from redis_toolkit.converters import ImageConverter

# 創建自定義配置的轉換器
converter = ImageConverter(default_format='png', default_quality=100)

# 使用轉換器
encoded = converter.encode(img)
decoded = converter.decode(encoded)

# 覆蓋默認設置
jpeg_encoded = converter.encode(img, format='jpg', quality=80)
```

## 音頻轉換器

### encode_audio

將音頻數據編碼為字節串。

```python
encode_audio(
    audio_data: np.ndarray,
    sample_rate: int = 44100
) -> bytes
```

#### 參數

- **audio_data** (`np.ndarray`): 音頻樣本數組（浮點數，範圍 -1 到 1）
- **sample_rate** (`int`, 可選): 採樣率（Hz），默認為 44100

#### 返回

`bytes`: 編碼後的音頻字節串

#### 示例

```python
import numpy as np
from redis_toolkit.converters import encode_audio

# 生成音頻信號（440Hz A4 音符）
sample_rate = 44100
duration = 2  # 秒
t = np.linspace(0, duration, int(sample_rate * duration))
audio_data = np.sin(2 * np.pi * 440 * t)

# 編碼音頻
audio_bytes = encode_audio(audio_data, sample_rate=sample_rate)

# 存儲到 Redis
toolkit.setter('audio:a4_tone', audio_bytes)
```

### decode_audio

將字節串解碼為音頻數據。

```python
decode_audio(data: bytes) -> Tuple[int, np.ndarray]
```

#### 參數

- **data** (`bytes`): 編碼的音頻字節串

#### 返回

`Tuple[int, np.ndarray]`: (採樣率, 音頻數據數組)

#### 示例

```python
from redis_toolkit.converters import decode_audio

# 從 Redis 獲取並解碼音頻
audio_bytes = toolkit.getter('audio:a4_tone')
sample_rate, audio_data = decode_audio(audio_bytes)

print(f"採樣率: {sample_rate} Hz")
print(f"音頻長度: {len(audio_data)} 樣本")
print(f"持續時間: {len(audio_data) / sample_rate:.2f} 秒")
```

### AudioConverter 類

音頻轉換器類，提供進階功能。

```python
class AudioConverter:
    def __init__(self, default_sample_rate: int = 44100):
        pass
        
    def encode(self, audio_data: np.ndarray, sample_rate: int = None) -> bytes:
        pass
        
    def decode(self, data: bytes) -> Tuple[int, np.ndarray]:
        pass
        
    def resample(self, audio_data: np.ndarray, 
                  from_rate: int, to_rate: int) -> np.ndarray:
        pass
```

#### 進階示例

```python
from redis_toolkit.converters import AudioConverter

# 創建轉換器
converter = AudioConverter(default_sample_rate=48000)

# 重採樣音頻
audio_48k = converter.resample(audio_data, from_rate=44100, to_rate=48000)

# 編碼和解碼
encoded = converter.encode(audio_48k)
rate, decoded = converter.decode(encoded)
```

## 視頻轉換器

### VideoConverter 類

視頻幀轉換器，用於處理視頻數據。

```python
class VideoConverter:
    def __init__(self, format: str = 'jpg', quality: int = 90):
        pass
        
    def encode(self, frame: np.ndarray, **kwargs) -> bytes:
        pass
        
    def decode(self, data: bytes) -> np.ndarray:
        pass
        
    def encode_frames(self, frames: List[np.ndarray]) -> List[bytes]:
        pass
        
    def decode_frames(self, data_list: List[bytes]) -> List[np.ndarray]:
        pass
```

#### 示例

```python
from redis_toolkit.converters import VideoConverter
import cv2

# 創建視頻轉換器
converter = VideoConverter(format='jpg', quality=85)

# 處理視頻文件
cap = cv2.VideoCapture('video.mp4')
frames = []

# 讀取前 10 幀
for i in range(10):
    ret, frame = cap.read()
    if ret:
        frames.append(frame)
    else:
        break

cap.release()

# 批次編碼幀
encoded_frames = converter.encode_frames(frames)

# 存儲到 Redis
for i, frame_bytes in enumerate(encoded_frames):
    toolkit.setter(f'video:frame:{i}', frame_bytes)

# 讀取並解碼
stored_frames = []
for i in range(len(encoded_frames)):
    frame_bytes = toolkit.getter(f'video:frame:{i}')
    if frame_bytes:
        frame = converter.decode(frame_bytes)
        stored_frames.append(frame)
```

## 工具函數

### check_dependencies

檢查媒體處理所需的依賴項。

```python
check_dependencies() -> Dict[str, bool]
```

#### 返回

`Dict[str, bool]`: 各依賴項的安裝狀態

#### 示例

```python
from redis_toolkit.converters import check_dependencies

deps = check_dependencies()
for lib, installed in deps.items():
    status = "已安裝" if installed else "未安裝"
    print(f"{lib}: {status}")
```

### get_image_info

獲取圖片信息而不完全解碼。

```python
get_image_info(data: bytes) -> Dict[str, Any]
```

#### 返回

包含圖片信息的字典：
- `width`: 圖片寬度
- `height`: 圖片高度
- `channels`: 通道數
- `format`: 圖片格式

#### 示例

```python
from redis_toolkit.converters import get_image_info

image_bytes = toolkit.getter('image:123')
info = get_image_info(image_bytes)

print(f"尺寸: {info['width']}x{info['height']}")
print(f"格式: {info['format']}")
```

## 自定義轉換器

您可以創建自定義轉換器來處理特定的數據類型：

```python
from redis_toolkit.converters.base import BaseConverter

class CustomConverter(BaseConverter):
    """自定義數據轉換器"""
    
    def encode(self, data: Any) -> bytes:
        """實現編碼邏輯"""
        # 您的編碼實現
        return encoded_bytes
    
    def decode(self, data: bytes) -> Any:
        """實現解碼邏輯"""
        # 您的解碼實現
        return decoded_data
    
    def validate(self, data: Any) -> bool:
        """驗證數據是否可以被編碼"""
        # 您的驗證邏輯
        return True
```

### 註冊自定義轉換器

```python
from redis_toolkit import RedisToolkit

# 創建自定義轉換器
custom_converter = CustomConverter()

# 在選項中指定自定義序列化器
options = RedisOptions(
    custom_serializer=custom_converter.encode,
    custom_deserializer=custom_converter.decode
)

toolkit = RedisToolkit(options=options)
```

## 錯誤處理

### ConverterError

轉換器相關錯誤的基類。

```python
class ConverterError(Exception):
    pass
```

### ImageConversionError

圖片轉換失敗時拋出。

```python
try:
    img = decode_image(corrupted_data)
except ImageConversionError as e:
    print(f"圖片解碼失敗: {e}")
```

### AudioConversionError

音頻轉換失敗時拋出。

```python
try:
    rate, audio = decode_audio(invalid_data)
except AudioConversionError as e:
    print(f"音頻解碼失敗: {e}")
```

## 性能優化建議

### 1. 批次處理

```python
# 批次編碼多個圖片
images = [cv2.imread(f'image_{i}.jpg') for i in range(10)]
encoded_images = [encode_image(img, quality=85) for img in images]

# 批次存儲
image_data = {f'image:{i}': data for i, data in enumerate(encoded_images)}
toolkit.batch_set(image_data)
```

### 2. 壓縮策略

```python
def adaptive_compress(image, target_size_kb=100):
    """自適應壓縮到目標大小"""
    quality = 95
    
    while quality > 10:
        encoded = encode_image(image, format='jpg', quality=quality)
        size_kb = len(encoded) / 1024
        
        if size_kb <= target_size_kb:
            return encoded, quality
            
        quality -= 5
    
    return encoded, quality
```

### 3. 緩存解碼結果

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_decode_image(image_key: str) -> np.ndarray:
    """緩存解碼的圖片"""
    image_bytes = toolkit.getter(image_key)
    if image_bytes:
        return decode_image(image_bytes)
    return None
```

## 支援的格式

### 圖片格式
- JPEG (.jpg, .jpeg)
- PNG (.png)
- WebP (.webp)
- BMP (.bmp)
- TIFF (.tiff, .tif)

### 音頻格式
- WAV (通過 scipy.io.wavfile)
- 原始 PCM 數據
- NumPy 數組

### 視頻格式
- 任何 OpenCV 支援的視頻格式
- 單獨的視頻幀（作為圖片）