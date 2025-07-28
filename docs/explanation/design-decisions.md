# 設計決策

本文檔解釋 Redis Toolkit 開發過程中的關鍵設計決策及其背後的理由。

## 為什麼選擇 Redis Toolkit？

### 問題陳述

在使用 Redis 與 Python 時，開發者經常面臨以下挑戰：

1. **序列化困擾**：需要手動處理 Python 對象與 Redis 字符串之間的轉換
2. **性能瓶頸**：逐個操作導致大量網絡往返
3. **媒體處理**：存儲圖片、音頻等二進制數據需要額外處理
4. **錯誤處理**：需要處理各種連接和操作錯誤
5. **配置複雜**：管理連接池、超時等配置繁瑣

### 解決方案

Redis Toolkit 通過以下方式解決這些問題：

```python
# 傳統方式
import redis
import json

r = redis.Redis()
data = {"name": "Alice", "age": 30}
r.set("user:1", json.dumps(data))
user = json.loads(r.get("user:1"))

# Redis Toolkit 方式
from redis_toolkit import RedisToolkit

toolkit = RedisToolkit()
toolkit.setter("user:1", {"name": "Alice", "age": 30})
user = toolkit.getter("user:1")
```

## 核心設計決策

### 1. 自動序列化

**決策**：默認使用 JSON 序列化，支援自定義序列化器。

**理由**：
- JSON 是人類可讀的，便於調試
- 廣泛支援，跨語言兼容
- 對於特殊類型（如 NumPy 數組），自動切換到 Pickle

**實現**：
```python
def _serialize(self, value: Any) -> bytes:
    if isinstance(value, bytes):
        return value
    
    try:
        # 優先使用 JSON
        return json.dumps(value).encode('utf-8')
    except (TypeError, ValueError):
        # 回退到 Pickle
        return pickle.dumps(value)
```

**權衡**：
- ✅ 簡單易用，自動處理
- ✅ 大多數情況下性能足夠
- ❌ JSON 不支援所有 Python 類型
- ❌ Pickle 存在安全風險

### 2. 批次操作優先

**決策**：提供專門的批次操作 API，內部使用管道優化。

**理由**：
- 顯著減少網絡往返（5-20x 性能提升）
- 更好的錯誤處理粒度
- 簡化並發操作

**實現考量**：
```python
# 不使用事務，提高性能
pipe = client.pipeline(transaction=False)

# 自動分批，避免內存問題
for chunk in chunks(data, size=1000):
    process_chunk(chunk)
```

### 3. 連接池管理

**決策**：默認啟用連接池，自動管理連接生命週期。

**理由**：
- 避免頻繁創建/銷毀連接的開銷
- 更好的並發性能
- 自動處理連接錯誤和重連

**配置策略**：
```python
# 開發環境：較少連接
max_connections = 10

# 生產環境：更多連接
max_connections = 100

# 自動調整：基於負載
max_connections = min(cpu_count() * 10, 200)
```

### 4. 發布/訂閱設計

**決策**：使用專用線程處理訂閱，支援多頻道訂閱。

**理由**：
- 非阻塞主線程
- 支援同時訂閱多個頻道
- 自動反序列化消息

**架構選擇**：
```
主線程
  │
  ├─> 發布操作（非阻塞）
  │
  └─> 訂閱線程（專用）
       │
       ├─> 頻道 1 處理器
       ├─> 頻道 2 處理器
       └─> 頻道 N 處理器
```

### 5. 媒體處理集成

**決策**：內建圖片、音頻、視頻轉換器。

**理由**：
- 多媒體數據是常見需求
- 統一的 API 接口
- 優化的編碼/解碼流程

**設計原則**：
- 可選依賴（不強制安裝 OpenCV）
- 智能格式選擇
- 壓縮與質量平衡

## API 設計哲學

### 1. 簡單優先

**原則**：最常見的用例應該最簡單。

```python
# 簡單用例 - 一行代碼
toolkit = RedisToolkit()

# 高級用例 - 明確配置
toolkit = RedisToolkit(
    config=RedisConnectionConfig(...),
    options=RedisOptions(...)
)
```

### 2. 漸進式複雜度

用戶可以從簡單開始，逐步深入：

1. **初級**：基本 get/set 操作
2. **中級**：批次操作、發布訂閱
3. **高級**：自定義序列化、性能調優
4. **專家**：直接訪問底層客戶端

