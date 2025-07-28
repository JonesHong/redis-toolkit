# redis_toolkit/converters/video.py
"""
視頻轉換器模組
支援視頻檔案的讀取和基本處理
"""

from typing import Any, Tuple, Optional
import numpy as np
from . import BaseConverter, ConversionError


class VideoConverter(BaseConverter):
    """
    視頻數據轉換器
    支援讀取視頻檔案並提取幀數據
    """
    
    def __init__(self, **kwargs):
        """
        初始化視頻轉換器
        
        參數:
            **kwargs: 其他配置參數
        """
        super().__init__(**kwargs)
        self._cv2 = None
        self._np = None
    
    def _check_dependencies(self) -> None:
        """檢查 OpenCV 依賴"""
        missing_packages = []
        
        try:
            import cv2
            self._cv2 = cv2
        except ImportError:
            missing_packages.append('opencv-python')
        
        try:
            import numpy as np
            self._np = np
        except ImportError:
            missing_packages.append('numpy')
        
        if missing_packages:
            from ..errors import ConverterDependencyError
            raise ConverterDependencyError(
                converter_name='video',
                missing_packages=missing_packages,
                install_command='pip install redis-toolkit[video]'
            )
    
    @property
    def supported_formats(self) -> list:
        """支援的視頻格式"""
        return ['mp4', 'avi', 'mov', 'mkv']
    
    @property
    def default_format(self) -> str:
        """預設格式"""
        return 'mp4'
    
    def encode(self, video_path: str) -> bytes:
        """
        讀取視頻檔案並轉換為位元組
        
        參數:
            video_path: 視頻檔案路徑
            
        回傳:
            bytes: 視頻檔案的位元組內容
            
        拋出:
            ConversionError: 當讀取失敗時
        """
        try:
            # 直接讀取檔案位元組（最簡單的方式）
            with open(video_path, 'rb') as f:
                video_bytes = f.read()
            
            if len(video_bytes) == 0:
                raise ValueError(f"視頻檔案為空: {video_path}")
            
            return video_bytes
            
        except FileNotFoundError:
            raise ConversionError(f"找不到視頻檔案: {video_path}")
        except Exception as e:
            raise ConversionError(f"讀取視頻檔案失敗: {e}", e)
    
    def decode(self, video_bytes: bytes) -> bytes:
        """
        將位元組轉換回視頻數據
        
        參數:
            video_bytes: 視頻位元組資料
            
        回傳:
            bytes: 原始視頻位元組資料
        """
        # 對於檔案存儲，解碼就是返回原始位元組
        return video_bytes
    
    def extract_frames(self, video_path: str, max_frames: int = 10) -> list:
        """
        從視頻中提取幀
        
        參數:
            video_path: 視頻檔案路徑
            max_frames: 最大提取幀數
            
        回傳:
            list: 幀列表（numpy 陣列）
        """
        self._ensure_dependencies()
        
        try:
            cap = self._cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise ValueError(f"無法開啟視頻檔案: {video_path}")
            
            frames = []
            frame_count = 0
            total_frames = int(cap.get(self._cv2.CAP_PROP_FRAME_COUNT))
            
            # 計算取樣間隔
            if total_frames <= max_frames:
                step = 1
            else:
                step = total_frames // max_frames
            
            while frame_count < max_frames:
                # 跳到指定幀
                cap.set(self._cv2.CAP_PROP_POS_FRAMES, frame_count * step)
                
                ret, frame = cap.read()
                if not ret:
                    break
                
                frames.append(frame)
                frame_count += 1
            
            cap.release()
            return frames
            
        except Exception as e:
            raise ConversionError(f"提取視頻幀失敗: {e}", e)
    
    def get_info(self, video_bytes: bytes) -> dict:
        """
        取得視頻資訊
        
        參數:
            video_bytes: 視頻位元組資料
            
        回傳:
            dict: 視頻資訊
        """
        # 對於位元組資料，無法直接獲取資訊，需先保存為檔案
        import tempfile
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            temp_file.write(video_bytes)
            temp_path = temp_file.name
        
        try:
            return self.get_video_info(temp_path)
        finally:
            import os
            os.remove(temp_path)
    def get_video_info(self, video_path: str) -> dict:
        """
        取得視頻資訊
        
        參數:
            video_path: 視頻檔案路徑
            
        回傳:
            dict: 視頻資訊
        """
        self._ensure_dependencies()
        
        try:
            cap = self._cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise ValueError(f"無法開啟視頻檔案: {video_path}")
            
            # 取得視頻屬性
            fps = cap.get(self._cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(self._cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(self._cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(self._cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            cap.release()
            
            # 取得檔案大小
            import os
            file_size = os.path.getsize(video_path)
            
            return {
                'width': width,
                'height': height,
                'fps': fps,
                'frame_count': frame_count,
                'duration_seconds': duration,
                'file_size_bytes': file_size,
                'resolution': f"{width}x{height}"
            }
            
        except Exception as e:
            raise ConversionError(f"取得視頻資訊失敗: {e}", e)
    
    def save_video_bytes(self, video_bytes: bytes, output_path: str) -> None:
        """
        將視頻位元組保存為檔案
        
        參數:
            video_bytes: 視頻位元組資料
            output_path: 輸出檔案路徑
        """
        try:
            with open(output_path, 'wb') as f:
                f.write(video_bytes)
        except Exception as e:
            raise ConversionError(f"保存視頻檔案失敗: {e}", e)


# 便利函數
def create_video_converter(**kwargs) -> VideoConverter:
    """工廠函數，創建視頻轉換器"""
    return VideoConverter(**kwargs)

# 預設實例（延遲初始化）
_default_converter = None

def get_default_video_converter() -> VideoConverter:
    """取得預設視頻轉換器"""
    global _default_converter
    if _default_converter is None:
        _default_converter = VideoConverter()
    return _default_converter