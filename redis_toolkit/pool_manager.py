# -*- coding: utf-8 -*-
"""
Redis 連接池管理器
提供全局的連接池管理，避免重複創建連接
"""

import threading
from typing import Dict, Optional, Tuple
import hashlib
import json

from redis import ConnectionPool, Redis
from redis.connection import ConnectionPool as RedisConnectionPool
from pretty_loguru import create_logger

from .options import RedisConnectionConfig

logger = create_logger(
    name="redis_toolkit.pool_manager",
    level="INFO"
)


class ConnectionPoolManager:
    """
    連接池管理器（單例模式）
    根據連接配置管理和共享連接池
    """
    
    _instance = None
    _lock = threading.Lock()
    _pools: Dict[str, ConnectionPool] = {}
    
    def __new__(cls) -> 'ConnectionPoolManager':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ConnectionPoolManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化連接池管理器"""
        if self._initialized:
            return
            
        self._pools = {}
        self._pool_lock = threading.Lock()
        self._initialized = True
        logger.info("ConnectionPoolManager 初始化完成")
    
    def _get_pool_key(self, config: RedisConnectionConfig) -> str:
        """
        根據連接配置生成唯一的池標識
        
        參數:
            config: Redis 連接配置
            
        回傳:
            str: 連接池的唯一標識
        """
        # 使用關鍵連接參數生成唯一標識
        key_params = {
            'host': config.host,
            'port': config.port,
            'db': config.db,
            'username': config.username,
            'password': config.password,
        }
        
        # 將參數轉換為穩定的字符串
        key_str = json.dumps(key_params, sort_keys=True)
        
        # 使用 MD5 生成短的唯一標識
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get_pool(
        self, 
        config: RedisConnectionConfig,
        max_connections: Optional[int] = None
    ) -> ConnectionPool:
        """
        獲取或創建連接池
        
        參數:
            config: Redis 連接配置
            max_connections: 最大連接數（預設為 None，表示無限制）
            
        回傳:
            ConnectionPool: Redis 連接池
        """
        pool_key = self._get_pool_key(config)
        
        # 快速路徑：如果池已存在，直接返回
        if pool_key in self._pools:
            return self._pools[pool_key]
        
        # 慢速路徑：需要創建新池
        with self._pool_lock:
            # 雙重檢查
            if pool_key in self._pools:
                return self._pools[pool_key]
            
            # 創建新的連接池
            pool_kwargs = config.to_redis_kwargs()
            if max_connections is not None:
                pool_kwargs['max_connections'] = max_connections
            
            pool = ConnectionPool(**pool_kwargs)
            self._pools[pool_key] = pool
            
            logger.info(
                f"創建新的連接池 - Host: {config.host}:{config.port}, "
                f"DB: {config.db}, Pool ID: {pool_key[:8]}..."
            )
            
            return pool
    
    def create_client(
        self,
        config: RedisConnectionConfig,
        max_connections: Optional[int] = None
    ) -> Redis:
        """
        使用共享連接池創建 Redis 客戶端
        
        參數:
            config: Redis 連接配置
            max_connections: 最大連接數
            
        回傳:
            Redis: Redis 客戶端實例
        """
        pool = self.get_pool(config, max_connections)
        return Redis(connection_pool=pool)
    
    def close_pool(self, config: RedisConnectionConfig) -> bool:
        """
        關閉特定配置的連接池
        
        參數:
            config: Redis 連接配置
            
        回傳:
            bool: 是否成功關閉
        """
        pool_key = self._get_pool_key(config)
        
        with self._pool_lock:
            if pool_key in self._pools:
                pool = self._pools[pool_key]
                try:
                    pool.disconnect()
                    del self._pools[pool_key]
                    logger.info(f"關閉連接池: {pool_key[:8]}...")
                    return True
                except Exception as e:
                    logger.error(f"關閉連接池時發生錯誤: {e}")
                    return False
        
        return False
    
    def close_all_pools(self) -> None:
        """關閉所有連接池"""
        with self._pool_lock:
            for pool_key, pool in list(self._pools.items()):
                try:
                    pool.disconnect()
                    # 在程式關閉時避免日誌錯誤
                    try:
                        logger.info(f"關閉連接池: {pool_key[:8]}...")
                    except:
                        pass
                except Exception as e:
                    try:
                        logger.error(f"關閉連接池 {pool_key[:8]}... 時發生錯誤: {e}")
                    except:
                        pass
            
            self._pools.clear()
            try:
                logger.info("所有連接池已關閉")
            except:
                pass
    
    def get_pool_stats(self) -> Dict[str, Dict[str, int]]:
        """
        獲取所有連接池的統計信息
        
        回傳:
            Dict: 連接池統計信息
        """
        stats = {}
        
        with self._pool_lock:
            for pool_key, pool in self._pools.items():
                # 獲取連接池的基本信息
                pool_stats = {
                    'created_connections': pool._created_connections,
                    'available_connections': len(pool._available_connections),
                    'in_use_connections': len(pool._in_use_connections),
                }
                
                # 如果有最大連接數限制
                if hasattr(pool, 'max_connections') and pool.max_connections:
                    pool_stats['max_connections'] = pool.max_connections
                
                stats[pool_key[:8] + '...'] = pool_stats
        
        return stats
    
    def __del__(self):
        """清理時關閉所有連接池"""
        try:
            # 直接斷開連接，不記錄日誌
            with self._pool_lock:
                for pool in self._pools.values():
                    try:
                        pool.disconnect()
                    except:
                        pass
                self._pools.clear()
        except Exception:
            pass  # 忽略清理時的錯誤


# 全局連接池管理器實例
pool_manager = ConnectionPoolManager()