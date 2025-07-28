# 批次操作指南

本指南說明如何使用 Redis Toolkit 的批次操作功能來大幅提升性能。

## 為什麼使用批次操作？

批次操作可以：
- 減少網絡往返次數
- 提升 5-20 倍的性能
- 降低 Redis 服務器負載
- 簡化代碼邏輯

## 批次設置（Batch Set）

### 基本用法

```python
from redis_toolkit import RedisToolkit

toolkit = RedisToolkit()

# 準備要設置的數據
users = {
    "user:1": {"name": "Alice", "score": 95},
    "user:2": {"name": "Bob", "score": 87},
    "user:3": {"name": "Charlie", "score": 92}
}

# 批次設置
toolkit.batch_set(users)
```

### 大量數據處理

```python
# 生成大量測試數據
test_data = {}
for i in range(10000):
    test_data[f"item:{i}"] = {
        "id": i,
        "value": f"value_{i}",
        "timestamp": time.time()
    }

# 分批處理避免內存問題
batch_size = 1000
for i in range(0, len(test_data), batch_size):
    batch_keys = list(test_data.keys())[i:i+batch_size]
    batch_data = {k: test_data[k] for k in batch_keys}
    toolkit.batch_set(batch_data)
```

## 批次獲取（Batch Get）

### 基本用法

```python
# 指定要獲取的鍵
keys = ["user:1", "user:2", "user:3"]

# 批次獲取
results = toolkit.batch_get(keys)

# 處理結果
for key, value in results.items():
    if value is not None:
        print(f"{key}: {value}")
    else:
        print(f"{key}: 不存在")
```

### 處理缺失的鍵

```python
def safe_batch_get(toolkit, keys):
    """安全的批次獲取，處理缺失的鍵"""
    results = toolkit.batch_get(keys)
    
    processed = {}
    missing_keys = []
    
    for key, value in results.items():
        if value is not None:
            processed[key] = value
        else:
            missing_keys.append(key)
    
    if missing_keys:
        print(f"缺失的鍵: {missing_keys}")
    
    return processed, missing_keys
```

## 實際應用案例

### 1. 用戶數據緩存

```python
class UserCache:
    def __init__(self):
        self.toolkit = RedisToolkit()
        self.cache_prefix = "user:cache:"
        
    def cache_users(self, users):
        """批次緩存用戶數據"""
        cache_data = {
            f"{self.cache_prefix}{user['id']}": user
            for user in users
        }
        self.toolkit.batch_set(cache_data)
        
        # 設置過期時間（需要單獨處理）
        pipe = self.toolkit.client.pipeline()
        for key in cache_data.keys():
            pipe.expire(key, 3600)  # 1小時過期
        pipe.execute()
    
    def get_users(self, user_ids):
        """批次獲取用戶數據"""
        keys = [f"{self.cache_prefix}{uid}" for uid in user_ids]
        results = self.toolkit.batch_get(keys)
        
        # 整理結果
        users = []
        missing_ids = []
        
        for uid in user_ids:
            key = f"{self.cache_prefix}{uid}"
            if results.get(key):
                users.append(results[key])
            else:
                missing_ids.append(uid)
        
        return users, missing_ids
```

### 2. 會話管理

```python
class SessionManager:
    def __init__(self):
        self.toolkit = RedisToolkit()
        
    def create_sessions(self, sessions_data):
        """批次創建會話"""
        sessions = {}
        for session_id, user_data in sessions_data.items():
            sessions[f"session:{session_id}"] = {
                "user_id": user_data["user_id"],
                "username": user_data["username"],
                "created_at": time.time(),
                "last_active": time.time()
            }
        
        self.toolkit.batch_set(sessions)
        
    def get_active_sessions(self, session_ids):
        """批次獲取活躍會話"""
        keys = [f"session:{sid}" for sid in session_ids]
        sessions = self.toolkit.batch_get(keys)
        
        # 過濾活躍會話（30分鐘內）
        active_sessions = {}
        current_time = time.time()
        
        for key, session in sessions.items():
            if session and current_time - session["last_active"] < 1800:
                active_sessions[key] = session
                
        return active_sessions
```

### 3. 庫存管理

