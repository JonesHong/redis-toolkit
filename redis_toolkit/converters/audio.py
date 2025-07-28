# redis_toolkit/converters/audio.py
"""
音頻轉換器模組
支援多種音頻格式的編解碼
"""

from typing import Any, Tuple, Optional, Union
import numpy as np
from io import BytesIO
from . import BaseConverter, ConversionError


class AudioConverter(BaseConverter):
    """
    音頻數據轉換器
    支援 WAV、FLAC、MP3 等格式
    """
    
    def __init__(self, sample_rate: int = 44100, format: str = 'wav', 
                 channels: int = 1, bit_depth: int = 16, **kwargs):
        """
        初始化音頻轉換器
        
        參數:
            sample_rate: 採樣率 (Hz)
            format: 音頻格式 ('wav', 'flac', 'mp3')
            channels: 聲道數 (1=單聲道, 2=立體聲)
            bit_depth: 位元深度 (16, 24, 32)
            **kwargs: 其他配置參數
        """
        super().__init__(
            sample_rate=sample_rate, 
            format=format, 
            channels=channels,
            bit_depth=bit_depth,
            **kwargs
        )
        self.sample_rate = sample_rate
        self.format = format.lower()
        self.channels = channels
        self.bit_depth = bit_depth
        self._scipy_wavfile = None
        self._soundfile = None
        self._np = None
    
    def _check_dependencies(self) -> None:
        """檢查音頻處理依賴"""
        missing_packages = []
        
        # 檢查基本依賴
        try:
            import numpy as np
            self._np = np
        except ImportError:
            missing_packages.append('numpy')
        
        # 檢查格式特定依賴
        if self.format == 'wav':
            try:
                from scipy.io import wavfile
                self._scipy_wavfile = wavfile
            except ImportError:
                missing_packages.append('scipy')
        
        if self.format in ['flac', 'ogg', 'mp3', 'wav']:  # 所有格式都可以使用 soundfile
            try:
                import soundfile as sf
                self._soundfile = sf
            except ImportError:
                # 如果是 WAV 且已經有 scipy，就不需要 soundfile
                if self.format != 'wav' or 'scipy' in missing_packages:
                    missing_packages.append('soundfile')
        
        if missing_packages:
            from ..errors import ConverterDependencyError
            raise ConverterDependencyError(
                converter_name='audio',
                missing_packages=missing_packages,
                install_command='pip install redis-toolkit[audio]'
            )
    
    @property
    def supported_formats(self) -> list:
        """支援的音頻格式"""
        return ['wav', 'flac', 'ogg', 'mp3']
    
    @property
    def default_format(self) -> str:
        """預設格式"""
        return 'wav'
    
    def encode(self, audio_data: Union[np.ndarray, Tuple[int, np.ndarray]]) -> bytes:
        """
        將音頻陣列編碼為位元組
        
        參數:
            audio_data: 音頻資料，可以是：
                       - numpy 陣列（使用預設採樣率）
                       - (sample_rate, audio_array) 元組
            
        回傳:
            bytes: 編碼後的音頻位元組
            
        拋出:
            ConversionError: 當編碼失敗時
        """
        self._ensure_dependencies()
        
        try:
            # 解析輸入資料
            if isinstance(audio_data, tuple) and len(audio_data) == 2:
                sample_rate, audio_array = audio_data
            elif isinstance(audio_data, self._np.ndarray):
                sample_rate = self.sample_rate
                audio_array = audio_data
            else:
                raise ValueError("音頻資料必須是 numpy 陣列或 (sample_rate, array) 元組")
            
            # 驗證音頻陣列
            if not isinstance(audio_array, self._np.ndarray):
                raise ValueError("音頻陣列必須是 numpy 陣列")
            
            # 確保資料類型正確
            if audio_array.dtype != self._np.float32 and audio_array.dtype != self._np.int16:
                # 轉換為適當的資料類型
                if audio_array.dtype.kind == 'f':  # 浮點型
                    audio_array = audio_array.astype(self._np.float32)
                else:  # 整數型
                    audio_array = audio_array.astype(self._np.int16)
            
            # 根據格式進行編碼
            buffer = BytesIO()
            
            if self.format == 'wav':
                self._scipy_wavfile.write(buffer, sample_rate, audio_array)
            elif self.format in ['flac', 'ogg', 'mp3']:
                if self._soundfile is None:
                    raise RuntimeError("soundfile 未初始化")
                self._soundfile.write(buffer, audio_array, sample_rate, format=self.format.upper())
            else:
                raise ValueError(f"不支援的格式: {self.format}")
            
            return buffer.getvalue()
            
        except Exception as e:
            if isinstance(e, (ValueError, RuntimeError)):
                raise ConversionError(str(e), e)
            else:
                raise ConversionError(f"音頻編碼過程中發生未預期錯誤: {e}", e)
    
    def decode(self, audio_bytes: bytes) -> Tuple[int, np.ndarray]:
        """
        將位元組解碼為音頻陣列
        
        參數:
            audio_bytes: 音頻位元組資料
            
        回傳:
            Tuple[int, np.ndarray]: (sample_rate, audio_array)
            
        拋出:
            ConversionError: 當解碼失敗時
        """
        self._ensure_dependencies()
        
        try:
            # 驗證輸入
            if not isinstance(audio_bytes, bytes):
                raise ValueError("輸入必須是位元組資料")
            
            if len(audio_bytes) == 0:
                raise ValueError("位元組資料不能為空")
            
            buffer = BytesIO(audio_bytes)
            
            # 根據格式進行解碼
            if self.format == 'wav':
                sample_rate, audio_array = self._scipy_wavfile.read(buffer)
            elif self.format in ['flac', 'ogg', 'mp3']:
                if self._soundfile is None:
                    raise RuntimeError("soundfile 未初始化")
                audio_array, sample_rate = self._soundfile.read(buffer)
            else:
                # 嘗試自動偵測格式
                try:
                    if self._soundfile:
                        audio_array, sample_rate = self._soundfile.read(buffer)
                    else:
                        sample_rate, audio_array = self._scipy_wavfile.read(buffer)
                except Exception:
                    raise ValueError(f"無法解碼音頻，格式可能不支援: {self.format}")
            
            if audio_array is None or len(audio_array) == 0:
                raise RuntimeError("音頻解碼失敗，可能是格式不支援或資料損壞")
            
            return sample_rate, audio_array
            
        except Exception as e:
            if isinstance(e, (ValueError, RuntimeError)):
                raise ConversionError(str(e), e)
            else:
                raise ConversionError(f"音頻解碼過程中發生未預期錯誤: {e}", e)
    
    def encode_from_file(self, audio_file_path: str) -> bytes:
        """
        從音頻檔案編碼為位元組
        
        參數:
            audio_file_path: 音頻檔案路徑
            
        回傳:
            bytes: 編碼後的音頻位元組
            
        拋出:
            ConversionError: 當讀取失敗時
        """
        self._ensure_dependencies()
        
        try:
            # 嘗試使用 soundfile 讀取各種格式
            try:
                import soundfile as sf
                # 讀取音頻檔案
                audio_array, sample_rate = sf.read(audio_file_path)
                # 使用讀取到的數據編碼
                return self.encode((sample_rate, audio_array))
            except ImportError:
                # soundfile 不可用，嘗試直接讀取檔案位元組
                with open(audio_file_path, 'rb') as f:
                    return f.read()
            except Exception:
                # soundfile 讀取失敗，嘗試直接讀取檔案位元組
                with open(audio_file_path, 'rb') as f:
                    return f.read()
                    
        except FileNotFoundError:
            raise ConversionError(f"找不到音頻檔案: {audio_file_path}")
        except Exception as e:
            raise ConversionError(f"讀取音頻檔案失敗: {e}", e)
    
    def get_file_info(self, audio_file_path: str) -> dict:
        """
        取得音頻檔案資訊
        
        參數:
            audio_file_path: 音頻檔案路徑
            
        回傳:
            dict: 音頻檔案資訊
            
        拋出:
            ConversionError: 當取得資訊失敗時
        """
        self._ensure_dependencies()
        
        try:
            import soundfile as sf
            
            # 使用 soundfile 讀取檔案資訊
            info = sf.info(audio_file_path)
            
            # 取得檔案大小
            import os
            file_size = os.path.getsize(audio_file_path)
            
            return {
                'sample_rate': info.samplerate,
                'channels': info.channels,
                'frames': info.frames,
                'duration_seconds': info.duration,
                'format': info.format,
                'subtype': info.subtype,
                'file_size_bytes': file_size,
            }
            
        except ImportError as e:
            raise ConversionError("取得音頻檔案資訊需要 soundfile", e)
        except Exception as e:
            raise ConversionError(f"取得音頻檔案資訊失敗: {e}", e)
    
    def resample(self, audio_array: np.ndarray, original_rate: int, 
                 target_rate: int) -> np.ndarray:
        """
        重新採樣音頻（需要額外依賴）
        
        參數:
            audio_array: 原始音頻陣列
            original_rate: 原始採樣率
            target_rate: 目標採樣率
            
        回傳:
            np.ndarray: 重新採樣後的音頻陣列
            
        拋出:
            ImportError: 當 scipy 未安裝時
        """
        self._ensure_dependencies()
        
        try:
            from scipy import signal
        except ImportError:
            raise ImportError("重新採樣需要 scipy.signal")
        
        if original_rate == target_rate:
            return audio_array
        
        # 計算重採樣比例
        num_samples = int(len(audio_array) * target_rate / original_rate)
        return signal.resample(audio_array, num_samples)
    
    def normalize(self, audio_array: np.ndarray, target_level: float = 0.9) -> np.ndarray:
        """
        正規化音頻音量
        
        參數:
            audio_array: 音頻陣列
            target_level: 目標音量等級 (0.0-1.0)
            
        回傳:
            np.ndarray: 正規化後的音頻陣列
        """
        self._ensure_dependencies()
        
        if audio_array.dtype.kind == 'f':  # 浮點型
            max_val = self._np.max(self._np.abs(audio_array))
            if max_val > 0:
                return audio_array * (target_level / max_val)
        else:  # 整數型
            max_val = self._np.max(self._np.abs(audio_array))
            if max_val > 0:
                target_max = target_level * self._np.iinfo(audio_array.dtype).max
                return (audio_array * (target_max / max_val)).astype(audio_array.dtype)
        
        return audio_array
    
    def get_info(self, audio_bytes: bytes) -> dict:
        """
        取得音頻資訊
        
        參數:
            audio_bytes: 音頻位元組資料
            
        回傳:
            dict: 音頻資訊
        """
        sample_rate, audio_array = self.decode(audio_bytes)
        
        duration = len(audio_array) / sample_rate
        
        info = {
            'sample_rate': sample_rate,
            'duration_seconds': duration,
            'samples': len(audio_array),
            'channels': 1 if audio_array.ndim == 1 else audio_array.shape[1],
            'dtype': str(audio_array.dtype),
            'size_bytes': len(audio_bytes),
        }
        
        if audio_array.ndim > 1:
            info['shape'] = audio_array.shape
        
        return info


# 便利函數
def create_audio_converter(sample_rate: int = 44100, format: str = 'wav', **kwargs) -> AudioConverter:
    """工廠函數，創建音頻轉換器"""
    return AudioConverter(sample_rate=sample_rate, format=format, **kwargs)

# 預設實例（延遲初始化）
_default_converter = None

def get_default_audio_converter() -> AudioConverter:
    """取得預設音頻轉換器"""
    global _default_converter
    if _default_converter is None:
        _default_converter = AudioConverter()
    return _default_converter