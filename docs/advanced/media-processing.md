# 媒體處理

Redis Toolkit 提供強大的媒體處理功能，讓您輕鬆在 Redis 中存儲和處理圖片、音頻、視頻等多媒體資料。

## 🎯 功能概覽

Redis Toolkit 的媒體處理功能包括：

- **圖片處理**：編碼、解碼、格式轉換、縮放、壓縮
- **音頻處理**：WAV/MP3 支援、取樣率轉換、音量調整
- **視頻處理**：視頻檔案處理、幀提取、基本資訊獲取

## 📦 安裝依賴

媒體處理功能需要額外的依賴套件：

```bash
# 圖片處理
pip install redis-toolkit[cv2]

# 音頻處理（基礎）
pip install redis-toolkit[audio]

# 音頻處理（含 MP3 支援）
pip install redis-toolkit[audio-full]

# 完整媒體支援
pip install redis-toolkit[media]

# 或安裝所有功能
pip install redis-toolkit[all]
```

## 🖼️ 圖片處理

### 基本使用

```python
from redis_toolkit import RedisToolkit
from redis_toolkit.converters import encode_image, decode_image
import cv2

toolkit = RedisToolkit()

# 讀取圖片
img = cv2.imread('photo.jpg')

# 編碼圖片（自動選擇最佳參數）
img_bytes = encode_image(img)
toolkit.setter('user:avatar', img_bytes)

# 解碼圖片
retrieved_bytes = toolkit.getter('user:avatar')
decoded_img = decode_image(retrieved_bytes)

# 儲存解碼後的圖片
cv2.imwrite('decoded_photo.jpg', decoded_img)
```

### 進階圖片處理

```python
from redis_toolkit.converters import get_converter

# 創建圖片轉換器
img_converter = get_converter('image')

# 1. 格式轉換
img_bytes = encode_image(img, format='png')  # 轉為 PNG
img_bytes = encode_image(img, format='jpg', quality=90)  # 高品質 JPEG

# 2. 圖片縮放
resized = img_converter.resize(img, width=800, height=600)
thumbnail = img_converter.resize(img, width=150)  # 等比例縮放

# 3. 批次處理多張圖片
images = {
    'photo1': cv2.imread('photo1.jpg'),
    'photo2': cv2.imread('photo2.jpg'),
    'photo3': cv2.imread('photo3.jpg')
}

for name, image in images.items():
    # 創建縮圖
    thumb = img_converter.resize(image, width=200)
    thumb_bytes = encode_image(thumb, format='jpg', quality=80)
    toolkit.setter(f'thumbnail:{name}', thumb_bytes)
    
    # 儲存原圖
    full_bytes = encode_image(image, format='jpg', quality=95)
    toolkit.setter(f'full:{name}', full_bytes)
```

### 圖片資訊獲取

```python
# 獲取圖片資訊而不解碼整張圖片
img_bytes = toolkit.getter('user:avatar')
info = img_converter.get_info(img_bytes)

print(f"圖片尺寸: {info['width']}x{info['height']}")
print(f"圖片格式: {info['format']}")
print(f"檔案大小: {info['size']} bytes")
```

### 實用範例：頭像處理系統

```python
class AvatarProcessor:
    def __init__(self):
        self.toolkit = RedisToolkit()
        self.converter = get_converter('image')
    
    def process_avatar(self, user_id, image_path):
        """處理用戶頭像：生成多種尺寸"""
        # 讀取原圖
        original = cv2.imread(image_path)
        
        # 生成不同尺寸
        sizes = {
            'large': 500,   # 個人主頁
            'medium': 200,  # 文章列表
            'small': 50     # 評論區
        }
        
        for size_name, width in sizes.items():
            # 縮放圖片
            resized = self.converter.resize(original, width=width)
            
            # 根據尺寸選擇品質
            quality = 95 if size_name == 'large' else 85
            
            # 編碼並儲存
            encoded = encode_image(resized, format='jpg', quality=quality)
            key = f"avatar:{user_id}:{size_name}"
            self.toolkit.setter(key, encoded, ex=86400)  # 快取 24 小時
        
        # 儲存原圖資訊
        self.toolkit.setter(f"avatar:{user_id}:info", {
            "original_size": original.shape[:2],
            "upload_time": time.time(),
            "sizes_available": list(sizes.keys())
        })
    
    def get_avatar(self, user_id, size='medium'):
        """獲取指定尺寸的頭像"""
        key = f"avatar:{user_id}:{size}"
        encoded = self.toolkit.getter(key)
        
        if encoded:
            return decode_image(encoded)
        return None

# 使用範例
processor = AvatarProcessor()
processor.process_avatar(1001, 'user_photo.jpg')

# 獲取不同尺寸
large_avatar = processor.get_avatar(1001, 'large')
small_avatar = processor.get_avatar(1001, 'small')
```

## 🎵 音頻處理

### 基本音頻操作

