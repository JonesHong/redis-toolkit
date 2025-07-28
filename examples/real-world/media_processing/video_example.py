#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Redis Toolkit 視訊快取範例

展示如何使用 Redis 建立視訊快取系統
"""

import time
import os
import hashlib
from redis_toolkit import RedisToolkit, RedisOptions


def check_dependencies():
    """檢查必要的依賴"""
    try:
        import cv2
        from redis_toolkit.converters import get_converter
        return True
    except ImportError as e:
        print(f"❌ 缺少必要的依賴: {e}")
        print("請安裝: pip install redis-toolkit[video]")
        return False


def video_caching_basics():
    """基本視訊快取範例"""
    print("=== 基本視訊快取範例 ===\n")
    
    from redis_toolkit.converters import get_converter
    
    toolkit = RedisToolkit(options=RedisOptions(
        is_logger_info=False,
        max_value_size=100 * 1024 * 1024  # 100MB
    ))
    video_converter = get_converter('video')
    
    try:
        # 檢查範例視訊檔案
        video_file = "examples/real-world/media_processing/data/BigBuckBunny_320x180.mp4"
        
        if os.path.exists(video_file):
            print("1. 讀取視訊檔案")
            
            # 獲取視訊資訊
            info = video_converter.get_video_info(video_file)
            print(f"   檔案: {video_file}")
            print(f"   視訊資訊: {info}")
            
            # 讀取視訊檔案
            video_bytes = video_converter.encode(video_file)
            file_size = len(video_bytes)
            print(f"   檔案大小: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
            
            # 生成快取鍵（使用檔案雜湊）
            file_hash = hashlib.md5(video_file.encode()).hexdigest()[:8]
            cache_key = f"video:cache:{file_hash}"
            
            # 快取視訊
            print("\n2. 快取視訊到 Redis")
            start_time = time.time()
            toolkit.setter(cache_key, video_bytes)
            cache_time = time.time() - start_time
            print(f"   ✅ 快取完成")
            print(f"   快取時間: {cache_time:.2f} 秒")
            print(f"   快取速度: {file_size/cache_time/1024/1024:.2f} MB/s")
            
            # 設定過期時間
            toolkit.client.expire(cache_key, 3600)  # 1小時
            print("   設定過期時間: 1小時")
            
            # 從快取讀取
            print("\n3. 從快取讀取視訊")
            start_time = time.time()
            cached_video = toolkit.getter(cache_key)
            retrieve_time = time.time() - start_time
            
            if cached_video:
                print(f"   ✅ 成功讀取")
                print(f"   讀取時間: {retrieve_time:.2f} 秒")
                print(f"   讀取速度: {len(cached_video)/retrieve_time/1024/1024:.2f} MB/s")
                print(f"   資料完整性: {'✅ 完整' if len(cached_video) == file_size else '❌ 不完整'}")
            
            # 清理
            toolkit.deleter(cache_key)
            
        else:
            print(f"找不到範例視訊檔案: {video_file}")
            print("\n模擬視訊快取（使用假資料）")
            
            # 模擬視訊資料
            fake_video_size = 5 * 1024 * 1024  # 5MB
            fake_video = b"FAKE_VIDEO_DATA" * (fake_video_size // 15)
            
            cache_key = "video:cache:fake"
            toolkit.setter(cache_key, fake_video)
            print(f"   已快取模擬視訊: {len(fake_video):,} bytes")
            
            # 測試讀取
            cached = toolkit.getter(cache_key)
            print(f"   讀取驗證: {'✅ 成功' if cached else '❌ 失敗'}")
            
            # 清理
            toolkit.deleter(cache_key)
            
    finally:
        toolkit.cleanup()


def video_thumbnail_cache():
    """視訊縮圖快取系統"""
    print("\n=== 視訊縮圖快取系統 ===\n")
    
    import cv2
    from redis_toolkit.converters import get_converter, encode_image
    
    toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
    video_converter = get_converter('video')
    
    try:
        video_file = "examples/real-world/media_processing/data/BigBuckBunny_320x180.mp4"
        
        if os.path.exists(video_file):
            print("1. 擷取視訊關鍵幀作為縮圖")
            
            # 擷取幀
            frames = video_converter.extract_frames(video_file, max_frames=5)
            print(f"   擷取了 {len(frames)} 個關鍵幀")
            
            # 生成並快取縮圖
            print("\n2. 生成並快取縮圖")
            file_hash = hashlib.md5(video_file.encode()).hexdigest()[:8]
            
            for i, frame in enumerate(frames):
                # 調整縮圖大小
                thumbnail = cv2.resize(frame, (160, 90))  # 16:9 縮圖
                
                # 編碼縮圖
                encoded_thumb = encode_image(thumbnail, format='jpg', quality=70)
                
                # 快取縮圖
                thumb_key = f"video:thumb:{file_hash}:{i}"
                toolkit.setter(thumb_key, encoded_thumb)
                
                print(f"   縮圖 {i+1}: {len(encoded_thumb)} bytes")
            
            # 設定縮圖列表
            thumb_list_key = f"video:thumbs:{file_hash}"
            toolkit.setter(thumb_list_key, {
                "video_file": video_file,
                "thumb_count": len(frames),
                "thumb_size": "160x90",
                "created_at": time.time()
            })
            
            print(f"\n3. 讀取快取的縮圖")
            # 獲取縮圖資訊
            thumb_info = toolkit.getter(thumb_list_key)
            if thumb_info:
                print(f"   視訊: {thumb_info['video_file']}")
                print(f"   縮圖數量: {thumb_info['thumb_count']}")
                
                # 批次讀取所有縮圖
                thumb_keys = [f"video:thumb:{file_hash}:{i}" for i in range(thumb_info['thumb_count'])]
                cached_thumbs = toolkit.batch_get(thumb_keys)
                
                valid_thumbs = sum(1 for thumb in cached_thumbs.values() if thumb)
                print(f"   成功讀取: {valid_thumbs}/{len(thumb_keys)} 個縮圖")
            
            # 清理
            toolkit.deleter(thumb_list_key)
            for key in thumb_keys:
                toolkit.deleter(key)
                
        else:
            print("找不到範例視訊檔案，跳過縮圖快取範例")
            
    finally:
        toolkit.cleanup()


def video_segment_cache():
    """視訊分段快取系統"""
    print("\n=== 視訊分段快取系統 ===\n")
    
    toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
    
    try:
        print("1. 模擬視訊分段快取（適用於 HLS/DASH 串流）")
        
        # 模擬視訊分段
        video_id = "video_123"
        segment_duration = 10  # 每段 10 秒
        total_segments = 6  # 總共 6 段（1 分鐘視訊）
        segment_size = 2 * 1024 * 1024  # 每段約 2MB
        
        # 生成並快取分段
        print("\n2. 生成並快取視訊分段")
        manifest = {
            "video_id": video_id,
            "duration": total_segments * segment_duration,
            "segment_duration": segment_duration,
            "segments": []
        }
        
        for i in range(total_segments):
            # 模擬視訊分段資料
            segment_data = f"VIDEO_SEGMENT_{i}_DATA".encode() * (segment_size // 20)
            
            # 分段鍵
            segment_key = f"video:segment:{video_id}:{i}"
            
            # 快取分段
            toolkit.setter(segment_key, segment_data)
            
            # 更新清單
            manifest["segments"].append({
                "index": i,
                "key": segment_key,
                "size": len(segment_data),
                "duration": segment_duration
            })
            
            print(f"   分段 {i}: {len(segment_data):,} bytes")
        
        # 快取清單
        manifest_key = f"video:manifest:{video_id}"
        toolkit.setter(manifest_key, manifest)
        print(f"\n   ✅ 已快取 {total_segments} 個視訊分段")
        
        # 模擬播放器請求分段
        print("\n3. 模擬播放器請求分段")
        
        # 獲取清單
        cached_manifest = toolkit.getter(manifest_key)
        if cached_manifest:
            print(f"   視訊時長: {cached_manifest['duration']} 秒")
            print(f"   分段數量: {len(cached_manifest['segments'])}")
            
            # 模擬順序請求前 3 個分段
            print("\n   模擬播放前 30 秒:")
            for i in range(3):
                segment_info = cached_manifest["segments"][i]
                segment_data = toolkit.getter(segment_info["key"])
                
                if segment_data:
                    print(f"     分段 {i}: ✅ 成功載入 ({len(segment_data):,} bytes)")
                else:
                    print(f"     分段 {i}: ❌ 載入失敗")
        
        # 設定分段過期時間
        print("\n4. 設定分段過期時間")
        for i in range(total_segments):
            segment_key = f"video:segment:{video_id}:{i}"
            toolkit.client.expire(segment_key, 1800)  # 30 分鐘
        print("   所有分段設定 30 分鐘過期時間")
        
        # 清理
        toolkit.deleter(manifest_key)
        for i in range(total_segments):
            toolkit.deleter(f"video:segment:{video_id}:{i}")
            
    finally:
        toolkit.cleanup()


def video_metadata_cache():
    """視訊元資料快取"""
    print("\n=== 視訊元資料快取 ===\n")
    
    toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
    
    try:
        print("1. 建立視訊元資料快取系統")
        
        # 模擬視訊庫
        videos = [
            {
                "id": "vid_001",
                "title": "Redis Toolkit 教學",
                "duration": 600,
                "resolution": "1920x1080",
                "format": "mp4",
                "size": 150 * 1024 * 1024,
                "views": 1234,
                "likes": 89,
                "tags": ["教學", "Redis", "Python"]
            },
            {
                "id": "vid_002", 
                "title": "Python 進階技巧",
                "duration": 1200,
                "resolution": "1280x720",
                "format": "mp4",
                "size": 280 * 1024 * 1024,
                "views": 5678,
                "likes": 234,
                "tags": ["Python", "程式設計", "進階"]
            },
            {
                "id": "vid_003",
                "title": "資料結構與演算法",
                "duration": 1800,
                "resolution": "1920x1080", 
                "format": "mp4",
                "size": 450 * 1024 * 1024,
                "views": 8901,
                "likes": 567,
                "tags": ["演算法", "資料結構", "教學"]
            }
        ]
        
        # 快取元資料
        print("\n2. 快取視訊元資料")
        meta_keys = []
        for video in videos:
            meta_key = f"video:meta:{video['id']}"
            toolkit.setter(meta_key, video)
            meta_keys.append(meta_key)
            print(f"   {video['id']}: {video['title']}")
        
        # 建立索引
        print("\n3. 建立視訊索引")
        
        # 按觀看次數排序（使用 Redis 有序集合）
        for video in videos:
            toolkit.client.zadd("video:index:views", {video['id']: video['views']})
        
        # 按標籤分類（使用 Redis 集合）
        for video in videos:
            for tag in video['tags']:
                toolkit.client.sadd(f"video:tag:{tag}", video['id'])
        
        print("   ✅ 建立觀看次數索引")
        print("   ✅ 建立標籤索引")
        
        # 查詢範例
        print("\n4. 查詢視訊")
        
        # 最熱門的視訊
        print("\n   最熱門的 2 個視訊:")
        top_videos = toolkit.client.zrevrange("video:index:views", 0, 1, withscores=True)
        for video_id, views in top_videos:
            vid_id = video_id.decode() if isinstance(video_id, bytes) else video_id
            meta = toolkit.getter(f"video:meta:{vid_id}")
            if meta:
                print(f"     - {meta['title']} ({int(views)} 次觀看)")
        
        # 按標籤查詢
        print("\n   標籤 '教學' 的視訊:")
        teaching_videos = toolkit.client.smembers("video:tag:教學")
        for video_id in teaching_videos:
            vid_id = video_id.decode() if isinstance(video_id, bytes) else video_id
            meta = toolkit.getter(f"video:meta:{vid_id}")
            if meta:
                print(f"     - {meta['title']}")
        
        # 批次獲取元資料
        print("\n5. 批次獲取元資料")
        all_metas = toolkit.batch_get(meta_keys)
        total_size = sum(video['size'] for video in all_metas.values() if video)
        total_duration = sum(video['duration'] for video in all_metas.values() if video)
        
        print(f"   視訊總數: {len(all_metas)}")
        print(f"   總大小: {total_size/1024/1024/1024:.2f} GB")
        print(f"   總時長: {total_duration/3600:.1f} 小時")
        
        # 清理
        for key in meta_keys:
            toolkit.deleter(key)
        toolkit.client.delete("video:index:views")
        for video in videos:
            for tag in video['tags']:
                toolkit.client.delete(f"video:tag:{tag}")
                
    finally:
        toolkit.cleanup()


def adaptive_bitrate_cache():
    """自適應位元率快取系統"""
    print("\n=== 自適應位元率快取系統 ===\n")
    
    toolkit = RedisToolkit(options=RedisOptions(
        is_logger_info=False,
        max_value_size=600 * 1024 * 1024  # 600MB
    ))
    
    try:
        print("1. 建立多位元率視訊快取")
        
        video_id = "adaptive_video_001"
        qualities = [
            {"name": "1080p", "bitrate": 5000, "resolution": "1920x1080", "size_mb": 50},
            {"name": "720p", "bitrate": 2500, "resolution": "1280x720", "size_mb": 25},
            {"name": "480p", "bitrate": 1000, "resolution": "854x480", "size_mb": 10},
            {"name": "360p", "bitrate": 500, "resolution": "640x360", "size_mb": 5}
        ]
        
        # 模擬快取不同品質的視訊
        print("\n2. 快取不同品質版本")
        quality_map = {}
        
        for quality in qualities:
            # 模擬視訊資料
            video_size = quality['size_mb'] * 1024 * 1024
            video_data = f"VIDEO_{quality['name']}_DATA".encode() * (video_size // 20)
            
            # 快取鍵
            cache_key = f"video:abr:{video_id}:{quality['name']}"
            
            # 快取視訊
            toolkit.setter(cache_key, video_data[:video_size])  # 截取到指定大小
            
            quality_map[quality['name']] = {
                "key": cache_key,
                "bitrate": quality['bitrate'],
                "resolution": quality['resolution'],
                "size": video_size
            }
            
            print(f"   {quality['name']}: {quality['size_mb']} MB @ {quality['bitrate']} kbps")
        
        # 快取品質映射表
        map_key = f"video:abr:map:{video_id}"
        toolkit.setter(map_key, quality_map)
        
        # 模擬客戶端請求
        print("\n3. 模擬自適應串流")
        
        # 模擬不同網路條件
        network_conditions = [
            {"name": "高速網路", "bandwidth": 6000},
            {"name": "中速網路", "bandwidth": 2000},
            {"name": "低速網路", "bandwidth": 800}
        ]
        
        cached_map = toolkit.getter(map_key)
        if cached_map:
            for condition in network_conditions:
                print(f"\n   {condition['name']} (頻寬: {condition['bandwidth']} kbps):")
                
                # 選擇合適的品質
                selected_quality = None
                for q_name, q_info in sorted(cached_map.items(), 
                                           key=lambda x: x[1]['bitrate'], 
                                           reverse=True):
                    if q_info['bitrate'] <= condition['bandwidth']:
                        selected_quality = q_name
                        break
                
                if selected_quality:
                    q_info = cached_map[selected_quality]
                    # 模擬載入
                    video_data = toolkit.getter(q_info['key'])
                    if video_data:
                        print(f"     選擇品質: {selected_quality} ({q_info['resolution']})")
                        print(f"     載入大小: {len(video_data)/1024/1024:.1f} MB")
                else:
                    print("     ❌ 頻寬不足，無法串流")
        
        # 快取統計
        print("\n4. 快取使用統計")
        total_cached = 0
        for quality in qualities:
            cache_key = f"video:abr:{video_id}:{quality['name']}"
            if toolkit.client.exists(cache_key):
                total_cached += quality['size_mb']
        
        print(f"   總快取大小: {total_cached} MB")
        print(f"   快取版本數: {len(qualities)}")
        
        # 清理
        toolkit.deleter(map_key)
        for quality in qualities:
            toolkit.deleter(f"video:abr:{video_id}:{quality['name']}")
            
    finally:
        toolkit.cleanup()


def main():
    """主程式"""
    print("Redis Toolkit 視訊快取範例")
    print("=" * 60)
    print()
    
    # 檢查依賴
    if not check_dependencies():
        print("\n請先安裝必要的依賴後再執行此範例")
        return
    
    try:
        # 基本快取
        video_caching_basics()
        print("\n" + "=" * 60)
        
        # 縮圖快取
        video_thumbnail_cache()
        print("\n" + "=" * 60)
        
        # 分段快取
        video_segment_cache()
        print("\n" + "=" * 60)
        
        # 元資料快取
        video_metadata_cache()
        print("\n" + "=" * 60)
        
        # 自適應位元率
        adaptive_bitrate_cache()
        
        print("\n" + "=" * 60)
        print("✅ 所有視訊快取範例執行完成！")
        print("\n💡 重點總結：")
        print("  - 可快取完整視訊檔案")
        print("  - 支援視訊縮圖快取系統")
        print("  - 可實現 HLS/DASH 分段快取")
        print("  - 支援視訊元資料索引")
        print("  - 可建立自適應位元率快取")
        
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()