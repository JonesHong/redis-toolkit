# Batch Operations

Batch operations are a key technique for improving Redis performance, significantly reducing network round trips and improving data processing efficiency.

## 🚀 Why Batch Operations?

Performance difference between single operations vs batch operations:

```python
import time

# ❌ Single operations: Poor performance
start = time.time()
for i in range(10000):
    toolkit.setter(f"key:{i}", f"value:{i}")
print(f"Single operations took: {time.time() - start:.2f} seconds")

# ✅ Batch operations: 10x+ performance improvement
start = time.time()
batch_data = {f"key:{i}": f"value:{i}" for i in range(10000)}
toolkit.batch_set(batch_data)
print(f"Batch operations took: {time.time() - start:.2f} seconds")
```

## 📝 Batch Operation Methods

### batch_set - Batch Set

```python
# Prepare batch data
users = {
    "user:1001": {"name": "Alice", "score": 95},
    "user:1002": {"name": "Bob", "score": 87},
    "user:1003": {"name": "Charlie", "score": 92}
}

# Set multiple key-values at once
toolkit.batch_set(users)

# Support setting expiration time
toolkit.batch_set(users, ex=3600)  # Set all to expire in 1 hour
```

### batch_get - Batch Get

```python
# Batch read multiple keys
keys = ["user:1001", "user:1002", "user:1003"]
results = toolkit.batch_get(keys)

# results is in dictionary format
for key, value in results.items():
    if value:  # Check if key exists
        print(f"{key}: {value['name']} - Score: {value['score']}")
```

## 🔧 Using Pipeline

Pipeline provides a more flexible way for batch operations:

```python
# Create pipeline
pipe = toolkit.client.pipeline()

# Queue multiple commands of different types
pipe.set("counter", 0)
pipe.incr("counter")
pipe.incr("counter")
pipe.get("counter")

# Execute all commands
results = pipe.execute()
print(results)  # [True, 1, 2, b'2']
```

### Pipeline Transaction Support

```python
# Use transactions to ensure atomicity
pipe = toolkit.client.pipeline(transaction=True)

try:
    # Watch key (optimistic locking)
    pipe.watch("account:balance")
    
    # Get current balance
    balance = int(pipe.get("account:balance") or 0)
    
    # Start transaction
    pipe.multi()
    
    # Execute transfer operation
    if balance >= 100:
        pipe.decrby("account:balance", 100)
        pipe.incrby("account:savings", 100)
        pipe.execute()
        print("Transfer successful")
    else:
        pipe.reset()  # Cancel transaction
        print("Insufficient balance")
        
except redis.WatchError:
    print("Balance was modified during transaction")
```

## 🎯 Practical Examples

### Batch Update User Scores

```python
class ScoreManager:
    def __init__(self):
        self.toolkit = RedisToolkit()
    
    def update_scores(self, score_updates):
        """Batch update user scores"""
        # First batch read existing data
        user_ids = list(score_updates.keys())
        keys = [f"user:{uid}" for uid in user_ids]
        existing_users = self.toolkit.batch_get(keys)
        
        # Update scores
        updated_data = {}
        for uid, score_delta in score_updates.items():
            key = f"user:{uid}"
            user_data = existing_users.get(key, {"score": 0})
            user_data["score"] = user_data.get("score", 0) + score_delta
            updated_data[key] = user_data
        
        # Batch write back
        self.toolkit.batch_set(updated_data)
        
        return updated_data

# Usage example
manager = ScoreManager()

# Batch update scores for multiple users
updates = {
    "1001": 10,   # User 1001 gains 10 points
    "1002": -5,   # User 1002 loses 5 points
    "1003": 20    # User 1003 gains 20 points
}

result = manager.update_scores(updates)
```

### Batch Cache Warming

```python
def cache_warmup(data_loader, cache_keys):
    """Batch warm up cache"""
    # Batch load data from data source
    data = data_loader.load_batch(cache_keys)
    
    # Convert to Redis key-value format
    cache_data = {}
    for item in data:
        key = f"cache:{item['id']}"
        cache_data[key] = item
    
    # Batch write to cache with expiration
    toolkit.batch_set(cache_data, ex=3600)
    
    print(f"Warmed up {len(cache_data)} cache items")
```

## 🚀 Performance Optimization Tips

### 1. Process Large Datasets in Chunks

```python
def batch_process_large_dataset(data, batch_size=1000):
    """Process large datasets in chunks"""
    total = len(data)
    
    for i in range(0, total, batch_size):
        batch = dict(list(data.items())[i:i + batch_size])
        toolkit.batch_set(batch)
        print(f"Processed {min(i + batch_size, total)}/{total}")
```

### 2. Parallel Batch Operations

```python
from concurrent.futures import ThreadPoolExecutor
import threading

def parallel_batch_operations(datasets):
    """Execute multiple batch operations in parallel"""
    def process_batch(batch_id, data):
        local_toolkit = RedisToolkit()
        local_toolkit.batch_set(data)
        print(f"Batch {batch_id} completed")
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for i, dataset in enumerate(datasets):
            future = executor.submit(process_batch, i, dataset)
            futures.append(future)
        
        # Wait for all batches to complete
        for future in futures:
            future.result()
```

## 📊 Performance Comparison

| Operation Type | Time for 10,000 items | Network Round Trips |
|---------------|----------------------|-------------------|
| Single Operations | ~5.2 seconds | 10,000 |
| Batch Operations | ~0.3 seconds | 1 |
| Pipeline | ~0.4 seconds | 1 |
| Chunked Processing (1000/batch) | ~0.5 seconds | 10 |

## 🎯 Best Practices

1. **Choose Appropriate Batch Size**
   ```python
   # Recommended batch size: 100-1000 items
   # Too small: Limited performance gain
   # Too large: May exceed Redis limits or memory
   optimal_batch_size = 500
   ```

2. **Handle Partial Failures**
   ```python
   try:
       toolkit.batch_set(large_batch)
   except Exception as e:
       # Fallback to individual operations
       for key, value in large_batch.items():
           try:
               toolkit.setter(key, value)
           except:
               logger.error(f"Failed to set {key}")
   ```

3. **Monitor Batch Operations**
   ```python
   import time
   
   start = time.time()
   toolkit.batch_set(data)
   elapsed = time.time() - start
   
   logger.info(f"Batch wrote {len(data)} items in {elapsed:.3f} seconds")
   ```

## 📚 Further Reading

- [Performance Optimization](./performance.md) - More performance tuning tips
- [Connection Pool Management](./connection-pool.md) - Optimize connection resources
- [Error Handling](./error-handling.md) - Handle batch operation errors

::: tip Summary
Batch operations are a powerful tool for improving Redis performance. Remember to choose appropriate batch sizes, handle error cases, and monitor operation performance!
:::