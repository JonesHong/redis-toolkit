#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Redis Toolkit 圖片傳輸範例

展示如何透過 Redis 傳輸和處理圖片
"""

import time
import base64
import os
from redis_toolkit import RedisToolkit, RedisOptions


def check_dependencies():
    """檢查必要的依賴"""
    try:
        import cv2
        import numpy as np
        from redis_toolkit.converters import encode_image, decode_image
        return True
    except ImportError as e:
        print(f"❌ 缺少必要的依賴: {e}")
        print("請安裝: pip install redis-toolkit[cv2]")
        return False


def basic_image_transfer():
    """基本圖片傳輸範例"""
    print("=== 基本圖片傳輸範例 ===\n")
    
    import cv2
    import numpy as np
    from redis_toolkit.converters import encode_image, decode_image
    
    toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
    
    try:
        # 創建測試圖片
        print("1. 創建測試圖片")
        # 創建一個彩色漸變圖片
        height, width = 300, 400
        image = np.zeros((height, width, 3), dtype=np.uint8)
        
        # 添加顏色漸變
        for y in range(height):
            for x in range(width):
                image[y, x] = [
                    int(255 * x / width),      # R: 從左到右漸變
                    int(255 * y / height),      # G: 從上到下漸變
                    128                         # B: 固定值
                ]
        
        # 添加文字
        cv2.putText(image, "Redis Toolkit", (50, 150), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
        
        print(f"   圖片尺寸: {width}x{height}")
        print(f"   圖片大小: {image.nbytes} bytes")
        
        # 編碼圖片
        print("\n2. 編碼圖片")
        encoded_jpg = encode_image(image, format='jpg', quality=90)
        encoded_png = encode_image(image, format='png')
        
        print(f"   JPEG 大小: {len(encoded_jpg)} bytes")
        print(f"   PNG 大小: {len(encoded_png)} bytes")
        print(f"   壓縮率: JPEG 是原始大小的 {len(encoded_jpg)/image.nbytes*100:.1f}%")
        
        # 存儲到 Redis
        print("\n3. 存儲到 Redis")
        toolkit.setter("image:test:jpg", encoded_jpg)
        toolkit.setter("image:test:png", encoded_png)
        print("   ✅ 圖片已存儲")
        
        # 從 Redis 讀取
        print("\n4. 從 Redis 讀取並解碼")
        retrieved_jpg = toolkit.getter("image:test:jpg")
        retrieved_png = toolkit.getter("image:test:png")
        
        decoded_jpg = decode_image(retrieved_jpg)
        decoded_png = decode_image(retrieved_png)
        
        print(f"   JPEG 解碼後尺寸: {decoded_jpg.shape}")
        print(f"   PNG 解碼後尺寸: {decoded_png.shape}")
        
        # 驗證圖片完整性
        # 注意：JPEG 是有損壓縮，所以不會完全相同
        png_identical = np.array_equal(image, decoded_png)
        print(f"   PNG 完整性: {'✅ 完全相同' if png_identical else '❌ 有差異'}")
        
        # 清理
        toolkit.deleter("image:test:jpg")
        toolkit.deleter("image:test:png")
        
    finally:
        toolkit.cleanup()


def image_processing_pipeline():
    """圖片處理管線範例"""
    print("\n=== 圖片處理管線範例 ===\n")
    
    import cv2
    import numpy as np
    from redis_toolkit.converters import encode_image, decode_image, get_converter
    
    toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
    
    try:
        # 創建原始圖片
        print("1. 創建原始圖片")
        original = np.ones((400, 600, 3), dtype=np.uint8) * 255  # 白色背景
        
        # 畫一些圖形
        cv2.rectangle(original, (50, 50), (250, 150), (0, 0, 255), -1)      # 紅色矩形
        cv2.circle(original, (400, 200), 80, (0, 255, 0), -1)              # 綠色圓形
        cv2.ellipse(original, (300, 300), (100, 50), 45, 0, 360, (255, 0, 0), -1)  # 藍色橢圓
        
        # 存儲原始圖片
        encoded_original = encode_image(original, format='png')
        toolkit.setter("pipeline:original", encoded_original)
        print(f"   原始圖片大小: {len(encoded_original)} bytes")
        
        # 處理步驟 1：調整大小
        print("\n2. 處理步驟 1：調整大小")
        converter = get_converter('image')
        resized = converter.resize(original, width=300, height=200)
        encoded_resized = encode_image(resized, format='jpg', quality=85)
        toolkit.setter("pipeline:resized", encoded_resized)
        print(f"   調整後尺寸: {resized.shape}")
        print(f"   儲存大小: {len(encoded_resized)} bytes")
        
        # 處理步驟 2：灰度轉換
        print("\n3. 處理步驟 2：灰度轉換")
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        # 灰度圖需要轉回 BGR 以便統一處理
        gray_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        encoded_gray = encode_image(gray_bgr, format='jpg', quality=85)
        toolkit.setter("pipeline:gray", encoded_gray)
        print(f"   灰度圖片大小: {len(encoded_gray)} bytes")
        
        # 處理步驟 3：邊緣檢測
        print("\n4. 處理步驟 3：邊緣檢測")
        edges = cv2.Canny(gray, 100, 200)
        edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        encoded_edges = encode_image(edges_bgr, format='png')
        toolkit.setter("pipeline:edges", encoded_edges)
        print(f"   邊緣圖片大小: {len(encoded_edges)} bytes")
        
        # 讀取所有處理結果
        print("\n5. 讀取處理管線的所有結果")
        pipeline_keys = [
            "pipeline:original",
            "pipeline:resized", 
            "pipeline:gray",
            "pipeline:edges"
        ]
        
        results = toolkit.batch_get(pipeline_keys)
        for key in pipeline_keys:
            if results[key]:
                stage = key.split(":")[-1]
                print(f"   {stage}: ✅ 成功讀取")
        
        # 獲取圖片資訊
        print("\n6. 圖片資訊")
        for key, data in results.items():
            if data:
                info = converter.get_info(data)
                stage = key.split(":")[-1]
                print(f"   {stage}: {info}")
        
        # 清理
        for key in pipeline_keys:
            toolkit.deleter(key)
            
    finally:
        toolkit.cleanup()


def image_pubsub_transfer():
    """透過發布訂閱傳輸圖片"""
    print("\n=== 透過發布訂閱傳輸圖片 ===\n")
    
    import cv2
    import numpy as np
    from redis_toolkit.converters import encode_image, decode_image
    
    received_images = []
    
    def image_handler(channel: str, data):
        """處理接收到的圖片"""
        if isinstance(data, dict) and "image_data" in data:
            # 解碼 base64
            image_bytes = base64.b64decode(data["image_data"])
            image = decode_image(image_bytes)
            
            received_images.append({
                "channel": channel,
                "sender": data.get("sender", "Unknown"),
                "timestamp": data.get("timestamp", 0),
                "image": image,
                "size": len(image_bytes)
            })
            
            print(f"📸 收到圖片")
            print(f"   頻道: {channel}")
            print(f"   發送者: {data.get('sender', 'Unknown')}")
            print(f"   尺寸: {image.shape}")
            print(f"   大小: {len(image_bytes)} bytes")
            print()
    
    # 創建訂閱者
    subscriber = RedisToolkit(
        channels=["images:upload", "images:processed"],
        message_handler=image_handler,
        options=RedisOptions(is_logger_info=False)
    )
    
    # 創建發布者
    publisher = RedisToolkit(options=RedisOptions(is_logger_info=False))
    
    time.sleep(0.5)
    
    try:
        # 創建並發送圖片
        print("1. 創建並發送測試圖片\n")
        
        # 圖片 1：漸變色
        img1 = np.zeros((200, 300, 3), dtype=np.uint8)
        for i in range(200):
            img1[i, :] = [i, 128, 255-i]
        
        encoded1 = encode_image(img1, format='jpg', quality=80)
        encoded1_b64 = base64.b64encode(encoded1).decode('utf-8')
        
        publisher.publisher("images:upload", {
            "sender": "User1",
            "image_data": encoded1_b64,
            "timestamp": time.time(),
            "description": "漸變色測試圖"
        })
        
        time.sleep(0.5)
        
        # 圖片 2：隨機噪點
        img2 = np.random.randint(0, 255, (150, 150, 3), dtype=np.uint8)
        
        encoded2 = encode_image(img2, format='png')
        encoded2_b64 = base64.b64encode(encoded2).decode('utf-8')
        
        publisher.publisher("images:processed", {
            "sender": "ImageProcessor",
            "image_data": encoded2_b64,
            "timestamp": time.time(),
            "description": "隨機噪點圖"
        })
        
        time.sleep(0.5)
        
        # 圖片 3：幾何圖形
        img3 = np.ones((250, 250, 3), dtype=np.uint8) * 255
        cv2.circle(img3, (125, 125), 50, (255, 0, 0), -1)
        cv2.rectangle(img3, (50, 50), (200, 200), (0, 255, 0), 3)
        
        encoded3 = encode_image(img3, format='jpg', quality=90)
        encoded3_b64 = base64.b64encode(encoded3).decode('utf-8')
        
        publisher.publisher("images:upload", {
            "sender": "User2",
            "image_data": encoded3_b64,
            "timestamp": time.time(),
            "description": "幾何圖形"
        })
        
        time.sleep(1)
        
        # 統計
        print(f"\n2. 傳輸統計")
        print(f"   發送圖片: 3 張")
        print(f"   接收圖片: {len(received_images)} 張")
        
        if received_images:
            total_size = sum(img["size"] for img in received_images)
            avg_size = total_size / len(received_images)
            print(f"   總傳輸量: {total_size} bytes")
            print(f"   平均大小: {avg_size:.0f} bytes")
        
    finally:
        subscriber.cleanup()
        publisher.cleanup()


def image_caching_example():
    """圖片快取範例"""
    print("\n=== 圖片快取範例 ===\n")
    
    import cv2
    import numpy as np
    from redis_toolkit.converters import encode_image, decode_image
    
    toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
    
    try:
        # 模擬圖片快取系統
        print("1. 建立圖片快取系統")
        
        # 生成一些測試圖片作為"原始圖片"
        test_images = {}
        for i in range(3):
            img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            cv2.putText(img, f"IMG{i+1}", (20, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            test_images[f"img_{i+1}"] = img
        
        # 快取函數
        def get_image_with_cache(image_id: str, format: str = 'jpg') -> np.ndarray:
            """獲取圖片，優先從快取讀取"""
            cache_key = f"cache:image:{image_id}:{format}"
            
            # 檢查快取
            cached = toolkit.getter(cache_key)
            if cached:
                print(f"   ✅ 快取命中: {image_id}")
                return decode_image(cached)
            
            # 快取未命中，獲取原始圖片
            print(f"   ❌ 快取未命中: {image_id}")
            if image_id in test_images:
                original = test_images[image_id]
                
                # 編碼並快取
                encoded = encode_image(original, format=format, quality=85)
                toolkit.setter(cache_key, encoded)
                
                # 設定過期時間（300秒）
                toolkit.client.expire(cache_key, 300)
                
                return original
            else:
                return None
        
        # 測試快取
        print("\n2. 測試快取系統")
        
        # 第一次請求（快取未命中）
        print("\n第一輪請求：")
        for img_id in ["img_1", "img_2", "img_3"]:
            img = get_image_with_cache(img_id)
            if img is not None:
                print(f"     取得圖片 {img_id}, 尺寸: {img.shape}")
        
        # 第二次請求（快取命中）
        print("\n第二輪請求：")
        for img_id in ["img_1", "img_2", "img_3"]:
            img = get_image_with_cache(img_id)
            if img is not None:
                print(f"     取得圖片 {img_id}, 尺寸: {img.shape}")
        
        # 測試不同格式
        print("\n3. 測試不同格式快取")
        img = get_image_with_cache("img_1", format="png")
        print(f"   PNG 格式: {img.shape if img is not None else 'None'}")
        
        # 檢查快取狀態
        print("\n4. 快取狀態")
        cache_pattern = "cache:image:*"
        cache_keys = toolkit.client.keys(cache_pattern)
        print(f"   快取項目數: {len(cache_keys)}")
        
        for key in cache_keys:
            ttl = toolkit.client.ttl(key)
            key_str = key.decode() if isinstance(key, bytes) else key
            print(f"   {key_str}: TTL {ttl} 秒")
        
        # 清理快取
        print("\n5. 清理快取")
        for key in cache_keys:
            toolkit.client.delete(key)
        print("   ✅ 快取已清理")
        
    finally:
        toolkit.cleanup()


def main():
    """主程式"""
    print("Redis Toolkit 圖片傳輸範例")
    print("=" * 60)
    print()
    
    # 檢查依賴
    if not check_dependencies():
        print("\n請先安裝必要的依賴後再執行此範例")
        return
    
    try:
        # 基本傳輸
        basic_image_transfer()
        print("\n" + "=" * 60)
        
        # 處理管線
        image_processing_pipeline()
        print("\n" + "=" * 60)
        
        # 發布訂閱傳輸
        image_pubsub_transfer()
        print("\n" + "=" * 60)
        
        # 圖片快取
        image_caching_example()
        
        print("\n" + "=" * 60)
        print("✅ 所有圖片傳輸範例執行完成！")
        print("\n💡 重點總結：")
        print("  - 支援 JPEG/PNG 格式，可調整品質")
        print("  - 自動處理 numpy 陣列序列化")
        print("  - 可透過發布訂閱傳輸圖片")
        print("  - 支援圖片處理管線")
        print("  - 可建立高效的圖片快取系統")
        
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()