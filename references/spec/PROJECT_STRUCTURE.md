# Redis Toolkit 專案檔案架構

## 專案概述

Redis Toolkit 是一個專為 Python 開發者設計的 Redis 操作增強函式庫，旨在簡化常見的 Redis 操作場景，特別是針對多媒體數據（圖片、音頻、視頻）的傳輸與處理。本專案提供高層次的抽象，減少樣板代碼和重複工作，同時確保連接可靠性和數據安全性。

## 檔案架構

```
redis-toolkit/
├── redis_toolkit/                  # 主要套件目錄
│   ├── __init__.py                # 套件初始化，匯出主要類別和函數
│   ├── core.py                    # 核心類別 RedisToolkit（Facade 模式）
│   ├── options.py                 # RedisOptions 配置管理（dataclass）
│   ├── exceptions.py              # 自定義異常類別
│   ├── pool_manager.py            # 連接池管理器（Singleton 模式）
│   ├── converters/                # 數據轉換器模組（Abstract Factory 模式）
│   │   ├── __init__.py           # 轉換器註冊和管理
│   │   ├── errors.py             # 轉換器錯誤處理和依賴檢查
│   │   ├── image.py              # 圖片轉換器（支援 JPEG、PNG、WebP）
│   │   ├── audio.py              # 音頻轉換器（支援 WAV、FLAC、MP3）
│   │   └── video.py              # 視頻轉換器（基本視頻支援）
│   └── utils/                     # 工具函數模組
│       ├── __init__.py           
│       ├── serializers.py        # 數據序列化/反序列化（JSON 基礎）
│       └── retry.py              # 重試裝飾器（指數退避策略）
├── tests/                         # 測試套件
│   ├── __init__.py
│   ├── conftest.py               # pytest 配置和 fixtures
│   ├── test_core.py              # 核心功能測試
│   ├── test_serializers.py       # 序列化測試
│   ├── test_pubsub.py            # 發布訂閱測試
│   ├── test_pubsub_thread.py     # 線程管理測試
│   ├── test_conveters.py         # 轉換器測試
│   ├── test_converter_errors.py  # 轉換器錯誤處理測試
│   ├── test_batch_operations.py  # 批次操作測試
│   ├── test_input_validation.py  # 輸入驗證測試
│   └── test_pool_manager.py      # 連接池測試
├── examples/                      # 使用範例
│   ├── basic_usage.py            # 基礎使用示例
│   ├── batch_operations.py       # 批次操作示例
│   ├── pubsub_example.py         # 發布訂閱示例
│   ├── image_transfer.py         # 圖片傳輸示例
│   ├── audio_streaming.py        # 音頻串流示例
│   └── video_caching.py          # 視頻緩存示例
├── docs/                         # 文檔目錄
│   ├── API.md                   # API 參考文檔
│   ├── QUICKSTART.md            # 快速入門指南
│   ├── EXAMPLES.md              # 詳細使用範例
│   ├── SECURITY.md              # 安全性說明
│   └── CHANGELOG.md             # 變更日誌
├── references/                   # 參考文檔
│   ├── ARCHITECTURE_ANALYSIS_UPDATED.md  # 架構分析報告
│   └── spec/                    # 規格文檔
│       ├── SRS.md              # 軟體需求規格
│       ├── PRINCIPLE.md        # 設計原則
│       └── PROJECT_STRUCTURE.md # 本文件
├── pyproject.toml               # 專案配置（PEP 518）
├── setup.py                     # 安裝配置
├── requirements.txt             # 基本依賴
├── requirements-dev.txt         # 開發依賴
├── .gitignore                  # Git 忽略規則
├── LICENSE                     # MIT 授權條款
├── README.md                   # 專案說明
└── SRS.md                      # 軟體需求規格文檔

```

## 模組詳細說明

### 核心模組 (Core Module)

#### `redis_toolkit/core.py`
- **職責**：實現 Facade 模式，提供統一的高層次接口
- **主要類別**：`RedisToolkit`
- **核心功能**：
  - 基本操作：`setter()`, `getter()`, `delete()`, `exists()`
  - 批次操作：`batch_set()`, `batch_get()`, `batch_delete()`
  - 發布訂閱：`publisher()`, `start_subscriber()`, `stop_subscriber()`
  - 連接管理：`health_check()`, `cleanup()`
- **設計特點**：
  - 自動處理序列化/反序列化
  - 內建重試機制
  - 輸入驗證保護
  - 線程安全設計

#### `redis_toolkit/options.py`
- **職責**：配置管理和參數驗證
- **主要類別**：`RedisOptions` (dataclass)
- **配置項目**：
  - 連接參數：host, port, db, password
  - 性能參數：max_retries, retry_delay, timeout
  - 安全參數：max_value_size, max_key_length, enable_validation
  - 連接池參數：use_connection_pool, max_connections
- **設計特點**：使用 dataclass 確保類型安全

#### `redis_toolkit/pool_manager.py`
- **職責**：管理共享連接池，減少資源消耗
- **主要類別**：`ConnectionPoolManager` (Singleton)
- **核心功能**：
  - 基於連接參數的池緩存
  - 連接池統計信息
  - 資源清理機制
- **設計特點**：單例模式確保全局唯一

### 轉換器模組 (Converters Module)

#### `redis_toolkit/converters/__init__.py`
- **職責**：轉換器註冊和管理
- **核心功能**：
  - 動態載入可用轉換器
  - 依賴檢查和錯誤處理
  - 提供便利函數（如 `encode_image()`, `decode_image()`）
