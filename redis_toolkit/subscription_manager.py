# -*- coding: utf-8 -*-
"""
動態訂閱管理器
提供動態訂閱、自動過期、續訂等功能
"""

import threading
import time
from typing import Callable, Dict, Optional, Set, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from pretty_loguru import create_logger

# 使用 pretty-loguru 設定日誌
logger = create_logger(
    name="redis_toolkit.subscription",
    level="INFO",
    log_path=None,
    rotation=None,
    retention=None
)


@dataclass
class ChannelInfo:
    """頻道資訊"""
    name: str
    callback: Callable[[str, Any], None]
    last_activity: float = field(default_factory=time.time)
    subscribe_time: float = field(default_factory=time.time)
    message_count: int = 0
    is_active: bool = True


class SubscriptionManager:
    """
    動態訂閱管理器
    
    功能特點:
    - 動態新增/移除訂閱頻道
    - 自動過期機制（預設5分鐘無活動自動取消訂閱）
    - 過期頻道記錄與查詢
    - 續訂過期頻道
    - 執行緒安全設計
    """
    
    def __init__(
        self,
        expire_minutes: float = 5.0,
        check_interval: float = 30.0,
        auto_cleanup: bool = True
    ):
        """
        初始化訂閱管理器
        
        參數:
            expire_minutes: 過期時間（分鐘），預設5分鐘
            check_interval: 檢查間隔（秒），預設30秒
            auto_cleanup: 是否自動清理過期頻道，預設True
        """
        self.expire_minutes = expire_minutes
        self.check_interval = check_interval
        self.auto_cleanup = auto_cleanup
        
        # 頻道管理
        self._channels: Dict[str, ChannelInfo] = {}
        self._expired_channels: Dict[str, ChannelInfo] = {}
        
        # 執行緒安全
        self._lock = threading.RLock()
        
        # 定時器
        self._timer: Optional[threading.Timer] = None
        self._running = False
        
        # 統計資訊
        self._total_subscribed = 0
        self._total_expired = 0
        
        logger.info(
            f"訂閱管理器已初始化: "
            f"過期時間={expire_minutes}分鐘, "
            f"檢查間隔={check_interval}秒"
        )
    
    def start(self) -> None:
        """啟動管理器"""
        with self._lock:
            if not self._running:
                self._running = True
                self._schedule_next_check()
                logger.info("訂閱管理器已啟動")
    
    def stop(self) -> None:
        """停止管理器"""
        with self._lock:
            self._running = False
            if self._timer:
                self._timer.cancel()
                self._timer = None
            logger.info("訂閱管理器已停止")
    
    def subscribe_dynamic(
        self,
        channel: str,
        callback: Callable[[str, Any], None]
    ) -> bool:
        """
        動態訂閱頻道
        
        參數:
            channel: 頻道名稱
            callback: 訊息處理回調函數
            
        返回:
            bool: 訂閱是否成功
        """
        with self._lock:
            # 檢查是否已訂閱
            if channel in self._channels:
                logger.warning(f"頻道 '{channel}' 已訂閱，更新回調函數")
                self._channels[channel].callback = callback
                self._channels[channel].last_activity = time.time()
                return True
            
            # 檢查是否在過期列表中
            if channel in self._expired_channels:
                # 從過期列表恢復
                info = self._expired_channels.pop(channel)
                info.callback = callback
                info.last_activity = time.time()
                info.is_active = True
                self._channels[channel] = info
                logger.info(f"頻道 '{channel}' 從過期列表恢復")
            else:
                # 新建訂閱
                info = ChannelInfo(name=channel, callback=callback)
                self._channels[channel] = info
                self._total_subscribed += 1
                logger.info(f"新增訂閱頻道 '{channel}'")
            
            # 啟動管理器（如果尚未啟動）
            if not self._running:
                self.start()
            
            return True
    
    def unsubscribe_dynamic(self, channel: str) -> bool:
        """
        取消訂閱頻道
        
        參數:
            channel: 頻道名稱
            
        返回:
            bool: 取消訂閱是否成功
        """
        with self._lock:
            if channel in self._channels:
                info = self._channels.pop(channel)
                info.is_active = False
                # 加入過期列表供查詢
                self._expired_channels[channel] = info
                logger.info(f"取消訂閱頻道 '{channel}'")
                return True
            
            logger.warning(f"頻道 '{channel}' 未訂閱")
            return False
    
    def update_activity(self, channel: str) -> None:
        """
        更新頻道活動時間（收到訊息時調用）
        
        參數:
            channel: 頻道名稱
        """
        with self._lock:
            if channel in self._channels:
                self._channels[channel].last_activity = time.time()
                self._channels[channel].message_count += 1
    
    def get_active_channels(self) -> Dict[str, Dict[str, Any]]:
        """
        獲取所有活躍頻道資訊
        
        返回:
            活躍頻道字典
        """
        with self._lock:
            result = {}
            for channel, info in self._channels.items():
                result[channel] = {
                    'last_activity': datetime.fromtimestamp(info.last_activity).isoformat(),
                    'subscribe_time': datetime.fromtimestamp(info.subscribe_time).isoformat(),
                    'message_count': info.message_count,
                    'is_active': info.is_active
                }
            return result
    
    def get_expired_channels(self) -> Dict[str, Dict[str, Any]]:
        """
        獲取過期頻道列表
        
        返回:
            過期頻道字典
        """
        with self._lock:
            result = {}
            for channel, info in self._expired_channels.items():
                result[channel] = {
                    'last_activity': datetime.fromtimestamp(info.last_activity).isoformat(),
                    'subscribe_time': datetime.fromtimestamp(info.subscribe_time).isoformat(),
                    'message_count': info.message_count,
                    'expired_time': datetime.fromtimestamp(time.time()).isoformat()
                }
            return result
    
    def resubscribe(self, channel: str) -> bool:
        """
        續訂過期頻道
        
        參數:
            channel: 頻道名稱
            
        返回:
            bool: 續訂是否成功
        """
        with self._lock:
            if channel in self._expired_channels:
                info = self._expired_channels.pop(channel)
                info.last_activity = time.time()
                info.is_active = True
                self._channels[channel] = info
                logger.info(f"續訂頻道 '{channel}'")
                return True
            
            logger.warning(f"頻道 '{channel}' 不在過期列表中")
            return False
    
    def clear_expired(self) -> int:
        """
        清理過期頻道記錄
        
        返回:
            清理的頻道數量
        """
        with self._lock:
            count = len(self._expired_channels)
            self._expired_channels.clear()
            logger.info(f"清理了 {count} 個過期頻道記錄")
            return count
    
    def get_channel_callback(self, channel: str) -> Optional[Callable]:
        """
        獲取頻道的回調函數
        
        參數:
            channel: 頻道名稱
            
        返回:
            回調函數或None
        """
        with self._lock:
            if channel in self._channels:
                return self._channels[channel].callback
            return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        獲取統計資訊
        
        返回:
            統計資訊字典
        """
        with self._lock:
            active_channels = list(self._channels.keys())
            expired_channels = list(self._expired_channels.keys())
            
            total_messages = sum(
                info.message_count for info in self._channels.values()
            )
            
            return {
                'active_channels': active_channels,
                'active_count': len(active_channels),
                'expired_channels': expired_channels,
                'expired_count': len(expired_channels),
                'total_subscribed': self._total_subscribed,
                'total_expired': self._total_expired,
                'total_messages': total_messages,
                'expire_minutes': self.expire_minutes,
                'check_interval': self.check_interval,
                'is_running': self._running
            }
    
    def _check_expired_channels(self) -> None:
        """檢查並處理過期頻道"""
        current_time = time.time()
        expire_seconds = self.expire_minutes * 60
        
        with self._lock:
            expired_list = []
            
            # 檢查過期頻道
            for channel, info in self._channels.items():
                if current_time - info.last_activity > expire_seconds:
                    expired_list.append(channel)
            
            # 處理過期頻道
            for channel in expired_list:
                info = self._channels.pop(channel)
                info.is_active = False
                self._expired_channels[channel] = info
                self._total_expired += 1
                logger.info(
                    f"頻道 '{channel}' 已過期 "
                    f"(最後活動: {datetime.fromtimestamp(info.last_activity).isoformat()})"
                )
            
            # 自動清理過期記錄（保留最近100個）
            if self.auto_cleanup and len(self._expired_channels) > 100:
                # 按過期時間排序，保留最近的100個
                sorted_expired = sorted(
                    self._expired_channels.items(),
                    key=lambda x: x[1].last_activity,
                    reverse=True
                )
                self._expired_channels = dict(sorted_expired[:100])
                logger.debug(f"自動清理過期記錄，保留最近 100 個")
            
            # 如果沒有活躍頻道了，停止檢查
            if not self._channels and self._running:
                logger.info("沒有活躍頻道，暫停定期檢查")
                self._running = False
                return
            
            # 排程下次檢查
            if self._running:
                self._schedule_next_check()
    
    def _schedule_next_check(self) -> None:
        """排程下次檢查"""
        if self._timer:
            self._timer.cancel()
        
        self._timer = threading.Timer(
            self.check_interval,
            self._check_expired_channels
        )
        self._timer.daemon = True
        self._timer.start()
    
    def __enter__(self):
        """上下文管理器進入"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.stop()
    
    def __repr__(self) -> str:
        """字串表示"""
        with self._lock:
            return (
                f"SubscriptionManager("
                f"active={len(self._channels)}, "
                f"expired={len(self._expired_channels)}, "
                f"running={self._running})"
            )