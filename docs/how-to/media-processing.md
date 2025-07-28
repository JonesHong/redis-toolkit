# 媒體處理指南

本指南介紹如何使用 Redis Toolkit 處理圖片、音頻和視頻數據。

## 概述

Redis Toolkit 提供了專門的轉換器來處理媒體數據：
- **圖片轉換器**：支援 OpenCV 格式的圖片編碼/解碼
- **音頻轉換器**：支援 NumPy 數組格式的音頻處理
- **視頻轉換器**：支援視頻幀的存儲和檢索

## 安裝依賴

```bash
# 圖片處理
pip install redis-toolkit[cv2]

# 音頻處理  
pip install redis-toolkit[audio]

# 完整媒體支援
pip install redis-toolkit[all]
```

## 圖片處理

### 基本圖片存儲

```python
from redis_toolkit import RedisToolkit
from redis_toolkit.converters import encode_image, decode_image
import cv2

toolkit = RedisToolkit()

# 讀取圖片
img = cv2.imread('photo.jpg')

# 編碼並存儲
img_bytes = encode_image(img, format='jpg', quality=85)
toolkit.setter('user:avatar:123', img_bytes)

# 讀取並解碼
stored_bytes = toolkit.getter('user:avatar:123')
restored_img = decode_image(stored_bytes)

# 保存恢復的圖片
cv2.imwrite('restored_photo.jpg', restored_img)
```

### 圖片格式和質量控制

```python
# JPEG 格式（有損壓縮，文件較小）
jpg_bytes = encode_image(img, format='jpg', quality=90)

# PNG 格式（無損壓縮，文件較大）
png_bytes = encode_image(img, format='png')

# WebP 格式（更好的壓縮率）
webp_bytes = encode_image(img, format='webp', quality=80)

print(f"JPEG 大小: {len(jpg_bytes):,} bytes")
print(f"PNG 大小: {len(png_bytes):,} bytes")
print(f"WebP 大小: {len(webp_bytes):,} bytes")
```

### 縮略圖生成

```python
def create_thumbnail(image, max_size=(200, 200)):
    """創建縮略圖"""
    height, width = image.shape[:2]
    
    # 計算縮放比例
    scale = min(max_size[0]/width, max_size[1]/height)
    new_width = int(width * scale)
    new_height = int(height * scale)
    
    # 調整大小
    thumbnail = cv2.resize(image, (new_width, new_height))
    return thumbnail

# 存儲原圖和縮略圖
original = cv2.imread('large_photo.jpg')
thumbnail = create_thumbnail(original)

# 存儲
toolkit.setter('photo:original:123', encode_image(original, format='jpg', quality=90))
toolkit.setter('photo:thumbnail:123', encode_image(thumbnail, format='jpg', quality=80))
```

### 批次圖片處理

```python
def batch_process_images(image_paths):
    """批次處理圖片"""
    images_data = {}
    
    for path in image_paths:
        img = cv2.imread(path)
        if img is not None:
            # 生成唯一鍵
            img_id = path.split('/')[-1].split('.')[0]
            
            # 編碼圖片
            img_bytes = encode_image(img, format='jpg', quality=85)
            images_data[f'image:{img_id}'] = img_bytes
            
            # 創建縮略圖
            thumb = create_thumbnail(img, max_size=(150, 150))
            thumb_bytes = encode_image(thumb, format='jpg', quality=75)
            images_data[f'image:thumb:{img_id}'] = thumb_bytes
    
    # 批次存儲
    toolkit.batch_set(images_data)
    return len(images_data) // 2  # 返回處理的圖片數量
```

## 音頻處理

### 基本音頻存儲

```python
from redis_toolkit.converters import encode_audio, decode_audio
import numpy as np

# 生成測試音頻（440Hz A4音符）
sample_rate = 44100
duration = 2  # 秒
frequency = 440  # Hz

t = np.linspace(0, duration, int(sample_rate * duration))
audio_data = np.sin(2 * np.pi * frequency * t)

# 編碼並存儲
audio_bytes = encode_audio(audio_data, sample_rate=sample_rate)
toolkit.setter('audio:tone:a4', audio_bytes)

# 讀取並解碼
stored_bytes = toolkit.getter('audio:tone:a4')
rate, restored_audio = decode_audio(stored_bytes)

print(f"採樣率: {rate} Hz")
print(f"音頻長度: {len(restored_audio)} 樣本")
```