### 3. 明確優於隱晦

```python
# 明確的方法名
toolkit.setter()      # 而不是 set() - 避免與 Python 內建衝突
toolkit.getter()      # 而不是 get()
toolkit.deleter()     # 而不是 delete()

# 明確的參數
toolkit.batch_set(data)  # 而不是 mset()
toolkit.batch_get(keys)  # 而不是 mget()
```

## 錯誤處理策略

### 1. 分層異常體系

**決策**：創建專門的異常類層次結構。

```
RedisToolkitError (基類)
├── ValidationError (輸入驗證)
├── SerializationError (序列化問題)
├── ConnectionError (連接問題)
└── OperationError (操作失敗)
```

**理由**：
- 更精確的錯誤處理
- 便於調試和日誌記錄
- 允許選擇性捕獲

### 2. 智能重試

**決策**：實現指數退避重試機制。

```python
retry_delays = [0.1, 0.2, 0.4, 0.8, 1.6]  # 指數增長
```

**考量因素**：
- 瞬時網絡問題
- Redis 臨時過載
- 避免雪崩效應

## 性能優化決策

### 1. 序列化緩存

**決策**：不實現序列化緩存。

**理由**：
- 增加複雜性
- 內存開銷
- Redis 本身就是緩存

### 2. 連接預熱

**決策**：延遲連接創建。

**理由**：
- 更快的啟動時間
- 按需創建連接
- 避免不必要的資源佔用

### 3. 批次大小限制

**決策**：自動分批大數據集。

```python
optimal_batch_size = min(
    1000,  # 經驗值
    available_memory / average_item_size / 10
)
```

## 安全性考量

### 1. 輸入驗證

**決策**：默認啟用嚴格驗證。

**驗證項目**：
- 鍵長度（最大 512 字符）
- 值大小（最大 512MB）
- 特殊字符過濾

### 2. 序列化安全

**決策**：JSON 優先，Pickle 可選。

**安全措施**：
- 不自動反序列化不信任的數據
- 提供安全模式選項
- 警告文檔

## 向後兼容性

### 1. 語義化版本

遵循語義化版本規範：
- **主版本**：不兼容的 API 變更
- **次版本**：向後兼容的功能添加
- **修訂版本**：向後兼容的錯誤修復

### 2. 棄用策略

```python
def old_method(self):
    warnings.warn(
        "old_method is deprecated, use new_method instead",
        DeprecationWarning,
        stacklevel=2
    )
    return self.new_method()
```

## 未來考量

### 1. 異步支援

**當前決策**：暫不支援異步。

**未來計劃**：
```python
# 未來的異步 API
async with AsyncRedisToolkit() as toolkit:
    await toolkit.setter("key", "value")
    value = await toolkit.getter("key")
```

### 2. Redis Cluster

**當前限制**：僅支援單機 Redis。

**擴展方向**：
- 自動路由
- 分片策略
- 故障轉移

### 3. 更多序列化格式

**計劃支援**：
- MessagePack（更快）
- Protocol Buffers（更小）
- Apache Avro（模式演化）

## 設計權衡總結

| 決策 | 優點 | 缺點 | 適用場景 |
|-----|-----|-----|---------|
| JSON 默認序列化 | 可讀、跨語言 | 不支援所有類型 | 一般應用 |
| 同步 API | 簡單、穩定 | 不適合高並發 | 中小型應用 |
| 內建媒體處理 | 方便、優化 | 增加依賴 | 多媒體應用 |
| 自動重試 | 提高可靠性 | 可能掩蓋問題 | 生產環境 |

## 學到的經驗

### 1. 簡單性的價值

> "簡單性是可靠性的先決條件。" - Edsger W. Dijkstra

保持 API 簡單比添加功能更困難但更有價值。

### 2. 合理的默認值

大多數用戶不會調整配置，因此默認值必須適用於 80% 的用例。

### 3. 漸進式披露

不要一次展示所有功能，讓用戶按需發現高級特性。

### 4. 錯誤的代價

寧可在早期失敗，也不要默默忽略錯誤。

## 結論

Redis Toolkit 的設計決策反映了在簡單性、功能性和性能之間的平衡。通過關注最常見的用例，同時為高級用戶提供擴展點，我們創建了一個既易用又強大的工具。這些決策將隨著用戶反饋和 Redis 生態系統的發展而演進。