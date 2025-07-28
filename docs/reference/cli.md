# CLI 參考

Redis Toolkit 提供命令行界面（CLI）工具，用於快速執行常見的 Redis 操作。

## 安裝

安裝 Redis Toolkit 後，`redis-toolkit` 命令將自動可用：

```bash
pip install redis-toolkit
redis-toolkit --version
```

## 基本用法

```bash
redis-toolkit [選項] 命令 [參數]
```

### 全局選項

| 選項 | 簡寫 | 描述 | 默認值 |
|-----|------|-----|--------|
| `--host` | `-h` | Redis 服務器主機 | localhost |
| `--port` | `-p` | Redis 服務器端口 | 6379 |
| `--db` | `-n` | Redis 數據庫索引 | 0 |
| `--password` | | Redis 密碼 | None |
| `--timeout` | `-t` | 操作超時（秒） | 10 |
| `--verbose` | `-v` | 詳細輸出 | False |
| `--quiet` | `-q` | 靜默模式 | False |
| `--format` | `-f` | 輸出格式 (json/table/raw) | table |

## 命令

### 基本操作

#### get - 獲取值

```bash
redis-toolkit get KEY

# 示例
redis-toolkit get user:123
redis-toolkit get user:123 -f json
redis-toolkit get "user:*" --pattern  # 模式匹配
```

#### set - 設置值

```bash
redis-toolkit set KEY VALUE [--expire SECONDS]

# 示例
redis-toolkit set user:123 '{"name": "Alice", "age": 30}'
redis-toolkit set session:abc "active" --expire 3600
redis-toolkit set counter 100
```

#### delete - 刪除鍵

```bash
redis-toolkit delete KEY [KEY ...]

# 示例
redis-toolkit delete user:123
redis-toolkit delete session:* --pattern  # 刪除匹配的鍵
redis-toolkit delete key1 key2 key3  # 批次刪除
```

### 批次操作

#### batch-get - 批次獲取

```bash
redis-toolkit batch-get KEY [KEY ...]

# 示例
redis-toolkit batch-get user:1 user:2 user:3
redis-toolkit batch-get --file keys.txt  # 從文件讀取鍵
redis-toolkit batch-get --pattern "session:*"  # 模式匹配
```

#### batch-set - 批次設置

```bash
redis-toolkit batch-set --file FILE [--expire SECONDS]

# 示例
redis-toolkit batch-set --file data.json
redis-toolkit batch-set --file data.csv --format csv
```

文件格式示例：

**data.json:**
```json
{
  "user:1": {"name": "Alice", "age": 30},
  "user:2": {"name": "Bob", "age": 25},
  "user:3": {"name": "Charlie", "age": 35}
}
```

**data.csv:**
```csv
key,value
user:1,"{""name"": ""Alice"", ""age"": 30}"
user:2,"{""name"": ""Bob"", ""age"": 25}"
```

### 發布/訂閱

#### publish - 發布消息

```bash
redis-toolkit publish CHANNEL MESSAGE

# 示例
redis-toolkit publish notifications '{"event": "user_login", "user_id": 123}'
redis-toolkit publish alerts "System maintenance at 10 PM"
```

#### subscribe - 訂閱頻道

```bash
redis-toolkit subscribe CHANNEL [CHANNEL ...]

# 示例
redis-toolkit subscribe notifications
redis-toolkit subscribe events alerts  # 多頻道
redis-toolkit subscribe "channel:*" --pattern  # 模式訂閱
```

### 媒體處理

#### store-image - 存儲圖片

```bash
redis-toolkit store-image KEY FILE [--format FORMAT] [--quality QUALITY]

# 示例
redis-toolkit store-image user:avatar:123 photo.jpg
redis-toolkit store-image logo company_logo.png --format png
redis-toolkit store-image thumbnail pic.jpg --format jpg --quality 80
```

#### get-image - 獲取圖片

```bash
redis-toolkit get-image KEY OUTPUT_FILE

# 示例
redis-toolkit get-image user:avatar:123 avatar.jpg
redis-toolkit get-image logo logo.png
```

