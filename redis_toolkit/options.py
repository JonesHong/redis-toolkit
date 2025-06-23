# -*- coding: utf-8 -*-
"""
Redis Toolkit 配置選項模組
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class RedisOptions:
    """
    配置 RedisToolkit 的行為選項
    """
    # 日誌相關
    is_logger_info: bool = True              # 是否啟用日誌
    max_log_size: int = 256                  # 最大日誌大小（位元組）
    
    # 訂閱者相關
    subscriber_retry_delay: int = 5          # 訂閱者重連延遲（秒）
    subscriber_stop_timeout: int = 5         # 訂閱者停止逾時（秒）


@dataclass 
class RedisConnectionConfig:
    """
    Redis 連線配置
    """
    host: str = 'localhost'
    port: int = 51201
    db: int = 0
    password: Optional[str] = None
    username: Optional[str] = None
    encoding: str = 'utf-8'
    decode_responses: bool = False
    socket_keepalive: bool = True
    socket_keepalive_options: Optional[dict] = None
    
    def to_redis_kwargs(self) -> dict:
        """
        轉換為 redis.Redis 建構函數參數
        """
        kwargs = {
            'host': self.host,
            'port': self.port,
            'db': self.db,
            'encoding': self.encoding,
            'decode_responses': self.decode_responses,
            'socket_keepalive': self.socket_keepalive,
        }
        
        if self.password:
            kwargs['password'] = self.password
            
        if self.username:
            kwargs['username'] = self.username
            
        if self.socket_keepalive_options:
            kwargs['socket_keepalive_options'] = self.socket_keepalive_options
            
        return kwargs


# 預設配置實例
DEFAULT_OPTIONS = RedisOptions()
DEFAULT_CONNECTION_CONFIG = RedisConnectionConfig()