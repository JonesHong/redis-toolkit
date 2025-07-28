#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Redis Toolkit 音訊串流範例

展示如何透過 Redis 處理音訊資料
"""

import time
import base64
import threading
from redis_toolkit import RedisToolkit, RedisOptions


def check_dependencies():
    """檢查必要的依賴"""
    try:
        import numpy as np
        from scipy import signal
        from redis_toolkit.converters import encode_audio, decode_audio
        return True
    except ImportError as e:
        print(f"❌ 缺少必要的依賴: {e}")
        print("請安裝: pip install redis-toolkit[audio]")
        return False


def basic_audio_transfer():
    """基本音訊傳輸範例"""
    print("=== 基本音訊傳輸範例 ===\n")
    
    import numpy as np
    from redis_toolkit.converters import encode_audio, decode_audio
    
    toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
    
    try:
        # 生成測試音訊
        print("1. 生成測試音訊訊號")
        sample_rate = 44100  # CD 品質
        duration = 2.0       # 2 秒
        
        # 生成 A4 音符 (440 Hz)
        t = np.linspace(0, duration, int(sample_rate * duration))
        frequency = 440.0
        audio_data = np.sin(2 * np.pi * frequency * t)
        
        # 添加泛音使聲音更豐富
        audio_data += 0.3 * np.sin(2 * np.pi * frequency * 2 * t)  # 第二泛音
        audio_data += 0.2 * np.sin(2 * np.pi * frequency * 3 * t)  # 第三泛音
        
        # 正規化
        audio_data = audio_data / np.max(np.abs(audio_data))
        
        print(f"   取樣率: {sample_rate} Hz")
        print(f"   時長: {duration} 秒")
        print(f"   樣本數: {len(audio_data)}")
        print(f"   資料大小: {audio_data.nbytes} bytes")
        
        # 編碼音訊
        print("\n2. 編碼音訊資料")
        encoded_wav = encode_audio(audio_data, sample_rate=sample_rate)
        print(f"   WAV 格式大小: {len(encoded_wav)} bytes")
        print(f"   壓縮率: {len(encoded_wav)/audio_data.nbytes*100:.1f}%")
        
        # 存儲到 Redis
        print("\n3. 存儲到 Redis")
        toolkit.setter("audio:test:a4", encoded_wav)
        print("   ✅ 音訊已存儲")
        
        # 從 Redis 讀取
        print("\n4. 從 Redis 讀取並解碼")
        retrieved = toolkit.getter("audio:test:a4")
        decoded_rate, decoded_audio = decode_audio(retrieved)
        
        print(f"   解碼取樣率: {decoded_rate} Hz")
        print(f"   解碼樣本數: {len(decoded_audio)}")
        
        # 驗證資料完整性
        # 由於音訊編解碼可能有些微差異，使用近似比較
        is_similar = np.allclose(audio_data, decoded_audio, rtol=1e-3)
        print(f"   資料完整性: {'✅ 相似' if is_similar else '❌ 差異較大'}")
        
        # 清理
        toolkit.deleter("audio:test:a4")
        
    finally:
        toolkit.cleanup()


def audio_streaming_simulation():
    """模擬音訊串流"""
    print("\n=== 音訊串流模擬 ===\n")
    
    import numpy as np
    from redis_toolkit.converters import encode_audio, decode_audio
    
    # 串流參數
    sample_rate = 22050  # 較低的取樣率以減少資料量
    chunk_duration = 0.1  # 每個區塊 0.1 秒
    chunk_samples = int(sample_rate * chunk_duration)
    
    stream_active = True
    received_chunks = []
    
    def audio_consumer(channel: str, data):
        """音訊串流消費者"""
        if isinstance(data, dict) and "audio_chunk" in data:
            # 解碼 base64
            chunk_bytes = base64.b64decode(data["audio_chunk"])
            rate, chunk_audio = decode_audio(chunk_bytes)
            
            received_chunks.append({
                "sequence": data.get("sequence", 0),
                "audio": chunk_audio,
                "timestamp": data.get("timestamp", 0)
            })
            
            print(f"🎵 收到音訊區塊 #{data.get('sequence', 0)}")
            print(f"   大小: {len(chunk_bytes)} bytes")
            print(f"   樣本數: {len(chunk_audio)}")
    
    # 創建訂閱者
    subscriber = RedisToolkit(
        channels=["audio:stream"],
        message_handler=audio_consumer,
        options=RedisOptions(is_logger_info=False)
    )
    
    # 創建發布者
    publisher = RedisToolkit(options=RedisOptions(is_logger_info=False))
    
    time.sleep(0.5)
    
    try:
        print("開始音訊串流模擬...\n")
        
        # 生成並串流音訊
        sequence = 0
        total_duration = 2.0  # 總共串流 2 秒
        total_chunks = int(total_duration / chunk_duration)
        
        for i in range(total_chunks):
            # 生成音訊區塊（變頻正弦波）
            t = np.linspace(i * chunk_duration, (i + 1) * chunk_duration, chunk_samples)
            
            # 頻率從 440Hz 漸變到 880Hz
            freq = 440 + (440 * i / total_chunks)
            chunk_data = np.sin(2 * np.pi * freq * t) * 0.5
            
            # 編碼區塊
            encoded_chunk = encode_audio(chunk_data, sample_rate=sample_rate)
            encoded_b64 = base64.b64encode(encoded_chunk).decode('utf-8')
            
            # 發布區塊
            publisher.publisher("audio:stream", {
                "sequence": sequence,
                "audio_chunk": encoded_b64,
                "timestamp": time.time(),
                "sample_rate": sample_rate
            })
            
            sequence += 1
            time.sleep(chunk_duration)  # 模擬實時串流
        
        # 等待所有區塊接收完成
        time.sleep(0.5)
        
        print(f"\n串流統計:")
        print(f"  發送區塊: {total_chunks}")
        print(f"  接收區塊: {len(received_chunks)}")
        print(f"  接收率: {len(received_chunks)/total_chunks*100:.0f}%")
        
        # 重組音訊
        if received_chunks:
            print("\n重組音訊...")
            # 按序號排序
            received_chunks.sort(key=lambda x: x["sequence"])
            
            # 合併音訊
            full_audio = np.concatenate([chunk["audio"] for chunk in received_chunks])
            print(f"  重組後總樣本數: {len(full_audio)}")
            print(f"  重組後時長: {len(full_audio)/sample_rate:.2f} 秒")
        
    finally:
        subscriber.cleanup()
        publisher.cleanup()


def audio_effects_pipeline():
    """音訊效果處理管線"""
    print("\n=== 音訊效果處理管線 ===\n")
    
    import numpy as np
    from scipy import signal
    from redis_toolkit.converters import encode_audio, decode_audio, get_converter
    
    toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
    converter = get_converter('audio')
    
    try:
        # 生成原始音訊
        print("1. 生成原始音訊")
        sample_rate = 44100
        duration = 1.0
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # 複合音訊：基頻 + 和聲
        original = np.sin(2 * np.pi * 440 * t)  # A4
        original += 0.5 * np.sin(2 * np.pi * 554.37 * t)  # C#5
        original += 0.3 * np.sin(2 * np.pi * 659.25 * t)  # E5
        original = original / np.max(np.abs(original))
        
        # 存儲原始音訊
        encoded_original = encode_audio(original, sample_rate=sample_rate)
        toolkit.setter("audio:pipeline:original", encoded_original)
        print(f"   原始音訊大小: {len(encoded_original)} bytes")
        
        # 效果 1：音量正規化
        print("\n2. 效果 1：音量正規化")
        normalized = converter.normalize(original, target_level=0.8)
        encoded_normalized = encode_audio(normalized, sample_rate=sample_rate)
        toolkit.setter("audio:pipeline:normalized", encoded_normalized)
        print(f"   正規化後峰值: {np.max(np.abs(normalized)):.2f}")
        
        # 效果 2：低通濾波
        print("\n3. 效果 2：低通濾波")
        # 設計低通濾波器（截止頻率 1000 Hz）
        nyquist = sample_rate / 2
        cutoff = 1000 / nyquist
        b, a = signal.butter(4, cutoff, btype='low')
        filtered = signal.filtfilt(b, a, normalized)
        
        encoded_filtered = encode_audio(filtered, sample_rate=sample_rate)
        toolkit.setter("audio:pipeline:filtered", encoded_filtered)
        print(f"   濾波後大小: {len(encoded_filtered)} bytes")
        
        # 效果 3：添加回音
        print("\n4. 效果 3：添加回音")
        delay_samples = int(0.2 * sample_rate)  # 0.2 秒延遲
        echo = np.zeros(len(filtered) + delay_samples)
        echo[:len(filtered)] = filtered
        echo[delay_samples:] += filtered * 0.5  # 50% 回音強度
        
        # 截取到原始長度
        echo = echo[:len(filtered)]
        echo = echo / np.max(np.abs(echo))
        
        encoded_echo = encode_audio(echo, sample_rate=sample_rate)
        toolkit.setter("audio:pipeline:echo", encoded_echo)
        print(f"   回音效果大小: {len(encoded_echo)} bytes")
        
        # 效果 4：淡入淡出
        print("\n5. 效果 4：淡入淡出")
        fade_duration = 0.1  # 0.1 秒淡入淡出
        fade_samples = int(fade_duration * sample_rate)
        
        faded = echo.copy()
        # 淡入
        fade_in = np.linspace(0, 1, fade_samples)
        faded[:fade_samples] *= fade_in
        # 淡出
        fade_out = np.linspace(1, 0, fade_samples)
        faded[-fade_samples:] *= fade_out
        
        encoded_faded = encode_audio(faded, sample_rate=sample_rate)
        toolkit.setter("audio:pipeline:faded", encoded_faded)
        print(f"   淡入淡出後大小: {len(encoded_faded)} bytes")
        
        # 讀取所有處理結果
        print("\n6. 讀取處理管線的所有結果")
        pipeline_keys = [
            "audio:pipeline:original",
            "audio:pipeline:normalized",
            "audio:pipeline:filtered",
            "audio:pipeline:echo",
            "audio:pipeline:faded"
        ]
        
        results = toolkit.batch_get(pipeline_keys)
        for key in pipeline_keys:
            if results[key]:
                stage = key.split(":")[-1]
                rate, audio = decode_audio(results[key])
                print(f"   {stage}: ✅ 成功讀取 ({len(audio)} 樣本)")
        
        # 清理
        for key in pipeline_keys:
            toolkit.deleter(key)
            
    finally:
        toolkit.cleanup()


def audio_file_processing():
    """音訊檔案處理範例"""
    print("\n=== 音訊檔案處理範例 ===\n")
    
    import numpy as np
    import os
    from redis_toolkit.converters import get_converter, encode_audio, decode_audio
    
    toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
    converter = get_converter('audio')
    
    try:
        # 檢查是否有範例音訊檔案
        audio_file = "examples/real-world/media_processing/data/RobertoPrado_CourtScheme.mp3"
        
        if os.path.exists(audio_file):
            print("1. 讀取音訊檔案")
            try:
                # 使用 encode_from_file（需要 soundfile）
                encoded = converter.encode_from_file(audio_file)
                print(f"   ✅ 成功讀取: {audio_file}")
                print(f"   編碼大小: {len(encoded)} bytes")
                
                # 獲取檔案資訊
                info = converter.get_file_info(audio_file)
                print(f"   檔案資訊: {info}")
                
                # 存儲到 Redis
                toolkit.setter("audio:file:sample", encoded)
                
                # 讀取並解碼
                retrieved = toolkit.getter("audio:file:sample")
                rate, audio_data = decode_audio(retrieved)
                print(f"\n2. 解碼結果")
                print(f"   取樣率: {rate} Hz")
                print(f"   時長: {len(audio_data)/rate:.2f} 秒")
                print(f"   聲道數: {audio_data.shape[1] if len(audio_data.shape) > 1 else 1}")
                
                # 清理
                toolkit.deleter("audio:file:sample")
                
            except Exception as e:
                print(f"   ❌ 讀取檔案失敗: {e}")
                print("   可能需要安裝: pip install redis-toolkit[audio-full]")
        else:
            print(f"找不到範例音訊檔案: {audio_file}")
            print("跳過檔案處理範例")
            
            # 改為生成測試音訊
            print("\n生成替代測試音訊")
            sample_rate = 44100
            duration = 3.0
            t = np.linspace(0, duration, int(sample_rate * duration))
            
            # 生成鳥鳴聲效果
            chirp = signal.chirp(t, f0=1000, f1=4000, t1=duration, method='linear')
            chirp *= np.exp(-t * 2)  # 添加衰減
            
            encoded = encode_audio(chirp, sample_rate=sample_rate)
            toolkit.setter("audio:synthetic:chirp", encoded)
            print(f"   生成鳥鳴音效: {len(encoded)} bytes")
            
            # 清理
            toolkit.deleter("audio:synthetic:chirp")
            
    finally:
        toolkit.cleanup()


def audio_queue_system():
    """音訊佇列系統範例"""
    print("\n=== 音訊佇列系統範例 ===\n")
    
    import numpy as np
    from redis_toolkit.converters import encode_audio, decode_audio
    
    toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
    
    try:
        print("1. 建立音訊處理佇列")
        
        # 生成待處理的音訊任務
        sample_rate = 22050
        tasks = []
        
        for i in range(5):
            # 生成不同頻率的音訊
            duration = 0.5
            t = np.linspace(0, duration, int(sample_rate * duration))
            frequency = 220 * (2 ** (i/12))  # 音階
            audio = np.sin(2 * np.pi * frequency * t) * 0.5
            
            # 編碼音訊
            encoded = encode_audio(audio, sample_rate=sample_rate)
            task_id = f"task_{i+1}"
            
            # 加入佇列
            task_data = {
                "id": task_id,
                "audio_data": base64.b64encode(encoded).decode('utf-8'),
                "sample_rate": sample_rate,
                "frequency": frequency,
                "status": "pending"
            }
            
            toolkit.setter(f"audio:queue:{task_id}", task_data)
            toolkit.client.lpush("audio:task_queue", task_id)
            tasks.append(task_id)
            
            print(f"   加入任務: {task_id} (頻率: {frequency:.1f} Hz)")
        
        print(f"\n2. 處理佇列中的任務")
        processed_count = 0
        
        while True:
            # 從佇列取出任務
            task_id_bytes = toolkit.client.rpop("audio:task_queue")
            if not task_id_bytes:
                break
                
            task_id = task_id_bytes.decode() if isinstance(task_id_bytes, bytes) else task_id_bytes
            
            # 獲取任務資料
            task_data = toolkit.getter(f"audio:queue:{task_id}")
            if task_data:
                print(f"\n   處理任務: {task_id}")
                
                # 解碼音訊
                audio_bytes = base64.b64decode(task_data["audio_data"])
                rate, audio = decode_audio(audio_bytes)
                
                # 模擬處理（添加簡單效果）
                processed_audio = audio * 0.8  # 降低音量
                processed_audio = np.concatenate([processed_audio, processed_audio[::-1]])  # 添加反向
                
                # 更新任務狀態
                task_data["status"] = "completed"
                task_data["processed_samples"] = len(processed_audio)
                toolkit.setter(f"audio:queue:{task_id}", task_data)
                
                processed_count += 1
                print(f"     ✅ 完成處理，輸出樣本數: {len(processed_audio)}")
        
        print(f"\n3. 處理統計")
        print(f"   總任務數: {len(tasks)}")
        print(f"   已處理: {processed_count}")
        print(f"   佇列剩餘: {toolkit.client.llen('audio:task_queue')}")
        
        # 清理
        for task_id in tasks:
            toolkit.deleter(f"audio:queue:{task_id}")
            
    finally:
        toolkit.cleanup()


def main():
    """主程式"""
    print("Redis Toolkit 音訊串流範例")
    print("=" * 60)
    print()
    
    # 檢查依賴
    if not check_dependencies():
        print("\n請先安裝必要的依賴後再執行此範例")
        return
    
    try:
        # 基本傳輸
        basic_audio_transfer()
        print("\n" + "=" * 60)
        
        # 串流模擬
        audio_streaming_simulation()
        print("\n" + "=" * 60)
        
        # 效果處理
        audio_effects_pipeline()
        print("\n" + "=" * 60)
        
        # 檔案處理
        audio_file_processing()
        print("\n" + "=" * 60)
        
        # 佇列系統
        audio_queue_system()
        
        print("\n" + "=" * 60)
        print("✅ 所有音訊串流範例執行完成！")
        print("\n💡 重點總結：")
        print("  - 支援 WAV 格式的音訊編解碼")
        print("  - 可模擬實時音訊串流")
        print("  - 支援音訊效果處理管線")
        print("  - 可建立音訊處理佇列系統")
        print("  - 支援從檔案讀取（需要額外依賴）")
        
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()