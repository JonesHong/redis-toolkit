#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis Toolkit 轉換器測試
"""

import pytest
import tempfile
import os
import numpy as np
from redis_toolkit.converters import (
    BaseConverter, ConversionError, register_converter, 
    get_converter, list_converters
)


class TestBaseConverter:
    """基礎轉換器測試"""
    
    def test_base_converter_interface(self):
        """測試基礎轉換器介面"""
        
        class MockConverter(BaseConverter):
            def _check_dependencies(self):
                pass
            
            def encode(self, data):
                return f"encoded_{data}".encode()
            
            def decode(self, data):
                return data.decode().replace("encoded_", "")
            
            @property
            def supported_formats(self):
                return ['mock']
            
            @property
            def default_format(self):
                return 'mock'
        
        converter = MockConverter()
        
        # 測試編碼
        encoded = converter.encode("test")
        assert encoded == b"encoded_test"
        
        # 測試解碼
        decoded = converter.decode(encoded)
        assert decoded == "test"
        
        # 測試屬性
        assert converter.supported_formats == ['mock']
        assert converter.default_format == 'mock'
    
    def test_converter_registry(self):
        """測試轉換器註冊功能"""
        
        class TestConverter(BaseConverter):
            def _check_dependencies(self):
                pass
            
            def encode(self, data):
                return b"test_encoded"
            
            def decode(self, data):
                return "test_decoded"
            
            @property
            def supported_formats(self):
                return ['test']
            
            @property
            def default_format(self):
                return 'test'
        
        # 註冊轉換器
        register_converter('test_converter', TestConverter)
        
        # 檢查是否已註冊
        assert 'test_converter' in list_converters()
        
        # 取得轉換器實例
        converter = get_converter('test_converter')
        assert isinstance(converter, TestConverter)
        
        # 測試功能
        assert converter.encode("data") == b"test_encoded"
        assert converter.decode(b"data") == "test_decoded"
    
    def test_unknown_converter(self):
        """測試未知轉換器"""
        with pytest.raises(ValueError, match="未知的轉換器"):
            get_converter('unknown_converter')


@pytest.mark.skipif(
    not pytest.importorskip("cv2", minversion=None),
    reason="OpenCV 未安裝"
)
class TestImageConverter:
    """圖片轉換器測試"""
    
    def setup_method(self):
        """測試設定"""
        try:
            from redis_toolkit.converters.image import ImageConverter
            self.converter = ImageConverter()
        except ImportError:
            pytest.skip("圖片轉換器依賴未安裝")
    
    def test_image_encode_decode_simple(self):
        """測試簡單圖片編解碼"""
        import cv2
        
        # 建立測試圖片（100x100 紅色正方形）
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        test_image[:, :] = [0, 0, 255]  # BGR 紅色
        
        # 編碼
        encoded = self.converter.encode(test_image)
        assert isinstance(encoded, bytes)
        assert len(encoded) > 0
        
        # 解碼
        decoded = self.converter.decode(encoded)
        assert isinstance(decoded, np.ndarray)
        assert decoded.shape == test_image.shape
        
        # 由於 JPEG 壓縮會有損失，檢查大致相似
        assert np.allclose(decoded, test_image, atol=10)
    
    def test_image_formats(self):
        """測試不同圖片格式"""
        import cv2
        from redis_toolkit.converters.image import ImageConverter
        
        test_image = np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)
        
        formats = ['jpg', 'png', 'webp']
        
        for fmt in formats:
            if fmt == 'webp':
                # WebP 可能不被所有 OpenCV 版本支援
                try:
                    converter = ImageConverter(format=fmt)
                    encoded = converter.encode(test_image)
                    decoded = converter.decode(encoded)
                    assert decoded.shape == test_image.shape
                except Exception:
                    pytest.skip(f"WebP 格式不被支援")
            else:
                converter = ImageConverter(format=fmt)
                encoded = converter.encode(test_image)
                decoded = converter.decode(encoded)
                assert decoded.shape == test_image.shape
    
    def test_image_quality_settings(self):
        """測試圖片品質設定"""
        from redis_toolkit.converters.image import ImageConverter
        
        test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        # 測試不同品質
        qualities = [50, 80, 95]
        sizes = []
        
        for quality in qualities:
            converter = ImageConverter(format='jpg', quality=quality)
            encoded = converter.encode(test_image)
            sizes.append(len(encoded))
            
            # 確保可以解碼
            decoded = converter.decode(encoded)
            assert decoded.shape == test_image.shape
        
        # 較高品質應該產生較大檔案
        assert sizes[0] < sizes[1] < sizes[2]
    
    def test_grayscale_image(self):
        """測試灰階圖片"""
        # 建立灰階圖片
        gray_image = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        
        encoded = self.converter.encode(gray_image)
        decoded = self.converter.decode(encoded)
        
        # 灰階圖片解碼後可能變成 3 通道
        assert len(decoded.shape) in [2, 3]
        assert decoded.shape[:2] == gray_image.shape
    
    def test_image_resize_utility(self):
        """測試圖片縮放功能"""
        test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        # 縮放到 50x50
        resized = self.converter.resize(test_image, 50, 50)
        assert resized.shape == (50, 50, 3)
        
        # 放大到 200x200
        enlarged = self.converter.resize(test_image, 200, 200)
        assert enlarged.shape == (200, 200, 3)
    
    def test_image_info(self):
        """測試圖片資訊取得"""
        test_image = np.random.randint(0, 255, (100, 150, 3), dtype=np.uint8)
        
        encoded = self.converter.encode(test_image)
        info = self.converter.get_info(encoded)
        
        assert 'width' in info
        assert 'height' in info
        assert 'channels' in info
        assert info['height'] == 100
        assert info['width'] == 150
        assert info['channels'] == 3
    
    def test_invalid_image_data(self):
        """測試無效圖片資料"""
        with pytest.raises(ConversionError):
            self.converter.encode("not_an_array")
        
        with pytest.raises(ConversionError):
            self.converter.decode(b"invalid_image_data")
        
        # 測試無效維度
        invalid_image = np.random.randint(0, 255, (100,), dtype=np.uint8)
        with pytest.raises(ConversionError):
            self.converter.encode(invalid_image)


@pytest.mark.skipif(
    not pytest.importorskip("numpy", minversion="1.19"),
    reason="Numpy 未安裝或版本過舊"
)
class TestAudioConverter:
    """音頻轉換器測試"""
    
    def setup_method(self):
        """測試設定"""
        try:
            from redis_toolkit.converters.audio import AudioConverter
            self.converter = AudioConverter()
        except ImportError:
            pytest.skip("音頻轉換器依賴未安裝")
    
    def test_audio_encode_decode_simple(self):
        """測試簡單音頻編解碼"""
        # 建立測試音頻（1 秒 440Hz 正弦波）
        import numpy as np
        
        sample_rate = 44100
        duration = 1.0
        frequency = 440.0
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio_data = np.sin(2 * np.pi * frequency * t).astype(np.float32)
        
        # 編碼
        encoded = self.converter.encode(audio_data)
        assert isinstance(encoded, bytes)
        assert len(encoded) > 0
        
        # 解碼
        decoded_rate, decoded_data = self.converter.decode(encoded)
        assert decoded_rate == sample_rate
        assert isinstance(decoded_data, np.ndarray)
        assert len(decoded_data) > 0
    
    def test_audio_with_sample_rate(self):
        """測試帶採樣率的音頻編解碼"""
        import numpy as np
        
        sample_rate = 22050
        audio_data = np.random.rand(1000).astype(np.float32)
        
        # 使用元組格式 (sample_rate, data)
        encoded = self.converter.encode((sample_rate, audio_data))
        decoded_rate, decoded_data = self.converter.decode(encoded)
        
        assert decoded_rate == sample_rate
        assert len(decoded_data) == len(audio_data)
    
    def test_audio_formats(self):
        """測試不同音頻格式"""
        from redis_toolkit.converters.audio import AudioConverter
        import numpy as np
        
        audio_data = np.random.rand(1000).astype(np.float32)
        
        # 測試 WAV 格式
        wav_converter = AudioConverter(format='wav')
        encoded = wav_converter.encode(audio_data)
        decoded_rate, decoded_data = wav_converter.decode(encoded)
        assert decoded_rate == 44100
        assert len(decoded_data) > 0
    
    def test_audio_normalization(self):
        """測試音頻正規化"""
        import numpy as np
        
        # 建立音量較大的音頻
        audio_data = np.random.rand(1000).astype(np.float32) * 2.0
        
        # 正規化
        normalized = self.converter.normalize(audio_data, target_level=0.5)
        
        assert np.max(np.abs(normalized)) <= 0.5
        assert normalized.shape == audio_data.shape
    
    def test_audio_file_operations(self):
        """測試音頻檔案操作"""
        import numpy as np
        
        # 建立暫存音頻檔案
        sample_rate = 44100
        audio_data = np.random.rand(1000).astype(np.float32)
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # 使用 scipy 寫入 WAV 檔案
            try:
                from scipy.io import wavfile
                wavfile.write(temp_path, sample_rate, audio_data)
                
                # 測試從檔案編碼
                encoded = self.converter.encode_from_file(temp_path)
                assert isinstance(encoded, bytes)
                assert len(encoded) > 0
                
                # 測試取得檔案資訊
                try:
                    info = self.converter.get_file_info(temp_path)
                    assert 'sample_rate' in info
                    assert 'duration_seconds' in info
                except Exception:
                    # 如果 soundfile 不可用，跳過此測試
                    pass
                
            except ImportError:
                pytest.skip("scipy 未安裝，跳過檔案操作測試")
        
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_invalid_audio_data(self):
        """測試無效音頻資料"""
        with pytest.raises(ConversionError):
            self.converter.encode("not_an_array")
        
        with pytest.raises(ConversionError):
            self.converter.decode(b"invalid_audio_data")


class TestVideoConverter:
    """視頻轉換器測試"""
    
    def setup_method(self):
        """測試設定"""
        try:
            from redis_toolkit.converters.video import VideoConverter
            self.converter = VideoConverter()
        except ImportError:
            pytest.skip("視頻轉換器依賴未安裝")
    
    def test_video_file_operations(self):
        """測試視頻檔案操作"""
        # 建立一個虛擬視頻檔案（實際上是空檔案）
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            temp_file.write(b"fake video data for testing")
            temp_path = temp_file.name
        
        try:
            # 測試檔案編碼（讀取）
            encoded = self.converter.encode(temp_path)
            assert isinstance(encoded, bytes)
            assert len(encoded) > 0
            
            # 測試解碼（回傳原始資料）
            decoded = self.converter.decode(encoded)
            assert decoded == encoded
            
            # 測試保存檔案
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as output_file:
                output_path = output_file.name
            
            try:
                self.converter.save_video_bytes(encoded, output_path)
                assert os.path.exists(output_path)
                
                # 檢查檔案內容
                with open(output_path, 'rb') as f:
                    content = f.read()
                assert content == encoded
            
            finally:
                if os.path.exists(output_path):
                    os.remove(output_path)
        
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_nonexistent_file(self):
        """測試不存在的檔案"""
        with pytest.raises(ConversionError):
            self.converter.encode("/nonexistent/video/file.mp4")


class TestConversionError:
    """轉換錯誤測試"""
    
    def test_conversion_error_creation(self):
        """測試轉換錯誤建立"""
        original_error = ValueError("原始錯誤")
        error = ConversionError("轉換失敗", original_error)
        
        assert str(error) == "轉換失敗"
        assert error.original_error == original_error
    
    def test_conversion_error_without_original(self):
        """測試不帶原始錯誤的轉換錯誤"""
        error = ConversionError("簡單錯誤")
        
        assert str(error) == "簡單錯誤"
        assert error.original_error is None


class TestConverterIntegration:
    """轉換器整合測試"""
    
    def test_available_converters(self):
        """測試可用轉換器列表"""
        converters = list_converters()
        assert isinstance(converters, list)
        
        # 檢查是否包含預期的轉換器（如果依賴可用）
        try:
            import cv2
            assert 'image' in converters
        except ImportError:
            pass
        
        try:
            import numpy as np
            from scipy.io import wavfile
            assert 'audio' in converters
        except ImportError:
            pass
    
    def test_converter_configuration(self):
        """測試轉換器配置"""
        try:
            from redis_toolkit.converters.image import ImageConverter
            
            # 測試自訂配置
            converter = ImageConverter(format='png', quality=90)
            assert converter.format == 'png'
            assert converter.quality == 90
            
        except ImportError:
            pytest.skip("圖片轉換器不可用")
    
    def test_convenience_functions(self):
        """測試便利函數"""
        try:
            from redis_toolkit.converters import encode_image, decode_image
            import numpy as np
            
            test_image = np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)
            
            # 測試便利函數
            encoded = encode_image(test_image, format='jpg', quality=80)
            decoded = decode_image(encoded)
            
            assert isinstance(encoded, bytes)
            assert isinstance(decoded, np.ndarray)
            assert decoded.shape == test_image.shape
            
        except ImportError:
            pytest.skip("圖片轉換器便利函數不可用")


class TestMemoryUsage:
    """記憶體使用測試"""
    
    @pytest.mark.slow
    def test_large_image_memory_usage(self):
        """測試大圖片的記憶體使用"""
        try:
            from redis_toolkit.converters.image import ImageConverter
            import numpy as np
            
            converter = ImageConverter()
            
            # 建立較大的圖片 (1000x1000)
            large_image = np.random.randint(0, 255, (1000, 1000, 3), dtype=np.uint8)
            
            # 編解碼測試
            encoded = converter.encode(large_image)
            decoded = converter.decode(encoded)
            
            assert decoded.shape == large_image.shape
            
        except ImportError:
            pytest.skip("圖片轉換器不可用")
        except MemoryError:
            pytest.skip("記憶體不足，跳過大圖片測試")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])