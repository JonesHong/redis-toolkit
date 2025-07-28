# 性能調優指南

本指南介紹如何優化 Redis Toolkit 應用的性能，包括連接池管理、批次操作優化、序列化策略等。

## 性能分析基礎

### 測量工具

```python
import time
import cProfile
import pstats
from functools import wraps

def measure_time(func):
    """測量函數執行時間的裝飾器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} 執行時間: {end - start:.4f} 秒")
        return result
    return wrapper

@measure_time
def example_operation():
    toolkit = RedisToolkit()
    for i in range(1000):
        toolkit.setter(f"key:{i}", {"value": i})
```

### 性能分析

```python
def profile_redis_operations():
    """分析 Redis 操作性能"""
    profiler = cProfile.Profile()
    
    # 開始分析
    profiler.enable()
    
    # 執行操作
    toolkit = RedisToolkit()
    data = {f"test:{i}": {"value": i} for i in range(10000)}
    toolkit.batch_set(data)
    
    # 停止分析
    profiler.disable()
    
    # 顯示結果
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # 顯示前 10 個最耗時的函數
```

## 連接池優化

### 配置連接池

```python
from redis_toolkit import RedisToolkit, RedisConnectionConfig, RedisOptions

# 優化的連接池配置
config = RedisConnectionConfig(
    host='localhost',
    port=6379,
    # 連接池設置
    max_connections=100,        # 最大連接數
    socket_connect_timeout=5,   # 連接超時（秒）
    socket_timeout=5,          # 操作超時（秒）
    socket_keepalive=True,     # 保持連接
    socket_keepalive_options={
        1: 1,  # TCP_KEEPIDLE
        2: 1,  # TCP_KEEPINTVL
        3: 3,  # TCP_KEEPCNT
    }
)

options = RedisOptions(
    use_connection_pool=True,
    max_connections=100
)

toolkit = RedisToolkit(config=config, options=options)
```

### 連接池監控

```python
class ConnectionPoolMonitor:
    def __init__(self, toolkit):
        self.toolkit = toolkit
        self.pool = toolkit.client.connection_pool
        
    def get_pool_stats(self):
        """獲取連接池統計信息"""
        return {
            "created_connections": self.pool.created_connections,
            "available_connections": len(self.pool._available_connections),
            "in_use_connections": len(self.pool._in_use_connections),
            "max_connections": self.pool.max_connections
        }
    
    def monitor_pool_usage(self, duration=60, interval=5):
        """監控連接池使用情況"""
        import matplotlib.pyplot as plt
        from datetime import datetime
        
        timestamps = []
        in_use = []
        available = []
        
        start_time = time.time()
        while time.time() - start_time < duration:
            stats = self.get_pool_stats()
            timestamps.append(datetime.now())
            in_use.append(stats["in_use_connections"])
            available.append(stats["available_connections"])
            time.sleep(interval)
        
        # 繪製圖表
        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, in_use, label='使用中')
        plt.plot(timestamps, available, label='可用')
        plt.xlabel('時間')
        plt.ylabel('連接數')
        plt.title('連接池使用情況')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
```

## 批次操作優化

### 動態批次大小

```python
class DynamicBatchProcessor:
    def __init__(self, toolkit, initial_batch_size=1000):
        self.toolkit = toolkit
        self.batch_size = initial_batch_size
        self.performance_history = []
        
    def process_batch(self, data):
        """處理一個批次並測量性能"""
        start_time = time.time()
        self.toolkit.batch_set(data)
        elapsed = time.time() - start_time
        
        items_per_second = len(data) / elapsed
        self.performance_history.append(items_per_second)
        
        return elapsed, items_per_second
    
    def optimize_batch_size(self, total_data):
        """動態優化批次大小"""
        keys = list(total_data.keys())
        best_batch_size = self.batch_size
        best_performance = 0
        
        # 測試不同的批次大小
        test_sizes = [500, 1000, 2000, 5000, 10000]
        
        for size in test_sizes:
            if size > len(keys):
                continue
                
            # 測試批次
            test_data = {k: total_data[k] for k in keys[:size]}
            elapsed, performance = self.process_batch(test_data)
            
            print(f"批次大小 {size}: {performance:.0f} items/秒")
            
            if performance > best_performance:
                best_performance = performance
                best_batch_size = size
        
        self.batch_size = best_batch_size
        print(f"最優批次大小: {best_batch_size}")
        
        return best_batch_size
```

