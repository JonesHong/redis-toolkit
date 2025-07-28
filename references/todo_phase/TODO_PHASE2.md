# Redis Toolkit 改進計畫 - Phase 2：異步與集群支援

## 📋 目標
根據深度架構分析，實現 Redis Toolkit 的異步支援和 Redis Cluster 支援，使其成為真正全面的 Redis 工具包。

## 🎯 核心目標
1. **異步支援**：支援現代 Python 異步生態系統（FastAPI、Starlette 等）
2. **集群支援**：支援 Redis Cluster 實現水平擴展
3. **向後兼容**：確保現有 API 完全不受影響

## ✅ 高優先級工作項目（P0）

### 1. 異步支援實現 - 預計 2-3 週

#### 週 1：核心異步功能
- [ ] 1.1 創建異步核心模組
  - [ ] 創建 `redis_toolkit/async_core.py`
  - [ ] 實現 `AsyncRedisToolkit` 類
  - [ ] 支援基本操作：`async def getter()`, `async def setter()`, `async def deleter()`
  - [ ] 支援 TTL 操作：`async def setter_with_ttl()`, `async def get_ttl()`

- [ ] 1.2 異步連接池管理
  - [ ] 創建 `redis_toolkit/async_pool_manager.py`
  - [ ] 實現 `AsyncConnectionPoolManager` 單例類
  - [ ] 支援異步連接池的創建、獲取和釋放
  - [ ] 實現 `async def close_all_pools()`

#### 週 2：進階異步功能
- [ ] 1.3 異步 Pub/Sub 實現
  - [ ] 實現 `async def start_subscriber()`
  - [ ] 實現 `async def stop_subscriber()`
  - [ ] 實現 `async def publish()`
  - [ ] 支援異步訊息處理函數：`Callable[[str, Any], Awaitable[None]]`
  
- [ ] 1.4 異步批量操作
  - [ ] 實現 `async def batch_set(items: Dict[str, Any])`
  - [ ] 實現 `async def batch_get(keys: List[str])`
  - [ ] 實現 `async def batch_delete(keys: List[str])`
  - [ ] 使用 pipeline 優化批量操作性能

- [ ] 1.5 異步上下文管理器
  ```python
  class AsyncRedisToolkit:
      async def __aenter__(self):
          await self.client.ping()
          return self
          
      async def __aexit__(self, exc_type, exc_val, exc_tb):
          await self.cleanup()
  ```

#### 週 3：測試、文檔與範例
- [ ] 1.6 異步測試套件
  - [ ] 創建 `tests/test_async_core.py`
  - [ ] 創建 `tests/test_async_pubsub.py`
  - [ ] 創建 `tests/test_async_batch.py`
  - [ ] 安裝並使用 `pytest-asyncio`
  - [ ] 確保異步功能覆蓋率 > 80%

- [ ] 1.7 異步範例程式
  - [ ] 創建 `examples/async/basic_usage.py`
  - [ ] 創建 `examples/async/pubsub_demo.py`
  - [ ] 創建 `examples/async/fastapi_integration.py`
  - [ ] 創建 `examples/async/performance_comparison.py`

- [ ] 1.8 異步文檔
  - [ ] 更新 `docs/API.md` 加入完整異步 API 文檔
  - [ ] 創建 `docs/ASYNC_GUIDE.md` 詳細說明異步使用
  - [ ] 更新 `README.md` 加入異步範例
  - [ ] 創建異步最佳實踐指南

### 2. Redis Cluster 支援 - 預計 3-4 週

#### 週 1-2：基礎集群支援
- [ ] 2.1 擴展連接配置
  ```python
  @dataclass
  class RedisConnectionConfig:
      # 現有欄位...
      
      # 集群相關配置
      cluster_mode: bool = False
      startup_nodes: Optional[List[Dict[str, Any]]] = None
      skip_full_coverage_check: bool = False
      max_connections_per_node: int = 32
      readonly_mode: bool = False
      
      def validate_cluster_config(self) -> None:
          """驗證集群配置"""
  ```

- [ ] 2.2 修改核心類支援集群
  - [ ] 修改 `RedisToolkit._setup_client()` 支援集群模式判斷
  - [ ] 實現 `_create_cluster_client()` 方法
  - [ ] 處理集群特定的連接異常
  - [ ] 支援集群健康檢查

- [ ] 2.3 異步集群支援
  - [ ] 在 `AsyncRedisToolkit` 中支援集群模式
  - [ ] 實現異步集群客戶端創建
  - [ ] 處理異步集群連接

#### 週 3：集群特定功能
- [ ] 2.4 集群特定操作
  - [ ] 創建 `redis_toolkit/cluster_utils.py`
  - [ ] 實現 `ClusterOperations` 類
  - [ ] 實現跨節點掃描：`scan_cluster(pattern: str)`
  - [ ] 實現跨槽批量操作：`mget_cluster()`, `mset_cluster()`
  - [ ] 實現節點信息獲取：`get_nodes_info()`

- [ ] 2.5 集群 Pub/Sub 處理
  - [ ] 處理集群中的 Pub/Sub 限制
  - [ ] 實現鍵標籤策略：`{user:123}:channel`
  - [ ] 提供集群 Pub/Sub 最佳實踐
  - [ ] 處理節點故障時的 Pub/Sub 重連

