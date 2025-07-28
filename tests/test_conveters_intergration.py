#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis Toolkit 轉換器與核心整合測試
測試轉換器與 Redis 存儲、Pub/Sub 等功能的整合
"""

import pytest
import time
import tempfile
import os
import numpy as np
from redis_toolkit import RedisToolkit, RedisOptions


@pytest.mark.skipif(
    not pytest.importorskip("cv2", minversion=None),
    reason="OpenCV 未安裝"
)
class TestImageRedisIntegration:
    """圖片轉換器與 Redis 整合測試"""
    
    def setup_method(self):
        """測試設定"""
        self.toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
    
    def teardown_method(self):
        """測試清理"""
        self.toolkit.cleanup()
    
    def test_image_storage_retrieval(self):
        """測試圖片存儲和取得"""
        try:
            from redis_toolkit.converters import encode_image, decode_image
        except ImportError:
            pytest.skip("圖片轉換器不可用")
        
        # 建立測試圖片
        test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        # 編碼圖片
        encoded_image = encode_image(test_image, format='jpg', quality=85)
        
        # 存儲到 Redis
        self.toolkit.setter("test_image", encoded_image)
        
        # 從 Redis 取得
        retrieved_data = self.toolkit.getter("test_image")
        assert retrieved_data == encoded_image
        
        # 解碼圖片
        decoded_image = decode_image(retrieved_data)
        
        # 驗證圖片形狀
        assert decoded_image.shape == test_image.shape
    
    def test_multiple_image_formats_storage(self):
        """測試多種圖片格式存儲"""
        try:
            from redis_toolkit.converters import encode_image, decode_image
        except ImportError:
            pytest.skip("圖片轉換器不可用")
        
        test_image = np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)
        formats = ['jpg', 'png']
        
        for fmt in formats:
            # 編碼
            encoded = encode_image(test_image, format=fmt)
            
            # 存儲
            key = f"image_{fmt}"
            self.toolkit.setter(key, encoded)
            
            # 取得並解碼
            retrieved = self.toolkit.getter(key)
            decoded = decode_image(retrieved)
            
            assert decoded.shape == test_image.shape
    
    def test_image_batch_operations(self):
        """測試圖片批次操作"""
        try:
            from redis_toolkit.converters import encode_image, decode_image
        except ImportError:
            pytest.skip("圖片轉換器不可用")
        
        # 建立多張測試圖片
        images = {}
        for i in range(3):
            img = np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)
            encoded = encode_image(img, format='jpg')
            images[f"batch_image_{i}"] = encoded
        
        # 批次存儲
        self.toolkit.batch_set(images)
        
        # 批次取得
        keys = list(images.keys())
        retrieved = self.toolkit.batch_get(keys)
        
        # 驗證所有圖片
        for key in keys:
            assert retrieved[key] == images[key]
            decoded = decode_image(retrieved[key])
            assert decoded.shape == (50, 50, 3)


@pytest.mark.skipif(
    not pytest.importorskip("numpy", minversion="1.19"),
    reason="Numpy 未安裝或版本過舊"
)
class TestAudioRedisIntegration:
    """音頻轉換器與 Redis 整合測試"""
    
    def setup_method(self):
        """測試設定"""
        self.toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
    
    def teardown_method(self):
        """測試清理"""
        self.toolkit.cleanup()
    
    def test_audio_storage_retrieval(self):
        """測試音頻存儲和取得"""
        try:
            from redis_toolkit.converters import encode_audio, decode_audio
        except ImportError:
            pytest.skip("音頻轉換器不可用")
        
        # 建立測試音頻
        sample_rate = 44100
        duration = 0.1  # 100ms
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio_data = np.sin(2 * np.pi * 440 * t).astype(np.float32)
        
        # 編碼音頻
        encoded_audio = encode_audio(audio_data, sample_rate=sample_rate)
        
        # 存儲到 Redis
        self.toolkit.setter("test_audio", encoded_audio)
        
        # 從 Redis 取得
        retrieved_data = self.toolkit.getter("test_audio")
        assert retrieved_data == encoded_audio
        
        # 解碼音頻
        decoded_rate, decoded_data = decode_audio(retrieved_data)
        
        # 驗證音頻資料
        assert decoded_rate == sample_rate
        assert len(decoded_data) > 0
    
    def test_audio_metadata_storage(self):
        """測試音頻與元資料一起存儲"""
        try:
            from redis_toolkit.converters import encode_audio
        except ImportError:
            pytest.skip("音頻轉換器不可用")
        
        # 建立音頻資料
        audio_data = np.random.rand(1000).astype(np.float32)
        encoded_audio = encode_audio(audio_data, sample_rate=22050)
        
        # 現在可以直接在字典中包含 bytes 資料了！
        # (因為我們改進了序列化器)
        audio_record = {
            "title": "測試音頻",
            "duration": 1.0,
            "format": "wav",
            "sample_rate": 22050,
            "audio_data": encoded_audio,  # 直接包含 bytes
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        # 存儲整個記錄
        self.toolkit.setter("audio_record", audio_record)
        
        # 取得並驗證
        retrieved = self.toolkit.getter("audio_record")
        assert retrieved["title"] == "測試音頻"
        assert retrieved["sample_rate"] == 22050
        assert retrieved["audio_data"] == encoded_audio
        assert isinstance(retrieved["audio_data"], bytes)
        
        # 額外測試：複雜嵌套結構
        complex_record = {
            "metadata": {
                "title": "複雜音頻記錄",
                "files": [
                    {
                        "name": "audio1.wav",
                        "data": encoded_audio,
                        "size": len(encoded_audio)
                    },
                    {
                        "name": "audio2.wav", 
                        "data": b"another audio data",
                        "size": len(b"another audio data")
                    }
                ]
            },
            "settings": {
                "quality": "high",
                "compressed": False
            }
        }
        
        # 存儲複雜結構
        self.toolkit.setter("complex_audio_record", complex_record)
        
        # 取得並驗證
        retrieved_complex = self.toolkit.getter("complex_audio_record")
        assert retrieved_complex["metadata"]["title"] == "複雜音頻記錄"
        assert len(retrieved_complex["metadata"]["files"]) == 2
        assert retrieved_complex["metadata"]["files"][0]["data"] == encoded_audio
        assert isinstance(retrieved_complex["metadata"]["files"][0]["data"], bytes)
        assert retrieved_complex["metadata"]["files"][1]["data"] == b"another audio data"


class TestMediaPubSubIntegration:
    """媒體發布訂閱整合測試"""
    
    def test_image_pubsub_sharing(self):
        """測試圖片通過 Pub/Sub 分享"""
        try:
            from redis_toolkit.converters import encode_image, decode_image
            import base64
        except ImportError:
            pytest.skip("圖片轉換器不可用")
        
        received_messages = []
        
        def message_handler(channel: str, data):
            received_messages.append((channel, data))
        
        # 建立發布訂閱
        subscriber = RedisToolkit(
            channels=["image_sharing"],
            message_handler=message_handler,
            options=RedisOptions(is_logger_info=False)
        )
        
        publisher = RedisToolkit(options=RedisOptions(is_logger_info=False))
        
        time.sleep(0.5)  # 等待訂閱者啟動
        
        # 建立測試圖片
        test_image = np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)
        encoded_image = encode_image(test_image, format='jpg', quality=80)
        
        # 發布圖片訊息（確保使用 base64 字串而非原始 bytes）
        image_message = {
            "type": "image",
            "user": "test_user",
            "image_data": base64.b64encode(encoded_image).decode('utf-8'),
            "timestamp": time.time(),
            "width": test_image.shape[1],
            "height": test_image.shape[0]
        }
        
        publisher.publisher("image_sharing", image_message)
        time.sleep(1)
        
        # 驗證接收
        assert len(received_messages) == 1
        channel, data = received_messages[0]
        assert channel == "image_sharing"
        assert data["type"] == "image"
        assert data["user"] == "test_user"
        assert "image_data" in data
        
        # 解碼並驗證圖片
        received_image_data = base64.b64decode(data["image_data"])
        decoded_image = decode_image(received_image_data)
        assert decoded_image.shape == test_image.shape
        
        # 清理
        subscriber.cleanup()
        publisher.cleanup()
    
    def test_audio_pubsub_sharing(self):
        """測試音頻通過 Pub/Sub 分享"""
        try:
            from redis_toolkit.converters import encode_audio, decode_audio
            import base64
        except ImportError:
            pytest.skip("音頻轉換器不可用")
        
        received_messages = []
        
        def message_handler(channel: str, data):
            received_messages.append((channel, data))
        
        subscriber = RedisToolkit(
            channels=["audio_sharing"],
            message_handler=message_handler,
            options=RedisOptions(is_logger_info=False)
        )
        
        publisher = RedisToolkit(options=RedisOptions(is_logger_info=False))
        time.sleep(0.5)
        
        # 建立測試音頻
        audio_data = np.random.rand(100).astype(np.float32)
        encoded_audio = encode_audio(audio_data, sample_rate=44100)
        
        # 發布音頻訊息
        audio_message = {
            "type": "audio",
            "user": "audio_user",
            "audio_data": base64.b64encode(encoded_audio).decode('utf-8'),
            "sample_rate": 44100,
            "duration": len(audio_data) / 44100
        }
        
        publisher.publisher("audio_sharing", audio_message)
        time.sleep(1)
        
        # 驗證接收
        assert len(received_messages) == 1
        channel, data = received_messages[0]
        assert data["type"] == "audio"
        assert data["sample_rate"] == 44100
        
        # 解碼並驗證音頻
        received_audio_data = base64.b64decode(data["audio_data"])
        decoded_rate, decoded_audio = decode_audio(received_audio_data)
        assert decoded_rate == 44100
        assert len(decoded_audio) > 0
        
        # 清理
        subscriber.cleanup()
        publisher.cleanup()


class TestRealTimeAnalytics:
    """即時分析整合測試"""
    
    def test_realtime_chart_generation(self):
        """測試即時圖表生成和分享"""
        try:
            from redis_toolkit.converters import encode_image, decode_image
            import base64
        except ImportError:
            pytest.skip("圖片轉換器不可用")
        
        received_charts = []
        
        def chart_handler(channel: str, data):
            received_charts.append((channel, data))
        
        subscriber = RedisToolkit(
            channels=["analytics"],
            message_handler=chart_handler,
            options=RedisOptions(is_logger_info=False)
        )
        
        publisher = RedisToolkit(options=RedisOptions(is_logger_info=False))
        time.sleep(0.5)
        
        # 生成模擬圖表（簡單的彩色矩形）
        chart_img = np.ones((200, 300, 3), dtype=np.uint8) * 255  # 白色背景
        
        # 繪製一些彩色區塊代表圖表
        chart_img[50:100, 50:100] = [255, 0, 0]    # 紅色
        chart_img[50:100, 150:200] = [0, 255, 0]   # 綠色
        chart_img[50:100, 250:300] = [0, 0, 255]   # 藍色
        
        # 編碼圖表
        encoded_chart = encode_image(chart_img, format='png')
        
        # 發布圖表
        chart_message = {
            "type": "chart",
            "title": "銷售數據圖表",
            "chart_data": base64.b64encode(encoded_chart).decode('utf-8'),
            "data_points": [100, 150, 200],
            "timestamp": time.time()
        }
        
        publisher.publisher("analytics", chart_message)
        time.sleep(1)
        
        # 驗證接收
        assert len(received_charts) == 1
        channel, data = received_charts[0]
        assert data["type"] == "chart"
        assert data["title"] == "銷售數據圖表"
        
        # 解碼並驗證圖表
        received_chart_data = base64.b64decode(data["chart_data"])
        decoded_chart = decode_image(received_chart_data)
        assert decoded_chart.shape == chart_img.shape
        
        subscriber.cleanup()
        publisher.cleanup()
    
    def test_data_visualization_pipeline(self):
        """測試資料視覺化管道"""
        try:
            from redis_toolkit.converters import encode_image
        except ImportError:
            pytest.skip("圖片轉換器不可用")
        
        toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
        
        # 模擬資料處理管道
        raw_data = {"sales": [100, 120, 80, 150, 200], "dates": ["1月", "2月", "3月", "4月", "5月"]}
        
        # 存儲原始資料
        toolkit.setter("raw_sales_data", raw_data)
        
        # 生成圖表
        chart_img = np.zeros((150, 250, 3), dtype=np.uint8)
        # 簡單繪製條形圖
        for i, value in enumerate(raw_data["sales"]):
            height = int(value / max(raw_data["sales"]) * 100)
            x_start = 40 + i * 40
            chart_img[120-height:120, x_start:x_start+30] = [0, 255, 0]  # 綠色條
        
        # 編碼並存儲圖表（直接存儲 bytes，因為 RedisToolkit 的序列化器應該處理這個）
        encoded_chart = encode_image(chart_img, format='png')
        toolkit.setter("sales_chart", encoded_chart)
        
        # 建立分析報告（不直接包含 bytes 資料）
        report = {
            "title": "月度銷售報告",
            "data_key": "raw_sales_data",
            "chart_key": "sales_chart",
            "summary": {
                "total_sales": sum(raw_data["sales"]),
                "average": sum(raw_data["sales"]) / len(raw_data["sales"]),
                "max_month": "5月"
            },
            "generated_at": time.time(),
            "chart_info": {
                "format": "png",
                "size_bytes": len(encoded_chart),
                "dimensions": "250x150"
            }
        }
        
        toolkit.setter("sales_report", report)
        
        # 驗證完整管道
        retrieved_data = toolkit.getter("raw_sales_data")
        retrieved_chart = toolkit.getter("sales_chart")
        retrieved_report = toolkit.getter("sales_report")
        
        assert retrieved_data == raw_data
        assert retrieved_chart == encoded_chart
        assert retrieved_report["title"] == "月度銷售報告"
        assert retrieved_report["summary"]["total_sales"] == 650
        assert retrieved_report["chart_info"]["size_bytes"] == len(encoded_chart)
        
        toolkit.cleanup()


class TestConverterPerformance:
    """轉換器效能測試"""
    
    @pytest.mark.slow
    def test_large_image_performance(self):
        """測試大圖片處理效能"""
        try:
            from redis_toolkit.converters import encode_image, decode_image
        except ImportError:
            pytest.skip("圖片轉換器不可用")
        
        toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
        
        # 建立大圖片 (500x500)
        large_image = np.random.randint(0, 255, (500, 500, 3), dtype=np.uint8)
        
        start_time = time.time()
        
        # 編碼
        encoded = encode_image(large_image, format='jpg', quality=80)
        encode_time = time.time() - start_time
        
        # 存儲
        store_start = time.time()
        toolkit.setter("large_image", encoded)
        store_time = time.time() - store_start
        
        # 取得
        retrieve_start = time.time()
        retrieved = toolkit.getter("large_image")
        retrieve_time = time.time() - retrieve_start
        
        # 解碼
        decode_start = time.time()
        decoded = decode_image(retrieved)
        decode_time = time.time() - decode_start
        
        # 驗證結果
        assert decoded.shape == large_image.shape
        
        # 效能檢查（寬鬆的時間限制）
        assert encode_time < 5.0, f"編碼耗時過長: {encode_time:.2f}s"
        assert store_time < 2.0, f"存儲耗時過長: {store_time:.2f}s"
        assert retrieve_time < 2.0, f"取得耗時過長: {retrieve_time:.2f}s"
        assert decode_time < 5.0, f"解碼耗時過長: {decode_time:.2f}s"
        
        print(f"效能報告 - 編碼: {encode_time:.3f}s, 存儲: {store_time:.3f}s, "
              f"取得: {retrieve_time:.3f}s, 解碼: {decode_time:.3f}s")
        
        toolkit.cleanup()
    
    @pytest.mark.slow
    def test_batch_image_processing(self):
        """測試批次圖片處理效能"""
        try:
            from redis_toolkit.converters import encode_image, decode_image
        except ImportError:
            pytest.skip("圖片轉換器不可用")
        
        toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
        
        # 建立多張小圖片
        images = {}
        encode_start = time.time()
        
        for i in range(10):
            img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            encoded = encode_image(img, format='jpg', quality=70)
            images[f"batch_img_{i}"] = encoded
        
        encode_total = time.time() - encode_start
        
        # 批次存儲
        batch_store_start = time.time()
        toolkit.batch_set(images)
        batch_store_time = time.time() - batch_store_start
        
        # 批次取得
        batch_retrieve_start = time.time()
        keys = list(images.keys())
        retrieved = toolkit.batch_get(keys)
        batch_retrieve_time = time.time() - batch_retrieve_start
        
        # 驗證所有圖片
        decode_start = time.time()
        for key in keys:
            decoded = decode_image(retrieved[key])
            assert decoded.shape == (100, 100, 3)
        decode_total = time.time() - decode_start
        
        print(f"批次處理效能 - 編碼10張: {encode_total:.3f}s, "
              f"批次存儲: {batch_store_time:.3f}s, "
              f"批次取得: {batch_retrieve_time:.3f}s, "
              f"解碼10張: {decode_total:.3f}s")
        
        toolkit.cleanup()


class TestConverterErrorHandling:
    """轉換器錯誤處理測試"""
    
    def test_corrupted_image_data(self):
        """測試損壞的圖片資料處理"""
        try:
            from redis_toolkit.converters import decode_image
            from redis_toolkit.converters import ConversionError
        except ImportError:
            pytest.skip("圖片轉換器不可用")
        
        toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
        
        # 存儲損壞的圖片資料
        corrupted_data = b"this is not image data"
        toolkit.setter("corrupted_image", corrupted_data)
        
        # 取得資料
        retrieved = toolkit.getter("corrupted_image")
        assert retrieved == corrupted_data
        
        # 嘗試解碼應該失敗
        with pytest.raises(ConversionError):
            decode_image(retrieved)
        
        toolkit.cleanup()
    
    def test_invalid_format_handling(self):
        """測試無效格式處理"""
        try:
            from redis_toolkit.converters.image import ImageConverter
            from redis_toolkit.converters import ConversionError
        except ImportError:
            pytest.skip("圖片轉換器不可用")
        
        # 嘗試使用不支援的格式
        with pytest.raises((ConversionError, ValueError)):
            converter = ImageConverter(format='unsupported_format')
            test_image = np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)
            converter.encode(test_image)
    
    def test_redis_connection_failure_with_converters(self):
        """測試轉換器在 Redis 連線失敗時的行為"""
        try:
            from redis_toolkit.converters import encode_image
        except ImportError:
            pytest.skip("圖片轉換器不可用")
        
        from redis_toolkit import RedisConnectionConfig
        
        # 使用無效的 Redis 配置
        invalid_config = RedisConnectionConfig(host='invalid_host', port=9999)
        
        try:
            toolkit = RedisToolkit(
                config=invalid_config,
                options=RedisOptions(is_logger_info=False)
            )
            
            # 編碼圖片
            test_image = np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)
            encoded = encode_image(test_image)
            
            # 嘗試存儲應該失敗
            with pytest.raises(Exception):  # Redis 連線錯誤
                toolkit.setter("test_image", encoded)
            
        except Exception:
            # 連線建立就失敗也是預期的
            pass


class TestConverterCompatibility:
    """轉換器相容性測試"""
    
    def test_converter_with_different_numpy_dtypes(self):
        """測試轉換器對不同 numpy 資料類型的支援"""
        try:
            from redis_toolkit.converters import encode_image, decode_image
        except ImportError:
            pytest.skip("圖片轉換器不可用")
        
        toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
        
        # 測試不同的資料類型
        dtypes = [np.uint8, np.float32]
        
        for dtype in dtypes:
            if dtype == np.float32:
                # 浮點型資料範圍 [0, 1]
                test_image = np.random.rand(50, 50, 3).astype(dtype)
            else:
                # 整數型資料範圍 [0, 255]
                test_image = np.random.randint(0, 255, (50, 50, 3), dtype=dtype)
            
            # 編碼
            encoded = encode_image(test_image)
            
            # 存儲和取得
            key = f"image_{dtype.__name__}"
            toolkit.setter(key, encoded)
            retrieved = toolkit.getter(key)
            
            # 解碼
            decoded = decode_image(retrieved)
            
            # 驗證形狀
            assert decoded.shape == test_image.shape
        
        toolkit.cleanup()
    
    def test_cross_format_compatibility(self):
        """測試跨格式相容性"""
        try:
            from redis_toolkit.converters.image import ImageConverter
        except ImportError:
            pytest.skip("圖片轉換器不可用")
        
        toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
        
        test_image = np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)
        
        # 使用不同格式編碼
        formats = ['jpg', 'png']
        
        for fmt in formats:
            converter = ImageConverter(format=fmt)
            encoded = converter.encode(test_image)
            
            # 存儲
            toolkit.setter(f"cross_format_{fmt}", encoded)
            
            # 取得並用同格式解碼
            retrieved = toolkit.getter(f"cross_format_{fmt}")
            decoded = converter.decode(retrieved)
            
            assert decoded.shape == test_image.shape
        
        toolkit.cleanup()


class TestFileBasedConverters:
    """檔案型轉換器測試"""
    
    def test_video_file_integration(self):
        """測試視頻檔案與 Redis 整合"""
        try:
            from redis_toolkit.converters.video import VideoConverter
        except ImportError:
            pytest.skip("視頻轉換器不可用")
        
        toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
        converter = VideoConverter()
        
        # 建立假的視頻檔案
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            video_data = b"fake video content for testing" * 100  # 較大的假資料
            temp_file.write(video_data)
            temp_path = temp_file.name
        
        try:
            # 從檔案編碼
            encoded = converter.encode(temp_path)
            assert encoded == video_data
            
            # 存儲到 Redis
            toolkit.setter("test_video", encoded)
            
            # 取得並解碼
            retrieved = toolkit.getter("test_video")
            decoded = converter.decode(retrieved)
            
            assert decoded == video_data
            
            # 測試保存到新檔案
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as output_file:
                output_path = output_file.name
            
            try:
                converter.save_video_bytes(retrieved, output_path)
                
                # 驗證保存的檔案
                with open(output_path, 'rb') as f:
                    saved_content = f.read()
                assert saved_content == video_data
                
            finally:
                if os.path.exists(output_path):
                    os.remove(output_path)
        
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            toolkit.cleanup()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])