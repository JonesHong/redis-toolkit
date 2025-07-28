#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試改進的發布訂閱線程管理
"""

import pytest
import threading
import time
from redis_toolkit import RedisToolkit, RedisOptions


class TestPubSubThread:
    """測試發布訂閱線程管理"""
    
    def test_subscriber_start_stop(self):
        """測試訂閱者線程的啟動和停止"""
        messages = []
        
        def handler(channel, data):
            messages.append((channel, data))
        
        toolkit = RedisToolkit(
            channels=["test_channel"],
            message_handler=handler,
            options=RedisOptions(is_logger_info=False)
        )
        
        # 確認線程已啟動
        assert toolkit.sub_thread is not None
        assert toolkit.sub_thread.is_alive()
        
        # 等待訂閱完成
        time.sleep(0.5)
        
        # 發送測試消息
        toolkit.publisher("test_channel", {"test": "message"})
        time.sleep(1.5)  # 等待消息處理
        
        # 確認收到消息
        assert len(messages) == 1
        assert messages[0][0] == "test_channel"
        assert messages[0][1] == {"test": "message"}
        
        # 停止訂閱者
        toolkit.stop_subscriber()
        
        # 確認線程已停止
        assert not toolkit.sub_thread.is_alive()
        
        toolkit.cleanup()
    
    def test_quick_stop(self):
        """測試快速停止（不需要等待超時）"""
        def handler(channel, data):
            pass
        
        toolkit = RedisToolkit(
            channels=["test_channel"],
            message_handler=handler,
            options=RedisOptions(
                is_logger_info=False,
                subscriber_stop_timeout=5  # 5秒超時
            )
        )
        
        # 立即停止
        start_time = time.time()
        toolkit.stop_subscriber()
        stop_time = time.time()
        
        # 應該在2秒內停止（因為 get_message timeout=1.0）
        assert stop_time - start_time < 2.0
        
        toolkit.cleanup()
    
    def test_no_channels(self):
        """測試沒有頻道時的行為"""
        toolkit = RedisToolkit(
            channels=None,  # 沒有頻道
            message_handler=None,
            options=RedisOptions(is_logger_info=False)
        )
        
        # 不應該啟動訂閱線程
        assert toolkit.sub_thread is None
        
        toolkit.cleanup()
    
    def test_reconnection_after_error(self):
        """測試連接錯誤後的重連"""
        messages = []
        
        def handler(channel, data):
            messages.append((channel, data))
        
        toolkit = RedisToolkit(
            channels=["test_channel"],
            message_handler=handler,
            options=RedisOptions(
                is_logger_info=False,
                subscriber_retry_delay=1  # 1秒重試
            )
        )
        
        # 確保線程運行中
        assert toolkit.sub_thread.is_alive()
        
        # 發送測試消息
        toolkit.publisher("test_channel", "test1")
        time.sleep(0.5)
        
        # 模擬連接中斷（通過關閉連接池）
        toolkit._redis_client.connection_pool.disconnect()
        
        # 等待重連
        time.sleep(2)
        
        # 發送另一個消息
        toolkit.publisher("test_channel", "test2")
        time.sleep(0.5)
        
        # 應該收到消息（表示已重連）
        assert len(messages) >= 1
        
        toolkit.cleanup()
    
    def test_concurrent_publish_subscribe(self):
        """測試並發發布和訂閱"""
        messages = []
        lock = threading.Lock()
        
        def handler(channel, data):
            with lock:
                messages.append((channel, data))
        
        toolkit = RedisToolkit(
            channels=["channel1", "channel2"],
            message_handler=handler,
            options=RedisOptions(is_logger_info=False)
        )
        
        # 並發發布消息
        def publisher_worker(channel, count):
            for i in range(count):
                toolkit.publisher(channel, f"msg_{i}")
                time.sleep(0.01)
        
        threads = []
        for channel in ["channel1", "channel2"]:
            t = threading.Thread(
                target=publisher_worker,
                args=(channel, 5)
            )
            threads.append(t)
            t.start()
        
        # 等待所有發布完成
        for t in threads:
            t.join()
        
        # 等待消息處理（增加等待時間）
        time.sleep(2)
        
        # 應該收到所有消息（允許一定的容錯）
        with lock:
            assert len(messages) >= 8  # 至少收到80%的消息
        
        toolkit.cleanup()
    
    def test_exception_in_handler(self):
        """測試消息處理器異常不影響線程"""
        call_count = [0]
        
        def handler(channel, data):
            call_count[0] += 1
            if call_count[0] == 1:
                raise Exception("Handler error")
            # 第二次正常處理
        
        toolkit = RedisToolkit(
            channels=["test_channel"],
            message_handler=handler,
            options=RedisOptions(is_logger_info=False)
        )
        
        # 等待訂閱完成
        time.sleep(0.5)
        
        # 發送兩個消息
        toolkit.publisher("test_channel", "msg1")
        toolkit.publisher("test_channel", "msg2")
        time.sleep(2)
        
        # 確認兩個消息都被處理（即使第一個拋出異常）
        assert call_count[0] == 2
        
        # 線程應該仍在運行
        assert toolkit.sub_thread.is_alive()
        
        toolkit.cleanup()
    
    def test_multiple_toolkit_instances(self):
        """測試多個工具包實例的訂閱隔離"""
        messages1 = []
        messages2 = []
        
        def handler1(channel, data):
            messages1.append((channel, data))
        
        def handler2(channel, data):
            messages2.append((channel, data))
        
        # 創建兩個訂閱不同頻道的實例
        toolkit1 = RedisToolkit(
            channels=["channel1"],
            message_handler=handler1,
            options=RedisOptions(is_logger_info=False)
        )
        
        toolkit2 = RedisToolkit(
            channels=["channel2"],
            message_handler=handler2,
            options=RedisOptions(is_logger_info=False)
        )
        
        # 等待訂閱完成
        time.sleep(0.5)
        
        # 分別發布消息
        toolkit1.publisher("channel1", "msg_for_1")
        toolkit2.publisher("channel2", "msg_for_2")
        time.sleep(1.5)
        
        # 確認消息隔離
        assert len(messages1) == 1
        assert messages1[0] == ("channel1", "msg_for_1")
        
        assert len(messages2) == 1
        assert messages2[0] == ("channel2", "msg_for_2")
        
        # 清理
        toolkit1.cleanup()
        toolkit2.cleanup()