#### 週 4：測試與文檔
- [ ] 2.6 集群測試環境
  - [ ] 創建 `docker/docker-compose.cluster.yml`
  - [ ] 配置 6 節點測試集群（3 主 3 從）
  - [ ] 創建 `tests/test_cluster.py`
  - [ ] 創建 `tests/test_cluster_failover.py`
  - [ ] 測試跨槽操作和故障轉移

- [ ] 2.7 集群範例程式
  - [ ] 創建 `examples/cluster/basic_operations.py`
  - [ ] 創建 `examples/cluster/sharding_demo.py`
  - [ ] 創建 `examples/cluster/failover_handling.py`
  - [ ] 創建 `examples/cluster/performance_test.py`

- [ ] 2.8 集群文檔
  - [ ] 創建 `docs/CLUSTER_GUIDE.md`
  - [ ] 創建集群配置範例
  - [ ] 創建故障處理指南
  - [ ] 創建性能優化建議

## ✅ 中優先級工作項目（P1）

### 3. 向後兼容性與遷移支援

- [ ] 3.1 API 兼容性保證
  - [ ] 確保所有新功能都是額外添加
  - [ ] 運行完整回歸測試套件
  - [ ] 創建兼容性測試矩陣
  - [ ] 確保序列化格式不變

- [ ] 3.2 版本發布計劃
  - [ ] 0.4.0-alpha：內部測試版（異步支援）
  - [ ] 0.4.0-beta：公開測試版
  - [ ] 0.4.0：正式發布異步支援
  - [ ] 0.5.0-beta：集群支援測試版
  - [ ] 0.5.0：正式發布集群支援

- [ ] 3.3 遷移文檔
  - [ ] 創建 `docs/MIGRATION_GUIDE.md`
  - [ ] 提供同步到異步的漸進式遷移範例
  - [ ] 提供單節點到集群的遷移步驟
  - [ ] 創建遷移檢查清單

### 4. 性能優化與監控

- [ ] 4.1 性能基準測試
  - [ ] 創建異步 vs 同步性能對比測試
  - [ ] 創建集群 vs 單節點性能測試
  - [ ] 測試不同規模下的性能表現
  - [ ] 生成性能報告

- [ ] 4.2 監控指標（未來考慮）
  - [ ] 設計 Prometheus 指標接口
  - [ ] 連接池使用率監控
  - [ ] 操作延遲監控
  - [ ] 錯誤率監控

## 📋 技術實施細節

### 異步實現關鍵點：
```python
# 1. 保持序列化邏輯同步
async def setter(self, key: str, value: Any) -> None:
    serialized = serialize_value(value)  # 同步序列化
    await self.client.set(key, serialized)  # 異步 I/O

# 2. 異步批量操作優化
async def batch_set(self, items: Dict[str, Any]) -> None:
    async with self.client.pipeline() as pipe:
        for key, value in items.items():
            serialized = serialize_value(value)
            pipe.set(key, serialized)
        await pipe.execute()

# 3. 異步 Pub/Sub 處理
async def _subscriber_loop(self):
    async for message in self.pubsub.listen():
        if message['type'] == 'message':
            data = deserialize_value(message['data'])
            await self.message_handler(
                message['channel'].decode(), 
                data
            )
```

### 集群實現關鍵點：
```python
# 1. 自動客戶端選擇
def _setup_client(self, redis, config):
    if config and config.cluster_mode:
        self.client = RedisCluster(
            startup_nodes=config.startup_nodes,
            decode_responses=False,
            **config.get_cluster_options()
        )
    else:
        # 單節點邏輯保持不變
        
# 2. 處理跨槽操作
def mget_cluster(self, keys: List[str]) -> Dict[str, Any]:
    # 按節點分組鍵
    node_keys = self._group_keys_by_node(keys)
    results = {}
    
    # 並行從各節點獲取
    for node, keys in node_keys.items():
        values = self.client.mget(keys, target_nodes=node)
        # 處理結果...
```

## 🔍 驗收標準

### 異步支援驗收：
1. ✅ 所有核心功能都有對應的異步版本
2. ✅ 異步測試覆蓋率 > 80%
3. ✅ 與 FastAPI 整合範例正常運行
4. ✅ 異步性能優於同步版本 20% 以上
5. ✅ 文檔完整且包含充分範例

### 集群支援驗收：
1. ✅ 支援 Redis Cluster 所有基本操作
2. ✅ 正確處理跨槽操作
3. ✅ 故障轉移測試通過
4. ✅ 集群性能測試達標
5. ✅ 提供完整的集群使用指南

### 整體驗收：
1. ✅ 現有功能 100% 向後兼容
2. ✅ 所有測試通過（包括回歸測試）
3. ✅ 文檔更新完整
4. ✅ 版本發布符合語義化規範

## 📝 注意事項

1. **優先級管理**：先完成異步支援，再實現集群功能
2. **測試驅動**：每個功能都要先寫測試
3. **文檔同步**：功能和文檔同步更新
4. **性能監控**：持續監控性能影響
5. **社群反饋**：beta 版本收集用戶反饋

## 🚀 預期成果

完成 Phase 2 後，Redis Toolkit 將：
- 支援現代 Python 異步應用
- 支援大規模分散式部署
- 成為 Python Redis 生態中的領先工具
- 覆蓋從小型應用到企業級系統的全部需求

---
建立時間：2025-07-28
最後更新：2025-07-28
狀態：計劃中
負責人：Redis Toolkit Team
預計完成時間：5-7 週