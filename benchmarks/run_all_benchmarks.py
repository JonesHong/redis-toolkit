#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis Toolkit 完整性能基準測試套件
執行所有基準測試並生成綜合報告
"""

import os
import sys
import time
import json
from datetime import datetime
from typing import Dict, Any
from pretty_loguru import create_logger

# 添加項目根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 導入各個基準測試模組
from batch_operations_benchmark import BatchOperationsBenchmark
from serialization_benchmark import SerializationBenchmark
from connection_pool_benchmark import ConnectionPoolBenchmark

from redis_toolkit import RedisToolkit, RedisConnectionConfig

logger = create_logger(name="benchmark.suite", level="INFO")


class BenchmarkSuite:
    """基準測試套件"""
    
    def __init__(self):
        self.results = {}
        self.start_time = None
        self.end_time = None
    
    def check_redis_connection(self) -> bool:
        """檢查 Redis 連接"""
        try:
            config = RedisConnectionConfig(host='localhost', port=6379)
            toolkit = RedisToolkit(config=config)
            result = toolkit.health_check()
            toolkit.cleanup()
            return result
        except Exception as e:
            logger.error(f"無法連接到 Redis: {e}")
            return False
    
    def run_batch_operations_benchmark(self):
        """運行批次操作基準測試"""
        logger.info("\n" + "="*80)
        logger.info("執行批次操作基準測試")
        logger.info("="*80)
        
        try:
            config = RedisConnectionConfig(host='localhost', port=6379)
            toolkit = RedisToolkit(config=config)
            
            benchmark = BatchOperationsBenchmark(toolkit)
            data_sizes = [10, 50, 100, 500, 1000]
            results = benchmark.run_benchmark(data_sizes, iterations=3)
            
            toolkit.cleanup()
            
            self.results['batch_operations'] = {
                'status': 'completed',
                'summary': self._summarize_batch_results(results)
            }
            
            logger.success("批次操作基準測試完成")
            
        except Exception as e:
            logger.error(f"批次操作基準測試失敗: {e}")
            self.results['batch_operations'] = {
                'status': 'failed',
                'error': str(e)
            }
    
    def run_serialization_benchmark(self):
        """運行序列化基準測試"""
        logger.info("\n" + "="*80)
        logger.info("執行序列化基準測試")
        logger.info("="*80)
        
        try:
            benchmark = SerializationBenchmark()
            results = benchmark.run_benchmark(iterations=500)
            
            self.results['serialization'] = {
                'status': 'completed',
                'summary': self._summarize_serialization_results(results)
            }
            
            logger.success("序列化基準測試完成")
            
        except Exception as e:
            logger.error(f"序列化基準測試失敗: {e}")
            self.results['serialization'] = {
                'status': 'failed',
                'error': str(e)
            }
    
    def run_connection_pool_benchmark(self):
        """運行連接池基準測試"""
        logger.info("\n" + "="*80)
        logger.info("執行連接池效率測試")
        logger.info("="*80)
        
        try:
            benchmark = ConnectionPoolBenchmark()
            results = benchmark.run_benchmark()
            
            self.results['connection_pool'] = {
                'status': 'completed',
                'summary': self._summarize_connection_pool_results(results)
            }
            
            logger.success("連接池效率測試完成")
            
        except Exception as e:
            logger.error(f"連接池效率測試失敗: {e}")
            self.results['connection_pool'] = {
                'status': 'failed',
                'error': str(e)
            }
    
    def _summarize_batch_results(self, results: Dict) -> Dict:
        """總結批次操作結果"""
        summary = {
            'test_sizes': list(results.keys()),
            'average_improvements': {}
        }
        
        batch_improvements = []
        pipeline_improvements = []
        
        for size, data in results.items():
            if 'improvements' in data:
                batch_improvements.append(data['improvements']['batch_vs_single']['write'])
                pipeline_improvements.append(data['improvements']['pipeline_vs_single']['write'])
        
        if batch_improvements:
            summary['average_improvements']['batch_vs_single'] = sum(batch_improvements) / len(batch_improvements)
        if pipeline_improvements:
            summary['average_improvements']['pipeline_vs_single'] = sum(pipeline_improvements) / len(pipeline_improvements)
        
        return summary
    
    def _summarize_serialization_results(self, results: Dict) -> Dict:
        """總結序列化結果"""
        summary = {
            'data_types_tested': len(results),
            'average_performance': {
                'vs_json': {'serialize': [], 'deserialize': []},
                'vs_pickle': {'serialize': [], 'deserialize': []}
            }
        }
        
        for data_name, result in results.items():
            if 'performance_vs_json' in result:
                summary['average_performance']['vs_json']['serialize'].append(
                    result['performance_vs_json']['serialize']
                )
                summary['average_performance']['vs_json']['deserialize'].append(
                    result['performance_vs_json']['deserialize']
                )
            
            if 'performance_vs_pickle' in result:
                summary['average_performance']['vs_pickle']['serialize'].append(
                    result['performance_vs_pickle']['serialize']
                )
                summary['average_performance']['vs_pickle']['deserialize'].append(
                    result['performance_vs_pickle']['deserialize']
                )
        
        # 計算平均值
        for comparison in ['vs_json', 'vs_pickle']:
            for operation in ['serialize', 'deserialize']:
                values = summary['average_performance'][comparison][operation]
                if values:
                    summary['average_performance'][comparison][operation] = sum(values) / len(values)
                else:
                    summary['average_performance'][comparison][operation] = None
        
        return summary
    
    def _summarize_connection_pool_results(self, results: Dict) -> Dict:
        """總結連接池結果"""
        summary = {
            'single_thread_improvement': None,
            'multi_thread_improvements': {},
            'connection_overhead_reduction': None
        }
        
        # 單線程改善
        if 'single_thread' in results:
            single = results['single_thread']
            summary['single_thread_improvement'] = (
                single['without_pool']['mean'] / single['with_pool']['mean']
            )
        
        # 多線程改善
        if 'multi_thread' in results:
            for threads, data in results['multi_thread'].items():
                summary['multi_thread_improvements'][threads] = (
                    data['with_pool']['throughput'] / data['without_pool']['throughput']
                )
        
        # 連接開銷減少
        if 'connection_overhead' in results:
            summary['connection_overhead_reduction'] = results['connection_overhead']['improvement']
        
        return summary
    
    def generate_report(self):
        """生成綜合報告"""
        report = {
            'test_suite': 'Redis Toolkit Performance Benchmark Suite',
            'version': '1.0.0',
            'test_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'duration': self.end_time - self.start_time if self.end_time and self.start_time else None,
            'results': self.results,
            'overall_summary': self._generate_overall_summary()
        }
        
        # 保存報告
        report_dir = os.path.join(os.path.dirname(__file__), 'results')
        os.makedirs(report_dir, exist_ok=True)
        
        report_file = os.path.join(report_dir, 'benchmark_report.json')
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.success(f"綜合報告已保存到: {report_file}")
        
        # 生成基準值文件
        baseline_file = os.path.join(report_dir, 'performance_baseline.json')
        baseline = self._generate_baseline()
        with open(baseline_file, 'w', encoding='utf-8') as f:
            json.dump(baseline, f, indent=2, ensure_ascii=False)
        
        logger.success(f"性能基準值已保存到: {baseline_file}")
        
        return report
    
    def _generate_overall_summary(self) -> Dict:
        """生成整體總結"""
        summary = {
            'total_tests': len(self.results),
            'successful_tests': sum(1 for r in self.results.values() if r.get('status') == 'completed'),
            'failed_tests': sum(1 for r in self.results.values() if r.get('status') == 'failed'),
            'key_findings': []
        }
        
        # 批次操作發現
        if self.results.get('batch_operations', {}).get('status') == 'completed':
            batch_summary = self.results['batch_operations']['summary']
            if 'average_improvements' in batch_summary:
                avg_batch = batch_summary['average_improvements'].get('batch_vs_single', 0)
                if avg_batch > 1:
                    summary['key_findings'].append(
                        f"批次操作平均提升 {avg_batch:.1f}x 性能"
                    )
        
        # 序列化發現
        if self.results.get('serialization', {}).get('status') == 'completed':
            ser_summary = self.results['serialization']['summary']
            avg_perf = ser_summary.get('average_performance', {})
            if avg_perf.get('vs_json', {}).get('serialize'):
                json_perf = avg_perf['vs_json']['serialize']
                if json_perf < 1:
                    summary['key_findings'].append(
                        f"序列化速度比 JSON 快 {1/json_perf:.1f}x"
                    )
        
        # 連接池發現
        if self.results.get('connection_pool', {}).get('status') == 'completed':
            pool_summary = self.results['connection_pool']['summary']
            if pool_summary.get('connection_overhead_reduction'):
                reduction = pool_summary['connection_overhead_reduction']
                summary['key_findings'].append(
                    f"連接池減少連接開銷 {reduction:.1f}x"
                )
        
        return summary
    
    def _generate_baseline(self) -> Dict:
        """生成性能基準值"""
        baseline = {
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'redis_toolkit_version': '0.3.0',  # 應該從套件中動態獲取
            'benchmarks': {}
        }
        
        # 批次操作基準
        if self.results.get('batch_operations', {}).get('status') == 'completed':
            baseline['benchmarks']['batch_operations'] = {
                'batch_vs_single_improvement': self.results['batch_operations']['summary']
                    .get('average_improvements', {}).get('batch_vs_single', 0),
                'pipeline_vs_single_improvement': self.results['batch_operations']['summary']
                    .get('average_improvements', {}).get('pipeline_vs_single', 0)
            }
        
        # 序列化基準
        if self.results.get('serialization', {}).get('status') == 'completed':
            avg_perf = self.results['serialization']['summary'].get('average_performance', {})
            baseline['benchmarks']['serialization'] = {
                'vs_json_serialize': avg_perf.get('vs_json', {}).get('serialize'),
                'vs_json_deserialize': avg_perf.get('vs_json', {}).get('deserialize'),
                'vs_pickle_serialize': avg_perf.get('vs_pickle', {}).get('serialize'),
                'vs_pickle_deserialize': avg_perf.get('vs_pickle', {}).get('deserialize')
            }
        
        # 連接池基準
        if self.results.get('connection_pool', {}).get('status') == 'completed':
            pool_summary = self.results['connection_pool']['summary']
            baseline['benchmarks']['connection_pool'] = {
                'single_thread_improvement': pool_summary.get('single_thread_improvement'),
                'connection_overhead_reduction': pool_summary.get('connection_overhead_reduction'),
                'multi_thread_improvements': pool_summary.get('multi_thread_improvements', {})
            }
        
        return baseline
    
    def print_summary(self):
        """打印測試總結"""
        logger.info("\n" + "="*80)
        logger.info("性能基準測試總結")
        logger.info("="*80)
        
        overall = self._generate_overall_summary()
        
        logger.info(f"總測試數: {overall['total_tests']}")
        logger.info(f"成功: {overall['successful_tests']}")
        logger.info(f"失敗: {overall['failed_tests']}")
        
        if overall['key_findings']:
            logger.info("\n關鍵發現:")
            for finding in overall['key_findings']:
                logger.info(f"  • {finding}")
        
        if self.end_time and self.start_time:
            logger.info(f"\n總耗時: {self.end_time - self.start_time:.2f} 秒")
    
    def run_all(self):
        """執行所有基準測試"""
        self.start_time = time.time()
        
        # 檢查 Redis 連接
        if not self.check_redis_connection():
            logger.error("無法連接到 Redis，請確保 Redis 服務正在運行")
            return
        
        logger.info("開始執行完整性能基準測試套件...")
        
        # 執行各項測試
        self.run_batch_operations_benchmark()
        self.run_serialization_benchmark()
        self.run_connection_pool_benchmark()
        
        self.end_time = time.time()
        
        # 生成報告
        self.generate_report()
        
        # 打印總結
        self.print_summary()


def main():
    """主函數"""
    suite = BenchmarkSuite()
    suite.run_all()


if __name__ == "__main__":
    main()