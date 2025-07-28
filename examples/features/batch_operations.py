#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Redis Toolkit 批次操作範例

展示批次操作的效能優勢和使用方法
"""

import time
import random
from redis_toolkit import RedisToolkit, RedisOptions


def performance_comparison():
    """比較單一操作與批次操作的效能差異"""
    print("=== 效能比較：單一操作 vs 批次操作 ===\n")
    
    # 準備測試資料
    test_size = 100
    test_data = {
        f"user:{i}": {
            "id": i,
            "name": f"用戶{i}",
            "email": f"user{i}@example.com",
            "score": random.randint(0, 100),
            "active": random.choice([True, False])
        }
        for i in range(test_size)
    }
    
    toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
    
    try:
        # 測試 1：單一操作
        print(f"1. 單一操作（{test_size} 筆資料）")
        start_time = time.time()
        
        for key, value in test_data.items():
            toolkit.setter(key, value)
        
        single_set_time = time.time() - start_time
        print(f"   設定時間: {single_set_time:.3f} 秒")
        
        # 清理資料
        for key in test_data.keys():
            toolkit.deleter(key)
        
        # 測試 2：批次操作
        print(f"\n2. 批次操作（{test_size} 筆資料）")
        start_time = time.time()
        
        toolkit.batch_set(test_data)
        
        batch_set_time = time.time() - start_time
        print(f"   設定時間: {batch_set_time:.3f} 秒")
        
        # 效能改善
        improvement = (single_set_time / batch_set_time - 1) * 100
        print(f"\n📊 效能改善: {improvement:.1f}% 更快")
        print(f"   批次操作快了 {single_set_time / batch_set_time:.1f} 倍")
        
        # 測試批次讀取
        print("\n3. 批次讀取效能測試")
        keys = list(test_data.keys())
        
        # 單一讀取
        start_time = time.time()
        results_single = {}
        for key in keys:
            results_single[key] = toolkit.getter(key)
        single_get_time = time.time() - start_time
        
        # 批次讀取
        start_time = time.time()
        results_batch = toolkit.batch_get(keys)
        batch_get_time = time.time() - start_time
        
        print(f"   單一讀取時間: {single_get_time:.3f} 秒")
        print(f"   批次讀取時間: {batch_get_time:.3f} 秒")
        print(f"   改善: {(single_get_time / batch_get_time - 1) * 100:.1f}% 更快")
        
        # 驗證資料一致性
        all_match = all(results_single[k] == results_batch[k] for k in keys)
        print(f"\n4. 資料一致性檢查: {'✅ 通過' if all_match else '❌ 失敗'}")
        
    finally:
        # 清理所有測試資料
        for key in test_data.keys():
            toolkit.deleter(key)
        toolkit.cleanup()


def batch_operations_patterns():
    """展示批次操作的常見模式"""
    print("\n=== 批次操作常見模式 ===\n")
    
    toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
    
    try:
        # 模式 1：批次更新使用者資料
        print("1. 批次更新使用者資料")
        users = {
            "user:1001": {"name": "張三", "points": 100, "level": 1},
            "user:1002": {"name": "李四", "points": 250, "level": 2},
            "user:1003": {"name": "王五", "points": 500, "level": 3},
        }
        toolkit.batch_set(users)
        print("   ✅ 批次更新 3 個使用者")
        
        # 模式 2：批次快取 API 響應
        print("\n2. 批次快取 API 響應")
        api_cache = {
            "api:product:123": {"id": 123, "name": "產品A", "price": 99.9},
            "api:product:456": {"id": 456, "name": "產品B", "price": 199.9},
            "api:product:789": {"id": 789, "name": "產品C", "price": 299.9},
        }
        toolkit.batch_set(api_cache)
        
        # 設定過期時間（使用原生客戶端）
        for key in api_cache.keys():
            toolkit.client.expire(key, 3600)  # 1小時過期
        print("   ✅ 批次快取 3 個 API 響應（TTL: 1小時）")
        
        # 模式 3：批次讀取並處理
        print("\n3. 批次讀取並處理")
        product_keys = list(api_cache.keys())
        products = toolkit.batch_get(product_keys)
        
        # 計算總價
        total_price = sum(p["price"] for p in products.values() if p)
        print(f"   產品總價: ${total_price:.2f}")
        
        # 模式 4：條件式批次操作
        print("\n4. 條件式批次操作")
        # 只更新積分大於 200 的使用者
        high_score_users = {}
        all_users = toolkit.batch_get(list(users.keys()))
        
        for key, user in all_users.items():
            if user and user.get("points", 0) >= 200:
                user["bonus"] = 50  # 加贈積分
                high_score_users[key] = user
        
        if high_score_users:
            toolkit.batch_set(high_score_users)
            print(f"   ✅ 更新了 {len(high_score_users)} 個高積分使用者")
        
        # 模式 5：批次刪除
        print("\n5. 批次刪除過期資料")
        # 使用原生客戶端的 delete 方法
        all_keys = list(users.keys()) + list(api_cache.keys())
        deleted_count = toolkit.client.delete(*all_keys)
        print(f"   ✅ 批次刪除了 {deleted_count} 個鍵")
        
    finally:
        toolkit.cleanup()


def batch_with_pipeline():
    """展示如何結合 pipeline 進行更複雜的批次操作"""
    print("\n=== 結合 Pipeline 的進階批次操作 ===\n")
    
    toolkit = RedisToolkit(options=RedisOptions(is_logger_info=False))
    
    try:
        # 準備資料
        print("1. 使用 Pipeline 進行複雜批次操作")
        
        # 創建 pipeline
        pipe = toolkit.client.pipeline()
        
        # 混合操作：設定資料、增加計數器、添加到集合
        for i in range(5):
            user_key = f"user:{i}"
            user_data = {"id": i, "name": f"用戶{i}"}
            
            # 使用 toolkit 序列化資料
            from redis_toolkit.utils.serializers import serialize_value
            serialized = serialize_value(user_data)
            
            # 在 pipeline 中執行多個操作
            pipe.set(user_key, serialized)
            pipe.incr(f"counter:user:{i}")
            pipe.sadd("active_users", i)
            pipe.zadd("user_scores", {f"user:{i}": random.randint(0, 100)})
        
        # 執行 pipeline
        results = pipe.execute()
        print(f"   ✅ Pipeline 執行了 {len(results)} 個操作")
        
        # 驗證結果
        print("\n2. 驗證 Pipeline 操作結果")
        
        # 檢查使用者資料
        user_0 = toolkit.getter("user:0")
        print(f"   用戶資料: {user_0}")
        
        # 檢查計數器
        counter_0 = toolkit.client.get("counter:user:0")
        print(f"   計數器值: {counter_0.decode() if counter_0 else 'None'}")
        
        # 檢查集合成員
        active_count = toolkit.client.scard("active_users")
        print(f"   活躍用戶數: {active_count}")
        
        # 檢查有序集合
        top_users = toolkit.client.zrevrange("user_scores", 0, 2, withscores=True)
        print(f"   前三名用戶: {[(u[0].decode(), int(u[1])) for u in top_users]}")
        
        # 清理
        print("\n3. 批次清理所有測試資料")
        cleanup_pipe = toolkit.client.pipeline()
        for i in range(5):
            cleanup_pipe.delete(f"user:{i}", f"counter:user:{i}")
        cleanup_pipe.delete("active_users", "user_scores")
        cleanup_pipe.execute()
        print("   ✅ 清理完成")
        
    finally:
        toolkit.cleanup()


def error_handling_in_batch():
    """展示批次操作中的錯誤處理"""
    print("\n=== 批次操作錯誤處理 ===\n")
    
    from redis_toolkit.exceptions import ValidationError, SerializationError
    
    # 設定較嚴格的限制
    options = RedisOptions(
        max_key_length=20,
        max_value_size=1024,  # 1KB
        enable_validation=True,
        is_logger_info=False
    )
    
    toolkit = RedisToolkit(options=options)
    
    try:
        print("1. 測試鍵名過長的錯誤")
        invalid_data = {
            "valid_key": {"data": "OK"},
            "this_is_a_very_long_key_that_exceeds_limit": {"data": "Will fail"},
            "another_valid": {"data": "OK"}
        }
        
        try:
            toolkit.batch_set(invalid_data)
        except ValidationError as e:
            print(f"   ❌ 預期的錯誤: {e}")
            print("   💡 批次操作在驗證階段就會失敗，不會部分寫入")
        
        print("\n2. 測試值過大的錯誤")
        large_value_data = {
            "large_data": {"content": "x" * 2000}  # 超過 1KB
        }
        
        try:
            toolkit.batch_set(large_value_data)
        except ValidationError as e:
            print(f"   ❌ 預期的錯誤: {e}")
        
        print("\n3. 安全的批次操作模式")
        # 預先驗證資料
        safe_data = {}
        for key, value in invalid_data.items():
            if len(key) <= options.max_key_length:
                safe_data[key] = value
            else:
                print(f"   ⚠️  跳過無效鍵: {key}")
        
        # 執行安全的批次操作
        toolkit.batch_set(safe_data)
        print(f"   ✅ 成功寫入 {len(safe_data)} 筆資料")
        
        # 清理
        for key in safe_data.keys():
            toolkit.deleter(key)
            
    finally:
        toolkit.cleanup()


def main():
    """主程式"""
    print("Redis Toolkit 批次操作範例")
    print("=" * 60)
    print()
    
    try:
        # 執行各個範例
        performance_comparison()
        print("\n" + "=" * 60 + "\n")
        
        batch_operations_patterns()
        print("\n" + "=" * 60 + "\n")
        
        batch_with_pipeline()
        print("\n" + "=" * 60 + "\n")
        
        error_handling_in_batch()
        
        print("\n" + "=" * 60)
        print("✅ 所有批次操作範例執行完成！")
        print("\n💡 重點總結：")
        print("  - 批次操作可大幅提升效能（通常快 5-10 倍）")
        print("  - 適合大量資料的讀寫操作")
        print("  - 可結合 Pipeline 進行更複雜的操作")
        print("  - 注意錯誤處理，避免部分失敗的情況")
        
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()