### 並行批次處理

```python
import concurrent.futures
from threading import Lock

class ParallelBatchProcessor:
    def __init__(self, num_workers=4):
        self.num_workers = num_workers
        self.lock = Lock()
        self.processed_count = 0
        
    def process_chunk(self, chunk_data):
        """處理一個數據塊"""
        toolkit = RedisToolkit()
        toolkit.batch_set(chunk_data)
        
        with self.lock:
            self.processed_count += len(chunk_data)
            
        return len(chunk_data)
    
    def process_parallel(self, data, chunk_size=1000):
        """並行處理大量數據"""
        start_time = time.time()
        
        # 分割數據
        chunks = []
        items = list(data.items())
        for i in range(0, len(items), chunk_size):
            chunk = dict(items[i:i+chunk_size])
            chunks.append(chunk)
        
        # 並行處理
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            futures = [executor.submit(self.process_chunk, chunk) for chunk in chunks]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        elapsed = time.time() - start_time
        total_items = sum(results)
        
        print(f"並行處理 {total_items} 項，耗時 {elapsed:.2f} 秒")
        print(f"速度: {total_items/elapsed:.0f} items/秒")
        
        return results
```

## 序列化優化

### 自定義序列化器

```python
import json
import pickle
import msgpack

class OptimizedSerializer:
    def __init__(self, method='msgpack'):
        self.method = method
        self.stats = {
            'encode_time': 0,
            'decode_time': 0,
            'total_size': 0,
            'operations': 0
        }
    
    def encode(self, data):
        """編碼數據"""
        start = time.perf_counter()
        
        if self.method == 'json':
            encoded = json.dumps(data).encode('utf-8')
        elif self.method == 'pickle':
            encoded = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
        elif self.method == 'msgpack':
            encoded = msgpack.packb(data, use_bin_type=True)
        else:
            raise ValueError(f"未知的序列化方法: {self.method}")
        
        elapsed = time.perf_counter() - start
        self.stats['encode_time'] += elapsed
        self.stats['total_size'] += len(encoded)
        self.stats['operations'] += 1
        
        return encoded
    
    def decode(self, data):
        """解碼數據"""
        start = time.perf_counter()
        
        if self.method == 'json':
            decoded = json.loads(data.decode('utf-8'))
        elif self.method == 'pickle':
            decoded = pickle.loads(data)
        elif self.method == 'msgpack':
            decoded = msgpack.unpackb(data, raw=False)
        else:
            raise ValueError(f"未知的序列化方法: {self.method}")
        
        elapsed = time.perf_counter() - start
        self.stats['decode_time'] += elapsed
        
        return decoded
    
    def get_stats(self):
        """獲取性能統計"""
        if self.stats['operations'] == 0:
            return None
            
        return {
            'method': self.method,
            'avg_encode_time': self.stats['encode_time'] / self.stats['operations'],
            'avg_decode_time': self.stats['decode_time'] / self.stats['operations'],
            'avg_size': self.stats['total_size'] / self.stats['operations'],
            'total_operations': self.stats['operations']
        }
```

### 序列化方法比較

