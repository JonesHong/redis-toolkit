# redis_toolkit/converters/image.py
"""
圖片轉換器模組
支援多種圖片格式的編解碼
"""

from typing import Any, Optional
import numpy as np
from . import BaseConverter, ConversionError


class ImageConverter(BaseConverter):
    """
    圖片數據轉換器
    支援 JPEG、PNG、WebP 等格式
    """
    
    def __init__(self, format: str = 'jpg', quality: int = 95, **kwargs):
        """
        初始化圖片轉換器
        
        參數:
            format: 圖片格式 ('jpg', 'png', 'webp')
            quality: JPEG 品質 (1-100)
            **kwargs: 其他配置參數
        """
        super().__init__(format=format, quality=quality, **kwargs)
        self.format = format.lower()
        self.quality = max(1, min(100, quality))
        self._cv2 = None
        self._np = None
    
    def _check_dependencies(self) -> None:
        """檢查 OpenCV 和 numpy 依賴"""
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
                converter_name='image',
                missing_packages=missing_packages,
                install_command='pip install redis-toolkit[cv2]'
            )
    
    @property
    def supported_formats(self) -> list:
        """支援的圖片格式"""
        return ['jpg', 'jpeg', 'png', 'webp', 'bmp', 'tiff']
    
    @property
    def default_format(self) -> str:
        """預設格式"""
        return 'jpg'
    
    def encode(self, image_array: np.ndarray) -> bytes:
        """
        將 numpy 圖片陣列編碼為位元組
        
        參數:
            image_array: numpy 圖片陣列 (H, W, C) 或 (H, W)
            
        回傳:
            bytes: 編碼後的圖片位元組
            
        拋出:
            ConversionError: 當編碼失敗時
        """
        self._ensure_dependencies()
        
        try:
            # 驗證輸入
            if not isinstance(image_array, self._np.ndarray):
                raise ValueError("輸入必須是 numpy 陣列")
            
            if image_array.ndim not in [2, 3]:
                raise ValueError("圖片陣列必須是 2D (灰階) 或 3D (彩色)")
            
            # 根據格式選擇編碼參數
            if self.format in ['jpg', 'jpeg']:
                encode_params = [self._cv2.IMWRITE_JPEG_QUALITY, self.quality]
                success, buffer = self._cv2.imencode('.jpg', image_array, encode_params)
            elif self.format == 'png':
                # PNG 支援壓縮等級
                compression = self.config.get('png_compression', 1)  # 0-9
                encode_params = [self._cv2.IMWRITE_PNG_COMPRESSION, compression]
                success, buffer = self._cv2.imencode('.png', image_array, encode_params)
            elif self.format == 'webp':
                # WebP 品質設定
                encode_params = [self._cv2.IMWRITE_WEBP_QUALITY, self.quality]
                success, buffer = self._cv2.imencode('.webp', image_array, encode_params)
            elif self.format == 'bmp':
                success, buffer = self._cv2.imencode('.bmp', image_array)
            elif self.format == 'tiff':
                success, buffer = self._cv2.imencode('.tiff', image_array)
            else:
                raise ValueError(f"不支援的格式: {self.format}")
            
            if not success:
                raise RuntimeError(f"圖片編碼失敗: {self.format}")
            
            return buffer.tobytes()
            
        except Exception as e:
            if isinstance(e, (ValueError, RuntimeError)):
                raise ConversionError(str(e), e)
            else:
                raise ConversionError(f"圖片編碼過程中發生未預期錯誤: {e}", e)
    
    def decode(self, image_bytes: bytes) -> np.ndarray:
        """
        將位元組解碼為 numpy 圖片陣列
        
        參數:
            image_bytes: 圖片位元組資料
            
        回傳:
            np.ndarray: 解碼後的圖片陣列
            
        拋出:
            ConversionError: 當解碼失敗時
        """
        self._ensure_dependencies()
        
        try:
            # 驗證輸入
            if not isinstance(image_bytes, bytes):
                raise ValueError("輸入必須是位元組資料")
            
            if len(image_bytes) == 0:
                raise ValueError("位元組資料不能為空")
            
            # 將位元組轉換為 numpy 陣列
            arr = self._np.frombuffer(image_bytes, self._np.uint8)
            
            # 解碼圖片
            color_mode = self.config.get('color_mode', self._cv2.IMREAD_COLOR)
            image_array = self._cv2.imdecode(arr, color_mode)
            
            if image_array is None:
                raise RuntimeError("無法解碼圖片，可能是格式不支援或資料損壞")
            
            return image_array
            
        except Exception as e:
            if isinstance(e, (ValueError, RuntimeError)):
                raise ConversionError(str(e), e)
            else:
                raise ConversionError(f"圖片解碼過程中發生未預期錯誤: {e}", e)
    
    def resize(self, image_array: np.ndarray, width: int, height: int, 
               interpolation: str = 'linear') -> np.ndarray:
        """
        調整圖片大小（額外功能）
        
        參數:
            image_array: 圖片陣列
            width: 目標寬度
            height: 目標高度
            interpolation: 插值方法 ('linear', 'cubic', 'nearest')
            
        回傳:
            np.ndarray: 調整大小後的圖片
        """
        self._ensure_dependencies()
        
        interp_map = {
            'linear': self._cv2.INTER_LINEAR,
            'cubic': self._cv2.INTER_CUBIC,
            'nearest': self._cv2.INTER_NEAREST,
            'area': self._cv2.INTER_AREA,
            'lanczos': self._cv2.INTER_LANCZOS4
        }
        
        interp_method = interp_map.get(interpolation, self._cv2.INTER_LINEAR)
        return self._cv2.resize(image_array, (width, height), interpolation=interp_method)
    
    def get_info(self, image_bytes: bytes) -> dict:
        """
        取得圖片資訊（不完全解碼）
        
        參數:
            image_bytes: 圖片位元組資料
            
        回傳:
            dict: 圖片資訊（寬度、高度、通道數等）
        """
        # 先解碼以取得完整資訊（未來可優化為只讀取 header）
        image_array = self.decode(image_bytes)
        
        info = {
            'shape': image_array.shape,
            'dtype': str(image_array.dtype),
            'size_bytes': len(image_bytes),
        }
        
        if image_array.ndim == 3:
            info['height'], info['width'], info['channels'] = image_array.shape
        else:
            info['height'], info['width'] = image_array.shape
            info['channels'] = 1
            
        return info


# 便利函數
def create_image_converter(format: str = 'jpg', quality: int = 95, **kwargs) -> ImageConverter:
    """工廠函數，創建圖片轉換器"""
    return ImageConverter(format=format, quality=quality, **kwargs)

# 預設實例（延遲初始化）
_default_converter = None

def get_default_image_converter() -> ImageConverter:
    """取得預設圖片轉換器"""
    global _default_converter
    if _default_converter is None:
        _default_converter = ImageConverter()
    return _default_converter