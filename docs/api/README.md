# API 參考

歡迎查閱 Redis Toolkit 的 API 參考文檔。這裡提供所有公開類別、方法和函數的詳細說明。

## 📚 API 文檔組織

<div class="api-categories">
  <div class="api-card">
    <h3>🔧 核心 API</h3>
    <p>RedisToolkit 主類別的所有方法</p>
    <ul>
      <li>初始化與配置</li>
      <li>基本操作方法</li>
      <li>批次操作</li>
      <li>發布訂閱</li>
    </ul>
    <a href="./core.html" class="api-link">查看文檔 →</a>
  </div>
  
  <div class="api-card">
    <h3>🎨 轉換器 API</h3>
    <p>媒體處理相關的轉換器</p>
    <ul>
      <li>圖片轉換器</li>
      <li>音頻轉換器</li>
      <li>視頻轉換器</li>
      <li>通用介面</li>
    </ul>
    <a href="./converters.html" class="api-link">查看文檔 →</a>
  </div>
  
  <div class="api-card">
    <h3>⚙️ 配置 API</h3>
    <p>配置類別和選項</p>
    <ul>
      <li>RedisConnectionConfig</li>
      <li>RedisOptions</li>
      <li>預設配置</li>
      <li>驗證方法</li>
    </ul>
    <a href="./options.html" class="api-link">查看文檔 →</a>
  </div>
  
  <div class="api-card">
    <h3>🛠️ 工具函數</h3>
    <p>實用工具和輔助函數</p>
    <ul>
      <li>序列化函數</li>
      <li>重試裝飾器</li>
      <li>驗證工具</li>
      <li>異常類別</li>
    </ul>
    <a href="./utilities.html" class="api-link">查看文檔 →</a>
  </div>
</div>

## 🎯 快速導航

### 最常用的 API

```python
# 核心類別
from redis_toolkit import RedisToolkit

# 配置類別
from redis_toolkit import RedisConnectionConfig, RedisOptions

# 轉換器函數
from redis_toolkit.converters import (
    encode_image, decode_image,
    encode_audio, decode_audio,
    get_converter
)

# 工具函數
from redis_toolkit.utils import serialize_value, deserialize_value
from redis_toolkit.utils import with_retry

# 異常類別
from redis_toolkit.exceptions import (
    RedisToolkitError,
    SerializationError,
    ValidationError
)
```

## 📖 API 使用範例

### 基本初始化

```python
# 方式 1：使用預設配置
toolkit = RedisToolkit()

# 方式 2：自定義配置
config = RedisConnectionConfig(host='localhost', port=6379)
options = RedisOptions(is_logger_info=True)
toolkit = RedisToolkit(config=config, options=options)

# 方式 3：使用現有 Redis 客戶端
import redis
client = redis.Redis()
toolkit = RedisToolkit(redis=client)
```

### 常用操作

```python
# 存取資料
toolkit.setter("key", {"data": "value"})
data = toolkit.getter("key")

# 批次操作
batch_data = {"key1": "value1", "key2": "value2"}
toolkit.batch_set(batch_data)
results = toolkit.batch_get(["key1", "key2"])

# 發布訂閱
toolkit.publisher("channel", {"message": "Hello"})
```

### 媒體處理

```python
# 圖片處理
img_bytes = encode_image(image_array, format='jpg')
decoded_img = decode_image(img_bytes)

# 使用轉換器
converter = get_converter('image')
resized = converter.resize(image_array, width=800)
```

## 🔍 API 設計原則

### 1. 簡單直觀

我們的 API 設計遵循「簡單優先」原則：

```python
# ✅ 簡單明瞭
toolkit.setter("key", value)
toolkit.getter("key")

# ❌ 過度複雜
toolkit.storage.persistence.set_with_options("key", value, options={...})
```

### 2. 一致性

所有 API 保持一致的命名和行為模式：

