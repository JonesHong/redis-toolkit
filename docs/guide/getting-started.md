# 快速開始

只需要 5 分鐘，讓我們一起體驗 Redis Toolkit 的強大功能！

## 🚀 一分鐘安裝

打開終端機，執行以下命令：

```bash
pip install redis-toolkit
```

就這麼簡單！基礎功能已經可以使用了。

## 🎯 第一個範例

### 1. 導入並初始化

```python
from redis_toolkit import RedisToolkit

# 最簡單的初始化方式
toolkit = RedisToolkit()
```

::: tip 提示
預設連接到 `localhost:6379`。如果您的 Redis 在其他位置，請看[配置選項](./configuration.md)。
:::

### 2. 存儲和讀取資料

```python
# 存儲一個字典
user_data = {
    "id": 1001,
    "name": "Alice",
    "email": "alice@example.com",
    "scores": [95, 87, 92]
}
toolkit.setter("user:1001", user_data)

# 讀取資料 - 自動反序列化為原始類型！
retrieved = toolkit.getter("user:1001")
print(retrieved)
# 輸出: {'id': 1001, 'name': 'Alice', 'email': 'alice@example.com', 'scores': [95, 87, 92]}

# 注意：retrieved 是 dict，不是字串！
print(type(retrieved))  # <class 'dict'>
```

### 3. 處理不同資料類型

Redis Toolkit 的強大之處在於自動處理各種 Python 資料類型：

```python
# 列表
toolkit.setter("top_scores", [100, 98, 95, 92, 88])
scores = toolkit.getter("top_scores")  # 返回 list

# 布林值
toolkit.setter("is_active", True)
active = toolkit.getter("is_active")  # 返回 bool，不是字串 "true"

# 數字
toolkit.setter("temperature", 23.5)
temp = toolkit.getter("temperature")  # 返回 float

# 位元組資料
toolkit.setter("binary_data", b"Hello bytes!")
data = toolkit.getter("binary_data")  # 返回 bytes
```

## 📡 快速體驗發布訂閱

### 發送訊息

```python
# 發布者
publisher = RedisToolkit()

# 發送結構化訊息
message = {
    "event": "user_login",
    "user_id": 1001,
    "timestamp": "2024-01-01 10:00:00"
}
publisher.publisher("events", message)
```

### 接收訊息

```python
# 訂閱者
def handle_message(channel, data):
    print(f"收到來自 {channel} 的訊息:")
    print(f"事件: {data['event']}")
    print(f"用戶: {data['user_id']}")

subscriber = RedisToolkit(
    channels=["events"],
    message_handler=handle_message
)

# 訂閱者會自動在背景監聽訊息
```

## 🎨 媒體處理預覽

如果您安裝了媒體處理套件，可以輕鬆處理圖片：

```python
# 需要先安裝: pip install redis-toolkit[cv2]
from redis_toolkit.converters import encode_image, decode_image
import cv2

# 讀取並儲存圖片
img = cv2.imread('photo.jpg')
encoded = encode_image(img, format='jpg', quality=85)
toolkit.setter('user:1001:avatar', encoded)

# 取回圖片
avatar_bytes = toolkit.getter('user:1001:avatar')
avatar_img = decode_image(avatar_bytes)
```

## ✅ 完整範例：用戶系統

讓我們用一個實際的例子來整合所學：

```python
from redis_toolkit import RedisToolkit
from datetime import datetime

class UserCache:
    def __init__(self):
        self.toolkit = RedisToolkit()
    
    def save_user(self, user_id, user_info):
        """儲存用戶資訊"""
        # 添加時間戳記
        user_info['last_updated'] = datetime.now().isoformat()
        
        # 儲存到 Redis
        key = f"user:{user_id}"
        self.toolkit.setter(key, user_info)
        
        # 設定過期時間（選用）
        self.toolkit.client.expire(key, 3600)  # 1小時後過期
    
    def get_user(self, user_id):
        """獲取用戶資訊"""
        return self.toolkit.getter(f"user:{user_id}")
    
    def update_score(self, user_id, new_score):
        """更新用戶分數"""
        user = self.get_user(user_id)
        if user:
            if 'scores' not in user:
                user['scores'] = []
            user['scores'].append(new_score)
            self.save_user(user_id, user)
            return True
        return False

# 使用範例
cache = UserCache()

# 儲存用戶
cache.save_user(1001, {
    "name": "Alice",
    "email": "alice@example.com",
    "level": 5,
    "scores": [95, 87]
})

# 更新分數
cache.update_score(1001, 92)

# 獲取用戶
user = cache.get_user(1001)
print(f"{user['name']} 的分數: {user['scores']}")
# 輸出: Alice 的分數: [95, 87, 92]
```

## 🎉 恭喜！

您已經學會了 Redis Toolkit 的基本使用方法！在短短 5 分鐘內，您了解了：

- ✅ 如何安裝和初始化
- ✅ 自動序列化的強大功能
- ✅ 發布訂閱的基本用法
- ✅ 實際應用範例

## 🚀 下一步

準備深入學習了嗎？這裡有一些建議：

<div class="next-steps">
  <a href="./installation.html" class="next-step-card">
    <h4>📦 詳細安裝指南</h4>
    <p>了解各種安裝選項和依賴管理</p>
  </a>
  
  <a href="./basic-usage.html" class="next-step-card">
    <h4>📖 基礎使用教學</h4>
    <p>深入學習各項功能的使用方法</p>
  </a>
  
  <a href="../advanced/media-processing.html" class="next-step-card">
    <h4>🎨 媒體處理進階</h4>
    <p>探索圖片、音頻、視頻的處理能力</p>
  </a>
</div>

::: tip 學習建議
- 跟著範例動手做，加深理解
- 嘗試修改範例，看看會發生什麼
- 遇到問題時，查看 [FAQ](/reference/faq.html) 或 [疑難排解](/reference/troubleshooting.html)
:::

<style>
.next-steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin: 2rem 0;
}

.next-step-card {
  display: block;
  padding: 1.5rem;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  text-decoration: none;
  color: inherit;
  transition: all 0.2s;
}

.next-step-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border-color: #dc382d;
}

.next-step-card h4 {
  color: #dc382d;
  margin-top: 0;
  margin-bottom: 0.5rem;
}

.next-step-card p {
  color: #666;
  margin: 0;
  font-size: 0.95rem;
}
</style>