```python
def compare_serialization_methods(test_data):
    """比較不同序列化方法的性能"""
    methods = ['json', 'pickle', 'msgpack']
    results = {}
    
    for method in methods:
        serializer = OptimizedSerializer(method)
        
        # 測試編碼
        start = time.time()
        encoded = serializer.encode(test_data)
        encode_time = time.time() - start
        
        # 測試解碼
        start = time.time()
        decoded = serializer.decode(encoded)
        decode_time = time.time() - start
        
        results[method] = {
            'encode_time': encode_time,
            'decode_time': decode_time,
            'size': len(encoded),
            'correct': decoded == test_data
        }
    
    # 顯示結果
    print("序列化方法比較：")
    print(f"{'方法':<10} {'編碼時間':<12} {'解碼時間':<12} {'大小':<10} {'正確性':<8}")
    print("-" * 60)
    
    for method, result in results.items():
        print(f"{method:<10} {result['encode_time']:<12.6f} "
              f"{result['decode_time']:<12.6f} {result['size']:<10} "
              f"{str(result['correct']):<8}")
    
    return results
```

## 管道優化

### 智能管道處理

```python
class SmartPipeline:
    def __init__(self, toolkit, auto_execute_size=1000):
        self.toolkit = toolkit
        self.pipe = toolkit.client.pipeline(transaction=False)
        self.auto_execute_size = auto_execute_size
        self.command_count = 0
        
    def add_command(self, command, *args, **kwargs):
        """添加命令到管道"""
        getattr(self.pipe, command)(*args, **kwargs)
        self.command_count += 1
        
        # 自動執行
        if self.command_count >= self.auto_execute_size:
            return self.execute()
        return None
    
    def execute(self):
        """執行管道命令"""
        if self.command_count == 0:
            return []
            
        start_time = time.time()
        results = self.pipe.execute()
        elapsed = time.time() - start_time
        
        print(f"執行 {self.command_count} 個命令，耗時 {elapsed:.3f} 秒")
        
        # 重置
        self.pipe = self.toolkit.client.pipeline(transaction=False)
        self.command_count = 0
        
        return results
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.command_count > 0:
            self.execute()
```

### 管道批次操作

```python
def optimized_batch_operations(toolkit, operations):
    """優化的批次操作使用管道"""
    with SmartPipeline(toolkit) as pipe:
        for op in operations:
            if op['type'] == 'set':
                pipe.add_command('set', op['key'], 
                               toolkit._serialize(op['value']))
            elif op['type'] == 'get':
                pipe.add_command('get', op['key'])
            elif op['type'] == 'delete':
                pipe.add_command('delete', op['key'])
            elif op['type'] == 'expire':
                pipe.add_command('expire', op['key'], op['ttl'])
        
        results = pipe.execute()
    
    return results
```

## 內存優化

### 內存使用監控

```python
import psutil
import os

class MemoryMonitor:
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.initial_memory = self.get_memory_usage()
        
    def get_memory_usage(self):
        """獲取當前內存使用量（MB）"""
        return self.process.memory_info().rss / 1024 / 1024
    
    def get_memory_delta(self):
        """獲取內存使用變化"""
        current = self.get_memory_usage()
        return current - self.initial_memory
    
    def monitor_operation(self, operation, *args, **kwargs):
        """監控操作的內存使用"""
        before = self.get_memory_usage()
        result = operation(*args, **kwargs)
        after = self.get_memory_usage()
        
        print(f"{operation.__name__} 內存使用: {after - before:.2f} MB")
        return result
```

### 內存效率策略