```python
class InventoryManager:
    def __init__(self):
        self.toolkit = RedisToolkit()
        
    def update_inventory(self, inventory_updates):
        """批次更新庫存"""
        # 先獲取當前庫存
        product_ids = list(inventory_updates.keys())
        keys = [f"inventory:{pid}" for pid in product_ids]
        current_inventory = self.toolkit.batch_get(keys)
        
        # 計算新庫存
        updated_inventory = {}
        for pid, change in inventory_updates.items():
            key = f"inventory:{pid}"
            current = current_inventory.get(key, {"quantity": 0})
            new_quantity = current.get("quantity", 0) + change
            
            if new_quantity >= 0:
                updated_inventory[key] = {
                    "product_id": pid,
                    "quantity": new_quantity,
                    "last_updated": time.time()
                }
        
        # 批次更新
        self.toolkit.batch_set(updated_inventory)
        return updated_inventory
```

## 性能比較

```python
import time

def performance_test():
    toolkit = RedisToolkit()
    test_size = 1000
    
    # 準備測試數據
    test_data = {f"test:{i}": {"value": i} for i in range(test_size)}
    test_keys = list(test_data.keys())
    
    # 測試逐個操作
    start_time = time.time()
    for key, value in test_data.items():
        toolkit.setter(key, value)
    single_set_time = time.time() - start_time
    
    # 清理
    for key in test_keys:
        toolkit.deleter(key)
    
    # 測試批次操作
    start_time = time.time()
    toolkit.batch_set(test_data)
    batch_set_time = time.time() - start_time
    
    print(f"逐個設置 {test_size} 個項目: {single_set_time:.2f} 秒")
    print(f"批次設置 {test_size} 個項目: {batch_set_time:.2f} 秒")
    print(f"性能提升: {single_set_time/batch_set_time:.1f}x")
    
    # 測試批次獲取
    start_time = time.time()
    for key in test_keys:
        toolkit.getter(key)
    single_get_time = time.time() - start_time
    
    start_time = time.time()
    toolkit.batch_get(test_keys)
    batch_get_time = time.time() - start_time
    
    print(f"\n逐個獲取 {test_size} 個項目: {single_get_time:.2f} 秒")
    print(f"批次獲取 {test_size} 個項目: {batch_get_time:.2f} 秒")
    print(f"性能提升: {single_get_time/batch_get_time:.1f}x")
```

## 最佳實踐

### 1. 適當的批次大小

```python
def process_large_dataset(data, batch_size=1000):
    """處理大數據集時使用適當的批次大小"""
    toolkit = RedisToolkit()
    
    keys = list(data.keys())
    for i in range(0, len(keys), batch_size):
        batch_keys = keys[i:i+batch_size]
        batch_data = {k: data[k] for k in batch_keys}
        toolkit.batch_set(batch_data)
```

### 2. 錯誤處理

```python
def robust_batch_operation(toolkit, data):
    """健壯的批次操作，包含錯誤處理"""
    try:
        toolkit.batch_set(data)
        return True, None
    except Exception as e:
        # 記錄錯誤
        print(f"批次操作失敗: {e}")
        
        # 嘗試逐個處理
        failed_keys = []
        for key, value in data.items():
            try:
                toolkit.setter(key, value)
            except Exception as key_error:
                failed_keys.append(key)
                print(f"鍵 {key} 處理失敗: {key_error}")
        
        return False, failed_keys
```

### 3. 混合操作

```python
def mixed_batch_operations(toolkit):
    """混合使用批次操作和管道"""
    # 批次設置數據
    data = {f"data:{i}": {"value": i} for i in range(100)}
    toolkit.batch_set(data)
    
    # 使用管道設置過期時間
    pipe = toolkit.client.pipeline()
    for key in data.keys():
        pipe.expire(key, 86400)  # 24小時
    pipe.execute()
    
    # 批次獲取並處理
    results = toolkit.batch_get(list(data.keys()))
    
    # 更新特定項目
    updates = {}
    for key, value in results.items():
        if value and value.get("value", 0) > 50:
            value["processed"] = True
            updates[key] = value
    
    toolkit.batch_set(updates)
```

## 注意事項

1. **內存限制**：批次操作會將所有數據加載到內存中，注意內存使用
2. **網絡限制**：過大的批次可能超過 Redis 的緩衝區限制
3. **原子性**：批次操作不是原子的，如需原子性請使用事務或 Lua 腳本
4. **序列化開銷**：大量數據的序列化/反序列化會消耗 CPU

## 總結

批次操作是提升 Redis 應用性能的關鍵技術。通過合理使用批次操作，可以顯著減少網絡開銷，提升應用響應速度。記住要根據實際情況選擇合適的批次大小，並做好錯誤處理。