- `setter` / `getter` - 基本存取
- `batch_set` / `batch_get` - 批次操作
- `encode_*` / `decode_*` - 編碼解碼

### 3. 錯誤處理

統一的異常體系，便於錯誤處理：

```python
try:
    toolkit.setter("key", problematic_value)
except SerializationError:
    # 處理序列化錯誤
except ValidationError:
    # 處理驗證錯誤
except RedisToolkitError:
    # 處理其他錯誤
```

## 📊 API 版本和相容性

### 版本策略

我們遵循語意化版本控制（Semantic Versioning）：

- **主版本**：不相容的 API 變更
- **次版本**：向下相容的功能新增
- **修訂版本**：向下相容的錯誤修正

### 棄用政策

當 API 需要棄用時：

1. 在文檔中標記為 `@deprecated`
2. 發出棄用警告
3. 至少保留兩個次版本
4. 提供遷移指南

```python
# 棄用範例
@deprecated("使用 toolkit.setter 替代")
def set_value(key, value):
    warnings.warn("set_value 已棄用，請使用 setter", DeprecationWarning)
    return toolkit.setter(key, value)
```

## 🎯 API 最佳實踐

### 1. 使用類型提示

```python
from typing import Dict, Any, Optional

def process_data(
    key: str,
    data: Dict[str, Any],
    ttl: Optional[int] = None
) -> bool:
    """處理並儲存資料"""
    return toolkit.setter(key, data, ex=ttl)
```

### 2. 參數驗證

```python
# 使用配置類別的驗證功能
config = RedisConnectionConfig(port=6379)
config.validate()  # 確保配置有效

# 自定義驗證
if not isinstance(data, (dict, list)):
    raise ValidationError("資料必須是 dict 或 list")
```

### 3. 資源管理

```python
# 使用 context manager
with RedisToolkit() as toolkit:
    toolkit.setter("key", "value")
    # 自動清理資源

# 手動清理
toolkit = RedisToolkit()
try:
    # 使用 toolkit
finally:
    toolkit.cleanup()
```

## 📚 深入學習

根據您的需求，選擇相應的 API 文檔深入學習：

<div class="api-nav">
  <a href="./core.html" class="nav-item">
    <span class="icon">🔧</span>
    <span>核心 API</span>
  </a>
  <a href="./converters.html" class="nav-item">
    <span class="icon">🎨</span>
    <span>轉換器 API</span>
  </a>
  <a href="./options.html" class="nav-item">
    <span class="icon">⚙️</span>
    <span>配置 API</span>
  </a>
  <a href="./utilities.html" class="nav-item">
    <span class="icon">🛠️</span>
    <span>工具函數</span>
  </a>
</div>

::: tip 提示
- 使用 IDE 的自動完成功能探索 API
- 查看原始碼了解實現細節
- 參考範例程式碼學習最佳實踐
:::

<style>
.api-categories {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin: 2rem 0;
}

.api-card {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1.5rem;
  transition: all 0.2s;
}

.api-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border-color: #dc382d;
}

.api-card h3 {
  color: #dc382d;
  margin-top: 0;
  margin-bottom: 0.5rem;
}

.api-card p {
  color: #666;
  margin-bottom: 1rem;
}

.api-card ul {
  margin: 0 0 1rem 0;
  padding-left: 1.2rem;
  color: #555;
  font-size: 0.9rem;
}

.api-link {
  display: inline-block;
  color: #dc382d;
  text-decoration: none;
  font-weight: 500;
  transition: transform 0.2s;
}

.api-link:hover {
  transform: translateX(3px);
}

.api-nav {
  display: flex;
  gap: 1rem;
  margin: 2rem 0;
  flex-wrap: wrap;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.8rem 1.5rem;
  background: #dc382d;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  transition: all 0.2s;
}

.nav-item:hover {
  background: #e85d52;
  transform: translateY(-2px);
}

.nav-item .icon {
  font-size: 1.2rem;
}
</style>