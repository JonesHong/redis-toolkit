# -*- coding: utf-8 -*-
"""
Redis Toolkit 核心模組
簡化 Redis 操作，自動處理序列化和發布訂閱
"""

import json
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Union, Tuple

import redis
from redis import Redis
from pretty_loguru import create_logger

from .options import RedisOptions, RedisConnectionConfig, DEFAULT_OPTIONS
from .exceptions import RedisToolkitError, SerializationError, ValidationError, wrap_redis_exceptions
from .utils.serializers import serialize_value, deserialize_value
from .utils.retry import simple_retry, with_retry
from .pool_manager import pool_manager

# 使用 pretty-loguru 設定日誌
logger = create_logger(
    name="redis_toolkit",
    level="INFO",
    log_path=None,  # 預設不寫入檔案
    rotation=None,
    retention=None
)


class RedisToolkit:
    """
    增強版 Redis 工具包
    自動處理多種資料類型的序列化，簡化發布訂閱操作
    """

    def __init__(
        self,
        redis: Optional[Redis] = None,
        config: Optional[RedisConnectionConfig] = None,
        channels: Optional[List[str]] = None,
        message_handler: Optional[Callable[[str, Any], None]] = None,
        options: Optional[RedisOptions] = None,
    ):
        """
        初始化 RedisToolkit

        參數:
            redis: 現有的 Redis 客戶端實例（與 config 二選一）
            config: Redis 連線配置（與 redis 二選一）
            channels: 要訂閱的頻道列表
            message_handler: 訊息處理函數
            options: 工具包配置選項
            
        使用範例:
            # 方式 1：傳入現有的 Redis 實例
            redis_client = Redis(host='localhost', port=6379)
            toolkit = RedisToolkit(redis=redis_client)
            
            # 方式 2：使用配置創建（支援連接池管理）
            config = RedisConnectionConfig(host='localhost', port=6379)
            toolkit = RedisToolkit(config=config)
        """
        self.options = options or DEFAULT_OPTIONS
        self.run_subscriber = True
        self.sub_thread: Optional[threading.Thread] = None
        
        # 更新日誌級別
        global logger
        logger = create_logger(
            name="redis_toolkit",
            level=self.options.log_level,
            log_path=self.options.log_path,
            rotation="daily" if self.options.log_path else None,
            retention="7 days" if self.options.log_path else None
        )

        # 初始化 Redis 客戶端
        if redis is not None and config is not None:
            raise ValueError("不能同時提供 redis 和 config 參數，請選擇其中一種方式")
        elif redis is not None:
            # 使用提供的 Redis 實例
            self._redis_client = redis
            self._using_shared_pool = False
            self._config = None
            logger.debug("使用提供的 Redis 實例")
        else:
            # 使用配置創建
            self._init_redis_client(config)

        # 發布訂閱相關
        self._channels = channels
        self._message_handler = message_handler

        if channels and message_handler:
            self._start_subscriber()

    def _init_redis_client(self, config: Optional[RedisConnectionConfig]):
        """初始化 Redis 客戶端"""
        if config is None:
            config = RedisConnectionConfig()
        
        # 保存配置以便清理時使用
        self._config = config
        
        # 根據配置決定是否使用共享連接池
        if self.options.use_connection_pool:
            # 使用連接池管理器
            self._redis_client = pool_manager.create_client(
                config, 
                self.options.max_connections
            )
            self._using_shared_pool = True
            logger.debug("使用共享連接池")
        else:
            # 創建獨立的客戶端
            self._redis_client = Redis(**config.to_redis_kwargs())
            self._using_shared_pool = False
            logger.debug("使用獨立連接")

    @property
    def client(self) -> Redis:
        """取得原生 Redis 客戶端，用於呼叫未封裝的方法"""
        return self._redis_client

    def __enter__(self):
        """上下文管理器進入點"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出點"""
        self.cleanup()

    @wrap_redis_exceptions
    def health_check(self) -> bool:
        """
        檢查 Redis 連線是否正常

        回傳:
            bool: 連線是否正常
        """
        try:
            self._redis_client.ping()
            return True
        except redis.ConnectionError as e:
            logger.warning(f"Redis 連線錯誤: {e}")
            return False
        except redis.TimeoutError as e:
            logger.warning(f"Redis 連線超時: {e}")
            return False
        except redis.RedisError as e:
            logger.error(f"Redis 錯誤: {e}")
            return False
        except Exception as e:
            logger.error(f"健康檢查時發生未預期錯誤: {type(e).__name__}: {e}")
            return False

    def setter(
        self, name: str, value: Any, options: Optional[RedisOptions] = None
    ) -> None:
        """
        設定鍵值對，支援多種資料類型的自動序列化

        參數:
            name: 鍵名
            value: 值（支援 str, bytes, int, float, bool, dict, list 等）
            options: 配置選項
        """
        opts = options or self.options
        original_value = value

        # 驗證鍵名長度
        if opts.enable_validation and len(name) > opts.max_key_length:
            raise ValidationError(
                f"鍵名長度 ({len(name)}) 超過限制 ({opts.max_key_length})"
            )

        try:
            # 序列化處理
            serialized_value = serialize_value(value)
        except SerializationError:
            raise  # 重新拋出序列化錯誤
        except Exception as e:
            raise SerializationError(
                f"序列化鍵 '{name}' 的值時失敗",
                original_data=value,
                original_exception=e
            ) from e

        # 驗證序列化後的大小
        if opts.enable_validation and len(serialized_value) > opts.max_value_size:
            raise ValidationError(
                f"資料大小 ({len(serialized_value)} bytes) 超過限制 "
                f"({opts.max_value_size} bytes) for key '{name}'"
            )

        # 記錄日誌
        if opts.is_logger_info:
            log_content = self._format_log(original_value, opts.max_log_size)
            logger.info(f"設定 {name}: {log_content}")

        # 定義內部方法以應用重試裝飾器
        @with_retry(
            max_attempts=self.options.retry_attempts,
            delay=self.options.retry_delay,
            backoff_factor=self.options.retry_backoff,
            exceptions=(redis.ConnectionError, redis.TimeoutError)
        )
        def _set_with_retry():
            return self._redis_client.set(name, serialized_value)
        
        try:
            # 存儲到 Redis（使用重試）
            _set_with_retry()
        except redis.RedisError as e:
            raise RedisToolkitError(f"Redis 操作失敗 for key '{name}'") from e

    def getter(self, name: str, options: Optional[RedisOptions] = None) -> Any:
        """
        取得鍵值，支援多種資料類型的自動反序列化

        參數:
            name: 鍵名
            options: 配置選項

        回傳:
            Any: 反序列化後的值
        """
        opts = options or self.options

        # 定義內部方法以應用重試裝飾器
        @with_retry(
            max_attempts=self.options.retry_attempts,
            delay=self.options.retry_delay,
            backoff_factor=self.options.retry_backoff,
            exceptions=(redis.ConnectionError, redis.TimeoutError)
        )
        def _get_with_retry():
            return self._redis_client.get(name)
        
        try:
            # 從 Redis 取得資料（使用重試）
            raw_value = _get_with_retry()

            if raw_value is None:
                return None

            # 反序列化處理
            value = deserialize_value(raw_value)

            # 記錄日誌
            if opts.is_logger_info:
                log_content = self._format_log(value, opts.max_log_size)
                logger.info(f"取得 {name}: {log_content}")

            return value

        except Exception as e:
            raise SerializationError(
                f"取得鍵 '{name}' 失敗", original_exception=e
            ) from e

    def deleter(self, name: str) -> bool:
        """
        刪除鍵

        參數:
            name: 鍵名

        回傳:
            bool: 是否成功刪除
        """
        # 定義內部方法以應用重試裝飾器
        @with_retry(
            max_attempts=self.options.retry_attempts,
            delay=self.options.retry_delay,
            backoff_factor=self.options.retry_backoff,
            exceptions=(redis.ConnectionError, redis.TimeoutError)
        )
        def _delete_with_retry():
            return self._redis_client.delete(name)
        
        result = _delete_with_retry()

        logger.info(f"RedisToolkit 刪除 {name}")
        return bool(result)

    def batch_set(
        self, mapping: Dict[str, Any], options: Optional[RedisOptions] = None
    ) -> None:
        """
        批次設定鍵值對

        參數:
            mapping: 鍵值對字典
            options: 配置選項
        """
        opts = options or self.options
        
        # 預先驗證和序列化
        serialized_data, total_size = self._prepare_batch_data(mapping, opts)
        
        # 驗證總大小
        self._validate_batch_size(total_size, opts)
        
        # 執行批次設定
        self._execute_batch_set(serialized_data, len(mapping), opts)
    
    def _prepare_batch_data(
        self, mapping: Dict[str, Any], opts: RedisOptions
    ) -> Tuple[Dict[str, bytes], int]:
        """準備批次資料，返回序列化資料和總大小"""
        serialized_data = {}
        total_size = 0
        
        for key, value in mapping.items():
            serialized_value = self._validate_and_serialize_batch_item(key, value, opts)
            serialized_data[key] = serialized_value
            total_size += len(serialized_value)
        
        return serialized_data, total_size
    
    def _validate_and_serialize_batch_item(
        self, key: str, value: Any, opts: RedisOptions
    ) -> bytes:
        """驗證並序列化單個批次項目"""
        # 驗證鍵名長度
        if opts.enable_validation and len(key) > opts.max_key_length:
            raise ValidationError(
                f"批次操作中鍵名長度 ({len(key)}) 超過限制 ({opts.max_key_length})"
            )
        
        try:
            serialized_value = serialize_value(value)
        except SerializationError:
            raise
        except Exception as e:
            raise SerializationError(
                f"批次操作中序列化鍵 '{key}' 的值時失敗",
                original_data=value,
                original_exception=e
            ) from e
        
        # 驗證單一值大小
        if opts.enable_validation and len(serialized_value) > opts.max_value_size:
            raise ValidationError(
                f"批次操作中資料大小 ({len(serialized_value)} bytes) "
                f"超過限制 ({opts.max_value_size} bytes) for key '{key}'"
            )
        
        return serialized_value
    
    def _validate_batch_size(self, total_size: int, opts: RedisOptions) -> None:
        """驗證批次總大小"""
        batch_size_limit = opts.max_value_size * 10
        if opts.enable_validation and total_size > batch_size_limit:
            raise ValidationError(
                f"批次操作總大小 ({total_size} bytes) "
                f"超過限制 ({batch_size_limit} bytes)"
            )
    
    def _execute_batch_set(
        self, serialized_data: Dict[str, bytes], count: int, opts: RedisOptions
    ) -> None:
        """執行批次設定操作"""
        @with_retry(
            max_attempts=self.options.retry_attempts,
            delay=self.options.retry_delay,
            backoff_factor=self.options.retry_backoff,
            exceptions=(redis.ConnectionError, redis.TimeoutError)
        )
        def _batch_set_with_retry():
            with self._redis_client.pipeline() as pipe:
                for key, serialized_value in serialized_data.items():
                    pipe.set(key, serialized_value)
                return pipe.execute()
        
        try:
            _batch_set_with_retry()
            
            if opts.is_logger_info:
                logger.info(f"批次設定 {count} 個鍵")
                
        except redis.RedisError as e:
            raise RedisToolkitError(
                f"批次設定 {count} 個鍵的 Redis 操作失敗"
            ) from e

    def batch_get(
        self, names: List[str], options: Optional[RedisOptions] = None
    ) -> Dict[str, Any]:
        """
        批次取得鍵值

        參數:
            names: 鍵名列表
            options: 配置選項

        回傳:
            Dict[str, Any]: 鍵值對字典
        """
        opts = options or self.options

        # 定義內部方法以應用重試裝飾器
        @with_retry(
            max_attempts=self.options.retry_attempts,
            delay=self.options.retry_delay,
            backoff_factor=self.options.retry_backoff,
            exceptions=(redis.ConnectionError, redis.TimeoutError)
        )
        def _batch_get_with_retry():
            return self._redis_client.mget(names)
        
        try:
            raw_values = _batch_get_with_retry()
            result = {}

            for name, raw_value in zip(names, raw_values):
                if raw_value is not None:
                    result[name] = deserialize_value(raw_value)
                else:
                    result[name] = None

            if opts.is_logger_info:
                logger.info(f"批次取得 {len(names)} 個鍵")

            return result

        except Exception as e:
            raise SerializationError(
                f"批次取得 {len(names)} 個鍵失敗", original_exception=e
            ) from e

    def publisher(
        self, channel: str, data: Any, options: Optional[RedisOptions] = None
    ) -> None:
        """
        發布訊息到指定頻道

        參數:
            channel: 頻道名
            data: 要發布的資料
            options: 配置選項
        """
        opts = options or self.options

        try:
            # 序列化訊息
            message = serialize_value(data)

            # 記錄日誌
            if opts.is_logger_info:
                log_content = self._format_log(data, opts.max_log_size)
                logger.info(f"發布到 {channel}: {log_content}")

            # 定義內部方法以應用重試裝飾器
            @with_retry(
                max_attempts=self.options.retry_attempts,
                delay=self.options.retry_delay,
                backoff_factor=self.options.retry_backoff,
                exceptions=(redis.ConnectionError, redis.TimeoutError)
            )
            def _publish_with_retry():
                return self._redis_client.publish(channel, message)
            
            # 發布訊息（使用重試）
            _publish_with_retry()

        except Exception as e:
            raise SerializationError(
                f"發布到頻道 '{channel}' 失敗", original_data=data, original_exception=e
            ) from e


    def _start_subscriber(self) -> None:
        """啟動訂閱者執行緒"""
        if self.sub_thread is None or not self.sub_thread.is_alive():
            self.run_subscriber = True
            self.sub_thread = threading.Thread(
                target=self._subscriber_loop,
                daemon=True,
                name=f"RedisToolkit-Subscriber-{id(self)}",
            )
            self.sub_thread.start()
            logger.info("訂閱者執行緒已啟動")

    def stop_subscriber(self) -> None:
        """安全停止訂閱者"""
        if not self.run_subscriber:
            return

        self.run_subscriber = False

        # 等待執行緒結束
        if self.sub_thread and self.sub_thread.is_alive():
            self.sub_thread.join(timeout=self.options.subscriber_stop_timeout)
            if self.sub_thread.is_alive():
                logger.warning("訂閱者執行緒未能正常停止")
            else:
                logger.info("訂閱者執行緒已成功停止")

    def _subscriber_loop(self) -> None:
        """訂閱者主迴圈"""
        pubsub = None
        
        try:
            while self.run_subscriber:
                try:
                    # 初始化 pubsub
                    if pubsub is None and self._channels:
                        pubsub = self._initialize_pubsub()
                    
                    if not self._channels:
                        logger.info("沒有頻道需要訂閱")
                        break
                    
                    # 讀取並處理消息
                    self._read_and_process_message(pubsub)
                    
                except redis.ConnectionError as e:
                    pubsub = self._handle_connection_error(pubsub, e)
                except Exception as e:
                    self._handle_unexpected_error(e)
        
        finally:
            self._cleanup_pubsub(pubsub)
            logger.debug("訂閱者迴圈已結束")
    
    def _initialize_pubsub(self):
        """初始化 pubsub 連接"""
        pubsub = self._redis_client.pubsub()
        pubsub.subscribe(*self._channels)
        channel_names = ", ".join(self._channels)
        logger.info(f"正在監聽頻道 '{channel_names}'")
        
        # 忽略訂閱確認消息
        for _ in self._channels:
            pubsub.get_message(timeout=0.1)
        
        return pubsub
    
    def _read_and_process_message(self, pubsub) -> None:
        """讀取並處理消息"""
        message = pubsub.get_message(
            ignore_subscribe_messages=True,
            timeout=1.0  # 1 秒超時，讓線程可以定期檢查退出標誌
        )
        
        if message is not None and message["type"] == "message":
            self._process_message(message)
    
    def _handle_connection_error(self, pubsub, error: redis.ConnectionError):
        """處理連接錯誤"""
        logger.error(f"Redis 連線錯誤: {error}")
        
        # 清理現有的 pubsub
        if pubsub:
            try:
                pubsub.close()
            except Exception:
                pass
        
        # 等待並重試連接
        self._wait_and_retry_connection()
        return None
    
    def _handle_unexpected_error(self, error: Exception) -> None:
        """處理未預期的錯誤"""
        logger.error(f"訂閱者發生未預期錯誤: {error}")
        time.sleep(self.options.subscriber_retry_delay)
    
    def _cleanup_pubsub(self, pubsub) -> None:
        """清理 pubsub 連接"""
        if pubsub:
            try:
                pubsub.close()
            except Exception:
                pass

    def _process_message(self, message: dict) -> None:
        """處理接收到的訊息"""
        try:
            channel = message["channel"].decode()
            raw_data = message["data"]

            # 反序列化訊息
            parsed_data = deserialize_value(raw_data)

            # 記錄日誌
            if self.options.is_logger_info:
                log_content = self._format_log(parsed_data, self.options.max_log_size)
                logger.info(f"訂閱 '{channel}': {log_content}")

            # 呼叫訊息處理器
            if self._message_handler:
                self._message_handler(channel, parsed_data)

        except Exception as e:
            logger.error(f"處理訊息時發生錯誤: {e}")

    def _wait_and_retry_connection(self) -> None:
        """等待並重試連線"""
        retry_delay = self.options.subscriber_retry_delay
        while self.run_subscriber:
            try:
                self._redis_client.ping()
                logger.info("Redis 連線已恢復")
                break
            except redis.ConnectionError:
                logger.warning(f"Redis 仍無法連線，{retry_delay} 秒後重試...")
                time.sleep(retry_delay)

    def _format_log(self, data: Any, max_size: int) -> str:
        """
        格式化日誌內容，限制最大日誌長度

        參數:
            data: 要記錄的日誌資料
            max_size: 最大允許的字串大小

        回傳:
            str: 格式化後的日誌字串
        """
        if isinstance(data, bytes):
            return self._format_bytes_log(data, max_size)
        elif isinstance(data, dict):
            return self._format_dict_log(data, max_size)
        elif isinstance(data, (list, tuple)):
            return self._format_sequence_log(data, max_size)
        elif isinstance(data, str):
            return self._truncate_string(data, max_size)
        else:
            return self._format_object_log(data, max_size)
    
    def _format_bytes_log(self, data: bytes, max_size: int) -> str:
        """格式化位元組日誌"""
        try:
            decoded_data = data.decode("utf-8")
            return self._truncate_string(decoded_data, max_size)
        except UnicodeDecodeError:
            return f"<位元組: {len(data)} 位元組已隱藏>"
    
    def _format_dict_log(self, data: dict, max_size: int) -> str:
        """格式化字典日誌"""
        try:
            # 對於大字典，只顯示鍵的數量
            if len(str(data)) > max_size * 2:
                return f"<字典: {len(data)} 個鍵>"
            json_data = json.dumps(data, ensure_ascii=False)
            return self._truncate_string(json_data, max_size)
        except Exception as e:
            return f"<字典: {len(data)} 個鍵, 錯誤: {str(e)}>"
    
    def _format_sequence_log(self, data: Union[list, tuple], max_size: int) -> str:
        """格式化序列（列表/元組）日誌"""
        try:
            # 對於大列表/元組，只顯示元素數量
            if len(str(data)) > max_size * 2:
                return f"<{type(data).__name__}: {len(data)} 個元素>"
            return self._truncate_string(str(data), max_size)
        except Exception:
            return f"<{type(data).__name__}: {len(data)} 個元素>"
    
    def _format_object_log(self, data: Any, max_size: int) -> str:
        """格式化其他物件日誌"""
        try:
            data_str = str(data)
            # 對於其他大型物件，顯示類型和大小
            if len(data_str) > max_size * 2:
                return f"<{type(data).__name__} 物件: {len(data_str)} 字元>"
            return self._truncate_string(data_str, max_size)
        except Exception:
            return f"<{type(data).__name__} 物件>"

    def _truncate_string(self, data: str, max_size: int) -> str:
        """
        截斷字串，如果超過指定大小，用 '...' 代替多餘部分

        參數:
            data: 輸入字串
            max_size: 最大允許的字串大小

        回傳:
            str: 格式化後的字串
        """
        if len(data) > max_size:
            return f"{data[:max_size]}(...) <字串: {len(data)} 位元組，已截斷>"
        return data

    def cleanup(self) -> None:
        """清理資源，改進版本"""
        # 停止訂閱者
        self.stop_subscriber()

        # 明確關閉 Redis 連線
        if hasattr(self, "_redis_client") and self._redis_client:
            try:
                # 如果不是使用共享連接池，才需要關閉
                if not getattr(self, '_using_shared_pool', False):
                    # 關閉連線池
                    if hasattr(self._redis_client, "connection_pool"):
                        self._redis_client.connection_pool.disconnect()

                    # 關閉客戶端
                    self._redis_client.close()
                else:
                    # 使用共享連接池時，只需要釋放引用
                    logger.debug("釋放共享連接池的引用")

            except Exception as e:
                logger.warning(f"關閉 Redis 連線時發生警告: {e}")
            finally:
                # 確保清理引用
                self._redis_client = None

        logger.info("RedisToolkit 清理完成")

