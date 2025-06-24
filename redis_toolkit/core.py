# -*- coding: utf-8 -*-
"""
Redis Toolkit 核心模組
簡化 Redis 操作，自動處理序列化和發布訂閱
"""

import json
import threading
import time
import logging
from typing import Any, Callable, Dict, List, Optional, Union

import redis
from redis import Redis

from .options import RedisOptions, RedisConnectionConfig, DEFAULT_OPTIONS
from .exceptions import RedisToolkitError, SerializationError, wrap_redis_exceptions
from .utils.serializers import serialize_value, deserialize_value
from .utils.retry import simple_retry

# 設定預設日誌
logger = logging.getLogger(__name__)


class RedisToolkit:
    """
    增強版 Redis 工具包
    自動處理多種資料類型的序列化，簡化發布訂閱操作
    """

    def __init__(
        self,
        redis_client: Optional[Redis] = None,
        config: Optional[RedisConnectionConfig] = None,
        channels: Optional[List[str]] = None,
        message_handler: Optional[Callable[[str, Any], None]] = None,
        enable_retry: bool = True,
        options: Optional[RedisOptions] = None,
    ):
        """
        初始化 RedisToolkit

        參數:
            redis_client: Redis 客戶端實例，若為 None 則根據 config 建立
            config: Redis 連線配置
            channels: 要訂閱的頻道列表
            message_handler: 訊息處理函數
            enable_retry: 是否啟用重試機制
            options: 工具包配置選項
        """
        self.options = options or DEFAULT_OPTIONS
        self.enable_retry = enable_retry
        self.run_subscriber = True
        self.sub_thread: Optional[threading.Thread] = None

        # 初始化 Redis 客戶端
        self._init_redis_client(redis_client, config)

        # 發布訂閱相關
        self._channels = channels
        self._message_handler = message_handler

        if channels and message_handler:
            self._start_subscriber()

    def _init_redis_client(
        self, redis_client: Optional[Redis], config: Optional[RedisConnectionConfig]
    ):
        """初始化 Redis 客戶端"""
        if redis_client is None:
            if config is None:
                config = RedisConnectionConfig()
            self._redis_client = Redis(**config.to_redis_kwargs())
        else:
            self._redis_client = redis_client

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
        except redis.RedisError:
            return False
        except Exception:
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

        try:
            # 序列化處理
            serialized_value = serialize_value(value)

            # 記錄日誌
            if opts.is_logger_info:
                log_content = self._format_log(original_value, opts.max_log_size)
                logger.info(f"設定 {name}: {log_content}")

            # 存儲到 Redis（可選重試）
            if self.enable_retry:
                simple_retry(self._redis_client.set)(name, serialized_value)
            else:
                self._redis_client.set(name, serialized_value)

        except Exception as e:
            raise SerializationError(
                f"設定鍵 '{name}' 失敗",
                original_data=original_value,
                original_exception=e,
            ) from e

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

        try:
            # 從 Redis 取得資料（可選重試）
            if self.enable_retry:
                raw_value = simple_retry(self._redis_client.get)(name)
            else:
                raw_value = self._redis_client.get(name)

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
        if self.enable_retry:
            result = simple_retry(self._redis_client.delete)(name)
        else:
            result = self._redis_client.delete(name)

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

        try:
            with self._redis_client.pipeline() as pipe:
                for key, value in mapping.items():
                    serialized_value = serialize_value(value)
                    pipe.set(key, serialized_value)
                pipe.execute()

            if opts.is_logger_info:
                logger.info(f"批次設定 {len(mapping)} 個鍵")

        except Exception as e:
            raise SerializationError(
                f"批次設定 {len(mapping)} 個鍵失敗", original_exception=e
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

        try:
            raw_values = self._redis_client.mget(names)
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

            # 發布訊息（可選重試）
            if self.enable_retry:
                simple_retry(self._redis_client.publish)(channel, message)
            else:
                self._redis_client.publish(channel, message)

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

        # 嘗試透過發送特殊訊息來中斷監聽迴圈
        try:
            self._redis_client.publish("__redis_toolkit_stop__", "stop")
        except Exception:
            pass  # 忽略發布失敗的錯誤

        # 等待執行緒結束
        if self.sub_thread and self.sub_thread.is_alive():
            self.sub_thread.join(timeout=self.options.subscriber_stop_timeout)
            if self.sub_thread.is_alive():
                logger.warning("訂閱者執行緒未能正常停止")
            else:
                logger.info("訂閱者執行緒已成功停止")

    def _subscriber_loop(self) -> None:
        """訂閱者主迴圈"""
        while self.run_subscriber:
            try:
                pubsub = self._redis_client.pubsub()
                if self._channels:
                    # 訂閱使用者頻道和停止訊號頻道
                    all_channels = list(self._channels) + ["__redis_toolkit_stop__"]
                    pubsub.subscribe(*all_channels)
                    channel_names = ", ".join(self._channels)
                    logger.info(f"正在監聽頻道 '{channel_names}'")

                    for message in pubsub.listen():
                        if not self.run_subscriber:
                            break

                        if message["type"] == "message":
                            channel = message["channel"].decode()

                            # 檢查是否為停止訊號
                            if channel == "__redis_toolkit_stop__":
                                logger.debug("收到停止訊號，中斷訂閱迴圈")
                                break

                            # 處理正常訊息
                            self._process_message(message)

                    pubsub.close()
                else:
                    logger.info("沒有頻道需要訂閱")
                    break

            except redis.ConnectionError as e:
                logger.error(f"Redis 連線錯誤: {e}")
                self._wait_and_retry_connection()
            except Exception as e:
                logger.error(f"訂閱者發生未預期錯誤: {e}")
                time.sleep(self.options.subscriber_retry_delay)

        logger.debug("訂閱者迴圈已結束")

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
            try:
                decoded_data = data.decode("utf-8")
                return self._truncate_string(decoded_data, max_size)
            except UnicodeDecodeError:
                return f"<位元組: {len(data)} 位元組已隱藏>"

        elif isinstance(data, dict):
            try:
                json_data = json.dumps(data, ensure_ascii=False)
                return self._truncate_string(json_data, max_size)
            except Exception as e:
                return f"<字典錯誤: {str(e)}>"

        elif isinstance(data, str):
            return self._truncate_string(data, max_size)

        else:
            return str(data)

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
                # 關閉連線池
                if hasattr(self._redis_client, "connection_pool"):
                    self._redis_client.connection_pool.disconnect()

                # 關閉客戶端
                self._redis_client.close()

            except Exception as e:
                logger.warning(f"關閉 Redis 連線時發生警告: {e}")
            finally:
                # 確保清理引用
                self._redis_client = None

        logger.info("RedisToolkit 清理完成")

    def __del__(self):
        """析構函數，確保資源清理"""
        try:
            if hasattr(self, "_redis_client") and self._redis_client:
                self.cleanup()
        except:
            # 在析構函數中忽略所有錯誤，避免程式結束時的異常
            pass


# 向後相容的別名
RedisCore = RedisToolkit
