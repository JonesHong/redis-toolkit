# Media Processing

Redis Toolkit provides powerful media processing capabilities, allowing you to easily store and process images, audio, video, and other multimedia data in Redis.

## 🎯 Feature Overview

Redis Toolkit's media processing features include:

- **Image Processing**: Encoding, decoding, format conversion, scaling, compression
- **Audio Processing**: WAV/MP3 support, sample rate conversion, volume adjustment
- **Video Processing**: Video file processing, frame extraction, basic information retrieval

## 📦 Installing Dependencies

Media processing features require additional dependency packages:

```bash
# Image processing
pip install redis-toolkit[cv2]

# Audio processing (basic)
pip install redis-toolkit[audio]

# Audio processing (with MP3 support)
pip install redis-toolkit[audio-full]

# Complete media support
pip install redis-toolkit[media]

# Or install all features
pip install redis-toolkit[all]
```

## 🖼️ Image Processing

### Basic Usage

```python
from redis_toolkit import RedisToolkit
from redis_toolkit.converters import encode_image, decode_image
import cv2

toolkit = RedisToolkit()

# Read image
img = cv2.imread('photo.jpg')

# Encode image (automatically choose optimal parameters)
img_bytes = encode_image(img)
toolkit.setter('user:avatar', img_bytes)

# Decode image
retrieved_bytes = toolkit.getter('user:avatar')
decoded_img = decode_image(retrieved_bytes)

# Save decoded image
cv2.imwrite('decoded_photo.jpg', decoded_img)
```

### Advanced Image Processing

```python
from redis_toolkit.converters import get_converter

# Create image converter
img_converter = get_converter('image')

# 1. Format conversion
img_bytes = encode_image(img, format='png')  # Convert to PNG
img_bytes = encode_image(img, format='jpg', quality=90)  # High quality JPEG

# 2. Image scaling
resized = img_converter.resize(img, width=800, height=600)
thumbnail = img_converter.resize(img, width=150)  # Proportional scaling

# 3. Batch process multiple images
images = {
    'photo1': cv2.imread('photo1.jpg'),
    'photo2': cv2.imread('photo2.jpg'),
    'photo3': cv2.imread('photo3.jpg')
}

for name, image in images.items():
    # Create thumbnail
    thumb = img_converter.resize(image, width=200)
    thumb_bytes = encode_image(thumb, format='jpg', quality=80)
    toolkit.setter(f'thumbnail:{name}', thumb_bytes)
    
    # Save full image
    full_bytes = encode_image(image, format='jpg', quality=95)
    toolkit.setter(f'full:{name}', full_bytes)
```

### Getting Image Information

```python
# Get image info without decoding the entire image
img_bytes = toolkit.getter('user:avatar')
info = img_converter.get_info(img_bytes)

print(f"Image dimensions: {info['width']}x{info['height']}")
print(f"Image format: {info['format']}")
print(f"File size: {info['size']} bytes")
```

### Practical Example: Avatar Processing System

```python
class AvatarProcessor:
    def __init__(self):
        self.toolkit = RedisToolkit()
        self.converter = get_converter('image')
    
    def process_avatar(self, user_id, image_path):
        """Process user avatar: generate multiple sizes"""
        # Read original image
        original = cv2.imread(image_path)
        
        # Generate different sizes
        sizes = {
            'large': 500,   # Profile page
            'medium': 200,  # Article list
            'small': 50     # Comments section
        }
        
        for size_name, width in sizes.items():
            # Scale image
            resized = self.converter.resize(original, width=width)
            
            # Choose quality based on size
            quality = 95 if size_name == 'large' else 85
            
            # Encode and store
            encoded = encode_image(resized, format='jpg', quality=quality)
            key = f"avatar:{user_id}:{size_name}"
            self.toolkit.setter(key, encoded, ex=86400)  # Cache for 24 hours
        
        # Store original image info
        self.toolkit.setter(f"avatar:{user_id}:info", {
            "original_size": original.shape[:2],
            "upload_time": time.time(),
            "sizes_available": list(sizes.keys())
        })
    
    def get_avatar(self, user_id, size='medium'):
        """Get avatar of specified size"""
        key = f"avatar:{user_id}:{size}"
        encoded = self.toolkit.getter(key)
        
        if encoded:
            return decode_image(encoded)
        return None

# Usage example
processor = AvatarProcessor()
processor.process_avatar(1001, 'user_photo.jpg')

# Get different sizes
large_avatar = processor.get_avatar(1001, 'large')
small_avatar = processor.get_avatar(1001, 'small')
```

## 🎵 Audio Processing

### Basic Audio Operations

