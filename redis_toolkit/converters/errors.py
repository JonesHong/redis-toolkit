# -*- coding: utf-8 -*-
"""
轉換器錯誤處理模組
提供詳細的錯誤信息和解決方案
"""

from typing import Optional, List, Dict


class ConverterDependencyError(ImportError):
    """
    轉換器依賴錯誤
    當必要的依賴套件未安裝時拋出
    """
    
    def __init__(
        self, 
        converter_name: str,
        missing_packages: List[str],
        install_command: str,
        original_error: Optional[Exception] = None
    ):
        """
        初始化依賴錯誤
        
        參數:
            converter_name: 轉換器名稱
            missing_packages: 缺少的套件列表
            install_command: 安裝命令
            original_error: 原始錯誤
        """
        self.converter_name = converter_name
        self.missing_packages = missing_packages
        self.install_command = install_command
        self.original_error = original_error
        
        # 構建錯誤消息
        packages_str = ", ".join(missing_packages)
        message = (
            f"\n"
            f"{'='*60}\n"
            f"❌ {converter_name} 轉換器缺少必要的依賴套件\n"
            f"\n"
            f"缺少的套件: {packages_str}\n"
            f"\n"
            f"請執行以下命令安裝:\n"
            f"  {install_command}\n"
            f"{'='*60}"
        )
        
        super().__init__(message)


class ConverterNotAvailableError(RuntimeError):
    """
    轉換器不可用錯誤
    當請求的轉換器因為依賴問題無法使用時拋出
    """
    
    def __init__(
        self,
        converter_name: str,
        reason: str,
        available_converters: List[str]
    ):
        """
        初始化轉換器不可用錯誤
        
        參數:
            converter_name: 請求的轉換器名稱
            reason: 不可用的原因
            available_converters: 可用的轉換器列表
        """
        self.converter_name = converter_name
        self.reason = reason
        self.available_converters = available_converters
        
        # 構建錯誤消息
        if available_converters:
            available_str = ", ".join(available_converters)
            available_msg = f"\n可用的轉換器: {available_str}"
        else:
            available_msg = "\n目前沒有可用的轉換器"
        
        message = (
            f"\n"
            f"{'='*60}\n"
            f"❌ 轉換器 '{converter_name}' 不可用\n"
            f"\n"
            f"原因: {reason}\n"
            f"{available_msg}\n"
            f"\n"
            f"提示: 使用 redis_toolkit.converters.check_dependencies() \n"
            f"      來檢查所有轉換器的依賴狀態\n"
            f"{'='*60}"
        )
        
        super().__init__(message)


# 依賴資訊映射
CONVERTER_DEPENDENCIES: Dict[str, Dict[str, any]] = {
    'image': {
        'packages': ['opencv-python', 'numpy'],
        'imports': ['cv2', 'numpy'],
        'install_cmd': 'pip install redis-toolkit[cv2]',
        'description': '圖片處理（支援 JPEG, PNG, WebP 等格式）'
    },
    'audio': {
        'packages': ['numpy', 'scipy', 'soundfile'],
        'imports': ['numpy', 'scipy.io.wavfile', 'soundfile'],
        'install_cmd': 'pip install redis-toolkit[audio]',
        'description': '音頻處理（支援 WAV, FLAC, MP3 等格式）'
    },
    'video': {
        'packages': ['opencv-python', 'numpy'],
        'imports': ['cv2', 'numpy'],
        'install_cmd': 'pip install redis-toolkit[video]',
        'description': '視頻處理（支援多種視頻格式）'
    }
}


def check_converter_dependency(converter_name: str) -> Dict[str, any]:
    """
    檢查特定轉換器的依賴狀態
    
    參數:
        converter_name: 轉換器名稱
        
    回傳:
        Dict: 包含狀態信息的字典
    """
    if converter_name not in CONVERTER_DEPENDENCIES:
        return {
            'available': False,
            'reason': f'未知的轉換器: {converter_name}',
            'missing_packages': [],
            'install_command': None
        }
    
    deps = CONVERTER_DEPENDENCIES[converter_name]
    missing_packages = []
    
    for import_name in deps['imports']:
        try:
            if '.' in import_name:
                # 處理子模組匯入
                parts = import_name.split('.')
                module = __import__(parts[0])
                for part in parts[1:]:
                    module = getattr(module, part)
            else:
                __import__(import_name)
        except ImportError:
            # 找出對應的套件名稱
            for pkg, imp in zip(deps['packages'], deps['imports']):
                if imp == import_name or imp.startswith(import_name + '.'):
                    missing_packages.append(pkg)
                    break
    
    if missing_packages:
        return {
            'available': False,
            'reason': f'缺少依賴套件: {", ".join(missing_packages)}',
            'missing_packages': missing_packages,
            'install_command': deps['install_cmd'],
            'description': deps['description']
        }
    
    return {
        'available': True,
        'reason': '所有依賴都已安裝',
        'missing_packages': [],
        'install_command': None,
        'description': deps['description']
    }


def check_all_dependencies() -> Dict[str, Dict[str, any]]:
    """
    檢查所有轉換器的依賴狀態
    
    回傳:
        Dict: 每個轉換器的狀態信息
    """
    results = {}
    for converter_name in CONVERTER_DEPENDENCIES:
        results[converter_name] = check_converter_dependency(converter_name)
    return results


def format_dependency_report() -> str:
    """
    生成依賴檢查報告
    
    回傳:
        str: 格式化的報告字符串
    """
    results = check_all_dependencies()
    
    report_lines = [
        "Redis Toolkit 轉換器依賴檢查報告",
        "=" * 60,
        ""
    ]
    
    # 分組顯示
    available = []
    unavailable = []
    
    for name, status in results.items():
        if status['available']:
            available.append((name, status))
        else:
            unavailable.append((name, status))
    
    # 顯示可用的轉換器
    if available:
        report_lines.append("✅ 可用的轉換器:")
        for name, status in available:
            report_lines.append(f"  - {name}: {status['description']}")
        report_lines.append("")
    
    # 顯示不可用的轉換器
    if unavailable:
        report_lines.append("❌ 不可用的轉換器:")
        for name, status in unavailable:
            report_lines.append(f"  - {name}: {status['description']}")
            report_lines.append(f"    原因: {status['reason']}")
            if status['install_command']:
                report_lines.append(f"    安裝: {status['install_command']}")
        report_lines.append("")
    
    # 總結
    total = len(results)
    available_count = len(available)
    report_lines.extend([
        f"總計: {available_count}/{total} 個轉換器可用",
        "=" * 60
    ])
    
    return "\n".join(report_lines)