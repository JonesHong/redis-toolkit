# 轉換器 API

Redis Toolkit 提供多種媒體轉換器，用於處理圖片、音頻和視頻數據。

## 轉換器概覽

轉換器系統包含：
- 圖片轉換器（OpenCV、PIL）
- 音頻轉換器（NumPy、SciPy）
- 視頻轉換器（OpenCV）
- 通用轉換器介面

## 圖片轉換器

### encode_image()

```python
def encode_image(
    image: Union[np.ndarray, 'PIL.Image.Image'],
    format: str = '.jpg',
    quality: int = 95,
    **kwargs
) -> bytes:
    """
    編碼圖片為二進制數據
    
    參數:
        image: OpenCV 圖片 (np.ndarray) 或 PIL Image
        format: 圖片格式 (.jpg, .png, .webp 等)
        quality: JPEG 品質 (0-100)
        **kwargs: 其他編碼參數
        
    返回:
        bytes: 編碼後的圖片數據
    """
```

### decode_image()

```python
def decode_image(
    data: bytes,
    format: str = 'auto',
    return_format: str = 'opencv'
) -> Union[np.ndarray, 'PIL.Image.Image']:
    """
    解碼二進制數據為圖片
    
    參數:
        data: 圖片二進制數據
        format: 圖片格式（'auto' 為自動檢測）
        return_format: 返回格式 ('opencv' 或 'pil')
        
    返回:
        解碼後的圖片對象
    """
```

### 使用示例

```python
import cv2
from redis_toolkit import RedisToolkit
from redis_toolkit.converters import encode_image, decode_image

toolkit = RedisToolkit()

# 使用 OpenCV
image = cv2.imread('photo.jpg')
encoded = encode_image(image, format='.jpg', quality=90)
toolkit.set('image:1', encoded)

# 讀取並解碼
data = toolkit.get('image:1')
restored_image = decode_image(data)

# 使用 PIL
from PIL import Image
pil_image = Image.open('photo.png')
encoded = encode_image(pil_image, format='.png')
toolkit.set('image:2', encoded)

# 解碼為 PIL 格式
data = toolkit.get('image:2')
restored_pil = decode_image(data, return_format='pil')
```

## 音頻轉換器

### encode_audio()

```python
def encode_audio(
    audio_data: np.ndarray,
    sample_rate: int = 44100,
    format: str = 'wav',
    **kwargs
) -> bytes:
    """
    編碼音頻數據
    
    參數:
        audio_data: 音頻數據 (NumPy 數組)
        sample_rate: 採樣率
        format: 音頻格式 ('wav', 'flac', 'mp3')
        **kwargs: 其他編碼參數
        
    返回:
        bytes: 編碼後的音頻數據
    """
```

### decode_audio()

```python
def decode_audio(
    data: bytes,
    format: str = 'auto',
    return_sample_rate: bool = True
) -> Union[np.ndarray, Tuple[np.ndarray, int]]:
    """
    解碼音頻數據
    
    參數:
        data: 音頻二進制數據
        format: 音頻格式
        return_sample_rate: 是否返回採樣率
        
    返回:
        音頻數據或 (音頻數據, 採樣率) 元組
    """
```

### 使用示例

```python
import numpy as np
from redis_toolkit import RedisToolkit
from redis_toolkit.converters import encode_audio, decode_audio

toolkit = RedisToolkit()

# 生成測試音頻
sample_rate = 44100
duration = 2  # 秒
t = np.linspace(0, duration, int(sample_rate * duration))
audio = np.sin(2 * np.pi * 440 * t)  # 440Hz

# 編碼並存儲
encoded = encode_audio(audio, sample_rate=sample_rate)
toolkit.set('audio:1', encoded)

# 讀取並解碼
data = toolkit.get('audio:1')
restored_audio, sr = decode_audio(data)
print(f"採樣率: {sr}")
```

## 視頻轉換器

### VideoConverter 類

```python
class VideoConverter:
    """視頻轉換器類"""
    
    def encode(
        self,
        frames: List[np.ndarray],
        fps: float = 30.0,
        codec: str = 'mp4v',
        **kwargs
    ) -> bytes:
        """編碼視頻幀序列"""
        
    def decode(
        self,
        data: bytes,
        return_metadata: bool = False
    ) -> Union[List[np.ndarray], Tuple[List[np.ndarray], dict]]:
        """解碼視頻數據"""
```

### 使用示例

```python
import cv2
from redis_toolkit import RedisToolkit
from redis_toolkit.converters import VideoConverter

toolkit = RedisToolkit()
converter = VideoConverter()

# 讀取視頻
cap = cv2.VideoCapture('video.mp4')
frames = []
while True:
    ret, frame = cap.read()
    if not ret:
        break
    frames.append(frame)
cap.release()

# 編碼並存儲
encoded = converter.encode(frames, fps=30)
toolkit.set('video:1', encoded)

# 讀取並解碼
data = toolkit.get('video:1')
restored_frames = converter.decode(data)
```

## 通用轉換器介面

### get_converter()

```python
def get_converter(data_type: str) -> Optional[BaseConverter]:
    """
    獲取指定類型的轉換器
    
    參數:
        data_type: 數據類型 ('image', 'audio', 'video')
        
    返回:
        轉換器實例或 None
    """
```

### BaseConverter 介面

```python
class BaseConverter(ABC):
    """轉換器基類"""
    
    @abstractmethod
    def encode(self, data: Any, **kwargs) -> bytes:
        """編碼數據"""
        
    @abstractmethod
    def decode(self, data: bytes, **kwargs) -> Any:
        """解碼數據"""
        
    @abstractmethod
    def can_decode(self, data: bytes) -> bool:
        """檢查是否可以解碼"""
```

## 自定義轉換器

您可以創建自定義轉換器來處理特殊數據類型：

```python
from redis_toolkit.converters import BaseConverter

class CustomConverter(BaseConverter):
    def encode(self, data: Any, **kwargs) -> bytes:
        # 實現編碼邏輯
        return encoded_data
        
    def decode(self, data: bytes, **kwargs) -> Any:
        # 實現解碼邏輯
        return decoded_data
        
    def can_decode(self, data: bytes) -> bool:
        # 檢查數據格式
        return True

# 註冊轉換器
from redis_toolkit.converters import register_converter
register_converter('custom', CustomConverter())
```

## 性能優化建議

1. **圖片優化**
   - 使用適當的壓縮品質（JPEG: 85-95）
   - 考慮使用 WebP 格式以獲得更好的壓縮率
   - 預先調整圖片大小

2. **音頻優化**
   - 使用適當的採樣率（語音: 16kHz, 音樂: 44.1kHz）
   - 考慮使用 FLAC 進行無損壓縮
   - 使用單聲道代替立體聲（如果適用）

3. **視頻優化**
   - 使用硬件加速編碼（如果可用）
   - 調整幀率和分辨率
   - 使用現代編碼器（H.264, H.265）

## 錯誤處理

所有轉換器都包含錯誤處理：

```python
try:
    encoded = encode_image(image)
except ValueError as e:
    print(f"編碼錯誤: {e}")
except ImportError as e:
    print(f"缺少依賴: {e}")
```

## 依賴套件

不同轉換器需要不同的依賴：

```bash
# 圖片處理
pip install redis-toolkit[image]  # OpenCV + PIL

# 音頻處理
pip install redis-toolkit[audio]  # NumPy + SciPy

# 完整媒體支援
pip install redis-toolkit[media]  # 所有媒體依賴
```

## 相關文檔

- [核心 API](./core.md)
- [配置選項](./options.md)
- [媒體處理指南](/guide/media-processing.md)