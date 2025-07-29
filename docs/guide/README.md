# 使用指南

歡迎使用 Redis Toolkit！本指南將帶您從零開始，逐步掌握這個強大工具的使用方法。

## 📚 學習路徑

我們為不同程度的使用者設計了清晰的學習路徑：

### 🎯 新手入門（建議 1-2 小時）

1. **[快速開始](./getting-started.md)** - 5 分鐘上手體驗
   - 最簡單的安裝方式
   - 第一個 Hello World 範例
   - 基本概念快速了解

2. **[安裝指南](./installation.md)** - 詳細的安裝說明
   - 系統需求
   - 各種安裝方式
   - 可選依賴說明
   - 常見問題解決

3. **[基礎使用](./basic-usage.md)** - 掌握核心功能
   - 基本的存取操作
   - 資料類型處理
   - 簡單的配置

### 🚀 進階學習（建議 2-4 小時）

4. **[序列化功能](./serialization.md)** - 深入了解自動序列化
   - 支援的資料類型
   - 自定義序列化
   - 效能考量

5. **[發布訂閱](./pubsub.md)** - 掌握訊息傳遞
   - Pub/Sub 基礎
   - 訊息處理器設計
   - 多頻道訂閱

6. **[配置選項](./configuration.md)** - 客製化您的工具
   - 連線配置
   - 進階選項
   - 最佳實踐

## 🎯 選擇您的起點

<div class="learning-paths">
  <div class="path-card">
    <h3>🆕 完全新手</h3>
    <p>第一次接觸 Redis？</p>
    <a href="./getting-started.html" class="path-link">從快速開始學起 →</a>
  </div>
  
  <div class="path-card">
    <h3>💻 有經驗的開發者</h3>
    <p>熟悉 Redis 基礎操作？</p>
    <a href="./serialization.html" class="path-link">直接了解進階功能 →</a>
  </div>
  
  <div class="path-card">
    <h3>🏃 趕時間？</h3>
    <p>需要快速上手？</p>
    <a href="./basic-usage.html" class="path-link">看看實用範例 →</a>
  </div>
</div>

## 💡 學習建議

::: tip 最佳學習方式
1. **動手實作**：每個章節都有可執行的程式碼範例
2. **循序漸進**：按照建議的順序學習，避免跳過基礎
3. **實際應用**：嘗試將學到的功能應用到您的專案中
:::

::: warning 注意事項
- 確保您的 Redis 服務正在運行
- Python 版本需要 >= 3.7
- 某些進階功能需要額外的依賴套件
:::

## 🔗 快速連結

- **遇到問題？** 查看 [疑難排解](/reference/troubleshooting.html)
- **需要範例？** 瀏覽 [範例程式碼](/examples/)
- **API 細節？** 參考 [API 文檔](/api/)

<style>
.learning-paths {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin: 2rem 0;
}

.path-card {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1.5rem;
  text-align: center;
  transition: transform 0.2s, box-shadow 0.2s;
}

.path-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.path-card h3 {
  color: #dc382d;
  margin-top: 0;
  margin-bottom: 0.5rem;
}

.path-card p {
  color: #666;
  margin-bottom: 1rem;
}

.path-link {
  display: inline-block;
  color: #dc382d;
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border: 2px solid #dc382d;
  border-radius: 4px;
  transition: all 0.2s;
}

.path-link:hover {
  background: #dc382d;
  color: white;
}
</style>