```python
from redis_toolkit.converters import encode_audio, decode_audio
import numpy as np

# Generate test audio (1 second 440Hz sine wave)
sample_rate = 44100
duration = 1.0
t = np.linspace(0, duration, int(sample_rate * duration))
audio_data = np.sin(2 * np.pi * 440 * t)

# Encode audio
audio_bytes = encode_audio(audio_data, sample_rate=sample_rate)
toolkit.setter('audio:beep', audio_bytes)

# Decode audio
retrieved = toolkit.getter('audio:beep')
rate, decoded_audio = decode_audio(retrieved)

print(f"Sample rate: {rate} Hz")
print(f"Audio length: {len(decoded_audio)} samples")
```

### Audio File Processing

```python
from redis_toolkit.converters import get_converter

audio_converter = get_converter('audio')

# Read audio from file
audio_bytes = audio_converter.encode_from_file('song.mp3')
toolkit.setter('music:song1', audio_bytes)

# Get audio info
info = audio_converter.get_file_info('song.mp3')
print(f"Duration: {info['duration']} seconds")
print(f"Channels: {info['channels']}")
print(f"Sample rate: {info['sample_rate']} Hz")

# Audio normalization (adjust volume)
rate, audio_data = decode_audio(audio_bytes)
normalized = audio_converter.normalize(audio_data, target_level=0.8)
normalized_bytes = encode_audio(normalized, sample_rate=rate)
```

### Practical Example: Audio Clip Manager

```python
class AudioClipManager:
    def __init__(self):
        self.toolkit = RedisToolkit()
        self.converter = get_converter('audio')
    
    def store_audio_clip(self, clip_id, audio_file, metadata=None):
        """Store audio clip"""
        # Encode audio
        audio_bytes = self.converter.encode_from_file(audio_file)
        
        # Get audio info
        info = self.converter.get_file_info(audio_file)
        
        # Store audio data
        self.toolkit.setter(f"audio:{clip_id}:data", audio_bytes)
        
        # Store metadata
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
        """Get audio clip"""
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
        """Create audio preview (first 30 seconds)"""
        clip = self.get_audio_clip(clip_id)
        if not clip:
            return None
        
        # Extract first 30 seconds
        sample_rate = clip['sample_rate']
        preview_samples = int(preview_duration * sample_rate)
        preview_data = clip['data'][:preview_samples]
        
        # Fade in/out effect
        fade_samples = int(0.5 * sample_rate)  # 0.5 second fade
        fade_in = np.linspace(0, 1, fade_samples)
        fade_out = np.linspace(1, 0, fade_samples)
        
        preview_data[:fade_samples] *= fade_in
        preview_data[-fade_samples:] *= fade_out
        
        # Store preview
        preview_bytes = encode_audio(preview_data, sample_rate=sample_rate)
        self.toolkit.setter(f"audio:{clip_id}:preview", preview_bytes, ex=3600)
        
        return preview_data

# Usage example
manager = AudioClipManager()

# Store audio
manager.store_audio_clip('clip001', 'podcast.mp3', {
    'title': 'Redis Toolkit Tutorial',
    'author': 'Tech Podcast',
    'tags': ['redis', 'tutorial']
})

# Create preview
manager.create_preview('clip001')
```

## 🎥 Video Processing

### Basic Video Operations

```python
from redis_toolkit.converters import get_converter

video_converter = get_converter('video')

# Read video file
video_bytes = video_converter.encode('video.mp4')
toolkit.setter('video:intro', video_bytes)

# Get video info
info = video_converter.get_video_info('video.mp4')
print(f"Video dimensions: {info['width']}x{info['height']}")
print(f"Frame rate: {info['fps']} FPS")
print(f"Total frames: {info['total_frames']}")
print(f"Duration: {info['duration']} seconds")
```

### Video Frame Extraction

```python
# Extract video frames
frames = video_converter.extract_frames('video.mp4', max_frames=10)

# Store key frames
for i, frame in enumerate(frames):
    frame_bytes = encode_image(frame, format='jpg', quality=85)
    toolkit.setter(f'video:intro:frame:{i}', frame_bytes)

# Create video thumbnail
first_frame = frames[0]
thumbnail = get_converter('image').resize(first_frame, width=320)
thumb_bytes = encode_image(thumbnail, format='jpg', quality=80)
toolkit.setter('video:intro:thumbnail', thumb_bytes)
```

### Practical Example: Video Preview System

