#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis Toolkit 整合媒體範例
展示基本存儲、轉換器功能和 pub/sub 即時分享
程式會持續運行直到所有預覽檔案都被關閉
"""

import os
import time
import tempfile
import subprocess
import threading
import signal
import sys
from redis_toolkit import RedisToolkit, RedisOptions

# 測試檔案路徑
IMAGE_PATH = 'examples/real-world/media_processing/data/BigBuckBunny.jpg'
AUDIO_PATH = 'examples/real-world/media_processing/data/RobertoPrado_CourtScheme.mp3'
VIDEO_PATH = 'examples/real-world/media_processing/data/BigBuckBunny_320x180.mp4'

# 全域變數記錄所有暫存檔案
ALL_TEMP_FILES = []
CLEANUP_LOCK = threading.Lock()

def add_temp_file(file_path):
    """記錄暫存檔案"""
    with CLEANUP_LOCK:
        ALL_TEMP_FILES.append(file_path)
        print(f"📁 記錄暫存檔: {os.path.basename(file_path)}")

def check_files():
    """檢查測試檔案是否存在"""
    files = [
        ('圖片', IMAGE_PATH),
        ('音頻', AUDIO_PATH),
        ('視頻', VIDEO_PATH)
    ]
    
    existing_files = []
    for name, path in files:
        if os.path.exists(path):
            existing_files.append((name, path))
            print(f"✅ {name}: {path}")
        else:
            print(f"⚠️ {name}: {path} (未找到)")
    
    return existing_files

def open_file_preview(file_path):
    """開啟檔案預覽"""
    try:
        print(f"🎥 正在開啟預覽: {os.path.basename(file_path)}")
        
        if os.name == 'nt':  # Windows
            os.system(f'start "" "{file_path}"')
        else:  # Unix/Linux/Mac
            os.system(f'xdg-open "{file_path}"')
        
        print("📖 檔案已開啟，請在外部程式中查看")
        
    except Exception as e:
        print(f"⚠️ 無法開啟預覽: {e}")

def cleanup_temp_files():
    """清理暫存檔案，回傳是否全部清理成功"""
    with CLEANUP_LOCK:
        remaining_files = []
        cleaned_count = 0
        
        for file_path in ALL_TEMP_FILES:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
                    print(f"🗑️ 已刪除: {os.path.basename(file_path)}")
                    cleaned_count += 1
                else:
                    # 檔案已不存在（可能已被刪除）
                    cleaned_count += 1
            except (PermissionError, OSError) as e:
                remaining_files.append(file_path)
                print(f"⏳ 無法刪除 {os.path.basename(file_path)}: 檔案可能正在使用中")
        
        ALL_TEMP_FILES.clear()
        ALL_TEMP_FILES.extend(remaining_files)
        
        if remaining_files:
            print(f"📋 仍有 {len(remaining_files)} 個檔案無法刪除，繼續等待...")
            return False
        else:
            print(f"✅ 所有暫存檔案已清理完成 (共 {cleaned_count} 個)")
            return True

def wait_for_cleanup():
    """等待所有暫存檔案被清理"""
    print("\n" + "="*50)
    print("⏰ 等待所有預覽檔案關閉...")
    print("💡 請關閉所有已開啟的預覽視窗，程式將在檔案關閉後自動結束")
    print("🔴 或按 Ctrl+C 強制退出")
    print("="*50)
    
    while True:
        try:
            time.sleep(2)  # 每2秒檢查一次
            
            with CLEANUP_LOCK:
                if not ALL_TEMP_FILES:
                    print("✅ 沒有暫存檔案需要清理")
                    break
            
            # 嘗試清理
            if cleanup_temp_files():
                break
                
        except KeyboardInterrupt:
            print("\n⚠️ 用戶中斷，強制清理...")
            force_cleanup()
            break
        except Exception as e:
            print(f"❌ 清理過程中發生錯誤: {e}")
            time.sleep(1)

def force_cleanup():
    """強制清理所有暫存檔案"""
    with CLEANUP_LOCK:
        for file_path in ALL_TEMP_FILES:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
                    print(f"🗑️ 強制刪除: {os.path.basename(file_path)}")
            except Exception as e:
                print(f"⚠️ 無法刪除 {os.path.basename(file_path)}: {e}")
        ALL_TEMP_FILES.clear()

def setup_signal_handler():
    """設定信號處理器"""
    def signal_handler(signum, frame):
        print(f"\n⚠️ 收到退出信號 ({signum})，開始清理...")
        force_cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)

def test_basic_storage():
    """測試 1: 基本媒體存儲"""
    print("\n" + "="*50)
    print("🧪 測試 1: 基本媒體存儲")
    print("="*50)
    
    toolkit = RedisToolkit(options=RedisOptions(
        max_value_size=100 * 1024 * 1024  # 100MB
    ))
    
    try:
        existing_files = check_files()
        
        # 存儲檔案到 Redis
        print("\n💾 存儲媒體檔案到 Redis...")
        for name, file_path in existing_files:
            with open(file_path, 'rb') as f:
                file_bytes = f.read()
            
            key = f'basic:{name.lower()}'
            toolkit.setter(key, file_bytes)
            print(f"  {name}: {len(file_bytes):,} 位元組 → Redis[{key}]")
        
        # 從 Redis 取得並預覽
        print("\n📺 從 Redis 取得並預覽...")
        for name, _ in existing_files:
            key = f'basic:{name.lower()}'
            file_bytes = toolkit.getter(key)
            
            if file_bytes:
                # 創建暫存檔案
                suffix = {
                    '圖片': '.jpg',
                    '音頻': '.mp3', 
                    '視頻': '.mp4'
                }[name]
                
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                temp_file.write(file_bytes)
                temp_file.close()
                add_temp_file(temp_file.name)  # 記錄暫存檔案
                
                print(f"  {name}: {len(file_bytes):,} 位元組 → {os.path.basename(temp_file.name)}")
                
                # 開啟預覽
                open_file_preview(temp_file.name)
        
        print("✅ 基本存儲測試完成")
        
    finally:
        toolkit.cleanup()

def test_converters():
    """測試 2: 轉換器功能"""
    print("\n" + "="*50)
    print("🧪 測試 2: 轉換器功能")
    print("="*50)
    
    try:
        from redis_toolkit.converters import list_converters, get_converter
        from redis_toolkit.converters import encode_image, decode_image
        from redis_toolkit.converters import encode_audio, decode_audio
        from redis_toolkit.converters import encode_video, decode_video
        
        print(f"可用轉換器: {list_converters()}")
        
        toolkit = RedisToolkit(options=RedisOptions(
            max_value_size=100 * 1024 * 1024  # 100MB
        ))
        
        # 圖片轉換測試
        if os.path.exists(IMAGE_PATH):
            print(f"\n🖼️ 圖片轉換測試...")
            import cv2
            
            # 讀取並編碼
            img = cv2.imread(IMAGE_PATH)
            print(f"  原始圖片: {img.shape}")
            
            # 測試不同品質
            qualities = [50, 80, 95]
            for quality in qualities:
                img_bytes = encode_image(img, format='jpg', quality=quality)
                toolkit.setter(f'converted:image:q{quality}', img_bytes)
                
                decoded_img = decode_image(img_bytes)
                print(f"  品質 {quality}: {len(img_bytes):,} 位元組, 形狀 {decoded_img.shape}")
        
        # 音頻轉換測試
        if os.path.exists(AUDIO_PATH):
            print(f"\n🎵 音頻轉換測試...")
            
            audio_converter = get_converter('audio')
            try:
                # 取得檔案資訊
                info = audio_converter.get_file_info(AUDIO_PATH)
                print(f"  音頻資訊: {info['duration_seconds']:.1f}秒, {info['sample_rate']}Hz")
                
                # 編碼檔案
                audio_bytes = audio_converter.encode_from_file(AUDIO_PATH)
                toolkit.setter('converted:audio:file', audio_bytes)
                print(f"  檔案編碼: {len(audio_bytes):,} 位元組")
                
            except Exception as e:
                print(f"  音頻轉換失敗: {e}")
        
        # 視頻轉換測試  
        if os.path.exists(VIDEO_PATH):
            print(f"\n🎬 視頻轉換測試...")
            
            video_converter = get_converter('video')
            try:
                # 取得視頻資訊
                info = video_converter.get_video_info(VIDEO_PATH)
                print(f"  視頻資訊: {info['resolution']}, {info['duration_seconds']:.1f}秒")
                
                # 編碼檔案
                video_bytes = encode_video(VIDEO_PATH)
                toolkit.setter('converted:video:file', video_bytes)
                print(f"  檔案編碼: {len(video_bytes):,} 位元組")
                
            except Exception as e:
                print(f"  視頻轉換失敗: {e}")
        
        print("✅ 轉換器測試完成")
        toolkit.cleanup()
        
    except ImportError as e:
        print(f"⚠️ 轉換器不可用: {e}")

def test_pubsub_sharing():
    """測試 3: Pub/Sub 即時媒體分享"""
    print("\n" + "="*50)
    print("🧪 測試 3: Pub/Sub 即時媒體分享")
    print("="*50)
    
    try:
        from redis_toolkit.converters import encode_image, decode_image
        
        received_messages = []
        
        def media_handler(channel: str, data):
            """處理媒體訊息"""
            try:
                if isinstance(data, dict) and 'type' in data:
                    msg_type = data['type']
                    user = data.get('user', 'Unknown')
                    
                    print(f"📨 收到 {msg_type} 訊息 from {user}")
                    
                    if msg_type == 'image' and 'image_data' in data:
                        # 解碼 base64 圖片資料
                        import base64
                        try:
                            # 如果是 base64 編碼的字串，先解碼
                            if isinstance(data['image_data'], str):
                                img_bytes = base64.b64decode(data['image_data'])
                            else:
                                img_bytes = data['image_data']
                            
                            # 解碼圖片
                            img_array = decode_image(img_bytes)
                            print(f"   圖片尺寸: {img_array.shape}")
                            
                            # 保存並預覽
                            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                            temp_file.write(img_bytes)
                            temp_file.close()
                            add_temp_file(temp_file.name)  # 記錄暫存檔案
                            
                            open_file_preview(temp_file.name)
                            
                        except Exception as e:
                            print(f"   圖片處理失敗: {e}")
                            
                    elif msg_type == 'text':
                        print(f"   訊息: {data.get('message', '')}")
                    
                    received_messages.append(data)
                    
            except Exception as e:
                print(f"❌ 訊息處理失敗: {e}")
        
        # 建立發布訂閱
        subscriber = RedisToolkit(
            channels=["media_sharing"],
            message_handler=media_handler,
            options=RedisOptions(
                max_value_size=100 * 1024 * 1024  # 100MB
            )
        )
        
        publisher = RedisToolkit(options=RedisOptions(
            max_value_size=100 * 1024 * 1024  # 100MB
        ))
        
        time.sleep(0.5)  # 等待訂閱者啟動
        
        print("📡 開始媒體分享模擬...")
        
        # 發布文字訊息
        text_msg = {
            'type': 'text',
            'user': 'Alice',
            'message': '大家好！我要分享一張圖片',
            'timestamp': time.time()
        }
        publisher.publisher("media_sharing", text_msg)
        time.sleep(1)
        
        # 發布圖片訊息（如果圖片存在）
        if os.path.exists(IMAGE_PATH):
            import cv2
            import base64
            
            # 讀取並縮小圖片（模擬即時分享）
            img = cv2.imread(IMAGE_PATH)
            small_img = cv2.resize(img, (400, 300))
            
            # 編碼圖片
            img_bytes = encode_image(small_img, format='jpg', quality=70)
            
            # 轉換為 base64 字串以便 JSON 序列化
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
            
            img_msg = {
                'type': 'image',
                'user': 'Alice', 
                'image_data': img_base64,  # 使用 base64 字串
                'caption': '看看我的照片！',
                'timestamp': time.time()
            }
            
            publisher.publisher("media_sharing", img_msg)
            time.sleep(2)
        
        # 更多用戶加入
        text_msg2 = {
            'type': 'text',
            'user': 'Bob',
            'message': '很棒的照片！',
            'timestamp': time.time()
        }
        publisher.publisher("media_sharing", text_msg2)
        time.sleep(1)
        
        print(f"📊 總共收到 {len(received_messages)} 條訊息")
        print("✅ Pub/Sub 分享測試完成")
        
        # 清理
        subscriber.cleanup()
        publisher.cleanup()
        
    except ImportError as e:
        print(f"⚠️ Pub/Sub 測試需要轉換器: {e}")

def test_realtime_analytics():
    """測試 4: 即時圖表分享"""
    print("\n" + "="*50)
    print("🧪 測試 4: 即時圖表分享")
    print("="*50)
    
    try:
        from redis_toolkit.converters import encode_image, decode_image
        import cv2
        import numpy as np
        
        received_charts = []
        
        def chart_handler(channel: str, data):
            """處理圖表訊息"""
            try:
                if isinstance(data, dict) and data.get('type') == 'chart':
                    print(f"📈 收到圖表: {data.get('title', 'Unknown')}")
                    
                    # 解碼 base64 圖表資料
                    import base64
                    try:
                        if isinstance(data['chart_data'], str):
                            chart_bytes = base64.b64decode(data['chart_data'])
                        else:
                            chart_bytes = data['chart_data']
                        
                        # 解碼圖表
                        chart_img = decode_image(chart_bytes)
                        print(f"   圖表尺寸: {chart_img.shape}")
                        
                        # 保存並預覽
                        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                        temp_file.write(chart_bytes)
                        temp_file.close()
                        add_temp_file(temp_file.name)  # 記錄暫存檔案
                        
                        open_file_preview(temp_file.name)
                        
                        received_charts.append(data)
                        
                    except Exception as e:
                        print(f"   圖表解碼失敗: {e}")
                    
            except Exception as e:
                print(f"❌ 圖表處理失敗: {e}")
        
        # 建立圖表訂閱
        subscriber = RedisToolkit(
            channels=["analytics"],
            message_handler=chart_handler,
            options=RedisOptions(
                max_value_size=100 * 1024 * 1024  # 100MB
            )
        )
        
        publisher = RedisToolkit(options=RedisOptions(
            max_value_size=100 * 1024 * 1024  # 100MB
        ))
        time.sleep(0.5)
        
        print("📊 生成並分享即時圖表...")
        
        # 生成模擬圖表
        chart_img = np.ones((300, 400, 3), dtype=np.uint8) * 255  # 白色背景
        
        # 繪製簡單的條狀圖
        data_values = [50, 80, 120, 90, 150]
        colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255), 
                 (255, 255, 100), (255, 100, 255)]
        
        bar_width = 60
        max_height = 200
        
        for i, (value, color) in enumerate(zip(data_values, colors)):
            x = 50 + i * 70
            height = int(value / max(data_values) * max_height)
            y = 250 - height
            
            cv2.rectangle(chart_img, (x, y), (x + bar_width, 250), color, -1)
            cv2.putText(chart_img, str(value), (x + 10, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        # 添加標題
        cv2.putText(chart_img, 'Sales Data', (150, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
        # 編碼圖表
        chart_bytes = encode_image(chart_img, format='png')
        
        # 轉換為 base64 以便 JSON 序列化
        import base64
        chart_base64 = base64.b64encode(chart_bytes).decode('utf-8')
        
        # 發布圖表
        chart_msg = {
            'type': 'chart',
            'title': '銷售數據圖表',
            'chart_data': chart_base64,  # 使用 base64 字串
            'data_points': data_values,
            'timestamp': time.time()
        }
        
        publisher.publisher("analytics", chart_msg)
        time.sleep(2)
        
        print(f"📊 總共收到 {len(received_charts)} 個圖表")
        print("✅ 即時圖表測試完成")
        
        # 清理
        subscriber.cleanup()
        publisher.cleanup()
        
    except ImportError as e:
        print(f"⚠️ 圖表測試需要 opencv: {e}")

def main():
    """執行所有測試"""
    print("🚀 Redis Toolkit 整合媒體測試")
    print("支援檔案:")
    print(f"  📷 圖片: {IMAGE_PATH}")
    print(f"  🎵 音頻: {AUDIO_PATH}")
    print(f"  🎬 視頻: {VIDEO_PATH}")
    
    # 設定信號處理器
    setup_signal_handler()
    
    try:
        # 執行所有測試
        test_basic_storage()      # 基本存儲
        test_converters()         # 轉換器功能  
        test_pubsub_sharing()     # Pub/Sub 媒體分享
        test_realtime_analytics() # 即時圖表
        
        print("\n" + "="*50)
        print("🎉 所有測試完成！")
        
        print("\n💡 測試內容:")
        print("  ✅ 基本媒體存儲與預覽")
        print("  ✅ 轉換器編解碼功能")
        print("  ✅ Pub/Sub 即時媒體分享")
        print("  ✅ 即時圖表生成與分享")
        
        print("\n📦 安裝提示:")
        print("  pip install redis-toolkit[all]")
        
        # 等待所有預覽檔案關閉
        wait_for_cleanup()
        
    except KeyboardInterrupt:
        print("\n⚠️ 測試被用戶中斷")
        force_cleanup()
    except Exception as e:
        print(f"\n❌ 測試執行出錯: {e}")
        import traceback
        traceback.print_exc()
        force_cleanup()
    
    print("\n🎊 程式結束，所有暫存檔案已清理完成！")

if __name__ == "__main__":
    main()