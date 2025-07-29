---
home: true
heroImage: /hero.png
heroText: Redis Toolkit
tagline: 強大的 Redis 工具包，讓資料處理變得簡單優雅
actionText: 快速開始 →
actionLink: /guide/getting-started
features:
- title: 🎯 智慧序列化
  details: 自動處理 dict、list、numpy 陣列等多種資料類型，無需手動轉換。採用安全的 JSON 序列化，避免 pickle 的安全風險。
- title: 🔐 安全優先
  details: 拒絕使用 pickle，全面採用 JSON 序列化機制。內建輸入驗證和錯誤處理，確保資料操作的安全性。
- title: 🎵 媒體處理
  details: 內建圖片、音頻、視頻轉換器，輕鬆處理多媒體資料。支援 OpenCV、SciPy 等主流框架。
footer: MIT Licensed | Copyright © 2024 Redis Toolkit Team
---

<div class="features-extra">
  <div class="feature">
    <h3>🚀 極速上手</h3>
    <p>5 分鐘內完成安裝並運行第一個範例，立即體驗 Redis 的強大功能。</p>
  </div>
  <div class="feature">
    <h3>📡 發布訂閱</h3>
    <p>簡化的 Pub/Sub API，自動處理 JSON 序列化，讓訊息傳遞變得輕鬆。</p>
  </div>
  <div class="feature">
    <h3>⚡ 高效能</h3>
    <p>內建連接池管理、批次操作、重試機制，確保高效穩定的 Redis 操作。</p>
  </div>
</div>

## 🎯 快速安裝

<CodeGroup>
<CodeGroupItem title="基礎安裝">

```bash
pip install redis-toolkit
```

</CodeGroupItem>

<CodeGroupItem title="包含圖片處理">

```bash
pip install redis-toolkit[cv2]
```

</CodeGroupItem>

<CodeGroupItem title="完整安裝">

```bash
pip install redis-toolkit[all]
```

</CodeGroupItem>
</CodeGroup>

## 📝 簡單範例

```python
from redis_toolkit import RedisToolkit

# 初始化
toolkit = RedisToolkit()

# 儲存各種資料類型
toolkit.setter("user", {"name": "Alice", "age": 25})
toolkit.setter("scores", [95, 87, 92])
toolkit.setter("active", True)

# 自動反序列化
user = toolkit.getter("user")      # 返回 dict
scores = toolkit.getter("scores")  # 返回 list
active = toolkit.getter("active")  # 返回 bool
```

## 🎨 媒體處理範例

```python
from redis_toolkit import RedisToolkit
from redis_toolkit.converters import encode_image, decode_image
import cv2

toolkit = RedisToolkit()

# 處理圖片
img = cv2.imread('photo.jpg')
img_bytes = encode_image(img, format='jpg', quality=90)
toolkit.setter('my_image', img_bytes)

# 取回並解碼
retrieved = toolkit.getter('my_image')
decoded_img = decode_image(retrieved)
```

## 🌟 為什麼選擇 Redis Toolkit？

<div class="why-choose">
  <div class="reason">
    <h4>簡單直觀</h4>
    <p>API 設計簡潔，學習曲線平緩，讓您專注於業務邏輯而非底層實現。</p>
  </div>
  <div class="reason">
    <h4>功能完整</h4>
    <p>從基礎操作到進階功能，從資料存取到媒體處理，一個工具包滿足所有需求。</p>
  </div>
  <div class="reason">
    <h4>穩定可靠</h4>
    <p>完善的錯誤處理、自動重試機制、連接池管理，確保生產環境的穩定運行。</p>
  </div>
  <div class="reason">
    <h4>社群活躍</h4>
    <p>持續更新維護，快速響應問題，歡迎貢獻代碼，共同打造更好的工具。</p>
  </div>
</div>

---

<div class="getting-started-cta">
  <h2>準備好開始了嗎？</h2>
  <p>跟隨我們的指南，輕鬆掌握 Redis Toolkit 的強大功能</p>
  <a href="/guide/getting-started" class="action-button">立即開始 →</a>
</div>