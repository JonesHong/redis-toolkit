# -*- coding: utf-8 -*-
"""
Redis Toolkit 配置選項模組
"""

from dataclasses import dataclass
from typing import Optional, List, Type


@dataclass
class RedisOptions:
    """
    配置 RedisToolkit 的行為選項
    """
    # 日誌相關
    is_logger_info: bool = True              # 是否啟用日誌
    max_log_size: int = 256                  # 最大日誌大小（位元組）
    log_level: str = "INFO"                  # 日誌級別（DEBUG, INFO, WARNING, ERROR）
    log_path: Optional[str] = None           # 日誌檔案路徑（None 表示不寫入檔案）
    
    # 訂閱者相關
    subscriber_retry_delay: int = 5          # 訂閱者重連延遲（秒）
    subscriber_stop_timeout: int = 5         # 訂閱者停止逾時（秒）
    
    # 安全性相關
    max_value_size: int = 10 * 1024 * 1024   # 最大值大小（位元組），預設 10MB
    max_key_length: int = 512                # 最大鍵長度
    enable_validation: bool = True           # 是否啟用驗證
    
    # 連接池相關
    use_connection_pool: bool = True         # 是否使用共享連接池
    max_connections: Optional[int] = None    # 最大連接數（None 表示無限制）
    
    # 重試相關
    retry_attempts: int = 3                  # 最大重試次數
    retry_delay: float = 0.1                 # 初始重試延遲（秒）
    retry_backoff: float = 2.0               # 重試退避因子（指數退避）
    
    def validate(self) -> None:
        """
        驗證配置的有效性
        
        拋出:
            ValueError: 當配置無效時
        """
        # 驗證日誌級別
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        if self.log_level not in valid_log_levels:
            raise ValueError(
                f"無效的日誌級別: {self.log_level}. "
                f"必須是以下之一: {', '.join(valid_log_levels)}"
            )
        
        # 驗證數值範圍
        if self.max_log_size < 1:
            raise ValueError("max_log_size 必須大於 0")
        
        if self.subscriber_retry_delay < 1:
            raise ValueError("subscriber_retry_delay 必須大於 0")
        
        if self.subscriber_stop_timeout < 1:
            raise ValueError("subscriber_stop_timeout 必須大於 0")
        
        if self.max_value_size < 1:
            raise ValueError("max_value_size 必須大於 0")
        
        if self.max_key_length < 1:
            raise ValueError("max_key_length 必須大於 0")
        
        if self.max_connections is not None and self.max_connections < 1:
            raise ValueError("max_connections 必須大於 0 或為 None")
        
        # 驗證重試參數
        if self.retry_attempts < 0:
            raise ValueError("retry_attempts 必須大於或等於 0")
        
        if self.retry_delay < 0:
            raise ValueError("retry_delay 必須大於或等於 0")
        
        if self.retry_backoff < 1:
            raise ValueError("retry_backoff 必須大於或等於 1")
        
        # 驗證路徑（如果指定）
        if self.log_path is not None:
            import os
            log_dir = os.path.dirname(self.log_path)
            if log_dir and not os.path.exists(log_dir):
                raise ValueError(
                    f"日誌目錄不存在: {log_dir}. "
                    f"請先創建目錄或使用 None 表示不寫入檔案"
                )


@dataclass 
class RedisConnectionConfig:
    """
    Redis 連線配置
    """
    host: str = 'localhost'
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    username: Optional[str] = None
    encoding: str = 'utf-8'
    socket_keepalive: bool = True
    socket_keepalive_options: Optional[dict] = None
    connection_timeout: Optional[float] = None  # 連接超時（秒）
    socket_timeout: Optional[float] = None      # Socket 操作超時（秒）
    retry_on_timeout: bool = False              # 超時時是否重試
    retry_on_error: Optional[List[Type[Exception]]] = None  # 要重試的錯誤類型列表
    health_check_interval: int = 30             # 健康檢查間隔（秒）
    ssl: bool = False                           # 是否使用 SSL/TLS
    ssl_keyfile: Optional[str] = None           # SSL 密鑰檔案
    ssl_certfile: Optional[str] = None          # SSL 證書檔案
    ssl_ca_certs: Optional[str] = None          # SSL CA 證書檔案
    ssl_cert_reqs: str = 'required'             # SSL 證書要求級別
    
    def to_redis_kwargs(self) -> dict:
        """
        轉換為 redis.Redis 建構函數參數
        """
        kwargs = {
            'host': self.host,
            'port': self.port,
            'db': self.db,
            'encoding': self.encoding,
            'decode_responses': False,  # 總是 False 以保證正確的序列化
            'socket_keepalive': self.socket_keepalive,
            'retry_on_timeout': self.retry_on_timeout,
            'health_check_interval': self.health_check_interval,
        }
        
        # 可選參數
        if self.password:
            kwargs['password'] = self.password
            
        if self.username:
            kwargs['username'] = self.username
            
        if self.socket_keepalive_options:
            kwargs['socket_keepalive_options'] = self.socket_keepalive_options
            
        if self.connection_timeout is not None:
            kwargs['socket_connect_timeout'] = self.connection_timeout
            
        if self.socket_timeout is not None:
            kwargs['socket_timeout'] = self.socket_timeout
            
        if self.retry_on_error is not None:
            kwargs['retry_on_error'] = self.retry_on_error
            
        # SSL 相關參數
        if self.ssl:
            kwargs['ssl'] = True
            if self.ssl_keyfile:
                kwargs['ssl_keyfile'] = self.ssl_keyfile
            if self.ssl_certfile:
                kwargs['ssl_certfile'] = self.ssl_certfile
            if self.ssl_ca_certs:
                kwargs['ssl_ca_certs'] = self.ssl_ca_certs
            kwargs['ssl_cert_reqs'] = self.ssl_cert_reqs
            
        return kwargs
    
    def validate(self) -> None:
        """
        驗證連線配置的有效性
        
        拋出:
            ValueError: 當配置無效時
        """
        # 驗證端口範圍
        if not (1 <= self.port <= 65535):
            raise ValueError(f"無效的端口號: {self.port}. 必須在 1-65535 之間")
        
        # 驗證 db 索引
        if self.db < 0:
            raise ValueError(f"無效的數據庫索引: {self.db}. 必須大於或等於 0")
        
        # 驗證超時值
        if self.connection_timeout is not None and self.connection_timeout <= 0:
            raise ValueError("connection_timeout 必須大於 0")
        
        if self.socket_timeout is not None and self.socket_timeout <= 0:
            raise ValueError("socket_timeout 必須大於 0")
        
        # 驗證健康檢查間隔
        if self.health_check_interval < 0:
            raise ValueError("health_check_interval 必須大於或等於 0（0 表示禁用）")
        
        # 驗證 SSL 配置
        if self.ssl:
            if self.ssl_cert_reqs not in ['none', 'optional', 'required']:
                raise ValueError(
                    f"無效的 ssl_cert_reqs: {self.ssl_cert_reqs}. "
                    f"必須是 'none', 'optional' 或 'required' 之一"
                )


# 預設配置實例
DEFAULT_OPTIONS = RedisOptions()
DEFAULT_CONNECTION_CONFIG = RedisConnectionConfig()