### 音頻格式轉換

```python
import wave
import struct

def save_audio_to_wav(audio_data, sample_rate, filename):
    """將音頻數據保存為 WAV 文件"""
    # 標準化音頻數據到 16-bit 範圍
    audio_16bit = np.int16(audio_data * 32767)
    
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)  # 單聲道
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_16bit.tobytes())

# 從 Redis 讀取並保存為 WAV
stored_bytes = toolkit.getter('audio:tone:a4')
rate, audio = decode_audio(stored_bytes)
save_audio_to_wav(audio, rate, 'output.wav')
```

### 音頻片段管理

```python
class AudioClipManager:
    def __init__(self):
        self.toolkit = RedisToolkit()
        
    def store_audio_clip(self, clip_id, audio_data, sample_rate, metadata=None):
        """存儲音頻片段及其元數據"""
        # 存儲音頻數據
        audio_key = f"audio:clip:{clip_id}"
        audio_bytes = encode_audio(audio_data, sample_rate)
        self.toolkit.setter(audio_key, audio_bytes)
        
        # 存儲元數據
        meta_key = f"audio:meta:{clip_id}"
        meta_data = {
            "sample_rate": sample_rate,
            "duration": len(audio_data) / sample_rate,
            "channels": 1,
            "created_at": time.time()
        }
        if metadata:
            meta_data.update(metadata)
        self.toolkit.setter(meta_key, meta_data)
        
    def get_audio_clip(self, clip_id):
        """獲取音頻片段及其元數據"""
        audio_key = f"audio:clip:{clip_id}"
        meta_key = f"audio:meta:{clip_id}"
        
        audio_bytes = self.toolkit.getter(audio_key)
        metadata = self.toolkit.getter(meta_key)
        
        if audio_bytes and metadata:
            rate, audio_data = decode_audio(audio_bytes)
            return audio_data, rate, metadata
        return None, None, None
```

## 視頻處理

### 視頻幀存儲

```python
from redis_toolkit.converters import VideoConverter
import cv2

converter = VideoConverter()

# 打開視頻文件
cap = cv2.VideoCapture('video.mp4')
fps = int(cap.get(cv2.CAP_PROP_FPS))
frame_count = 0

# 存儲關鍵幀
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # 每秒存儲一幀
    if frame_count % fps == 0:
        second = frame_count // fps
        frame_bytes = converter.encode(frame)
        toolkit.setter(f'video:frame:123:{second}', frame_bytes)
    
    frame_count += 1

cap.release()
print(f"存儲了 {frame_count // fps} 個關鍵幀")
```

### 視頻縮略圖生成

```python
def generate_video_thumbnails(video_path, video_id, num_thumbnails=5):
    """從視頻生成多個縮略圖"""
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    thumbnails = {}
    
    for i in range(num_thumbnails):
        # 計算幀位置
        frame_pos = int((total_frames / (num_thumbnails + 1)) * (i + 1))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
        
        ret, frame = cap.read()
        if ret:
            # 創建縮略圖
            thumb = create_thumbnail(frame, max_size=(320, 240))
            thumb_bytes = encode_image(thumb, format='jpg', quality=80)
            thumbnails[f'video:thumb:{video_id}:{i}'] = thumb_bytes
    
    cap.release()
    
    # 批次存儲縮略圖
    toolkit.batch_set(thumbnails)
    return len(thumbnails)
```

## 實際應用案例

### 1. 用戶頭像系統

```python
class AvatarManager:
    def __init__(self):
        self.toolkit = RedisToolkit()
        self.sizes = {
            'small': (50, 50),
            'medium': (150, 150),
            'large': (300, 300)
        }
    
    def upload_avatar(self, user_id, image_path):
        """上傳並處理用戶頭像"""
        original = cv2.imread(image_path)
        if original is None:
            raise ValueError("無法讀取圖片")
        
        avatars = {}
        
        # 存儲原始圖片
        avatars[f'avatar:{user_id}:original'] = encode_image(
            original, format='png'
        )
        
        # 生成不同尺寸
        for size_name, dimensions in self.sizes.items():
            resized = cv2.resize(original, dimensions)
            avatars[f'avatar:{user_id}:{size_name}'] = encode_image(
                resized, format='jpg', quality=85
            )
        
        # 批次存儲
        self.toolkit.batch_set(avatars)
        
        # 設置過期時間（30天）
        pipe = self.toolkit.client.pipeline()
        for key in avatars.keys():
            pipe.expire(key, 30 * 24 * 3600)
        pipe.execute()
        
    def get_avatar(self, user_id, size='medium'):
        """獲取用戶頭像"""
        key = f'avatar:{user_id}:{size}'
        avatar_bytes = self.toolkit.getter(key)
        
        if avatar_bytes:
            return decode_image(avatar_bytes)
        return None
```

