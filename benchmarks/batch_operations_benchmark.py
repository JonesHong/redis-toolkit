#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis Toolkit 批次操作性能基準測試
比較單一操作與批次操作的性能差異
"""

import time
import random
import string
import statistics
from typing import Dict, List, Any, Tuple
from redis import Redis
from redis_toolkit import RedisToolkit, RedisConnectionConfig
from pretty_loguru import create_logger

logger = create_logger(name="benchmark.batch", level="INFO")


class BatchOperationsBenchmark:
    """批次操作性能測試"""
    
    def __init__(self, toolkit: RedisToolkit):
        self.toolkit = toolkit
        self.results: Dict[str, Any] = {}
    
    def generate_test_data(self, count: int, size: int = 100) -> Dict[str, Any]:
        """生成測試數據
        
        參數:
            count: 數據條數
            size: 每條數據的大小（字元數）
        """
        data = {}
        for i in range(count):
            key = f"bench:batch:{i}"
            # 生成不同類型的測試數據
            if i % 4 == 0:
                # 字串
                value = ''.join(random.choices(string.ascii_letters + string.digits, k=size))
            elif i % 4 == 1:
                # 字典
                value = {
                    'id': i,
                    'name': f'test_{i}',
                    'data': ''.join(random.choices(string.ascii_letters, k=size//2))
                }
            elif i % 4 == 2:
                # 列表
                value = [random.randint(0, 1000) for _ in range(size//10)]
            else:
                # 數字
                value = random.randint(1, 1000000)
            
            data[key] = value
        
        return data
    
    def benchmark_single_operations(self, data: Dict[str, Any]) -> Tuple[float, float]:
        """測試單一操作性能
        
        返回:
            (寫入時間, 讀取時間)
        """
        keys = list(data.keys())
        
        # 測試寫入
        start_time = time.perf_counter()
        for key, value in data.items():
            self.toolkit.setter(key, value)
        write_time = time.perf_counter() - start_time
        
        # 測試讀取
        start_time = time.perf_counter()
        for key in keys:
            self.toolkit.getter(key)
        read_time = time.perf_counter() - start_time
        
        # 清理數據
        for key in keys:
            self.toolkit.deleter(key)
        
        return write_time, read_time
    
    def benchmark_batch_operations(self, data: Dict[str, Any]) -> Tuple[float, float]:
        """測試批次操作性能
        
        返回:
            (寫入時間, 讀取時間)
        """
        keys = list(data.keys())
        
        # 測試批次寫入
        start_time = time.perf_counter()
        self.toolkit.batch_set(data)
        write_time = time.perf_counter() - start_time
        
        # 測試批次讀取
        start_time = time.perf_counter()
        self.toolkit.batch_get(keys)
        read_time = time.perf_counter() - start_time
        
        # 清理數據
        for key in keys:
            self.toolkit.deleter(key)
        
        return write_time, read_time
    
    def benchmark_pipeline_operations(self, data: Dict[str, Any]) -> Tuple[float, float]:
        """測試使用 Pipeline 的性能
        
        返回:
            (寫入時間, 讀取時間)
        """
        keys = list(data.keys())
        redis_client = self.toolkit.client
        
        # 測試 Pipeline 寫入
        start_time = time.perf_counter()
        with redis_client.pipeline() as pipe:
            for key, value in data.items():
                # 使用 toolkit 的序列化方法
                from redis_toolkit.utils.serializers import serialize_value
                serialized = serialize_value(value)
                pipe.set(key, serialized)
            pipe.execute()
        write_time = time.perf_counter() - start_time
        
        # 測試 Pipeline 讀取
        start_time = time.perf_counter()
        with redis_client.pipeline() as pipe:
            for key in keys:
                pipe.get(key)
            results = pipe.execute()
        read_time = time.perf_counter() - start_time
        
        # 清理數據
        with redis_client.pipeline() as pipe:
            for key in keys:
                pipe.delete(key)
            pipe.execute()
        
        return write_time, read_time
    
    def run_benchmark(self, data_sizes: List[int], iterations: int = 5) -> Dict[str, Any]:
        """運行完整的基準測試
        
        參數:
            data_sizes: 要測試的數據量大小列表
            iterations: 每個測試的迭代次數
        """
        results = {}
        
        for size in data_sizes:
            logger.info(f"測試數據量: {size} 條")
            
            single_write_times = []
            single_read_times = []
            batch_write_times = []
            batch_read_times = []
            pipeline_write_times = []
            pipeline_read_times = []
            
            for i in range(iterations):
                # 生成測試數據
                test_data = self.generate_test_data(size)
                
                # 單一操作測試
                write_time, read_time = self.benchmark_single_operations(test_data)
                single_write_times.append(write_time)
                single_read_times.append(read_time)
                
                # 批次操作測試
                write_time, read_time = self.benchmark_batch_operations(test_data)
                batch_write_times.append(write_time)
                batch_read_times.append(read_time)
                
                # Pipeline 操作測試
                write_time, read_time = self.benchmark_pipeline_operations(test_data)
                pipeline_write_times.append(write_time)
                pipeline_read_times.append(read_time)
                
                logger.debug(f"完成第 {i+1}/{iterations} 次迭代")
            
            # 計算統計數據
            results[size] = {
                'single': {
                    'write': {
                        'mean': statistics.mean(single_write_times),
                        'median': statistics.median(single_write_times),
                        'stdev': statistics.stdev(single_write_times) if len(single_write_times) > 1 else 0,
                        'min': min(single_write_times),
                        'max': max(single_write_times)
                    },
                    'read': {
                        'mean': statistics.mean(single_read_times),
                        'median': statistics.median(single_read_times),
                        'stdev': statistics.stdev(single_read_times) if len(single_read_times) > 1 else 0,
                        'min': min(single_read_times),
                        'max': max(single_read_times)
                    }
                },
                'batch': {
                    'write': {
                        'mean': statistics.mean(batch_write_times),
                        'median': statistics.median(batch_write_times),
                        'stdev': statistics.stdev(batch_write_times) if len(batch_write_times) > 1 else 0,
                        'min': min(batch_write_times),
                        'max': max(batch_write_times)
                    },
                    'read': {
                        'mean': statistics.mean(batch_read_times),
                        'median': statistics.median(batch_read_times),
                        'stdev': statistics.stdev(batch_read_times) if len(batch_read_times) > 1 else 0,
                        'min': min(batch_read_times),
                        'max': max(batch_read_times)
                    }
                },
                'pipeline': {
                    'write': {
                        'mean': statistics.mean(pipeline_write_times),
                        'median': statistics.median(pipeline_write_times),
                        'stdev': statistics.stdev(pipeline_write_times) if len(pipeline_write_times) > 1 else 0,
                        'min': min(pipeline_write_times),
                        'max': max(pipeline_write_times)
                    },
                    'read': {
                        'mean': statistics.mean(pipeline_read_times),
                        'median': statistics.median(pipeline_read_times),
                        'stdev': statistics.stdev(pipeline_read_times) if len(pipeline_read_times) > 1 else 0,
                        'min': min(pipeline_read_times),
                        'max': max(pipeline_read_times)
                    }
                }
            }
            
            # 計算性能提升比例
            single_write_mean = results[size]['single']['write']['mean']
            single_read_mean = results[size]['single']['read']['mean']
            batch_write_mean = results[size]['batch']['write']['mean']
            batch_read_mean = results[size]['batch']['read']['mean']
            pipeline_write_mean = results[size]['pipeline']['write']['mean']
            pipeline_read_mean = results[size]['pipeline']['read']['mean']
            
            results[size]['improvements'] = {
                'batch_vs_single': {
                    'write': single_write_mean / batch_write_mean if batch_write_mean > 0 else 0,
                    'read': single_read_mean / batch_read_mean if batch_read_mean > 0 else 0
                },
                'pipeline_vs_single': {
                    'write': single_write_mean / pipeline_write_mean if pipeline_write_mean > 0 else 0,
                    'read': single_read_mean / pipeline_read_mean if pipeline_read_mean > 0 else 0
                }
            }
        
        self.results = results
        return results
    
    def print_results(self):
        """打印測試結果"""
        logger.info("\n" + "="*80)
        logger.info("批次操作性能測試結果")
        logger.info("="*80)
        
        for size, data in self.results.items():
            logger.info(f"\n數據量: {size} 條")
            logger.info("-"*60)
            
            # 打印單一操作結果
            logger.info("單一操作:")
            logger.info(f"  寫入: {data['single']['write']['mean']:.4f}s (±{data['single']['write']['stdev']:.4f}s)")
            logger.info(f"  讀取: {data['single']['read']['mean']:.4f}s (±{data['single']['read']['stdev']:.4f}s)")
            
            # 打印批次操作結果
            logger.info("批次操作:")
            logger.info(f"  寫入: {data['batch']['write']['mean']:.4f}s (±{data['batch']['write']['stdev']:.4f}s)")
            logger.info(f"  讀取: {data['batch']['read']['mean']:.4f}s (±{data['batch']['read']['stdev']:.4f}s)")
            
            # 打印 Pipeline 操作結果
            logger.info("Pipeline 操作:")
            logger.info(f"  寫入: {data['pipeline']['write']['mean']:.4f}s (±{data['pipeline']['write']['stdev']:.4f}s)")
            logger.info(f"  讀取: {data['pipeline']['read']['mean']:.4f}s (±{data['pipeline']['read']['stdev']:.4f}s)")
            
            # 打印性能提升
            logger.info("性能提升:")
            improvements = data['improvements']
            logger.info(f"  批次 vs 單一 - 寫入: {improvements['batch_vs_single']['write']:.2f}x")
            logger.info(f"  批次 vs 單一 - 讀取: {improvements['batch_vs_single']['read']:.2f}x")
            logger.info(f"  Pipeline vs 單一 - 寫入: {improvements['pipeline_vs_single']['write']:.2f}x")
            logger.info(f"  Pipeline vs 單一 - 讀取: {improvements['pipeline_vs_single']['read']:.2f}x")
    
    def save_results(self, filename: str = "batch_operations_benchmark.json"):
        """保存測試結果到文件"""
        import json
        import os
        
        # 確保 benchmarks/results 目錄存在
        results_dir = os.path.join(os.path.dirname(__file__), 'results')
        os.makedirs(results_dir, exist_ok=True)
        
        filepath = os.path.join(results_dir, filename)
        
        # 添加元數據
        output = {
            'test_name': 'Batch Operations Benchmark',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'results': self.results
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        logger.success(f"測試結果已保存到: {filepath}")


def main():
    """主函數"""
    # 初始化 Redis Toolkit
    config = RedisConnectionConfig(host='localhost', port=6379)
    toolkit = RedisToolkit(config=config)
    
    # 確保 Redis 連接正常
    if not toolkit.health_check():
        logger.error("無法連接到 Redis 服務器")
        return
    
    # 創建基準測試實例
    benchmark = BatchOperationsBenchmark(toolkit)
    
    # 運行測試
    logger.info("開始批次操作性能測試...")
    data_sizes = [10, 50, 100, 500, 1000]  # 測試不同數據量
    results = benchmark.run_benchmark(data_sizes, iterations=5)
    
    # 打印結果
    benchmark.print_results()
    
    # 保存結果
    benchmark.save_results()
    
    # 清理資源
    toolkit.cleanup()
    logger.info("測試完成")


if __name__ == "__main__":
    main()