#### store-audio - 存儲音頻

```bash
redis-toolkit store-audio KEY FILE [--sample-rate RATE]

# 示例
redis-toolkit store-audio audio:message:1 voice.wav
redis-toolkit store-audio music:track:42 song.mp3 --sample-rate 44100
```

### 分析工具

#### info - 顯示信息

```bash
redis-toolkit info [SECTION]

# 示例
redis-toolkit info  # 所有信息
redis-toolkit info server  # 服務器信息
redis-toolkit info memory  # 內存使用
redis-toolkit info stats   # 統計信息
```

#### keys - 列出鍵

```bash
redis-toolkit keys [PATTERN]

# 示例
redis-toolkit keys  # 所有鍵
redis-toolkit keys "user:*"  # 匹配模式
redis-toolkit keys --count 100  # 限制數量
redis-toolkit keys --type hash  # 按類型過濾
```

#### analyze - 分析鍵空間

```bash
redis-toolkit analyze [--pattern PATTERN] [--sample-size SIZE]

# 示例
redis-toolkit analyze  # 分析所有鍵
redis-toolkit analyze --pattern "session:*"
redis-toolkit analyze --sample-size 1000  # 採樣分析
```

輸出示例：
```
鍵空間分析報告
==============
總鍵數: 10,234
採樣大小: 1,000

類型分佈:
- string: 45.2% (4,626 keys)
- hash: 30.1% (3,080 keys)
- list: 15.3% (1,565 keys)
- set: 9.4% (963 keys)

前綴分析:
- user:*     : 3,456 keys (33.8%)
- session:*  : 2,145 keys (21.0%)
- cache:*    : 1,823 keys (17.8%)

大小分佈:
- < 1KB      : 7,234 keys (70.7%)
- 1KB-10KB   : 2,456 keys (24.0%)
- 10KB-100KB : 456 keys (4.5%)
- > 100KB    : 88 keys (0.9%)
```

### 維護工具

#### export - 導出數據

```bash
redis-toolkit export [--pattern PATTERN] [--format FORMAT] OUTPUT_FILE

# 示例
redis-toolkit export backup.json
redis-toolkit export --pattern "user:*" users.json
redis-toolkit export --format csv all_data.csv
```

#### import - 導入數據

```bash
redis-toolkit import FILE [--clear] [--dry-run]

# 示例
redis-toolkit import backup.json
redis-toolkit import users.json --clear  # 清除現有數據
redis-toolkit import data.csv --dry-run  # 模擬運行
```

#### flush - 清空數據庫

```bash
redis-toolkit flush [--db DB] [--confirm]

# 示例
redis-toolkit flush --confirm  # 需要確認
redis-toolkit flush --db 1 --confirm  # 清空特定數據庫
```

### 性能測試

#### benchmark - 性能基準測試

```bash
redis-toolkit benchmark [--operations OPS] [--clients CLIENTS] [--size SIZE]

# 示例
redis-toolkit benchmark  # 默認測試
redis-toolkit benchmark --operations 100000
redis-toolkit benchmark --clients 50 --size 1024
```

輸出示例：
```
Redis Toolkit 性能基準測試
========================
測試參數:
- 操作數: 100,000
- 並發客戶端: 50
- 數據大小: 1,024 bytes

結果:
SET 操作:
- 總時間: 2.34 秒
- 吞吐量: 42,735 ops/秒
- 平均延遲: 1.17 ms
- P99 延遲: 3.45 ms

GET 操作:
- 總時間: 1.89 秒
- 吞吐量: 52,910 ops/秒
- 平均延遲: 0.95 ms
- P99 延遲: 2.87 ms

批次操作 (100 items):
- 總時間: 0.45 秒
- 吞吐量: 222,222 ops/秒
- 平均延遲: 0.23 ms
```

## 配置文件

### 使用配置文件

```bash
redis-toolkit --config config.yaml COMMAND
```

**config.yaml 示例:**
```yaml
redis:
  host: redis.example.com
  port: 6379
  password: secret
  db: 1

toolkit:
  log_level: INFO
  timeout: 30
  format: json
```

