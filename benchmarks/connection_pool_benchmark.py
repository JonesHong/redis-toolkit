#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis Toolkit 連接池效率基準測試
測試連接池與獨立連接的性能差異
"""

import time
import threading
import concurrent.futures
import statistics
from typing import Dict, List, Any, Tuple
from redis import Redis
from redis_toolkit import RedisToolkit, RedisConnectionConfig, RedisOptions
from redis_toolkit.pool_manager import pool_manager
from pretty_loguru import create_logger

logger = create_logger(name="benchmark.connection_pool", level="INFO")


class ConnectionPoolBenchmark:
    """連接池效率測試"""
    
    def __init__(self):
        self.results: Dict[str, Any] = {}
        self.config = RedisConnectionConfig(host='localhost', port=6379)
    
    def create_toolkit_with_pool(self) -> RedisToolkit:
        """創建使用連接池的 RedisToolkit"""
        options = RedisOptions(use_connection_pool=True, max_connections=50)
        return RedisToolkit(config=self.config, options=options)
    
    def create_toolkit_without_pool(self) -> RedisToolkit:
        """創建不使用連接池的 RedisToolkit"""
        options = RedisOptions(use_connection_pool=False)
        return RedisToolkit(config=self.config, options=options)
    
    def benchmark_single_thread_operations(self, use_pool: bool, operations: int = 1000) -> Dict[str, float]:
        """測試單線程操作性能"""
        # 創建 toolkit
        toolkit = self.create_toolkit_with_pool() if use_pool else self.create_toolkit_without_pool()
        
        operation_times = []
        
        try:
            # 預熱
            for i in range(10):
                toolkit.setter(f"warmup_{i}", f"value_{i}")
                toolkit.getter(f"warmup_{i}")
                toolkit.deleter(f"warmup_{i}")
            
            # 實際測試
            for i in range(operations):
                key = f"bench:single:{i}"
                value = f"value_{i}" * 10
                
                # 測量單次操作時間
                start_time = time.perf_counter()
                
                # SET 操作
                toolkit.setter(key, value)
                # GET 操作
                result = toolkit.getter(key)
                # DELETE 操作
                toolkit.deleter(key)
                
                operation_time = time.perf_counter() - start_time
                operation_times.append(operation_time)
            
            # 計算統計數據
            return {
                'mean': statistics.mean(operation_times) * 1000,  # 轉換為毫秒
                'median': statistics.median(operation_times) * 1000,
                'stdev': statistics.stdev(operation_times) * 1000 if len(operation_times) > 1 else 0,
                'min': min(operation_times) * 1000,
                'max': max(operation_times) * 1000,
                'total_time': sum(operation_times),
                'operations': operations
            }
        
        finally:
            toolkit.cleanup()
    
    def benchmark_multi_thread_operations(self, use_pool: bool, threads: int = 10, operations_per_thread: int = 100) -> Dict[str, float]:
        """測試多線程操作性能"""
        # 創建共享的 toolkit（用於連接池測試）
        shared_toolkit = self.create_toolkit_with_pool() if use_pool else None
        
        thread_results = []
        start_time = time.perf_counter()
        
        def worker(thread_id: int):
            """工作線程函數"""
            # 每個線程使用自己的 toolkit（非連接池）或共享 toolkit（連接池）
            if use_pool:
                toolkit = shared_toolkit
            else:
                toolkit = self.create_toolkit_without_pool()
            
            operation_times = []
            
            try:
                for i in range(operations_per_thread):
                    key = f"bench:thread{thread_id}:{i}"
                    value = f"thread_{thread_id}_value_{i}"
                    
                    op_start = time.perf_counter()
                    
                    # 執行操作
                    toolkit.setter(key, value)
                    result = toolkit.getter(key)
                    toolkit.deleter(key)
                    
                    op_time = time.perf_counter() - op_start
                    operation_times.append(op_time)
                
                return operation_times
            
            finally:
                # 非連接池模式下，每個線程清理自己的連接
                if not use_pool:
                    toolkit.cleanup()
        
        try:
            # 使用線程池執行並發操作
            with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
                futures = [executor.submit(worker, i) for i in range(threads)]
                
                # 收集所有結果
                for future in concurrent.futures.as_completed(futures):
                    thread_results.extend(future.result())
            
            total_time = time.perf_counter() - start_time
            
            # 計算統計數據
            return {
                'mean': statistics.mean(thread_results) * 1000,
                'median': statistics.median(thread_results) * 1000,
                'stdev': statistics.stdev(thread_results) * 1000 if len(thread_results) > 1 else 0,
                'min': min(thread_results) * 1000,
                'max': max(thread_results) * 1000,
                'total_time': total_time,
                'total_operations': threads * operations_per_thread,
                'threads': threads,
                'throughput': (threads * operations_per_thread) / total_time  # 操作/秒
            }
        
        finally:
            if shared_toolkit:
                shared_toolkit.cleanup()
    
    def benchmark_connection_overhead(self, iterations: int = 100) -> Dict[str, float]:
        """測試連接建立開銷"""
        # 測試使用連接池的連接開銷
        pool_times = []
        for _ in range(iterations):
            start_time = time.perf_counter()
            toolkit = self.create_toolkit_with_pool()
            toolkit.health_check()
            creation_time = time.perf_counter() - start_time
            pool_times.append(creation_time)
            toolkit.cleanup()
        
        # 測試不使用連接池的連接開銷
        no_pool_times = []
        for _ in range(iterations):
            start_time = time.perf_counter()
            toolkit = self.create_toolkit_without_pool()
            toolkit.health_check()
            creation_time = time.perf_counter() - start_time
            no_pool_times.append(creation_time)
            toolkit.cleanup()
        
        return {
            'with_pool': {
                'mean': statistics.mean(pool_times) * 1000,
                'median': statistics.median(pool_times) * 1000,
                'stdev': statistics.stdev(pool_times) * 1000 if len(pool_times) > 1 else 0,
                'min': min(pool_times) * 1000,
                'max': max(pool_times) * 1000
            },
            'without_pool': {
                'mean': statistics.mean(no_pool_times) * 1000,
                'median': statistics.median(no_pool_times) * 1000,
                'stdev': statistics.stdev(no_pool_times) * 1000 if len(no_pool_times) > 1 else 0,
                'min': min(no_pool_times) * 1000,
                'max': max(no_pool_times) * 1000
            },
            'improvement': statistics.mean(no_pool_times) / statistics.mean(pool_times)
        }
    
    def benchmark_pool_saturation(self, max_connections: int = 10) -> Dict[str, Any]:
        """測試連接池飽和情況"""
        options = RedisOptions(use_connection_pool=True, max_connections=max_connections)
        toolkit = RedisToolkit(config=self.config, options=options)
        
        results = []
        
        def worker(worker_id: int, operations: int = 50):
            """工作線程"""
            operation_times = []
            wait_times = []
            
            for i in range(operations):
                # 記錄等待時間
                wait_start = time.perf_counter()
                
                # 執行操作
                op_start = time.perf_counter()
                key = f"bench:saturation:{worker_id}:{i}"
                toolkit.setter(key, f"value_{i}")
                toolkit.getter(key)
                toolkit.deleter(key)
                op_time = time.perf_counter() - op_start
                
                wait_time = op_start - wait_start
                operation_times.append(op_time)
                wait_times.append(wait_time)
            
            return {
                'worker_id': worker_id,
                'operation_times': operation_times,
                'wait_times': wait_times
            }
        
        try:
            # 使用超過連接池大小的線程數
            thread_count = max_connections * 2
            
            start_time = time.perf_counter()
            with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
                futures = [executor.submit(worker, i) for i in range(thread_count)]
                
                for future in concurrent.futures.as_completed(futures):
                    results.append(future.result())
            
            total_time = time.perf_counter() - start_time
            
            # 分析結果
            all_op_times = []
            all_wait_times = []
            for result in results:
                all_op_times.extend(result['operation_times'])
                all_wait_times.extend(result['wait_times'])
            
            return {
                'max_connections': max_connections,
                'thread_count': thread_count,
                'total_time': total_time,
                'operation_stats': {
                    'mean': statistics.mean(all_op_times) * 1000,
                    'median': statistics.median(all_op_times) * 1000,
                    'stdev': statistics.stdev(all_op_times) * 1000 if len(all_op_times) > 1 else 0,
                    'min': min(all_op_times) * 1000,
                    'max': max(all_op_times) * 1000
                },
                'wait_stats': {
                    'mean': statistics.mean(all_wait_times) * 1000,
                    'median': statistics.median(all_wait_times) * 1000,
                    'stdev': statistics.stdev(all_wait_times) * 1000 if len(all_wait_times) > 1 else 0,
                    'min': min(all_wait_times) * 1000,
                    'max': max(all_wait_times) * 1000
                }
            }
        
        finally:
            toolkit.cleanup()
    
    def run_benchmark(self) -> Dict[str, Any]:
        """運行完整的基準測試"""
        logger.info("開始連接池效率測試...")
        
        results = {}
        
        # 1. 單線程測試
        logger.info("測試單線程操作...")
        results['single_thread'] = {
            'with_pool': self.benchmark_single_thread_operations(use_pool=True, operations=1000),
            'without_pool': self.benchmark_single_thread_operations(use_pool=False, operations=1000)
        }
        
        # 2. 多線程測試
        logger.info("測試多線程操作...")
        thread_counts = [5, 10, 20, 50]
        results['multi_thread'] = {}
        
        for thread_count in thread_counts:
            logger.info(f"  測試 {thread_count} 個線程...")
            results['multi_thread'][thread_count] = {
                'with_pool': self.benchmark_multi_thread_operations(
                    use_pool=True, 
                    threads=thread_count, 
                    operations_per_thread=100
                ),
                'without_pool': self.benchmark_multi_thread_operations(
                    use_pool=False, 
                    threads=thread_count, 
                    operations_per_thread=100
                )
            }
        
        # 3. 連接開銷測試
        logger.info("測試連接建立開銷...")
        results['connection_overhead'] = self.benchmark_connection_overhead(iterations=50)
        
        # 4. 連接池飽和測試
        logger.info("測試連接池飽和情況...")
        pool_sizes = [5, 10, 20]
        results['pool_saturation'] = {}
        
        for pool_size in pool_sizes:
            logger.info(f"  測試連接池大小: {pool_size}...")
            results['pool_saturation'][pool_size] = self.benchmark_pool_saturation(max_connections=pool_size)
        
        self.results = results
        return results
    
    def print_results(self):
        """打印測試結果"""
        logger.info("\n" + "="*80)
        logger.info("連接池效率測試結果")
        logger.info("="*80)
        
        # 單線程結果
        logger.info("\n1. 單線程操作性能")
        logger.info("-"*60)
        single = self.results['single_thread']
        logger.info("使用連接池:")
        logger.info(f"  平均: {single['with_pool']['mean']:.3f}ms")
        logger.info(f"  中位數: {single['with_pool']['median']:.3f}ms")
        logger.info("不使用連接池:")
        logger.info(f"  平均: {single['without_pool']['mean']:.3f}ms")
        logger.info(f"  中位數: {single['without_pool']['median']:.3f}ms")
        improvement = single['without_pool']['mean'] / single['with_pool']['mean']
        logger.info(f"性能提升: {improvement:.2f}x")
        
        # 多線程結果
        logger.info("\n2. 多線程操作性能")
        logger.info("-"*60)
        for threads, data in self.results['multi_thread'].items():
            logger.info(f"\n{threads} 個線程:")
            with_pool = data['with_pool']
            without_pool = data['without_pool']
            logger.info(f"  使用連接池 - 吞吐量: {with_pool['throughput']:.0f} ops/s")
            logger.info(f"  不使用連接池 - 吞吐量: {without_pool['throughput']:.0f} ops/s")
            improvement = with_pool['throughput'] / without_pool['throughput']
            logger.info(f"  吞吐量提升: {improvement:.2f}x")
        
        # 連接開銷結果
        logger.info("\n3. 連接建立開銷")
        logger.info("-"*60)
        overhead = self.results['connection_overhead']
        logger.info(f"使用連接池: {overhead['with_pool']['mean']:.3f}ms")
        logger.info(f"不使用連接池: {overhead['without_pool']['mean']:.3f}ms")
        logger.info(f"開銷減少: {overhead['improvement']:.2f}x")
        
        # 連接池飽和結果
        logger.info("\n4. 連接池飽和測試")
        logger.info("-"*60)
        for pool_size, data in self.results['pool_saturation'].items():
            logger.info(f"\n連接池大小: {pool_size}, 線程數: {data['thread_count']}")
            logger.info(f"  操作延遲: {data['operation_stats']['mean']:.3f}ms")
            logger.info(f"  等待時間: {data['wait_stats']['mean']:.3f}ms")
    
    def save_results(self, filename: str = "connection_pool_benchmark.json"):
        """保存測試結果到文件"""
        import json
        import os
        
        # 確保 benchmarks/results 目錄存在
        results_dir = os.path.join(os.path.dirname(__file__), 'results')
        os.makedirs(results_dir, exist_ok=True)
        
        filepath = os.path.join(results_dir, filename)
        
        # 添加元數據
        output = {
            'test_name': 'Connection Pool Efficiency Benchmark',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'results': self.results
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        logger.success(f"測試結果已保存到: {filepath}")


def main():
    """主函數"""
    # 確保清理現有的連接池
    pool_manager.cleanup_all()
    
    # 創建基準測試實例
    benchmark = ConnectionPoolBenchmark()
    
    # 運行測試
    results = benchmark.run_benchmark()
    
    # 打印結果
    benchmark.print_results()
    
    # 保存結果
    benchmark.save_results()
    
    # 清理連接池
    pool_manager.cleanup_all()
    
    logger.info("測試完成")


if __name__ == "__main__":
    main()