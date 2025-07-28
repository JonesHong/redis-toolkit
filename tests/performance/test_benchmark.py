#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單的基準測試驗證
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from redis_toolkit import RedisToolkit, RedisConnectionConfig, RedisOptions
from tests.performance.batch_operations_benchmark import BatchOperationsBenchmark
from pretty_loguru import create_logger

# 設定日誌為 WARNING 級別以減少輸出
logger = create_logger(name="test", level="WARNING")

def test_basic_benchmark():
    """測試基本的基準測試功能"""
    # 創建 RedisToolkit 實例（禁用日誌）
    options = RedisOptions(is_logger_info=False)
    config = RedisConnectionConfig(host='localhost', port=6379)
    toolkit = RedisToolkit(config=config, options=options)
    
    # 確保 Redis 連接正常
    if not toolkit.health_check():
        print("無法連接到 Redis 服務器")
        return
    
    print("Redis 連接正常")
    
    # 創建基準測試實例
    benchmark = BatchOperationsBenchmark(toolkit)
    
    # 運行小規模測試
    print("運行小規模批次操作測試...")
    results = benchmark.run_benchmark([10, 50], iterations=2)
    
    # 打印簡單結果
    print("\n測試結果:")
    for size, data in results.items():
        print(f"\n數據量: {size} 條")
        improvements = data.get('improvements', {})
        if improvements:
            batch_imp = improvements.get('batch_vs_single', {})
            if batch_imp:
                print(f"  批次 vs 單一 - 寫入提升: {batch_imp.get('write', 0):.2f}x")
                print(f"  批次 vs 單一 - 讀取提升: {batch_imp.get('read', 0):.2f}x")
    
    # 清理資源
    toolkit.cleanup()
    print("\n測試完成!")

if __name__ == "__main__":
    test_basic_benchmark()