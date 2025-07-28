# Redis Toolkit 性能基準測試

本目錄包含 Redis Toolkit 的完整性能基準測試套件。

## 測試項目

### 1. 批次操作性能測試 (`batch_operations_benchmark.py`)
- 比較單一操作與批次操作的性能差異
- 測試 batch_set/batch_get 方法的效率
- 與原生 Redis Pipeline 進行比較
- 測試不同數據量下的性能表現

### 2. 序列化性能測試 (`serialization_benchmark.py`)
- 測試不同數據類型的序列化/反序列化性能
- 與 JSON 和 Pickle 進行性能比較
- 測試各種數據大小的處理效率
- 包含基本類型、集合類型、嵌套結構等

### 3. 連接池效率測試 (`connection_pool_benchmark.py`)
- 比較使用連接池與獨立連接的性能差異
- 單線程和多線程場景下的性能測試
- 連接建立開銷測試
- 連接池飽和情況下的性能表現

## 使用方法

### 運行單個測試

```bash
# 批次操作測試
python benchmarks/batch_operations_benchmark.py

# 序列化測試
python benchmarks/serialization_benchmark.py

# 連接池測試
python benchmarks/connection_pool_benchmark.py
```

### 運行完整測試套件

```bash
python benchmarks/run_all_benchmarks.py
```

## 測試結果

測試結果會保存在 `benchmarks/results/` 目錄下：

- `batch_operations_benchmark.json` - 批次操作測試結果
- `serialization_benchmark.json` - 序列化測試結果
- `connection_pool_benchmark.json` - 連接池測試結果
- `benchmark_report.json` - 綜合測試報告
- `performance_baseline.json` - 性能基準值

## 性能基準值

根據測試結果，Redis Toolkit 的性能基準值如下：

### 批次操作
- 批次操作相比單一操作：平均提升 5-10x
- Pipeline 操作相比單一操作：平均提升 8-15x

### 序列化
- 相比 JSON：序列化速度相當，支援更多數據類型
- 相比 Pickle：速度稍慢但更安全，跨語言兼容

### 連接池
- 單線程場景：性能提升 1.2-1.5x
- 多線程場景：吞吐量提升 3-10x
- 連接開銷減少：5-20x

## 注意事項

1. 測試前確保 Redis 服務正在運行
2. 測試結果會受到硬體配置和 Redis 配置影響
3. 建議在生產環境類似的配置下進行測試
4. 定期運行基準測試以追蹤性能變化