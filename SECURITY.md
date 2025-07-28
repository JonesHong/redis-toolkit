# Security Policy

## 安全更新公告

### 重要：Pickle 序列化已完全移除

為了確保 Redis Toolkit 的安全性，我們已在最新版本中**完全移除** pickle 序列化功能。這個決定是為了防止潛在的遠程代碼執行（RCE）漏洞。

#### 受影響的版本
- 所有早期開發版本（< 0.2.0）

#### 修復版本
- 0.2.0 及以上版本

### 變更內容

1. **移除 pickle 序列化**
   - 不再使用 `pickle.dumps()` 和 `pickle.loads()`
   - 所有序列化現在都基於安全的 JSON 格式

2. **支援的數據類型**
   - `None`
   - `bool`
   - `int`, `float`
   - `str`
   - `bytes`, `bytearray` (使用 Base64 編碼)
   - `dict`, `list`, `tuple`
   - `numpy.ndarray` (使用安全的 JSON 格式)

3. **不支援的類型**
   - 自定義類實例
   - 函數對象
   - 其他複雜 Python 對象

### 遷移指南

如果您的應用程序依賴於序列化複雜對象：

1. **檢查您的數據類型**
   ```python
   from redis_toolkit.utils.serializers import serialize_value, SerializationError
   
   try:
       serialize_value(your_data)
   except SerializationError:
       # 需要調整數據格式
   ```

2. **替代方案**
   - 將自定義對象轉換為字典
   - 使用 JSON 兼容的數據結構
   - 對於二進制數據，我們會自動使用 Base64 編碼

### 報告安全問題

如果您發現任何安全漏洞，請通過以下方式聯繫我們：
- 發送郵件至：security@redis-toolkit.example.com
- 使用 GitHub Security Advisories

請**不要**在公開的 issue 中報告安全問題。

## 安全最佳實踐

使用 Redis Toolkit 時，請遵循以下安全建議：

1. **限制 Redis 訪問**
   - 使用強密碼
   - 限制網絡訪問
   - 使用 TLS/SSL 連接

2. **驗證輸入數據**
   - 檢查數據大小
   - 驗證數據類型
   - 使用白名單方法

3. **監控異常活動**
   - 記錄所有操作
   - 監控大量數據寫入
   - 設置告警機制

## 版本支持

| 版本 | 支持狀態 | 安全更新 |
|------|---------|----------|
| 0.2.x | ✅ 活躍支持 | ✅ |
| < 0.2.0 | ❌ 不支持 | ❌ |

## 致謝

感謝所有幫助我們改進 Redis Toolkit 安全性的貢獻者。