# -*- coding: utf-8 -*-
"""
Redis Toolkit 重試機制模組
提供簡單而有效的重試功能
"""
import time
import logging
import functools
from typing import Callable, Type, Tuple

import redis

logger = logging.getLogger(__name__)

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
