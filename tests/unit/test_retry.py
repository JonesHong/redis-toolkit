#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis Toolkit 重試機制測試
"""

import pytest
import time
from unittest.mock import Mock, patch
import redis
from redis_toolkit.utils.retry import simple_retry, with_retry


class TestSimpleRetry:
    """簡單重試裝飾器測試"""
    
    def test_successful_function(self):
        """測試成功執行的函數"""
        
        @simple_retry
        def successful_function():
            return "success"
        
        result = successful_function()
        assert result == "success"
    
    def test_retry_on_redis_error(self):
        """測試 Redis 錯誤時的重試"""
        call_count = [0]
        
        @simple_retry(max_retries=3, base_delay=0.01)
        def failing_function():
            call_count[0] += 1
            if call_count[0] < 3:
                raise redis.ConnectionError("模擬連線失敗")
            return "success after retries"
        
        result = failing_function()
        assert result == "success after retries"
        assert call_count[0] == 3
    
    def test_max_retries_exceeded(self):
        """測試超過最大重試次數"""
        call_count = [0]
        
        @simple_retry(max_retries=2, base_delay=0.01)
        def always_failing_function():
            call_count[0] += 1
            raise redis.ConnectionError("持續失敗")
        
        with pytest.raises(redis.ConnectionError):
            always_failing_function()
        
        assert call_count[0] == 3  # 初始嘗試 + 2 次重試
    
    def test_non_retryable_exception(self):
        """測試不可重試的異常"""
        call_count = [0]
        
        @simple_retry(max_retries=3, base_delay=0.01)
        def non_retryable_error():
            call_count[0] += 1
            raise ValueError("不可重試的錯誤")
        
        with pytest.raises(ValueError):
            non_retryable_error()
        
        assert call_count[0] == 1  # 只執行一次，不重試
    
    def test_custom_exceptions(self):
        """測試自訂異常類型"""
        call_count = [0]
        
        class CustomError(Exception):
            pass
        
        @simple_retry(max_retries=2, base_delay=0.01, exceptions=(CustomError,))
        def custom_error_function():
            call_count[0] += 1
            if call_count[0] < 2:
                raise CustomError("自訂錯誤")
            return "成功"
        
        result = custom_error_function()
        assert result == "成功"
        assert call_count[0] == 2
    
    def test_exponential_backoff(self):
        """測試指數退避延遲"""
        delays = []
        
        @simple_retry(max_retries=3, base_delay=0.1, max_delay=1.0)
        def function_with_delays():
            start = time.time()
            raise redis.ConnectionError("測試延遲")
        
        # 記錄實際延遲時間
        with patch('time.sleep') as mock_sleep:
            with pytest.raises(redis.ConnectionError):
                function_with_delays()
            
            # 檢查 sleep 被呼叫的次數和參數
            assert mock_sleep.call_count == 3
            call_args = [call[0][0] for call in mock_sleep.call_args_list]
            
            # 驗證指數退避：0.1, 0.2, 0.4
            assert call_args[0] == 0.1
            assert call_args[1] == 0.2
            assert call_args[2] == 0.4
    
    def test_max_delay_limit(self):
        """測試最大延遲限制"""
        @simple_retry(max_retries=5, base_delay=1.0, max_delay=2.0)
        def function_with_max_delay():
            raise redis.ConnectionError("測試最大延遲")
        
        with patch('time.sleep') as mock_sleep:
            with pytest.raises(redis.ConnectionError):
                function_with_max_delay()
            
            # 檢查延遲不超過最大值
            call_args = [call[0][0] for call in mock_sleep.call_args_list]
            for delay in call_args:
                assert delay <= 2.0
    
    def test_function_with_arguments(self):
        """測試帶參數的函數"""
        @simple_retry(max_retries=1, base_delay=0.01)
        def function_with_args(a, b, c=None):
            return f"a={a}, b={b}, c={c}"
        
        result = function_with_args("test1", "test2", c="test3")
        assert result == "a=test1, b=test2, c=test3"
    
    def test_decorator_without_parentheses(self):
        """測試不帶括號的裝飾器使用"""
        @simple_retry
        def simple_function():
            return "直接裝飾"
        
        result = simple_function()
        assert result == "直接裝飾"
    
    def test_decorator_with_parentheses(self):
        """測試帶括號的裝飾器使用"""
        @simple_retry()
        def function_with_parentheses():
            return "帶括號裝飾"
        
        result = function_with_parentheses()
        assert result == "帶括號裝飾"


class TestRetryIntegration:
    """重試機制整合測試"""
    
    @patch('redis.Redis.ping')
    def test_redis_ping_retry(self, mock_ping):
        """測試 Redis ping 重試"""
        # 設定前兩次失敗，第三次成功
        mock_ping.side_effect = [
            redis.ConnectionError("第一次失敗"),
            redis.ConnectionError("第二次失敗"),
            "PONG"
        ]
        
        @simple_retry(max_retries=3, base_delay=0.01)
        def ping_redis():
            return mock_ping()
        
        result = ping_redis()
        assert result == "PONG"
        assert mock_ping.call_count == 3
    
    @patch('redis.Redis.set')
    def test_redis_set_retry(self, mock_set):
        """測試 Redis set 重試"""
        # 第一次超時，第二次成功
        mock_set.side_effect = [
            redis.TimeoutError("設定超時"),
            True
        ]
        
        @simple_retry(max_retries=2, base_delay=0.01)
        def set_value(key, value):
            return mock_set(key, value)
        
        result = set_value("test_key", "test_value")
        assert result is True
        assert mock_set.call_count == 2


class TestRetryLogging:
    """重試日誌測試"""
    
    @patch('redis_toolkit.utils.retry.logger')
    def test_retry_logging(self, mock_logger):
        """測試重試過程的日誌記錄"""
        call_count = [0]
        
        @simple_retry(max_retries=2, base_delay=0.01)
        def logging_function():
            call_count[0] += 1
            if call_count[0] < 3:
                raise redis.ConnectionError(f"失敗 {call_count[0]}")
            return "成功"
        
        result = logging_function()
        assert result == "成功"
        
        # 檢查警告日誌被呼叫
        assert mock_logger.warning.call_count == 2
        
        # 檢查日誌內容
        warning_calls = mock_logger.warning.call_args_list
        assert "第 1 次嘗試失敗" in warning_calls[0][0][0]
        assert "第 2 次嘗試失敗" in warning_calls[1][0][0]
    
    @patch('redis_toolkit.utils.retry.logger')
    def test_final_failure_logging(self, mock_logger):
        """測試最終失敗的日誌記錄"""
        @simple_retry(max_retries=1, base_delay=0.01)
        def always_failing():
            raise redis.ConnectionError("持續失敗")
        
        with pytest.raises(redis.ConnectionError):
            always_failing()
        
        # 檢查錯誤日誌被呼叫
        mock_logger.error.assert_called_once()
        assert "在 2 次嘗試後失敗" in mock_logger.error.call_args[0][0]


class TestRetryPerformance:
    """重試機制效能測試"""
    
    def test_no_retry_performance(self):
        """測試無重試時的效能"""
        @simple_retry(max_retries=3, base_delay=0.01)
        def fast_function():
            return "快速執行"
        
        start_time = time.time()
        for _ in range(100):
            fast_function()
        end_time = time.time()
        
        # 100 次呼叫應該很快完成（無重試開銷）
        assert end_time - start_time < 1.0
    
    def test_retry_overhead(self):
        """測試重試的開銷"""
        call_count = [0]
        
        @simple_retry(max_retries=2, base_delay=0.01)
        def function_with_retry():
            call_count[0] += 1
            if call_count[0] == 1:
                raise redis.ConnectionError("第一次失敗")
            return "成功"
        
        start_time = time.time()
        result = function_with_retry()
        end_time = time.time()
        
        assert result == "成功"
        # 應該有一次重試延遲
        assert 0.01 <= end_time - start_time < 0.1


class TestRetryEdgeCases:
    """重試邊界情況測試"""
    
    def test_zero_retries(self):
        """測試零重試次數"""
        call_count = [0]
        
        @simple_retry(max_retries=0, base_delay=0.01)
        def no_retry_function():
            call_count[0] += 1
            raise redis.ConnectionError("立即失敗")
        
        with pytest.raises(redis.ConnectionError):
            no_retry_function()
        
        assert call_count[0] == 1  # 只執行一次
    
    def test_negative_retries(self):
        """測試負數重試次數（應該當作零處理）"""
        call_count = [0]
        
        @simple_retry(max_retries=-1, base_delay=0.01)
        def negative_retry_function():
            call_count[0] += 1
            raise redis.ConnectionError("負數重試")
        
        with pytest.raises(redis.ConnectionError):
            negative_retry_function()
        
        assert call_count[0] == 1
    
    def test_very_small_delay(self):
        """測試極小延遲"""
        @simple_retry(max_retries=1, base_delay=0.001)
        def small_delay_function():
            raise redis.ConnectionError("極小延遲")
        
        start_time = time.time()
        with pytest.raises(redis.ConnectionError):
            small_delay_function()
        end_time = time.time()
        
        # 應該有延遲但很小
        assert 0.001 <= end_time - start_time < 0.1


class TestWithRetry:
    """進階重試裝飾器測試"""
    
    def test_successful_function(self):
        """測試成功執行的函數"""
        
        @with_retry(max_attempts=3, delay=0.01)
        def successful_function():
            return "success"
        
        result = successful_function()
        assert result == "success"
    
    def test_retry_on_redis_error(self):
        """測試 Redis 錯誤時的重試"""
        call_count = [0]
        
        @with_retry(max_attempts=3, delay=0.01, backoff_factor=2)
        def failing_function():
            call_count[0] += 1
            if call_count[0] < 3:
                raise redis.ConnectionError("模擬連線失敗")
            return "success after retries"
        
        result = failing_function()
        assert result == "success after retries"
        assert call_count[0] == 3
    
    def test_max_attempts_exceeded(self):
        """測試超過最大嘗試次數"""
        call_count = [0]
        
        @with_retry(max_attempts=2, delay=0.01)
        def always_failing_function():
            call_count[0] += 1
            raise redis.ConnectionError("持續失敗")
        
        with pytest.raises(redis.ConnectionError):
            always_failing_function()
        
        assert call_count[0] == 2  # 總共嘗試 2 次
    
    def test_custom_exceptions(self):
        """測試自訂異常類型"""
        call_count = [0]
        
        class CustomError(Exception):
            pass
        
        @with_retry(max_attempts=2, delay=0.01, exceptions=(CustomError,))
        def custom_error_function():
            call_count[0] += 1
            if call_count[0] < 2:
                raise CustomError("自訂錯誤")
            return "成功"
        
        result = custom_error_function()
        assert result == "成功"
        assert call_count[0] == 2
    
    def test_single_exception_type(self):
        """測試單一異常類型（非 tuple）"""
        call_count = [0]
        
        @with_retry(max_attempts=2, delay=0.01, exceptions=redis.TimeoutError)
        def timeout_function():
            call_count[0] += 1
            if call_count[0] < 2:
                raise redis.TimeoutError("超時")
            return "成功"
        
        result = timeout_function()
        assert result == "成功"
        assert call_count[0] == 2
    
    def test_exponential_backoff(self):
        """測試指數退避延遲"""
        @with_retry(max_attempts=3, delay=0.1, backoff_factor=2)
        def function_with_delays():
            raise redis.ConnectionError("測試延遲")
        
        with patch('time.sleep') as mock_sleep:
            with pytest.raises(redis.ConnectionError):
                function_with_delays()
            
            # 檢查 sleep 被呼叫的次數和參數
            assert mock_sleep.call_count == 2  # 第1次和第2次重試需要延遲
            call_args = [call[0][0] for call in mock_sleep.call_args_list]
            
            # 驗證指數退避：0.1, 0.2
            assert call_args[0] == 0.1
            assert call_args[1] == 0.2
    
    def test_on_retry_callback(self):
        """測試重試回調函數"""
        callback_calls = []
        
        def retry_callback(exception, attempt):
            callback_calls.append((type(exception).__name__, attempt))
        
        @with_retry(max_attempts=3, delay=0.01, on_retry=retry_callback)
        def failing_with_callback():
            if len(callback_calls) < 2:
                raise redis.ConnectionError("需要重試")
            return "成功"
        
        result = failing_with_callback()
        assert result == "成功"
        assert len(callback_calls) == 2
        assert callback_calls[0] == ("ConnectionError", 1)
        assert callback_calls[1] == ("ConnectionError", 2)
    
    def test_callback_error_handling(self):
        """測試回調函數錯誤處理"""
        def bad_callback(exception, attempt):
            raise ValueError("回調錯誤")
        
        @with_retry(max_attempts=2, delay=0.01, on_retry=bad_callback)
        def function_with_bad_callback():
            raise redis.ConnectionError("觸發回調")
        
        # 即使回調失敗，重試機制仍應正常運作
        with patch('redis_toolkit.utils.retry.logger') as mock_logger:
            with pytest.raises(redis.ConnectionError):
                function_with_bad_callback()
            
            # 檢查回調錯誤被記錄
            assert any("重試回調失敗" in str(call) for call in mock_logger.error.call_args_list)
    
    def test_function_with_arguments(self):
        """測試帶參數的函數"""
        @with_retry(max_attempts=1, delay=0.01)
        def function_with_args(a, b, c=None):
            return f"a={a}, b={b}, c={c}"
        
        result = function_with_args("test1", "test2", c="test3")
        assert result == "a=test1, b=test2, c=test3"
    
    @patch('redis_toolkit.utils.retry.logger')
    def test_success_after_retry_logging(self, mock_logger):
        """測試重試後成功的日誌記錄"""
        call_count = [0]
        
        @with_retry(max_attempts=3, delay=0.01)
        def eventually_successful():
            call_count[0] += 1
            if call_count[0] < 3:
                raise redis.ConnectionError("暫時失敗")
            return "最終成功"
        
        result = eventually_successful()
        assert result == "最終成功"
        
        # 檢查成功日誌
        success_calls = [call for call in mock_logger.success.call_args_list 
                        if "在第 3 次嘗試成功" in str(call)]
        assert len(success_calls) == 1


class TestWithRetryIntegration:
    """with_retry 整合測試"""
    
    def test_with_redis_toolkit_methods(self):
        """測試與 RedisToolkit 方法的整合"""
        from redis_toolkit import RedisToolkit, RedisOptions
        
        # 創建一個模擬的 Redis 客戶端
        mock_redis = Mock()
        mock_redis.set.side_effect = [
            redis.ConnectionError("第一次失敗"),
            True  # 第二次成功
        ]
        
        toolkit = RedisToolkit(redis=mock_redis, options=RedisOptions(
            retry_attempts=2,
            retry_delay=0.01,
            retry_backoff=2
        ))
        
        # setter 方法應該會重試
        toolkit.setter("test_key", "test_value")
        
        # 驗證 set 被調用了兩次
        assert mock_redis.set.call_count == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])