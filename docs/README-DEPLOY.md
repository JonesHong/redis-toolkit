# 部署文檔到 GitHub Pages

本文檔說明如何設置自動部署 VuePress 文檔到 GitHub Pages。

## 設置步驟

### 1. 啟用 GitHub Pages

1. 進入您的 GitHub 倉庫設置（Settings）
2. 找到 "Pages" 部分
3. 在 "Source" 下選擇 "GitHub Actions"

### 2. 確認工作流程權限

1. 進入 Settings > Actions > General
2. 在 "Workflow permissions" 部分
3. 選擇 "Read and write permissions"
4. 勾選 "Allow GitHub Actions to create and approve pull requests"
5. 點擊 "Save"

### 3. 觸發部署

部署會在以下情況自動觸發：

- 推送到 `main` 或 `master` 分支
- 修改了 `docs/` 目錄下的任何文件
- 修改了 `.github/workflows/deploy-docs.yml` 文件

您也可以手動觸發：

1. 進入 Actions 頁面
2. 選擇 "Deploy Docs to GitHub Pages" 工作流程
3. 點擊 "Run workflow"

### 4. 訪問您的文檔

部署成功後，您可以通過以下 URL 訪問文檔：

```
https://[您的用戶名].github.io/redis-toolkit/
```

例如：`https://JonesHong.github.io/redis-toolkit/`

## 本地測試

在部署前，建議先在本地測試：

```bash
cd docs
npm install
npm run build
npm run dev
```

## 自定義域名（可選）

如果您想使用自定義域名：

1. 在 `docs/.vuepress/public/` 目錄下創建 `CNAME` 文件
2. 在文件中寫入您的域名（例如：`docs.example.com`）
3. 在 DNS 提供商處設置 CNAME 記錄指向 `[您的用戶名].github.io`

## 故障排除

### 構建失敗

- 檢查 Actions 頁面的錯誤日誌
- 確保所有依賴都已正確安裝
- 在本地運行 `npm run build` 測試

### 404 錯誤

- 確保 `base` 配置與倉庫名稱一致
- 檢查 GitHub Pages 是否已啟用
- 等待幾分鐘讓 GitHub Pages 完成部署

### 樣式或資源加載失敗

- 確保所有資源路徑使用相對路徑
- 檢查 `base` 配置是否正確
- 清除瀏覽器快取後重試

## 更新日誌

文檔更新後，GitHub Actions 會自動：

1. 構建最新的文檔
2. 上傳到 GitHub Pages
3. 更新線上版本

整個過程通常需要 2-5 分鐘。