# redis_toolkit/converters/__init__.py
"""
Redis Toolkit 轉換器模組
提供各種數據類型的編解碼器
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, Type
import warnings

class BaseConverter(ABC):
    """
    轉換器基礎類別
    定義編解碼的標準介面
    """
    
    def __init__(self, **kwargs):
        """
        初始化轉換器
        
        參數:
            **kwargs: 轉換器特定的配置參數
        """
        self.config = kwargs
        self._dependencies_checked = False
        
    @abstractmethod
    def _check_dependencies(self) -> None:
        """
        檢查並載入必要的依賴
        
        拋出:
            ImportError: 當必要依賴未安裝時
        """
        pass
    
    @abstractmethod
    def encode(self, data: Any) -> bytes:
        """
        將原始數據編碼為位元組
        
        參數:
            data: 要編碼的原始數據
            
        回傳:
            bytes: 編碼後的位元組數據
            
        拋出:
            ValueError: 當數據格式不正確時
            RuntimeError: 當編碼過程失敗時
        """
        pass
    
    @abstractmethod
    def decode(self, data: bytes) -> Any:
        """
        將位元組解碼為原始數據
        
        參數:
            data: 要解碼的位元組數據
            
        回傳:
            Any: 解碼後的原始數據
            
        拋出:
            ValueError: 當數據格式不正確時
            RuntimeError: 當解碼過程失敗時
        """
        pass
    
    def _ensure_dependencies(self) -> None:
        """確保依賴已檢查和載入"""
        if not self._dependencies_checked:
            self._check_dependencies()
            self._dependencies_checked = True
    
    @property
    @abstractmethod
    def supported_formats(self) -> list:
        """回傳支援的格式列表"""
        pass
    
    @property
    @abstractmethod
    def default_format(self) -> str:
        """回傳預設格式"""
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.config})"


class ConversionError(Exception):
    """轉換器相關錯誤"""
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.original_error = original_error


# 轉換器註冊表
_CONVERTERS: Dict[str, Type[BaseConverter]] = {}

def register_converter(name: str, converter_class: Type[BaseConverter]) -> None:
    """註冊轉換器"""
    _CONVERTERS[name] = converter_class

def get_converter(name: str, **kwargs) -> BaseConverter:
    """取得轉換器實例"""
    if name not in _CONVERTERS:
        raise ValueError(f"未知的轉換器: {name}")
    return _CONVERTERS[name](**kwargs)

def list_converters() -> list:
    """列出所有可用的轉換器"""
    return list(_CONVERTERS.keys())

# 嘗試匯入可用的轉換器
def _import_available_converters():
    """動態匯入可用的轉換器"""
    try:
        from .image import ImageConverter
        register_converter('image', ImageConverter)
    except ImportError:
        warnings.warn("圖片轉換器不可用：缺少相關依賴", ImportWarning)
    
    try:
        from .audio import AudioConverter
        register_converter('audio', AudioConverter)
    except ImportError:
        warnings.warn("音頻轉換器不可用：缺少相關依賴", ImportWarning)
    
    try:
        from .video import VideoConverter
        register_converter('video', VideoConverter)
    except ImportError:
        warnings.warn("視頻轉換器不可用：缺少相關依賴", ImportWarning)

# 初始化時載入轉換器
_import_available_converters()

# 公開的 API
__all__ = [
    'BaseConverter',
    'ConversionError',
    'register_converter',
    'get_converter',
    'list_converters',
]

# 便利函數（如果對應轉換器可用）
if 'image' in _CONVERTERS:
    def encode_image(image_array, format: str = 'jpg', **kwargs) -> bytes:
        """快速圖片編碼"""
        converter = get_converter('image', format=format, **kwargs)
        return converter.encode(image_array)
    
    def decode_image(image_bytes: bytes, **kwargs):
        """快速圖片解碼"""
        converter = get_converter('image', **kwargs)
        return converter.decode(image_bytes)
    
    __all__.extend(['encode_image', 'decode_image'])

if 'audio' in _CONVERTERS:
    def encode_audio(audio_array, sample_rate: int = 44100, **kwargs) -> bytes:
        """快速音頻編碼"""
        converter = get_converter('audio', sample_rate=sample_rate, **kwargs)
        return converter.encode(audio_array)
    
    def decode_audio(audio_bytes: bytes, **kwargs):
        """快速音頻解碼"""
        converter = get_converter('audio', **kwargs)
        return converter.decode(audio_bytes)
    
    __all__.extend(['encode_audio', 'decode_audio'])

if 'video' in _CONVERTERS:
    def encode_video(video_path: str, **kwargs) -> bytes:
        """快速視頻編碼（讀取檔案）"""
        converter = get_converter('video', **kwargs)
        return converter.encode(video_path)
    
    def decode_video(video_bytes: bytes, **kwargs) -> bytes:
        """快速視頻解碼"""
        converter = get_converter('video', **kwargs)
        return converter.decode(video_bytes)
    
    __all__.extend(['encode_video', 'decode_video'])