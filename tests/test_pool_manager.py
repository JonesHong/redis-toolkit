#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試連接池管理器
"""

import pytest
import threading
import time
from redis_toolkit import (
    RedisToolkit, 
    RedisOptions, 
    RedisConnectionConfig,
    pool_manager
)


class TestConnectionPoolManager:
    """測試連接池管理器功能"""
    
    def teardown_method(self):
        """每個測試後清理連接池"""
        pool_manager.close_all_pools()
    
    def test_singleton_pattern(self):
        """測試單例模式"""
        from redis_toolkit.pool_manager import ConnectionPoolManager
        
        manager1 = ConnectionPoolManager()
        manager2 = ConnectionPoolManager()
        
        assert manager1 is manager2
        assert manager1 is pool_manager
    
    def test_shared_pool(self):
        """測試連接池共享"""
        config = RedisConnectionConfig()
        
        # 創建兩個使用相同配置的工具包
        toolkit1 = RedisToolkit(
            config=config,
            options=RedisOptions(
                is_logger_info=False,
                use_connection_pool=True
            )
        )
        
        toolkit2 = RedisToolkit(
            config=config,
            options=RedisOptions(
                is_logger_info=False,
                use_connection_pool=True
            )
        )
        
        # 應該使用相同的連接池
        assert toolkit1._redis_client.connection_pool is toolkit2._redis_client.connection_pool
        
        # 測試功能正常
        toolkit1.setter("shared_test", "test_value")
        assert toolkit2.getter("shared_test") == "test_value"
        
        # 清理
        toolkit1.deleter("shared_test")
        toolkit1.cleanup()
        toolkit2.cleanup()
    
    def test_different_pools_for_different_configs(self):
        """測試不同配置使用不同的連接池"""
        config1 = RedisConnectionConfig(db=0)
        config2 = RedisConnectionConfig(db=1)
        
        toolkit1 = RedisToolkit(
            config=config1,
            options=RedisOptions(
                is_logger_info=False,
                use_connection_pool=True
            )
        )
        
        toolkit2 = RedisToolkit(
            config=config2,
            options=RedisOptions(
                is_logger_info=False,
                use_connection_pool=True
            )
        )
        
        # 應該使用不同的連接池
        assert toolkit1._redis_client.connection_pool is not toolkit2._redis_client.connection_pool
        
        # 測試隔離性
        toolkit1.setter("db_test", "db0_value")
        toolkit2.setter("db_test", "db1_value")
        
        assert toolkit1.getter("db_test") == "db0_value"
        assert toolkit2.getter("db_test") == "db1_value"
        
        # 清理
        toolkit1.deleter("db_test")
        toolkit2.deleter("db_test")
        toolkit1.cleanup()
        toolkit2.cleanup()
    
    def test_disable_connection_pool(self):
        """測試禁用連接池"""
        config = RedisConnectionConfig()
        
        toolkit1 = RedisToolkit(
            config=config,
            options=RedisOptions(
                is_logger_info=False,
                use_connection_pool=False  # 禁用連接池
            )
        )
        
        toolkit2 = RedisToolkit(
            config=config,
            options=RedisOptions(
                is_logger_info=False,
                use_connection_pool=False  # 禁用連接池
            )
        )
        
        # 應該使用不同的連接池（各自獨立）
        assert toolkit1._redis_client.connection_pool is not toolkit2._redis_client.connection_pool
        
        toolkit1.cleanup()
        toolkit2.cleanup()
    
    def test_max_connections(self):
        """測試最大連接數限制"""
        config = RedisConnectionConfig()
        
        # 創建有連接數限制的工具包
        toolkit = RedisToolkit(
            config=config,
            options=RedisOptions(
                is_logger_info=False,
                use_connection_pool=True,
                max_connections=5  # 限制最大連接數
            )
        )
        
        # 連接池應該有最大連接數限制
        pool = toolkit._redis_client.connection_pool
        assert hasattr(pool, 'max_connections')
        # 注意：實際的 max_connections 屬性可能因 redis-py 版本而異
        
        toolkit.cleanup()
    
    def test_pool_stats(self):
        """測試連接池統計信息"""
        config = RedisConnectionConfig()
        
        toolkit = RedisToolkit(
            config=config,
            options=RedisOptions(
                is_logger_info=False,
                use_connection_pool=True
            )
        )
        
        # 執行一些操作
        toolkit.setter("stats_test", "value")
        toolkit.getter("stats_test")
        
        # 獲取統計信息
        stats = pool_manager.get_pool_stats()
        assert len(stats) > 0
        
        # 應該包含連接信息
        pool_key = list(stats.keys())[0]
        assert 'created_connections' in stats[pool_key]
        assert 'available_connections' in stats[pool_key]
        assert 'in_use_connections' in stats[pool_key]
        
        # 清理
        toolkit.deleter("stats_test")
        toolkit.cleanup()
    
    def test_concurrent_access(self):
        """測試並發訪問連接池"""
        config = RedisConnectionConfig()
        results = []
        errors = []
        
        def worker(worker_id):
            try:
                toolkit = RedisToolkit(
                    config=config,
                    options=RedisOptions(
                        is_logger_info=False,
                        use_connection_pool=True
                    )
                )
                
                # 執行一些操作
                key = f"concurrent_test_{worker_id}"
                value = f"value_{worker_id}"
                toolkit.setter(key, value)
                result = toolkit.getter(key)
                
                results.append(result == value)
                
                # 清理
                toolkit.deleter(key)
                toolkit.cleanup()
                
            except Exception as e:
                errors.append(e)
        
        # 創建多個線程
        threads = []
        for i in range(10):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()
        
        # 等待所有線程完成
        for t in threads:
            t.join()
        
        # 檢查結果
        assert len(errors) == 0, f"發生錯誤: {errors}"
        assert all(results), "某些操作失敗"
        assert len(results) == 10
    
    def test_pool_cleanup(self):
        """測試連接池清理"""
        config1 = RedisConnectionConfig(db=0)
        config2 = RedisConnectionConfig(db=1)
        
        # 創建使用不同連接池的工具包
        toolkit1 = RedisToolkit(config=config1, options=RedisOptions(is_logger_info=False))
        toolkit2 = RedisToolkit(config=config2, options=RedisOptions(is_logger_info=False))
        
        # 確認有兩個連接池
        stats = pool_manager.get_pool_stats()
        assert len(stats) == 2
        
        # 關閉一個特定的連接池
        success = pool_manager.close_pool(config1)
        assert success
        
        # 應該只剩一個連接池
        stats = pool_manager.get_pool_stats()
        assert len(stats) == 1
        
        # 關閉所有連接池
        pool_manager.close_all_pools()
        stats = pool_manager.get_pool_stats()
        assert len(stats) == 0
        
        # 清理
        toolkit1.cleanup()
        toolkit2.cleanup()