```python
from redis_toolkit.converters import encode_audio, decode_audio
import numpy as np

# 生成測試音頻（1秒的 440Hz 正弦波）
sample_rate = 44100
duration = 1.0
t = np.linspace(0, duration, int(sample_rate * duration))
audio_data = np.sin(2 * np.pi * 440 * t)

# 編碼音頻
audio_bytes = encode_audio(audio_data, sample_rate=sample_rate)
toolkit.setter('audio:beep', audio_bytes)

# 解碼音頻
retrieved = toolkit.getter('audio:beep')
rate, decoded_audio = decode_audio(retrieved)

print(f"取樣率: {rate} Hz")
print(f"音頻長度: {len(decoded_audio)} 樣本")
```

### 音頻檔案處理

```python
from redis_toolkit.converters import get_converter

audio_converter = get_converter('audio')

# 從檔案讀取音頻
audio_bytes = audio_converter.encode_from_file('song.mp3')
toolkit.setter('music:song1', audio_bytes)

# 獲取音頻資訊
info = audio_converter.get_file_info('song.mp3')
print(f"時長: {info['duration']} 秒")
print(f"聲道數: {info['channels']}")
print(f"取樣率: {info['sample_rate']} Hz")

# 音頻正規化（調整音量）
rate, audio_data = decode_audio(audio_bytes)
normalized = audio_converter.normalize(audio_data, target_level=0.8)
normalized_bytes = encode_audio(normalized, sample_rate=rate)
```

### 實用範例：音頻片段管理

```python
class AudioClipManager:
    def __init__(self):
        self.toolkit = RedisToolkit()
        self.converter = get_converter('audio')
    
    def store_audio_clip(self, clip_id, audio_file, metadata=None):
        """儲存音頻片段"""
        # 編碼音頻
        audio_bytes = self.converter.encode_from_file(audio_file)
        
        # 獲取音頻資訊
        info = self.converter.get_file_info(audio_file)
        
        # 儲存音頻資料
        self.toolkit.setter(f"audio:{clip_id}:data", audio_bytes)
        
        # 儲存元資料
        meta = {
            "filename": audio_file,
            "duration": info['duration'],
            "sample_rate": info['sample_rate'],
            "channels": info['channels'],
            "uploaded_at": time.time()
        }
        if metadata:
            meta.update(metadata)
        
        self.toolkit.setter(f"audio:{clip_id}:meta", meta)
    
    def get_audio_clip(self, clip_id):
        """獲取音頻片段"""
        audio_bytes = self.toolkit.getter(f"audio:{clip_id}:data")
        metadata = self.toolkit.getter(f"audio:{clip_id}:meta")
        
        if audio_bytes:
            rate, audio_data = decode_audio(audio_bytes)
            return {
                "data": audio_data,
                "sample_rate": rate,
                "metadata": metadata
            }
        return None
    
    def create_preview(self, clip_id, preview_duration=30):
        """創建音頻預覽（前30秒）"""
        clip = self.get_audio_clip(clip_id)
        if not clip:
            return None
        
        # 截取前30秒
        sample_rate = clip['sample_rate']
        preview_samples = int(preview_duration * sample_rate)
        preview_data = clip['data'][:preview_samples]
        
        # 淡入淡出效果
        fade_samples = int(0.5 * sample_rate)  # 0.5秒淡入淡出
        fade_in = np.linspace(0, 1, fade_samples)
        fade_out = np.linspace(1, 0, fade_samples)
        
        preview_data[:fade_samples] *= fade_in
        preview_data[-fade_samples:] *= fade_out
        
        # 儲存預覽
        preview_bytes = encode_audio(preview_data, sample_rate=sample_rate)
        self.toolkit.setter(f"audio:{clip_id}:preview", preview_bytes, ex=3600)
        
        return preview_data

# 使用範例
manager = AudioClipManager()

# 儲存音頻
manager.store_audio_clip('clip001', 'podcast.mp3', {
    'title': 'Redis Toolkit 教學',
    'author': 'Tech Podcast',
    'tags': ['redis', 'tutorial']
})

# 創建預覽
manager.create_preview('clip001')
```

## 🎥 視頻處理

### 基本視頻操作

```python
from redis_toolkit.converters import get_converter

video_converter = get_converter('video')

# 讀取視頻檔案
video_bytes = video_converter.encode('video.mp4')
toolkit.setter('video:intro', video_bytes)

# 獲取視頻資訊
info = video_converter.get_video_info('video.mp4')
print(f"視頻尺寸: {info['width']}x{info['height']}")
print(f"幀率: {info['fps']} FPS")
print(f"總幀數: {info['total_frames']}")
print(f"時長: {info['duration']} 秒")
```

### 視頻幀提取

```python
# 提取視頻幀
frames = video_converter.extract_frames('video.mp4', max_frames=10)

# 儲存關鍵幀
for i, frame in enumerate(frames):
    frame_bytes = encode_image(frame, format='jpg', quality=85)
    toolkit.setter(f'video:intro:frame:{i}', frame_bytes)

# 創建視頻縮圖
first_frame = frames[0]
thumbnail = get_converter('image').resize(first_frame, width=320)
thumb_bytes = encode_image(thumbnail, format='jpg', quality=80)
toolkit.setter('video:intro:thumbnail', thumb_bytes)
```