```python
class MemoryEfficientStorage:
    def __init__(self, toolkit, compression_threshold=1024):
        self.toolkit = toolkit
        self.compression_threshold = compression_threshold
        
    def store_with_compression(self, key, value):
        """根據大小決定是否壓縮存儲"""
        import zlib
        
        # 序列化
        serialized = self.toolkit._serialize(value)
        
        # 檢查是否需要壓縮
        if len(serialized) > self.compression_threshold:
            compressed = zlib.compress(serialized)
            compression_ratio = len(compressed) / len(serialized)
            
            if compression_ratio < 0.8:  # 壓縮率超過 20%
                self.toolkit.client.set(f"{key}:compressed", compressed)
                self.toolkit.client.set(f"{key}:meta", {
                    "compressed": True,
                    "original_size": len(serialized),
                    "compressed_size": len(compressed)
                })
                return True
        
        # 不壓縮
        self.toolkit.setter(key, value)
        return False
    
    def retrieve_with_decompression(self, key):
        """檢索並解壓縮數據"""
        import zlib
        
        # 檢查是否壓縮
        meta = self.toolkit.getter(f"{key}:meta")
        
        if meta and meta.get("compressed"):
            compressed = self.toolkit.client.get(f"{key}:compressed")
            if compressed:
                decompressed = zlib.decompress(compressed)
                return self.toolkit._deserialize(decompressed)
        
        # 正常獲取
        return self.toolkit.getter(key)
```

## 實時性能監控

```python
class PerformanceDashboard:
    def __init__(self, toolkit):
        self.toolkit = toolkit
        self.metrics = {
            'operations': [],
            'latencies': [],
            'throughput': []
        }
        
    def record_operation(self, operation_type, latency, items=1):
        """記錄操作性能"""
        timestamp = time.time()
        
        self.metrics['operations'].append({
            'timestamp': timestamp,
            'type': operation_type,
            'latency': latency,
            'items': items
        })
        
        # 保持最近 1000 條記錄
        if len(self.metrics['operations']) > 1000:
            self.metrics['operations'].pop(0)
    
    def get_current_stats(self):
        """獲取當前性能統計"""
        if not self.metrics['operations']:
            return None
            
        recent_ops = [op for op in self.metrics['operations'] 
                     if time.time() - op['timestamp'] < 60]
        
        if not recent_ops:
            return None
            
        total_latency = sum(op['latency'] for op in recent_ops)
        total_items = sum(op['items'] for op in recent_ops)
        
        return {
            'avg_latency': total_latency / len(recent_ops),
            'operations_per_minute': len(recent_ops),
            'items_per_minute': total_items,
            'avg_items_per_op': total_items / len(recent_ops)
        }
    
    def print_dashboard(self):
        """打印性能儀表板"""
        stats = self.get_current_stats()
        if not stats:
            print("沒有足夠的數據")
            return
            
        print("\n=== Redis Toolkit 性能儀表板 ===")
        print(f"平均延遲: {stats['avg_latency']*1000:.2f} ms")
        print(f"每分鐘操作數: {stats['operations_per_minute']}")
        print(f"每分鐘處理項目: {stats['items_per_minute']}")
        print(f"每操作平均項目數: {stats['avg_items_per_op']:.1f}")
        print("================================\n")
```

## 最佳實踐總結

### 1. 連接管理

```python
# 使用單例模式管理連接
class RedisManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.toolkit = RedisToolkit(
                options=RedisOptions(
                    use_connection_pool=True,
                    max_connections=50
                )
            )
        return cls._instance
```

### 2. 批次大小選擇

```python
def determine_optimal_batch_size(data_size):
    """根據數據量確定最優批次大小"""
    if data_size < 100:
        return data_size
    elif data_size < 1000:
        return 100
    elif data_size < 10000:
        return 1000
    else:
        return 5000
```

### 3. 錯誤重試策略

```python
def retry_with_backoff(func, max_retries=3, initial_delay=0.1):
    """指數退避重試策略"""
    delay = initial_delay
    
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            print(f"操作失敗，{delay}秒後重試...")
            time.sleep(delay)
            delay *= 2  # 指數退避
```

## 總結

性能優化是一個持續的過程。通過：

1. **監控和測量**：了解系統的性能瓶頸
2. **連接池優化**：減少連接開銷
3. **批次操作**：減少網絡往返
4. **序列化優化**：選擇合適的序列化方法
5. **管道使用**：組合多個操作
6. **內存管理**：控制內存使用

您可以顯著提升 Redis Toolkit 應用的性能。記住，優化應該基於實際的性能測量，而不是假設。