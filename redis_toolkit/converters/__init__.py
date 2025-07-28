# redis_toolkit/converters/__init__.py
"""
Redis Toolkit 轉換器模組
提供各種數據類型的編解碼器
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, Type, Tuple
import warnings
from pretty_loguru import create_logger

logger = create_logger(
    name="redis_toolkit.converters",
    level="INFO"
)

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
# 不可用的轉換器及原因
_UNAVAILABLE_CONVERTERS: Dict[str, Tuple[str, str]] = {}

def register_converter(name: str, converter_class: Type[BaseConverter]) -> None:
    """註冊轉換器"""
    _CONVERTERS[name] = converter_class

def get_converter(name: str, **kwargs) -> BaseConverter:
    """
    取得轉換器實例
    
    參數:
        name: 轉換器名稱
        **kwargs: 轉換器配置參數
        
    回傳:
        BaseConverter: 轉換器實例
        
    拋出:
        ValueError: 當轉換器不存在時
        ConverterNotAvailableError: 當轉換器因依賴問題無法使用時
    """
    # 檢查轉換器是否存在
    if name not in _CONVERTERS and name not in _UNAVAILABLE_CONVERTERS:
        available = list_converters()
        raise ValueError(
            f"\n"
            f"{'='*60}\n"
            f"❌ 未知的轉換器: '{name}'\n"
            f"\n"
            f"可用的轉換器: {', '.join(available) if available else '無'}\n"
            f"支援的轉換器: image, audio, video\n"
            f"{'='*60}"
        )
    
    # 檢查轉換器是否可用
    if name in _UNAVAILABLE_CONVERTERS:
        from .errors import ConverterNotAvailableError
        reason, install_cmd = _UNAVAILABLE_CONVERTERS[name]
        raise ConverterNotAvailableError(
            converter_name=name,
            reason=reason,
            available_converters=list_converters()
        )
    
    # 創建轉換器實例
    try:
        converter = _CONVERTERS[name](**kwargs)
        # 立即檢查依賴（而不是等到使用時）
        converter._ensure_dependencies()
        return converter
    except ImportError as e:
        # 如果依賴檢查失敗，移除轉換器並記錄原因
        from .errors import check_converter_dependency
        dep_info = check_converter_dependency(name)
        if not dep_info['available']:
            _CONVERTERS.pop(name, None)
            _UNAVAILABLE_CONVERTERS[name] = (
                dep_info['reason'],
                dep_info.get('install_command', '')
            )
            from .errors import ConverterNotAvailableError
            raise ConverterNotAvailableError(
                converter_name=name,
                reason=dep_info['reason'],
                available_converters=list_converters()
            ) from e
        else:
            raise  # 重新拋出其他 ImportError

def list_converters() -> list:
    """列出所有可用的轉換器"""
    return list(_CONVERTERS.keys())

# 嘗試匯入可用的轉換器
def _import_available_converters():
    """動態匯入可用的轉換器並檢查依賴"""
    from .errors import check_converter_dependency
    
    # 檢查每個轉換器的依賴
    converters_to_try = [
        ('image', '.image', 'ImageConverter'),
        ('audio', '.audio', 'AudioConverter'),
        ('video', '.video', 'VideoConverter')
    ]
    
    for name, module_path, class_name in converters_to_try:
        # 先檢查依賴
        dep_info = check_converter_dependency(name)
        
        if dep_info['available']:
            # 依賴可用，嘗試匯入
            try:
                if module_path.startswith('.'):
                    # 相對導入
                    module = __import__(f'redis_toolkit.converters.{module_path[1:]}', fromlist=[class_name])
                else:
                    module = __import__(module_path, fromlist=[class_name])
                converter_class = getattr(module, class_name)
                register_converter(name, converter_class)
                logger.info(f"成功載入 {name} 轉換器")
            except Exception as e:
                logger.warning(f"載入 {name} 轉換器失敗: {e}")
                _UNAVAILABLE_CONVERTERS[name] = (
                    f"載入失敗: {str(e)}",
                    dep_info.get('install_command', '')
                )
        else:
            # 依賴不可用，記錄原因
            _UNAVAILABLE_CONVERTERS[name] = (
                dep_info['reason'],
                dep_info.get('install_command', '')
            )
            logger.debug(f"{name} 轉換器不可用: {dep_info['reason']}")

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

# 從 errors 模組匯出依賴檢查功能
try:
    from .errors import (
        ConverterDependencyError,
        ConverterNotAvailableError,
        check_converter_dependency,
        check_all_dependencies,
        format_dependency_report
    )
    __all__.extend([
        'ConverterDependencyError',
        'ConverterNotAvailableError',
        'check_converter_dependency',
        'check_all_dependencies',
        'format_dependency_report'
    ])
except ImportError:
    # 如果 errors 模組不可用，忽略
    pass

# 總是包含 check_dependencies
__all__.append('check_dependencies')

def check_dependencies() -> None:
    """
    檢查並顯示所有轉換器的依賴狀態
    
    這是一個便利函數，用於診斷依賴問題
    """
    try:
        from .errors import format_dependency_report
        print(format_dependency_report())
    except ImportError:
        print("無法載入依賴檢查模組")

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