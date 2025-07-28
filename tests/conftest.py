#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis Toolkit 測試配置
包含轉換器測試的額外配置
"""

import pytest
import redis
import time
import logging
import tempfile
import os
import numpy as np
from redis_toolkit import RedisToolkit, RedisOptions

# 設定測試日誌
logging.basicConfig(level=logging.WARNING)


@pytest.fixture(scope="session")
def redis_available():
    """檢查 Redis 是否可用"""
    try:
        client = redis.Redis(host='localhost', port=6379, db=0)
        client.ping()
        return True
    except (redis.ConnectionError, redis.TimeoutError):
        return False


@pytest.fixture(scope="session")
def opencv_available():
    """檢查 OpenCV 是否可用"""
    try:
        import cv2
        return True
    except ImportError:
        return False


@pytest.fixture(scope="session")
def numpy_available():
    """檢查 NumPy 是否可用"""
    try:
        import numpy as np
        return True
    except ImportError:
        return False


@pytest.fixture(scope="session")
def scipy_available():
    """檢查 SciPy 是否可用"""
    try:
        from scipy.io import wavfile
        return True
    except ImportError:
        return False


@pytest.fixture(scope="session")
def soundfile_available():
    """檢查 soundfile 是否可用"""
    try:
        import soundfile as sf
        return True
    except ImportError:
        return False


@pytest.fixture
def redis_client():
    """提供 Redis 客戶端實例"""
    client = redis.Redis(host='localhost', port=6379, db=15, decode_responses=False)  # 使用測試專用 DB
    yield client
    # 清理測試資料
    try:
        client.flushdb()
    except:
        pass


@pytest.fixture
def toolkit():
    """提供 RedisToolkit 實例"""
    instance = RedisToolkit(
        options=RedisOptions(is_logger_info=False)
    )
    yield instance
    instance.cleanup()


@pytest.fixture
def toolkit_with_custom_db():
    """提供使用自訂資料庫的 RedisToolkit 實例"""
    from redis_toolkit import RedisConnectionConfig
    
    config = RedisConnectionConfig(host='localhost', port=6379, db=14)
    instance = RedisToolkit(
        config=config,
        options=RedisOptions(is_logger_info=False)
    )
    yield instance
    instance.cleanup()
    
    # 清理測試資料
    try:
        instance.client.flushdb()
    except:
        pass


@pytest.fixture
def sample_data():
    """提供測試用的樣本資料"""
    return {
        "string_data": "測試字串資料",
        "dict_data": {
            "name": "測試用戶",
            "age": 25,
            "active": True,
            "score": 95.5,
            "tags": ["tag1", "tag2"],
            "metadata": {"type": "test", "version": "1.0"}
        },
        "list_data": [1, "二", 3.0, True, None, {"nested": "value"}],
        "bytes_data": b"binary test data \x00\x01\x02",
        "bool_true": True,
        "bool_false": False,
        "number_int": 42,
        "number_float": 3.14159,
        "empty_dict": {},
        "empty_list": [],
        "none_value": None,
    }


@pytest.fixture
def sample_image_data():
    """提供測試用的圖片資料"""
    if not numpy_available():
        pytest.skip("NumPy 未安裝，跳過圖片測試")
    
    # 建立測試圖片資料
    return {
        "small_rgb": np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8),
        "small_gray": np.random.randint(0, 255, (50, 50), dtype=np.uint8),
        "medium_rgb": np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8),
        "large_rgb": np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8),
        "float_image": np.random.rand(50, 50, 3).astype(np.float32),
    }


@pytest.fixture
def sample_audio_data():
    """提供測試用的音頻資料"""
    if not numpy_available():
        pytest.skip("NumPy 未安裝，跳過音頻測試")
    
    # 建立測試音頻資料
    sample_rate = 44100
    duration = 0.1  # 100ms
    frequency = 440.0  # A4 note
    
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    return {
        "sine_wave": np.sin(2 * np.pi * frequency * t).astype(np.float32),
        "random_noise": np.random.rand(1000).astype(np.float32),
        "silence": np.zeros(1000, dtype=np.float32),
        "sample_rate": sample_rate,
        "stereo_sine": np.column_stack([
            np.sin(2 * np.pi * frequency * t),
            np.sin(2 * np.pi * frequency * 1.5 * t)
        ]).astype(np.float32),
    }


@pytest.fixture
def temp_media_files():
    """提供暫存媒體檔案"""
    files = {}
    
    try:
        # 建立暫存圖片檔案
        if numpy_available():
            try:
                import cv2
                test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
                
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
                    cv2.imwrite(f.name, test_image)
                    files['image_jpg'] = f.name
                
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                    cv2.imwrite(f.name, test_image)
                    files['image_png'] = f.name
            except ImportError:
                # cv2 not available, skip image file creation
                pass
    except ImportError:
        pass
    
    try:
        # 建立暫存音頻檔案
        if numpy_available() and scipy_available():
            from scipy.io import wavfile
            
            sample_rate = 44100
            audio_data = np.random.rand(1000).astype(np.float32)
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                wavfile.write(f.name, sample_rate, audio_data)
                files['audio_wav'] = f.name
    except ImportError:
        pass
    
    # 建立暫存視頻檔案（假資料）
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
        f.write(b"fake video data for testing" * 100)
        files['video_mp4'] = f.name
    
    yield files
    
    # 清理暫存檔案
    for file_path in files.values():
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass


@pytest.fixture
def pubsub_setup():
    """設定發布訂閱測試環境"""
    received_messages = []
    
    def message_handler(channel: str, data):
        received_messages.append((channel, data, time.time()))
    
    subscriber = RedisToolkit(
        channels=["test_channel_1", "test_channel_2"],
        message_handler=message_handler,
        options=RedisOptions(is_logger_info=False)
    )
    
    publisher = RedisToolkit(
        options=RedisOptions(is_logger_info=False)
    )
    
    # 等待訂閱者啟動
    time.sleep(0.5)
    
    yield {
        'subscriber': subscriber,
        'publisher': publisher,
        'received_messages': received_messages,
        'message_handler': message_handler
    }
    
    # 清理
    subscriber.cleanup()
    publisher.cleanup()


@pytest.fixture
def media_pubsub_setup():
    """設定媒體發布訂閱測試環境"""
    received_messages = []
    
    def media_handler(channel: str, data):
        received_messages.append((channel, data, time.time()))
    
    subscriber = RedisToolkit(
        channels=["media_sharing", "analytics"],
        message_handler=media_handler,
        options=RedisOptions(is_logger_info=False)
    )
    
    publisher = RedisToolkit(
        options=RedisOptions(is_logger_info=False)
    )
    
    time.sleep(0.5)
    
    yield {
        'subscriber': subscriber,
        'publisher': publisher,
        'received_messages': received_messages,
        'media_handler': media_handler
    }
    
    subscriber.cleanup()
    publisher.cleanup()


def pytest_configure(config):
    """Pytest 配置"""
    config.addinivalue_line(
        "markers", "slow: 標記為慢速測試"
    )
    config.addinivalue_line(
        "markers", "integration: 標記為整合測試"
    )
    config.addinivalue_line(
        "markers", "requires_redis: 標記為需要 Redis 的測試"
    )
    config.addinivalue_line(
        "markers", "requires_opencv: 標記為需要 OpenCV 的測試"
    )
    config.addinivalue_line(
        "markers", "requires_numpy: 標記為需要 NumPy 的測試"
    )
    config.addinivalue_line(
        "markers", "requires_scipy: 標記為需要 SciPy 的測試"
    )
    config.addinivalue_line(
        "markers", "converter: 標記為轉換器測試"
    )
    config.addinivalue_line(
        "markers", "media: 標記為媒體處理測試"
    )


def pytest_collection_modifyitems(config, items):
    """修改測試項目收集"""
    for item in items:
        # 為需要 Redis 的測試添加標記
        if "redis" in item.name.lower() or "toolkit" in item.name.lower():
            item.add_marker(pytest.mark.requires_redis)
        
        # 為轉換器相關測試添加標記
        if any(keyword in item.name.lower() for keyword in ["converter", "image", "audio", "video"]):
            item.add_marker(pytest.mark.converter)
        
        # 為媒體相關測試添加標記
        if any(keyword in item.name.lower() for keyword in ["media", "image", "audio", "video"]):
            item.add_marker(pytest.mark.media)
        
        # 為 OpenCV 相關測試添加標記
        if any(keyword in item.name.lower() for keyword in ["image", "opencv", "cv2"]):
            item.add_marker(pytest.mark.requires_opencv)
        
        # 為 NumPy 相關測試添加標記
        if any(keyword in item.name.lower() for keyword in ["numpy", "array", "image", "audio"]):
            item.add_marker(pytest.mark.requires_numpy)


@pytest.fixture
def performance_timer():
    """效能測試計時器"""
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.perf_counter()
        
        def stop(self):
            self.end_time = time.perf_counter()
        
        @property
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
        
        def __enter__(self):
            self.start()
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            self.stop()
    
    return Timer()


@pytest.fixture
def large_data():
    """提供大型測試資料"""
    return {
        "large_string": "x" * 10000,  # 10KB 字串
        "large_dict": {f"key_{i}": f"value_{i}" for i in range(1000)},  # 1000 個鍵值對
        "large_list": list(range(1000)),  # 1000 個元素的列表
        "large_bytes": b"binary_data" * 1000,  # 約 11KB 的位元組資料
    }


@pytest.fixture
def converter_test_data():
    """提供轉換器測試專用資料"""
    data = {}
    
    if numpy_available():
        # 圖片測試資料
        data['images'] = {
            'rgb_small': np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8),
            'rgb_medium': np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8),
            'grayscale': np.random.randint(0, 255, (100, 100), dtype=np.uint8),
            'float_image': np.random.rand(50, 50, 3).astype(np.float32),
        }
        
        # 音頻測試資料
        sample_rate = 44100
        duration = 0.5  # 500ms
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        data['audio'] = {
            'sine_440': (sample_rate, np.sin(2 * np.pi * 440 * t).astype(np.float32)),
            'white_noise': (sample_rate, np.random.rand(int(sample_rate * duration)).astype(np.float32)),
            'silence': (sample_rate, np.zeros(int(sample_rate * duration), dtype=np.float32)),
            'stereo': (sample_rate, np.column_stack([
                np.sin(2 * np.pi * 440 * t),
                np.sin(2 * np.pi * 880 * t)
            ]).astype(np.float32)),
        }
    
    return data


# 測試跳過條件
skip_if_no_redis = pytest.mark.skipif(
    not pytest.importorskip("redis"),
    reason="Redis 未安裝"
)

skip_if_no_numpy = pytest.mark.skipif(
    not pytest.importorskip("numpy", minversion="1.19"),
    reason="Numpy 未安裝或版本過舊"
)

# 檢查 cv2 是否可用
try:
    import cv2
    _has_cv2 = True
except ImportError:
    _has_cv2 = False

skip_if_no_opencv = pytest.mark.skipif(
    not _has_cv2,
    reason="OpenCV 未安裝"
)

skip_if_no_scipy = pytest.mark.skipif(
    not pytest.importorskip("scipy"),
    reason="SciPy 未安裝"
)


class RedisTestHelper:
    """Redis 測試輔助類"""
    
    @staticmethod
    def wait_for_subscriber(timeout=2.0):
        """等待訂閱者啟動"""
        time.sleep(min(timeout, 2.0))
    
    @staticmethod
    def cleanup_redis_keys(client, pattern="*"):
        """清理 Redis 鍵"""
        try:
            keys = client.keys(pattern)
            if keys:
                client.delete(*keys)
        except:
            pass
    
    @staticmethod
    def verify_data_integrity(original, retrieved):
        """驗證資料完整性"""
        return original == retrieved and type(original) == type(retrieved)


class ConverterTestHelper:
    """轉換器測試輔助類"""
    
    @staticmethod
    def create_test_image(width=100, height=100, channels=3, dtype=np.uint8):
        """建立測試圖片"""
        if not numpy_available():
            pytest.skip("NumPy 未安裝")
        
        if dtype == np.uint8:
            return np.random.randint(0, 255, (height, width, channels), dtype=dtype)
        else:
            return np.random.rand(height, width, channels).astype(dtype)
    
    @staticmethod
    def create_test_audio(duration=1.0, sample_rate=44100, frequency=440.0):
        """建立測試音頻"""
        if not numpy_available():
            pytest.skip("NumPy 未安裝")
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        return sample_rate, np.sin(2 * np.pi * frequency * t).astype(np.float32)
    
    @staticmethod
    def compare_images(img1, img2, tolerance=10):
        """比較兩張圖片（考慮壓縮損失）"""
        if not numpy_available():
            return False
        
        if img1.shape != img2.shape:
            return False
        
        return np.allclose(img1, img2, atol=tolerance)
    
    @staticmethod
    def compare_audio(audio1, audio2, tolerance=0.01):
        """比較兩段音頻"""
        if not numpy_available():
            return False
        
        if len(audio1) != len(audio2):
            return False
        
        return np.allclose(audio1, audio2, atol=tolerance)


@pytest.fixture
def redis_helper():
    """提供 Redis 測試輔助工具"""
    return RedisTestHelper()


@pytest.fixture
def converter_helper():
    """提供轉換器測試輔助工具"""
    return ConverterTestHelper()


@pytest.fixture
def memory_monitor():
    """記憶體監控器（用於效能測試）"""
    import psutil
    import os
    
    class MemoryMonitor:
        def __init__(self):
            self.process = psutil.Process(os.getpid())
            self.start_memory = None
            self.end_memory = None
        
        def start(self):
            self.start_memory = self.process.memory_info().rss
        
        def stop(self):
            self.end_memory = self.process.memory_info().rss
        
        @property
        def memory_used(self):
            if self.start_memory and self.end_memory:
                return self.end_memory - self.start_memory
            return None
        
        @property
        def memory_used_mb(self):
            used = self.memory_used
            return used / 1024 / 1024 if used else None
    
    return MemoryMonitor()


# 測試資料快取（避免重複建立大型測試資料）
@pytest.fixture(scope="session")
def cached_test_images():
    """快取的測試圖片資料"""
    if not numpy_available():
        return {}
    
    return {
        'small': np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8),
        'medium': np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8),
    }


@pytest.fixture(scope="session") 
def cached_test_audio():
    """快取的測試音頻資料"""
    if not numpy_available():
        return {}
    
    sample_rate = 44100
    duration = 0.1
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    return {
        'sine': (sample_rate, np.sin(2 * np.pi * 440 * t).astype(np.float32)),
        'noise': (sample_rate, np.random.rand(int(sample_rate * duration)).astype(np.float32)),
    }