### 環境變量

支援通過環境變量配置：

```bash
export REDIS_HOST=redis.example.com
export REDIS_PORT=6379
export REDIS_PASSWORD=secret

redis-toolkit get user:123
```

## 輸出格式

### JSON 格式

```bash
redis-toolkit get user:123 -f json
```

輸出：
```json
{
  "key": "user:123",
  "value": {
    "name": "Alice",
    "age": 30,
    "email": "alice@example.com"
  },
  "type": "string",
  "ttl": -1,
  "size": 67
}
```

### 表格格式

```bash
redis-toolkit keys "user:*" -f table
```

輸出：
```
+----------+--------+------+-----+
| Key      | Type   | TTL  | Size|
+----------+--------+------+-----+
| user:123 | string | -1   | 67  |
| user:124 | hash   | 3600 | 128 |
| user:125 | string | -1   | 45  |
+----------+--------+------+-----+
```

### 原始格式

```bash
redis-toolkit get user:123 -f raw
```

輸出：
```
{"name": "Alice", "age": 30, "email": "alice@example.com"}
```

## 進階用法

### 管道模式

```bash
# 從標準輸入讀取
echo "user:123" | redis-toolkit get -

# 鏈接命令
redis-toolkit keys "temp:*" | redis-toolkit delete -
```

### 腳本集成

```bash
#!/bin/bash
# cleanup.sh - 清理過期會話

EXPIRED_SESSIONS=$(redis-toolkit keys "session:*" --ttl 0)
if [ ! -z "$EXPIRED_SESSIONS" ]; then
    echo "$EXPIRED_SESSIONS" | redis-toolkit delete -
    echo "清理了 $(echo "$EXPIRED_SESSIONS" | wc -l) 個過期會話"
fi
```

### 監控集成

```bash
# 導出 Prometheus 格式指標
redis-toolkit metrics --format prometheus

# 輸出:
# redis_toolkit_keys_total{db="0"} 10234
# redis_toolkit_memory_used_bytes{db="0"} 52428800
# redis_toolkit_ops_per_second{operation="get"} 1523.4
```

## 故障排除

### 常見問題

1. **連接錯誤**
   ```bash
   redis-toolkit --host redis.example.com --timeout 30 info
   ```

2. **認證失敗**
   ```bash
   redis-toolkit --password $REDIS_PASSWORD info
   ```

3. **超時問題**
   ```bash
   redis-toolkit --timeout 60 analyze --sample-size 10000
   ```

### 調試模式

```bash
redis-toolkit --verbose get user:123

# 輸出調試信息
[DEBUG] Connecting to redis://localhost:6379/0
[DEBUG] Executing command: GET user:123
[DEBUG] Raw response: b'{"name": "Alice", "age": 30}'
[DEBUG] Deserialized value: {'name': 'Alice', 'age': 30}
```

## 別名和快捷方式

創建便利的別名：

```bash
# ~/.bashrc 或 ~/.zshrc
alias rtk='redis-toolkit'
alias rget='redis-toolkit get'
alias rset='redis-toolkit set'
alias rdel='redis-toolkit delete'
alias rkeys='redis-toolkit keys'

# 特定環境
alias rtk-prod='redis-toolkit --host prod.redis.example.com --password $PROD_REDIS_PWD'
alias rtk-dev='redis-toolkit --host localhost --db 15'
```

使用：
```bash
rget user:123
rset user:123 '{"name": "Alice"}'
rtk-prod keys "session:*"
```

## 退出碼

| 代碼 | 含義 |
|-----|-----|
| 0 | 成功 |
| 1 | 一般錯誤 |
| 2 | 連接錯誤 |
| 3 | 認證錯誤 |
| 4 | 超時錯誤 |
| 5 | 序列化錯誤 |
| 127 | 命令未找到 |

使用退出碼：
```bash
if redis-toolkit get user:123 > /dev/null 2>&1; then
    echo "用戶存在"
else
    echo "用戶不存在"
fi
```