```python
class VideoPreviewSystem:
    def __init__(self):
        self.toolkit = RedisToolkit()
        self.video_conv = get_converter('video')
        self.image_conv = get_converter('image')
    
    def generate_preview(self, video_id, video_path):
        """Generate video preview"""
        # Get video info
        info = self.video_conv.get_video_info(video_path)
        
        # Extract key frames (one frame every 10 seconds)
        fps = info['fps']
        duration = info['duration']
        frame_interval = int(10 * fps)  # Every 10 seconds
        
        frames = self.video_conv.extract_frames(
            video_path,
            frame_interval=frame_interval,
            max_frames=6  # Maximum 6 preview images
        )
        
        # Process each frame
        preview_data = []
        for i, frame in enumerate(frames):
            # Create thumbnail
            thumb = self.image_conv.resize(frame, width=480)
            thumb_bytes = encode_image(thumb, format='jpg', quality=85)
            
            # Store thumbnail
            key = f"video:{video_id}:preview:{i}"
            self.toolkit.setter(key, thumb_bytes, ex=86400)
            
            # Record timestamp
            timestamp = (i * frame_interval) / fps
            preview_data.append({
                "index": i,
                "timestamp": timestamp,
                "key": key
            })
        
        # Store preview info
        self.toolkit.setter(f"video:{video_id}:preview_info", {
            "video_info": info,
            "previews": preview_data,
            "generated_at": time.time()
        })
        
        return preview_data
    
    def get_preview_grid(self, video_id):
        """Get preview image grid"""
        info = self.toolkit.getter(f"video:{video_id}:preview_info")
        if not info:
            return None
        
        # Load all preview images
        previews = []
        for preview in info['previews']:
            img_bytes = self.toolkit.getter(preview['key'])
            if img_bytes:
                img = decode_image(img_bytes)
                previews.append(img)
        
        # Create grid (2x3)
        if len(previews) >= 6:
            row1 = np.hstack(previews[:3])
            row2 = np.hstack(previews[3:6])
            grid = np.vstack([row1, row2])
            
            # Store grid image
            grid_bytes = encode_image(grid, format='jpg', quality=90)
            self.toolkit.setter(f"video:{video_id}:preview_grid", grid_bytes)
            
            return grid
        
        return None

# Usage example
preview_system = VideoPreviewSystem()

# Generate preview
previews = preview_system.generate_preview('video001', 'tutorial.mp4')

# Create preview grid
grid = preview_system.get_preview_grid('video001')
```

## 🚀 Performance Optimization Tips

### 1. Choose Appropriate Encoding Parameters

```python
# Choose quality based on purpose
# Thumbnails: low quality, small size
thumbnail = encode_image(img, format='jpg', quality=70)

# Preview: medium quality
preview = encode_image(img, format='jpg', quality=85)

# Original: high quality
original = encode_image(img, format='png')  # PNG lossless compression
```

### 2. Use Batch Processing

```python
# Batch process multiple images
def batch_process_images(image_paths):
    batch_data = {}
    
    for path in image_paths:
        img = cv2.imread(path)
        # Generate multiple sizes
        for size in [50, 200, 500]:
            resized = img_converter.resize(img, width=size)
            encoded = encode_image(resized, format='jpg', quality=85)
            key = f"img:{os.path.basename(path)}:w{size}"
            batch_data[key] = encoded
    
    # Store all at once
    toolkit.batch_set(batch_data)
```

### 3. Set Appropriate Cache Times

```python
# Set TTL based on data characteristics
# User avatar: longer cache
toolkit.setter('avatar:user:1001', avatar_bytes, ex=604800)  # 7 days

# Temporary preview: short cache
toolkit.setter('preview:temp:123', preview_bytes, ex=3600)  # 1 hour

# Permanent storage: no expiry
toolkit.setter('media:permanent:456', media_bytes)  # Permanent
```

## 🎯 Best Practices

1. **Compression Strategy**
   - Choose format based on use case (JPEG for photos, PNG for graphics)
   - Balance quality and file size
   - Consider using WebP format (if supported)

2. **Error Handling**
   ```python
   try:
       img = cv2.imread(image_path)
       if img is None:
           raise ValueError("Unable to read image")
       encoded = encode_image(img)
   except Exception as e:
       logger.error(f"Image processing failed: {e}")
       # Use default image or return error
   ```

3. **Resource Management**
   - Limit maximum file size
   - Monitor Redis memory usage
   - Regularly clean up expired media data

## 📚 Further Reading

- [Batch Operations](./batch-operations.md) - Learn how to batch process media files
- [Performance Optimization](./performance.md) - Optimize media processing performance
- [API Reference - Converters](/en/api/converters.md) - Detailed API documentation

::: tip Summary
Redis Toolkit's media processing features make it easy to handle multimedia data in Redis. Remember to choose appropriate encoding parameters, use cache wisely, and manage resources properly!
:::