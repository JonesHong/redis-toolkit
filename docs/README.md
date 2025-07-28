---
home: true
heroImage: /images/logo.png
heroText: Redis Toolkit
tagline: 簡化 Redis 操作的 Python 工具包
actionText: 快速開始 →
actionLink: /tutorials/getting-started
features:
  - title: 🚀 簡單易用
    details: 提供直觀的 API，讓 Redis 操作變得簡單。支援自動序列化/反序列化，無需手動處理數據轉換。
  - title: 🎯 功能豐富
    details: 內建批次操作、發布/訂閱、媒體處理等進階功能。支援圖片、音頻、視頻等多媒體數據的存儲和傳輸。
  - title: ⚡ 高性能
    details: 優化的批次操作提供 5-20 倍性能提升。智能連接池管理，確保最佳的資源利用率。
footer: MIT Licensed | Copyright © 2025 Redis Toolkit Team
---

## 安裝

```bash
pip install redis-toolkit
```

## 快速開始

```python
from redis_toolkit import RedisToolkit

# 創建 RedisToolkit 實例
toolkit = RedisToolkit()

# 存儲數據（自動序列化）
toolkit.setter("user:1", {
    "name": "Alice",
    "age": 30,
    "email": "alice@example.com"
})

# 讀取數據（自動反序列化）
user = toolkit.getter("user:1")
print(user)  # {'name': 'Alice', 'age': 30, 'email': 'alice@example.com'}
```

## 主要特性

### 🔄 自動序列化
支援 Python 常見數據類型的自動序列化和反序列化，包括字典、列表、NumPy 數組等。

### 📦 批次操作
提供高效的批次操作接口，大幅提升大量數據的處理性能。

### 📡 發布/訂閱
簡化的發布訂閱接口，支援自動序列化的消息傳遞。

### 🎨 媒體處理
內建圖片、音頻、視頻轉換器，輕鬆處理多媒體數據。

### 🔁 重試機制
智能重試機制，自動處理網絡異常和臨時錯誤。

### 🏊 連接池管理
優化的連接池管理，支援多線程環境下的高效連接複用。

## 文檔結構

- **[教程](/tutorials/getting-started)** - 學習如何使用 Redis Toolkit
- **[操作指南](/how-to/batch-operations)** - 解決具體問題的指南
- **[API 參考](/reference/api/core)** - 完整的 API 文檔
- **[深入理解](/explanation/architecture)** - 理解設計理念和架構

## 快速鏈接

- [GitHub 倉庫](https://github.com/yourusername/redis-toolkit)
- [問題回報](https://github.com/yourusername/redis-toolkit/issues)
- [更新日誌](/CHANGELOG)
- [貢獻指南](https://github.com/yourusername/redis-toolkit/blob/main/CONTRIBUTING.md)