- **設計模式**：Abstract Factory + Registry

#### `redis_toolkit/converters/errors.py`
- **職責**：轉換器錯誤處理和依賴診斷
- **主要類別**：
  - `ConverterDependencyError`：依賴缺失錯誤
  - `ConverterNotAvailableError`：轉換器不可用錯誤
- **核心功能**：
  - `check_dependencies()`：檢查所有轉換器依賴
  - `format_dependency_report()`：生成依賴報告

#### 具體轉換器實現
- **image.py**：處理圖片編解碼（OpenCV）
- **audio.py**：處理音頻編解碼（NumPy + SciPy/soundfile）
- **video.py**：處理視頻檔案（OpenCV）

### 工具模組 (Utils Module)

#### `redis_toolkit/utils/serializers.py`
- **職責**：處理 Python 對象的序列化和反序列化
- **核心功能**：
  - 支援原生類型（str, int, float, bool, list, dict）
  - 支援日期時間對象
  - Base64 編碼二進制數據
  - 使用 JSON 確保安全性（禁用 pickle）

#### `redis_toolkit/utils/retry.py`
- **職責**：實現重試機制
- **核心功能**：
  - `@with_retry` 裝飾器
  - 指數退避策略
  - 可配置重試次數和延遲

### 異常處理 (`exceptions.py`)
- **RedisToolkitError**：基礎異常類別
- **ConnectionError**：連接相關錯誤
- **SerializationError**：序列化錯誤
- **ValidationError**：輸入驗證錯誤
- **ConversionError**：轉換器錯誤

## 設計特點

### 1. 遵循 SOLID 原則
- **單一職責**：每個模組和類別都有明確的單一職責
- **開放封閉**：通過抽象基類和註冊機制支援擴展
- **里氏替換**：轉換器可以安全地替換使用
- **接口隔離**：精簡的公開 API，隱藏實現細節
- **依賴反轉**：核心模組依賴抽象而非具體實現

### 2. 設計模式應用
- **Facade 模式**：`RedisToolkit` 提供統一接口
- **Singleton 模式**：`ConnectionPoolManager` 確保唯一實例
- **Abstract Factory**：轉換器系統的擴展機制
- **Decorator 模式**：`@with_retry` 重試裝飾器
- **Strategy 模式**：序列化策略的靈活切換

### 3. 安全性設計
- 完全移除 pickle 序列化，防止 RCE 攻擊
- 輸入驗證機制，防止資源耗盡
- 清晰的錯誤信息，不洩露敏感信息

### 4. 可觀察性
- 使用 logging 模組記錄關鍵操作
- 詳細的 docstring 說明預期行為
- 錯誤信息包含解決方案建議

## 開發流程建議

### 1. 環境設置
```bash
# 克隆專案
git clone https://github.com/yourusername/redis-toolkit.git
cd redis-toolkit

# 創建虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安裝開發依賴
pip install -e ".[dev]"
```

### 2. 開發規範
- 遵循 PEP 8 編碼規範
- 使用 type hints 提升代碼可讀性
- 每個公開函數都需要完整的 docstring
- 提交前運行測試和 linter

### 3. 測試策略
```bash
# 運行所有測試
pytest

# 運行特定測試
pytest tests/test_core.py

# 查看覆蓋率報告
pytest --cov=redis_toolkit --cov-report=html
```

### 4. 提交流程
1. 創建功能分支：`git checkout -b feature/your-feature`
2. 編寫代碼和測試
3. 運行測試確保通過
4. 提交變更：`git commit -m "feat: add new feature"`
5. 推送分支並創建 PR

## 配置管理策略

### 1. 配置方式
Redis Toolkit 使用簡單的 Python dataclass 進行配置：

```python
from redis_toolkit import RedisToolkit, RedisOptions, RedisConnectionConfig

# 配置連線參數
config = RedisConnectionConfig(
    host='localhost',
    port=6379,
    db=0,
    password='your_password'
)

# 配置選項
options = RedisOptions(
    is_logger_info=True,
    max_log_size=512,
    use_connection_pool=True,
    max_connections=50
)

# 創建實例
toolkit = RedisToolkit(config=config, options=options)
```

### 2. 預設配置
如果不提供配置，會使用合理的預設值：

```python
# 使用預設配置
toolkit = RedisToolkit()
```

## 擴展指南

### 1. 新增轉換器
1. 在 `converters/` 目錄創建新檔案
2. 繼承 `BaseConverter` 抽象類別
3. 實現必要的方法：`encode()`, `decode()`, `_check_dependencies()`
4. 在 `converters/__init__.py` 註冊新轉換器

### 2. 新增序列化格式
1. 在 `utils/serializers.py` 添加新的序列化函數
2. 更新 `_serialize_value()` 和 `_deserialize_value()`
3. 添加相應的測試案例

### 3. 新增 Redis 操作
1. 在 `RedisToolkit` 類別添加新方法
2. 確保使用 `@with_retry` 裝飾器
3. 添加輸入驗證（如需要）
4. 更新 API 文檔

---

此架構設計遵循 PRINCIPLE.md 中的所有核心原則，並根據 SRS.md 的功能需求進行規劃，確保系統的可擴展性、可維護性和穩定性。通過清晰的模組劃分、設計模式的應用和完善的測試策略，Redis Toolkit 能夠持續演進並滿足不斷變化的需求。