### 2. 音頻消息系統

```python
class VoiceMessageSystem:
    def __init__(self):
        self.toolkit = RedisToolkit()
        
    def send_voice_message(self, sender_id, receiver_id, audio_data, sample_rate):
        """發送語音消息"""
        message_id = str(uuid.uuid4())
        
        # 存儲音頻
        audio_key = f"voice:{message_id}"
        audio_bytes = encode_audio(audio_data, sample_rate)
        self.toolkit.setter(audio_key, audio_bytes)
        
        # 存儲消息元數據
        message = {
            "id": message_id,
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "duration": len(audio_data) / sample_rate,
            "timestamp": time.time(),
            "read": False
        }
        self.toolkit.setter(f"message:{message_id}", message)
        
        # 添加到接收者的消息列表
        self.toolkit.client.lpush(
            f"inbox:{receiver_id}", 
            message_id
        )
        
        # 發布通知
        self.toolkit.publisher("voice_messages", {
            "event": "new_message",
            "receiver_id": receiver_id,
            "message_id": message_id
        })
        
        return message_id
```

## 性能優化

### 1. 壓縮策略

```python
def optimize_image_storage(image, max_size_kb=100):
    """優化圖片存儲大小"""
    quality = 95
    format = 'jpg'
    
    while quality > 10:
        encoded = encode_image(image, format=format, quality=quality)
        size_kb = len(encoded) / 1024
        
        if size_kb <= max_size_kb:
            return encoded, quality
        
        quality -= 5
    
    # 如果還是太大，調整圖片尺寸
    height, width = image.shape[:2]
    scale = 0.8
    new_size = (int(width * scale), int(height * scale))
    resized = cv2.resize(image, new_size)
    
    return encode_image(resized, format=format, quality=50), 50
```

### 2. 緩存策略

```python
class MediaCache:
    def __init__(self, ttl=3600):
        self.toolkit = RedisToolkit()
        self.ttl = ttl
        
    def get_or_generate(self, key, generator_func, *args, **kwargs):
        """獲取或生成媒體內容"""
        # 嘗試從緩存獲取
        cached = self.toolkit.getter(key)
        if cached:
            return cached
        
        # 生成新內容
        content = generator_func(*args, **kwargs)
        
        # 存儲到緩存
        self.toolkit.setter(key, content)
        self.toolkit.client.expire(key, self.ttl)
        
        return content
```

## 錯誤處理

```python
from redis_toolkit.exceptions import SerializationError

def safe_media_operation(func):
    """媒體操作的錯誤處理裝飾器"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except cv2.error as e:
            print(f"OpenCV 錯誤: {e}")
            return None
        except SerializationError as e:
            print(f"序列化錯誤: {e}")
            return None
        except Exception as e:
            print(f"未預期的錯誤: {e}")
            return None
    return wrapper

@safe_media_operation
def process_image(image_path):
    img = cv2.imread(image_path)
    return encode_image(img, format='jpg')
```

## 檢查依賴

```python
from redis_toolkit.converters import check_dependencies

# 檢查所有轉換器依賴
check_dependencies()

# 檢查特定依賴
try:
    import cv2
    print("OpenCV 已安裝")
except ImportError:
    print("需要安裝 OpenCV: pip install opencv-python")
```

## 總結

Redis Toolkit 的媒體處理功能讓您能夠輕鬆地在 Redis 中存儲和檢索圖片、音頻和視頻數據。記住要：

- 選擇合適的壓縮格式和質量設置
- 為大文件考慮分塊存儲
- 實施適當的緩存策略
- 處理好錯誤情況
- 監控內存使用情況