### 實用範例：視頻預覽系統

```python
class VideoPreviewSystem:
    def __init__(self):
        self.toolkit = RedisToolkit()
        self.video_conv = get_converter('video')
        self.image_conv = get_converter('image')
    
    def generate_preview(self, video_id, video_path):
        """生成視頻預覽"""
        # 獲取視頻資訊
        info = self.video_conv.get_video_info(video_path)
        
        # 提取關鍵幀（每10秒一幀）
        fps = info['fps']
        duration = info['duration']
        frame_interval = int(10 * fps)  # 每10秒
        
        frames = self.video_conv.extract_frames(
            video_path,
            frame_interval=frame_interval,
            max_frames=6  # 最多6個預覽圖
        )
        
        # 處理每個幀
        preview_data = []
        for i, frame in enumerate(frames):
            # 創建縮圖
            thumb = self.image_conv.resize(frame, width=480)
            thumb_bytes = encode_image(thumb, format='jpg', quality=85)
            
            # 儲存縮圖
            key = f"video:{video_id}:preview:{i}"
            self.toolkit.setter(key, thumb_bytes, ex=86400)
            
            # 記錄時間戳
            timestamp = (i * frame_interval) / fps
            preview_data.append({
                "index": i,
                "timestamp": timestamp,
                "key": key
            })
        
        # 儲存預覽資訊
        self.toolkit.setter(f"video:{video_id}:preview_info", {
            "video_info": info,
            "previews": preview_data,
            "generated_at": time.time()
        })
        
        return preview_data
    
    def get_preview_grid(self, video_id):
        """獲取預覽圖網格"""
        info = self.toolkit.getter(f"video:{video_id}:preview_info")
        if not info:
            return None
        
        # 載入所有預覽圖
        previews = []
        for preview in info['previews']:
            img_bytes = self.toolkit.getter(preview['key'])
            if img_bytes:
                img = decode_image(img_bytes)
                previews.append(img)
        
        # 創建網格（2x3）
        if len(previews) >= 6:
            row1 = np.hstack(previews[:3])
            row2 = np.hstack(previews[3:6])
            grid = np.vstack([row1, row2])
            
            # 儲存網格圖
            grid_bytes = encode_image(grid, format='jpg', quality=90)
            self.toolkit.setter(f"video:{video_id}:preview_grid", grid_bytes)
            
            return grid
        
        return None

# 使用範例
preview_system = VideoPreviewSystem()

# 生成預覽
previews = preview_system.generate_preview('video001', 'tutorial.mp4')

# 創建預覽網格
grid = preview_system.get_preview_grid('video001')
```

## 🚀 效能優化建議

### 1. 選擇適當的編碼參數

```python
# 根據用途選擇品質
# 縮圖：低品質，小尺寸
thumbnail = encode_image(img, format='jpg', quality=70)

# 預覽：中等品質
preview = encode_image(img, format='jpg', quality=85)

# 原圖：高品質
original = encode_image(img, format='png')  # PNG 無損壓縮
```

### 2. 使用批次處理

```python
# 批次處理多個圖片
def batch_process_images(image_paths):
    batch_data = {}
    
    for path in image_paths:
        img = cv2.imread(path)
        # 生成多種尺寸
        for size in [50, 200, 500]:
            resized = img_converter.resize(img, width=size)
            encoded = encode_image(resized, format='jpg', quality=85)
            key = f"img:{os.path.basename(path)}:w{size}"
            batch_data[key] = encoded
    
    # 一次性儲存
    toolkit.batch_set(batch_data)
```

### 3. 設定適當的快取時間

```python
# 根據資料特性設定 TTL
# 用戶頭像：較長快取
toolkit.setter('avatar:user:1001', avatar_bytes, ex=604800)  # 7天

# 臨時預覽：短期快取
toolkit.setter('preview:temp:123', preview_bytes, ex=3600)  # 1小時

# 永久儲存：不設過期
toolkit.setter('media:permanent:456', media_bytes)  # 永久
```

## 🎯 最佳實踐

1. **壓縮策略**
   - 根據用途選擇格式（JPEG for photos, PNG for graphics）
   - 平衡品質與檔案大小
   - 考慮使用 WebP 格式（如果支援）

2. **錯誤處理**
   ```python
   try:
       img = cv2.imread(image_path)
       if img is None:
           raise ValueError("無法讀取圖片")
       encoded = encode_image(img)
   except Exception as e:
       logger.error(f"圖片處理失敗: {e}")
       # 使用預設圖片或返回錯誤
   ```

3. **資源管理**
   - 限制最大檔案大小
   - 監控 Redis 記憶體使用
   - 定期清理過期的媒體資料

## 📚 延伸閱讀

- [批次操作](./batch-operations.md) - 學習如何批次處理媒體檔案
- [效能優化](./performance.md) - 優化媒體處理效能
- [API 參考 - 轉換器](/api/converters.md) - 詳細的 API 文檔

::: tip 小結
Redis Toolkit 的媒體處理功能讓您輕鬆在 Redis 中處理多媒體資料。記住選擇適當的編碼參數，合理使用快取，並注意資源管理！
:::