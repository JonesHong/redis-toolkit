#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis Toolkit 序列化性能基準測試
測試不同數據類型和大小的序列化/反序列化性能
"""

import time
import json
import pickle
import random
import string
import statistics
import numpy as np
from typing import Dict, List, Any, Tuple
from redis_toolkit.utils.serializers import serialize_value, deserialize_value
from pretty_loguru import create_logger

logger = create_logger(name="benchmark.serialization", level="INFO")


class SerializationBenchmark:
    """序列化性能測試"""
    
    def __init__(self):
        self.results: Dict[str, Any] = {}
    
    def generate_test_data(self) -> Dict[str, Any]:
        """生成各種類型的測試數據"""
        # 生成隨機字串
        def random_string(length: int) -> str:
            return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        
        test_data = {
            # 基本類型
            'small_string': 'Hello, Redis Toolkit!',
            'medium_string': random_string(1000),
            'large_string': random_string(10000),
            'integer': 42,
            'float': 3.14159265359,
            'boolean': True,
            
            # 集合類型
            'small_list': list(range(10)),
            'medium_list': [random.randint(0, 1000) for _ in range(100)],
            'large_list': [random.random() for _ in range(1000)],
            
            'small_dict': {'name': 'test', 'age': 25, 'active': True},
            'medium_dict': {f'key_{i}': random_string(50) for i in range(50)},
            'large_dict': {f'key_{i}': {
                'id': i,
                'data': random_string(100),
                'values': [random.random() for _ in range(10)]
            } for i in range(100)},
            
            # 嵌套結構
            'nested_structure': {
                'users': [
                    {
                        'id': i,
                        'name': f'user_{i}',
                        'email': f'user{i}@example.com',
                        'profile': {
                            'bio': random_string(200),
                            'interests': [random_string(20) for _ in range(5)],
                            'scores': [random.random() for _ in range(10)]
                        }
                    } for i in range(10)
                ],
                'metadata': {
                    'version': '1.0.0',
                    'timestamp': time.time(),
                    'config': {f'param_{i}': random.random() for i in range(20)}
                }
            },
            
            # 二進制數據
            'small_bytes': b'Binary data example',
            'medium_bytes': random_string(1000).encode('utf-8'),
            'large_bytes': random_string(10000).encode('utf-8'),
            
            # NumPy 數組（如果支援）
            'numpy_array_small': np.random.rand(10),
            'numpy_array_medium': np.random.rand(100, 10),
            'numpy_array_large': np.random.rand(100, 100),
        }
        
        return test_data
    
    def benchmark_single_serialization(self, data: Any, iterations: int = 1000) -> Dict[str, float]:
        """測試單個數據的序列化性能"""
        serialize_times = []
        deserialize_times = []
        
        for _ in range(iterations):
            # 測試序列化
            start_time = time.perf_counter()
            serialized = serialize_value(data)
            serialize_time = time.perf_counter() - start_time
            serialize_times.append(serialize_time)
            
            # 測試反序列化
            start_time = time.perf_counter()
            deserialized = deserialize_value(serialized)
            deserialize_time = time.perf_counter() - start_time
            deserialize_times.append(deserialize_time)
        
        return {
            'serialize': {
                'mean': statistics.mean(serialize_times) * 1000,  # 轉換為毫秒
                'median': statistics.median(serialize_times) * 1000,
                'stdev': statistics.stdev(serialize_times) * 1000 if len(serialize_times) > 1 else 0,
                'min': min(serialize_times) * 1000,
                'max': max(serialize_times) * 1000
            },
            'deserialize': {
                'mean': statistics.mean(deserialize_times) * 1000,
                'median': statistics.median(deserialize_times) * 1000,
                'stdev': statistics.stdev(deserialize_times) * 1000 if len(deserialize_times) > 1 else 0,
                'min': min(deserialize_times) * 1000,
                'max': max(deserialize_times) * 1000
            },
            'serialized_size': len(serialized),
            'iterations': iterations
        }
    
    def benchmark_json_comparison(self, data: Any, iterations: int = 1000) -> Dict[str, float]:
        """與原生 JSON 序列化進行比較"""
        # 跳過不支援 JSON 的數據類型
        try:
            json.dumps(data)
        except (TypeError, ValueError):
            return None
        
        json_serialize_times = []
        json_deserialize_times = []
        
        for _ in range(iterations):
            # 測試 JSON 序列化
            start_time = time.perf_counter()
            json_str = json.dumps(data)
            json_bytes = json_str.encode('utf-8')
            serialize_time = time.perf_counter() - start_time
            json_serialize_times.append(serialize_time)
            
            # 測試 JSON 反序列化
            start_time = time.perf_counter()
            json_str = json_bytes.decode('utf-8')
            json.loads(json_str)
            deserialize_time = time.perf_counter() - start_time
            json_deserialize_times.append(deserialize_time)
        
        return {
            'serialize': {
                'mean': statistics.mean(json_serialize_times) * 1000,
                'median': statistics.median(json_serialize_times) * 1000,
                'stdev': statistics.stdev(json_serialize_times) * 1000 if len(json_serialize_times) > 1 else 0,
                'min': min(json_serialize_times) * 1000,
                'max': max(json_serialize_times) * 1000
            },
            'deserialize': {
                'mean': statistics.mean(json_deserialize_times) * 1000,
                'median': statistics.median(json_deserialize_times) * 1000,
                'stdev': statistics.stdev(json_deserialize_times) * 1000 if len(json_deserialize_times) > 1 else 0,
                'min': min(json_deserialize_times) * 1000,
                'max': max(json_deserialize_times) * 1000
            },
            'serialized_size': len(json_bytes)
        }
    
    def benchmark_pickle_comparison(self, data: Any, iterations: int = 1000) -> Dict[str, float]:
        """與 Pickle 序列化進行比較"""
        pickle_serialize_times = []
        pickle_deserialize_times = []
        
        for _ in range(iterations):
            # 測試 Pickle 序列化
            start_time = time.perf_counter()
            pickled = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
            serialize_time = time.perf_counter() - start_time
            pickle_serialize_times.append(serialize_time)
            
            # 測試 Pickle 反序列化
            start_time = time.perf_counter()
            pickle.loads(pickled)
            deserialize_time = time.perf_counter() - start_time
            pickle_deserialize_times.append(deserialize_time)
        
        return {
            'serialize': {
                'mean': statistics.mean(pickle_serialize_times) * 1000,
                'median': statistics.median(pickle_serialize_times) * 1000,
                'stdev': statistics.stdev(pickle_serialize_times) * 1000 if len(pickle_serialize_times) > 1 else 0,
                'min': min(pickle_serialize_times) * 1000,
                'max': max(pickle_serialize_times) * 1000
            },
            'deserialize': {
                'mean': statistics.mean(pickle_deserialize_times) * 1000,
                'median': statistics.median(pickle_deserialize_times) * 1000,
                'stdev': statistics.stdev(pickle_deserialize_times) * 1000 if len(pickle_deserialize_times) > 1 else 0,
                'min': min(pickle_deserialize_times) * 1000,
                'max': max(pickle_deserialize_times) * 1000
            },
            'serialized_size': len(pickled)
        }
    
    def run_benchmark(self, iterations: int = 1000) -> Dict[str, Any]:
        """運行完整的基準測試"""
        test_data = self.generate_test_data()
        results = {}
        
        logger.info(f"開始序列化性能測試 (每項 {iterations} 次迭代)...")
        
        for data_name, data_value in test_data.items():
            logger.info(f"測試數據類型: {data_name}")
            
            # Redis Toolkit 序列化測試
            toolkit_result = self.benchmark_single_serialization(data_value, iterations)
            
            # JSON 比較（如果支援）
            json_result = self.benchmark_json_comparison(data_value, iterations)
            
            # Pickle 比較
            pickle_result = self.benchmark_pickle_comparison(data_value, iterations)
            
            results[data_name] = {
                'data_type': type(data_value).__name__,
                'toolkit': toolkit_result,
                'json': json_result,
                'pickle': pickle_result
            }
            
            # 計算性能比較
            if json_result:
                results[data_name]['performance_vs_json'] = {
                    'serialize': toolkit_result['serialize']['mean'] / json_result['serialize']['mean'],
                    'deserialize': toolkit_result['deserialize']['mean'] / json_result['deserialize']['mean'],
                    'size_ratio': toolkit_result['serialized_size'] / json_result['serialized_size']
                }
            
            results[data_name]['performance_vs_pickle'] = {
                'serialize': toolkit_result['serialize']['mean'] / pickle_result['serialize']['mean'],
                'deserialize': toolkit_result['deserialize']['mean'] / pickle_result['deserialize']['mean'],
                'size_ratio': toolkit_result['serialized_size'] / pickle_result['serialized_size']
            }
        
        self.results = results
        return results
    
    def print_results(self):
        """打印測試結果"""
        logger.info("\n" + "="*80)
        logger.info("序列化性能測試結果")
        logger.info("="*80)
        
        for data_name, result in self.results.items():
            logger.info(f"\n數據類型: {data_name} ({result['data_type']})")
            logger.info("-"*60)
            
            # Redis Toolkit 結果
            toolkit = result['toolkit']
            logger.info("Redis Toolkit:")
            logger.info(f"  序列化: {toolkit['serialize']['mean']:.3f}ms (±{toolkit['serialize']['stdev']:.3f}ms)")
            logger.info(f"  反序列化: {toolkit['deserialize']['mean']:.3f}ms (±{toolkit['deserialize']['stdev']:.3f}ms)")
            logger.info(f"  序列化大小: {toolkit['serialized_size']} bytes")
            
            # JSON 結果（如果有）
            if result['json']:
                json_data = result['json']
                logger.info("JSON:")
                logger.info(f"  序列化: {json_data['serialize']['mean']:.3f}ms (±{json_data['serialize']['stdev']:.3f}ms)")
                logger.info(f"  反序列化: {json_data['deserialize']['mean']:.3f}ms (±{json_data['deserialize']['stdev']:.3f}ms)")
                logger.info(f"  序列化大小: {json_data['serialized_size']} bytes")
                
                # 性能比較
                perf = result['performance_vs_json']
                logger.info(f"  相對 JSON - 序列化: {perf['serialize']:.2f}x, 反序列化: {perf['deserialize']:.2f}x, 大小: {perf['size_ratio']:.2f}x")
            
            # Pickle 結果
            pickle_data = result['pickle']
            logger.info("Pickle:")
            logger.info(f"  序列化: {pickle_data['serialize']['mean']:.3f}ms (±{pickle_data['serialize']['stdev']:.3f}ms)")
            logger.info(f"  反序列化: {pickle_data['deserialize']['mean']:.3f}ms (±{pickle_data['deserialize']['stdev']:.3f}ms)")
            logger.info(f"  序列化大小: {pickle_data['serialized_size']} bytes")
            
            # 性能比較
            perf = result['performance_vs_pickle']
            logger.info(f"  相對 Pickle - 序列化: {perf['serialize']:.2f}x, 反序列化: {perf['deserialize']:.2f}x, 大小: {perf['size_ratio']:.2f}x")
    
    def save_results(self, filename: str = "serialization_benchmark.json"):
        """保存測試結果到文件"""
        import json
        import os
        
        # 確保 benchmarks/results 目錄存在
        results_dir = os.path.join(os.path.dirname(__file__), 'results')
        os.makedirs(results_dir, exist_ok=True)
        
        filepath = os.path.join(results_dir, filename)
        
        # 添加元數據
        output = {
            'test_name': 'Serialization Performance Benchmark',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'results': self.results
        }
        
        # 移除 NumPy 數組結果（無法直接 JSON 序列化）
        for key in list(output['results'].keys()):
            if 'numpy' in key:
                del output['results'][key]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        logger.success(f"測試結果已保存到: {filepath}")


def main():
    """主函數"""
    # 創建基準測試實例
    benchmark = SerializationBenchmark()
    
    # 運行測試
    logger.info("開始序列化性能測試...")
    results = benchmark.run_benchmark(iterations=1000)
    
    # 打印結果
    benchmark.print_results()
    
    # 保存結果
    benchmark.save_results()
    
    logger.info("測試完成")


if __name__ == "__main__":
    main()