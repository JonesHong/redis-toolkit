# Redis Toolkit v0.3.2 Release Notes

## 📚 文檔增強版本 (Documentation Enhancement Release)

### 🌐 主要功能

#### 完整的 VuePress 文檔系統
- 實現了基於 VuePress 的完整文檔系統，支援雙語
- 繁體中文（預設）和英文版本
- 現代化、響應式的文檔網站，採用 Redis 主題風格

#### 多語言支援 (i18n)
- 完整的國際化支援，可切換語言
- 特定語言的搜尋過濾 - 搜尋結果現在會尊重當前語言
- 正確的 URL 結構：`/` 為中文，`/en/` 為英文
- 所有內部連結都已正確本地化

### 📖 文檔結構

#### 新的文檔分類：
1. **指南 (Guide)** - 入門、安裝、基本使用、核心功能
2. **進階 (Advanced)** - 媒體處理、批次操作、效能調優
3. **API 參考 (API Reference)** - 完整的 API 文檔
4. **範例 (Examples)** - 從基礎到實際應用的程式碼範例

#### 關鍵文檔檔案：
- 所有功能的完整指南
- 詳細說明的 API 參考
- 實際應用範例，包括聊天室、任務佇列和通知系統
- GitHub Pages 的部署文檔

### 🛠️ 技術改進

#### 建構系統
- 添加 VuePress 建構配置
- GitHub Actions 工作流程，用於自動文檔部署
- 優化的建構過程，具有正確的基礎 URL 配置

#### 開發者體驗
- 添加 CLAUDE.md 用於 AI 輔助開發指南
- 結構化的文檔，具有清晰的導航
- 具有語法高亮和複製功能的程式碼範例

### 🔧 配置更新
- 更新 `.gitignore` 以處理 VuePress 產物
- 增強 GitHub Pages 的部署腳本
- 版本升級至 0.3.2

### 🐛 錯誤修復
- 修復中文文檔中的編碼問題
- 解決多語言設置中的導航和路由問題
- 修正搜尋功能以按語言過濾

### 📝 文檔翻譯
所有文檔都已在繁體中文和英文之間進行 1:1 忠實翻譯，包括：
- 完整的 API 參考
- 所有程式碼範例
- 配置選項
- 錯誤訊息和提示

### 🚀 從 v0.3.1 升級

此版本完全向後兼容，無需修改程式碼。主要是文檔改進。

```bash
pip install redis-toolkit==0.3.2
```

---

此版本完全專注於文檔改進，使 Redis Toolkit 對中文和英文開發者都更加易於使用。新的 VuePress 文檔提供了專業、可搜尋和使用者友好的方式來學習和參考工具包。

發布日期：2025-07-29