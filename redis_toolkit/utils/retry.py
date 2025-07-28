# -*- coding: utf-8 -*-
"""
Redis Toolkit 重試機制模組
提供簡單而有效的重試功能
"""
import time
import functools
from typing import Callable, Type, Tuple, Optional, Union

import redis
from pretty_loguru import create_logger

logger = create_logger(name="redis_toolkit.retry", level="INFO")

def simple_retry(
    func: Callable = None,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exceptions: Tuple[Type[Exception], ...] = (redis.ConnectionError, redis.TimeoutError)
) -> Callable:
    """
    簡單的重試裝飾器

    參數:
        func: 要裝飾的函數
        max_retries: 最大重試次數
        base_delay: 基礎延遲時間（秒）
        max_delay: 最大延遲時間（秒）
        exceptions: 需要重試的例外類型

    回傳:
        Callable: 裝飾後的函數
    """
    def decorator(f: Callable) -> Callable:
        retries = max(0, max_retries)

        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(retries + 1):
                try:
                    return f(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == retries:
                        # 最後一次嘗試失敗
                        logger.error(f"函數 {f.__name__} 在 {retries + 1} 次嘗試後失敗: {e}")
                        raise

                    # 計算延遲時間（指數退避）
                    delay = min(base_delay * (2 ** attempt), max_delay)

                    # 記錄重試日誌
                    logger.warning(f"函數 {f.__name__} 第 {attempt + 1} 次嘗試失敗: {e}，{delay:.2f} 秒後重試.")

                    # 等待後重試
                    time.sleep(delay)
                except Exception as e:
                    # 不在重試範圍內的例外直接拋出
                    logger.error(f"函數 {f.__name__} 發生不可重試的例外: {e}")
                    raise

            # 理論上不會到達這裡
            if last_exception:
                raise last_exception

        return wrapper

    # 支援直接使用或帶參數使用
    if func is None:
        return decorator
    else:
        return decorator(func)


def with_retry(
    max_attempts: int = 3,
    delay: float = 0.1,
    backoff_factor: float = 2,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = (redis.RedisError,),
    on_retry: Optional[Callable[[Exception, int], None]] = None
) -> Callable[[Callable], Callable]:
    """
    進階的重試裝飾器，符合規格要求
    
    參數:
        max_attempts: 最大重試次數
        delay: 初始延遲時間（秒）
        backoff_factor: 延遲時間的退避因子（支援指數退避）
        exceptions: 要捕獲並重試的例外類型
        on_retry: 重試時的回調函數，接收 (exception, attempt_number)
        
    返回:
        裝飾器函數
        
    使用範例:
        >>> @with_retry(max_attempts=5, delay=0.5)
        ... def unstable_operation():
        ...     # 可能失敗的操作
        ...     pass
        
        >>> @with_retry(exceptions=(ConnectionError, TimeoutError))
        ... def network_operation():
        ...     # 網路相關操作
        ...     pass
    """
    # 如果傳入的是單個例外類型，轉換為 tuple
    if isinstance(exceptions, type) and issubclass(exceptions, Exception):
        exceptions = (exceptions,)
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    result = func(*args, **kwargs)
                    if attempt > 1:
                        logger.success(
                            f"函數 {func.__name__} 在第 {attempt} 次嘗試成功"
                        )
                    return result
                    
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts:
                        logger.error(
                            f"函數 {func.__name__} 在 {max_attempts} 次嘗試後失敗: {e}"
                        )
                        raise
                    
                    logger.warning(
                        f"函數 {func.__name__} 第 {attempt} 次嘗試失敗: {e}. "
                        f"等待 {current_delay:.2f} 秒後重試..."
                    )
                    
                    # 執行重試回調
                    if on_retry:
                        try:
                            on_retry(e, attempt)
                        except Exception as callback_error:
                            logger.error(f"重試回調失敗: {callback_error}")
                    
                    # 等待並更新延遲時間
                    time.sleep(current_delay)
                    current_delay *= backoff_factor
                    
                except Exception as e:
                    # 非預期的例外，不重試
                    logger.error(
                        f"函數 {func.__name__} 發生非預期錯誤: {type(e).__name__}: {e}"
                    )
                    raise
            
            # 理論上不應該到達這裡
            if last_exception:
                raise last_exception
            raise RuntimeError(f"函數 {func.__name__} 重試邏輯錯誤")
        
        return wrapper
    
    return decorator
