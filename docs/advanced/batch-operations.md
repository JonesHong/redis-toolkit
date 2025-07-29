# 批次操作

批次操作是提升 Redis 效能的關鍵技術，能夠大幅減少網路往返次數，提高資料處理效率。

## 🚀 為什麼需要批次操作？

單筆操作 vs 批次操作的效能差異：

```python
import time

# ❌ 單筆操作：效能低下
start = time.time()
for i in range(10000):
    toolkit.setter(f"key:{i}", f"value:{i}")
print(f"單筆操作耗時: {time.time() - start:.2f} 秒")

# ✅ 批次操作：效能提升 10 倍以上
start = time.time()
batch_data = {f"key:{i}": f"value:{i}" for i in range(10000)}
toolkit.batch_set(batch_data)
print(f"批次操作耗時: {time.time() - start:.2f} 秒")
```

## 📝 批次操作方法

### batch_set - 批次設定

```python
# 準備批次資料
users = {
    "user:1001": {"name": "Alice", "score": 95},
    "user:1002": {"name": "Bob", "score": 87},
    "user:1003": {"name": "Charlie", "score": 92}
}

# 一次設定多個鍵值
toolkit.batch_set(users)

# 支援設定過期時間
toolkit.batch_set(users, ex=3600)  # 全部設定 1 小時過期
```

### batch_get - 批次讀取

```python
# 批次讀取多個鍵
keys = ["user:1001", "user:1002", "user:1003"]
results = toolkit.batch_get(keys)

# results 是字典格式
for key, value in results.items():
    if value:  # 檢查鍵是否存在
        print(f"{key}: {value['name']} - 分數: {value['score']}")
```

## 🔧 使用 Pipeline

Pipeline 提供更靈活的批次操作方式：

```python
# 創建管線
pipe = toolkit.client.pipeline()

# 排隊多個不同類型的命令
pipe.set("counter", 0)
pipe.incr("counter")
pipe.incr("counter")
pipe.get("counter")

# 執行所有命令
results = pipe.execute()
print(results)  # [True, 1, 2, b'2']
```

### Pipeline 事務支援

```python
# 使用事務確保原子性
pipe = toolkit.client.pipeline(transaction=True)

try:
    # 監視鍵（樂觀鎖）
    pipe.watch("account:balance")
    
    # 獲取當前餘額
    balance = int(pipe.get("account:balance") or 0)
    
    # 開始事務
    pipe.multi()
    
    # 執行轉帳操作
    if balance >= 100:
        pipe.decrby("account:balance", 100)
        pipe.incrby("account:savings", 100)
        pipe.execute()
        print("轉帳成功")
    else:
        pipe.reset()  # 取消事務
        print("餘額不足")
        
except redis.WatchError:
    print("餘額在交易期間被修改")
```

## 🎯 實用範例

### 批次更新用戶積分

```python
class ScoreManager:
    def __init__(self):
        self.toolkit = RedisToolkit()
    
    def update_scores(self, score_updates):
        """批次更新用戶積分"""
        # 先批次讀取現有資料
        user_ids = list(score_updates.keys())
        keys = [f"user:{uid}" for uid in user_ids]
        existing_users = self.toolkit.batch_get(keys)
        
        # 更新積分
        updated_data = {}
        for uid, score_delta in score_updates.items():
            key = f"user:{uid}"
            user_data = existing_users.get(key, {"score": 0})
            user_data["score"] = user_data.get("score", 0) + score_delta
            updated_data[key] = user_data
        
        # 批次寫回
        self.toolkit.batch_set(updated_data)
        
        return updated_data

# 使用範例
manager = ScoreManager()

# 批次更新多個用戶的積分
updates = {
    "1001": 10,   # 用戶 1001 加 10 分
    "1002": -5,   # 用戶 1002 減 5 分
    "1003": 20    # 用戶 1003 加 20 分
}

result = manager.update_scores(updates)
```

### 批次快取預熱

```python
def cache_warmup(data_loader, cache_keys):
    """批次預熱快取"""
    # 從資料來源批次載入資料
    data = data_loader.load_batch(cache_keys)
    
    # 轉換為 Redis 鍵值格式
    cache_data = {}
    for item in data:
        key = f"cache:{item['id']}"
        cache_data[key] = item
    
    # 批次寫入快取，設定過期時間
    toolkit.batch_set(cache_data, ex=3600)
    
    print(f"預熱了 {len(cache_data)} 個快取項目")
```

## 🚀 效能優化技巧

### 1. 分批處理大量資料

```python
def batch_process_large_dataset(data, batch_size=1000):
    """分批處理大型資料集"""
    total = len(data)
    
    for i in range(0, total, batch_size):
        batch = dict(list(data.items())[i:i + batch_size])
        toolkit.batch_set(batch)
        print(f"已處理 {min(i + batch_size, total)}/{total}")
```

### 2. 並行批次操作

```python
from concurrent.futures import ThreadPoolExecutor
import threading

def parallel_batch_operations(datasets):
    """並行執行多個批次操作"""
    def process_batch(batch_id, data):
        local_toolkit = RedisToolkit()
        local_toolkit.batch_set(data)
        print(f"批次 {batch_id} 完成")
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for i, dataset in enumerate(datasets):
            future = executor.submit(process_batch, i, dataset)
            futures.append(future)
        
        # 等待所有批次完成
        for future in futures:
            future.result()
```

## 📊 效能比較

| 操作類型 | 10,000 筆資料耗時 | 網路往返次數 |
|---------|-----------------|-------------|
| 單筆操作 | ~5.2 秒 | 10,000 次 |
| 批次操作 | ~0.3 秒 | 1 次 |
| Pipeline | ~0.4 秒 | 1 次 |
| 分批處理(1000筆/批) | ~0.5 秒 | 10 次 |

## 🎯 最佳實踐

1. **選擇適當的批次大小**
   ```python
   # 建議批次大小：100-1000 筆
   # 太小：效能提升有限
   # 太大：可能超過 Redis 限制或記憶體
   optimal_batch_size = 500
   ```

2. **處理部分失敗**
   ```python
   try:
       toolkit.batch_set(large_batch)
   except Exception as e:
       # 降級為逐筆處理
       for key, value in large_batch.items():
           try:
               toolkit.setter(key, value)
           except:
               logger.error(f"Failed to set {key}")
   ```

3. **監控批次操作**
   ```python
   import time
   
   start = time.time()
   toolkit.batch_set(data)
   elapsed = time.time() - start
   
   logger.info(f"批次寫入 {len(data)} 筆，耗時 {elapsed:.3f} 秒")
   ```

## 📚 延伸閱讀

- [效能優化](./performance.md) - 更多效能調優技巧
- [連接池管理](./connection-pool.md) - 優化連線資源
- [錯誤處理](./error-handling.md) - 處理批次操作錯誤

::: tip 小結
批次操作是提升 Redis 效能的利器。記住選擇適當的批次大小，處理錯誤情況，並監控操作效能！
:::