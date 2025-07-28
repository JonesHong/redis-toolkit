#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試轉換器錯誤處理
"""

import pytest
import sys
from unittest.mock import patch, MagicMock
from redis_toolkit.converters import (
    get_converter,
    list_converters,
    ConversionError
)
from redis_toolkit.converters.errors import (
    ConverterDependencyError,
    ConverterNotAvailableError,
    check_converter_dependency,
    check_all_dependencies,
    format_dependency_report
)


class TestConverterErrors:
    """測試轉換器錯誤處理"""
    
    def test_unknown_converter(self):
        """測試請求未知的轉換器"""
        with pytest.raises(ValueError) as exc_info:
            get_converter('unknown_converter')
        
        error_msg = str(exc_info.value)
        assert '未知的轉換器' in error_msg
        assert 'unknown_converter' in error_msg
        assert '可用的轉換器' in error_msg
    
    def test_converter_dependency_error(self):
        """測試依賴錯誤的格式"""
        error = ConverterDependencyError(
            converter_name='test',
            missing_packages=['package1', 'package2'],
            install_command='pip install test-package'
        )
        
        error_msg = str(error)
        assert 'test 轉換器缺少必要的依賴套件' in error_msg
        assert 'package1, package2' in error_msg
        assert 'pip install test-package' in error_msg
    
    def test_converter_not_available_error(self):
        """測試轉換器不可用錯誤"""
        error = ConverterNotAvailableError(
            converter_name='test',
            reason='缺少依賴',
            available_converters=['converter1', 'converter2']
        )
        
        error_msg = str(error)
        assert "轉換器 'test' 不可用" in error_msg
        assert '缺少依賴' in error_msg
        assert 'converter1, converter2' in error_msg
    
    def test_check_converter_dependency(self):
        """測試檢查轉換器依賴"""
        # 測試未知轉換器
        result = check_converter_dependency('unknown')
        assert not result['available']
        assert '未知的轉換器' in result['reason']
        
        # 測試已知轉換器（image）
        result = check_converter_dependency('image')
        # 結果取決於是否安裝了 opencv-python
        assert 'available' in result
        assert 'reason' in result
        assert 'missing_packages' in result
    
    def test_check_all_dependencies(self):
        """測試檢查所有依賴"""
        results = check_all_dependencies()
        
        # 應該包含所有已知的轉換器
        assert 'image' in results
        assert 'audio' in results
        assert 'video' in results
        
        # 每個結果應該有必要的欄位
        for name, status in results.items():
            assert 'available' in status
            assert 'reason' in status
            assert 'missing_packages' in status
    
    def test_format_dependency_report(self):
        """測試格式化依賴報告"""
        report = format_dependency_report()
        
        # 報告應該包含標題和分隔線
        assert 'Redis Toolkit 轉換器依賴檢查報告' in report
        assert '=' * 60 in report
        
        # 應該有總計信息
        assert '總計:' in report
        assert '個轉換器可用' in report
    
    @patch('redis_toolkit.converters._CONVERTERS', {})
    @patch('redis_toolkit.converters._UNAVAILABLE_CONVERTERS', {
        'test': ('缺少測試依賴', 'pip install test')
    })
    def test_get_unavailable_converter(self):
        """測試獲取不可用的轉換器"""
        with pytest.raises(ConverterNotAvailableError) as exc_info:
            get_converter('test')
        
        error = exc_info.value
        assert error.converter_name == 'test'
        assert error.reason == '缺少測試依賴'
    
    def test_converter_encode_decode_errors(self):
        """測試轉換器編解碼錯誤"""
        # 如果有可用的轉換器，測試錯誤處理
        converters = list_converters()
        
        if 'image' in converters:
            converter = get_converter('image')
            
            # 測試編碼錯誤（無效輸入）
            with pytest.raises(ConversionError) as exc_info:
                converter.encode("not an array")
            assert '必須是 numpy 陣列' in str(exc_info.value)
            
            # 測試解碼錯誤（無效輸入）
            with pytest.raises(ConversionError) as exc_info:
                converter.decode("not bytes")
            assert '必須是位元組資料' in str(exc_info.value)
    
    def test_missing_dependency_on_usage(self):
        """測試使用時缺少依賴"""
        # 移除已註冊的轉換器
        from redis_toolkit.converters import _CONVERTERS, _UNAVAILABLE_CONVERTERS
        
        if 'image' in _CONVERTERS:
            # 模擬依賴檢查失敗
            with patch.object(_CONVERTERS['image'], '_check_dependencies') as mock_check:
                mock_check.side_effect = ConverterDependencyError(
                    converter_name='image',
                    missing_packages=['opencv-python'],
                    install_command='pip install redis-toolkit[cv2]'
                )
                
                with pytest.raises(ImportError):  # 會被轉換為 ConverterNotAvailableError
                    get_converter('image')
    
    def test_conversion_error_with_original(self):
        """測試帶有原始錯誤的轉換錯誤"""
        original_error = ValueError("Original error")
        error = ConversionError("Conversion failed", original_error)
        
        assert str(error) == "Conversion failed"
        assert error.original_error is original_error