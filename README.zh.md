# Redis Toolkit  

![Python 版本](https://img.shields.io/badge/python-3.7+-blue.svg)  
![Redis 版本](https://img.shields.io/badge/redis-4.0+-red.svg)  
![授權](https://img.shields.io/badge/license-MIT-green.svg)  

一套增強型 Redis 工具，可簡化多種資料類型操作、發布訂閱，以及音視頻緩衝區處理。  

## ✨ 功能特色

- 🚀 **多資料類型支援**  
  自動序列化／反序列化 `dict`、`list`、`bool`、Base64 JSON bytes、`int`/`float` 以及 NumPy 陣列 :contentReference[oaicite:1]{index=1}  
- 🎵 **音視頻緩衝優化**  
  專為音頻／視頻位元組緩衝設計  
- 📡 **簡易發布／訂閱**  
  內建 JSON 處理的 pub/sub API  
- 🔧 **彈性配置**  
  支援自訂 redis-py 客戶端或內建連線設定  
- 🛡️ **高韌性**  
  內建重試裝飾器（支援 `ConnectionError`、`TimeoutError`）及健康檢查  
- 📦 **批量操作**  
  高效 `batch_set` / `batch_get`  
- 🔄 **向後相容**  
  `RedisCore` 別名仍可使用  

## 📦 安裝

```bash
pip install redis-toolkit
```

## 🚀 快速上手

### 基本用法

```python
from redis_toolkit import RedisToolkit

toolkit = RedisToolkit()

# 設定多種資料
toolkit.setter("user", {"name": "小明", "age": 25, "active": True})
toolkit.setter("scores", [95, 87, 92, 88])
toolkit.setter("flag", True)

# 自動反序列化取得
user   = toolkit.getter("user")    # {'name': '小明', 'age': 25, 'active': True}
scores = toolkit.getter("scores")  # [95, 87, 92, 88]
flag   = toolkit.getter("flag")    # True

# 批量操作
data    = {"a": 1, "b": [2, 3, 4], "c": "hello"}
toolkit.batch_set(data)
results = toolkit.batch_get(["a", "b", "c"])
```

### 使用外部 Redis 實例

```python
import redis
from redis_toolkit import RedisToolkit

custom = redis.Redis(host="localhost", port=6379, db=1)
toolkit = RedisToolkit(redis_client=custom)

# 同時使用增強功能與原生命令
toolkit.setter("x", 123)
toolkit.client.lpush("list", "item1", "item2")
```

### 發布／訂閱

```python
from redis_toolkit import RedisToolkit

def handler(channel, msg):
    print(f"[{channel}] 收到：", msg)

sub = RedisToolkit(channels=["news"], message_handler=handler)
pub = RedisToolkit()
pub.publisher("news", {"headline": "最新消息", "time": "2025-06-23T10:00:00Z"})
```

### 音視頻緩衝範例

```python
import numpy as np
from redis_toolkit import RedisToolkit

audio = np.random.randn(44100).astype(np.float32)
toolkit = RedisToolkit()
toolkit.setter("audio_buf", audio.tobytes())

raw = toolkit.getter("audio_buf")
recovered = np.frombuffer(raw, np.float32)
assert np.array_equal(audio, recovered)
```

### 上下文管理器

```python
from redis_toolkit import RedisToolkit, RedisOptions

with RedisToolkit(options=RedisOptions(is_logger_info=False)) as tk:
    tk.setter("temp", {"x": 1})
    print(tk.getter("temp"))
# 離開時自動 cleanup()
```

## ⚙️ 配置選項

```python
from redis_toolkit import RedisToolkit, RedisOptions, RedisConnectionConfig

config = RedisConnectionConfig(host="...", port=6379, db=2)
options = RedisOptions(
    is_logger_info=True,
    max_log_size=256,
    max_retries=5,
    retry_delay=1.5,
    connection_timeout=10
)

toolkit = RedisToolkit(config=config, options=options)
```

## 🔄 從 RedisCore 遷移

```diff
- from your_module import RedisCore
- redis_core = RedisCore(channels=…, message_handler=…)
+ from redis_toolkit import RedisToolkit
+ toolkit = RedisToolkit(channels=…, message_handler=…)
# （別名 RedisCore 依舊可用）
```

## 📋 系統需求

* Python >= 3.7
* Redis >= 4.0
* redis-py >= 4.0

## 🤝 貢獻指南

1. Fork 專案
2. 建立分支 (`git checkout -b feature/...`)
3. 提交修改 (`git commit -m "Add feature"`)
4. 開啟 Pull Request

## 📄 授權

MIT 授權 — 詳見 [LICENSE](LICENSE)

## 📞 聯絡

* **文件**: [https://redis-toolkit.readthedocs.io](https://redis-toolkit.readthedocs.io)
* **Issues**: [https://github.com/yourusername/redis-toolkit/issues](https://github.com/yourusername/redis-toolkit/issues)
* **討論**: [https://github.com/yourusername/redis-toolkit/discussions](https://github.com/yourusername/redis-toolkit/discussions)

