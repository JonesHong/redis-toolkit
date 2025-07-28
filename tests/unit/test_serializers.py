#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis Toolkit 序列化功能測試
"""

import pytest
from redis_toolkit.utils.serializers import serialize_value, deserialize_value
from redis_toolkit.exceptions import SerializationError


class TestBasicSerialization:
    """基本序列化測試"""
    
    def test_string_serialization(self):
        """測試字串序列化"""
        test_cases = [
            "hello world",
            "你好世界",
            "🚀 emoji test",
            "",
            "special chars !@#$%^&*()",
        ]
        
        for original in test_cases:
            serialized = serialize_value(original)
            deserialized = deserialize_value(serialized)
            
            assert deserialized == original
            assert isinstance(deserialized, str)
    
    def test_boolean_serialization(self):
        """測試布林值序列化"""
        # 測試 True
        serialized_true = serialize_value(True)
        assert isinstance(serialized_true, bytes)
        assert b'"bool"' in serialized_true  # 確認有類型標記
        
        deserialized_true = deserialize_value(serialized_true)
        assert deserialized_true is True
        assert isinstance(deserialized_true, bool)
        
        # 測試 False
        serialized_false = serialize_value(False)
        assert isinstance(serialized_false, bytes)
        assert b'"bool"' in serialized_false  # 確認有類型標記
        
        deserialized_false = deserialize_value(serialized_false)
        assert deserialized_false is False
        assert isinstance(deserialized_false, bool)
    
    def test_integer_serialization(self):
        """測試整數序列化"""
        test_cases = [0, 1, -1, 42, -100, 999999, -999999]
        
        for original in test_cases:
            serialized = serialize_value(original)
            deserialized = deserialize_value(serialized)
            
            # 注意：0 和 1 會被解釋為布林值
            if original == 0:
                assert deserialized is False
            elif original == 1:
                assert deserialized is True
            else:
                assert deserialized == original
                assert isinstance(deserialized, int)
    
    def test_float_serialization(self):
        """測試浮點數序列化"""
        test_cases = [3.14, -2.71, 0.0, 1.23e-10, 1.23e10]
        
        for original in test_cases:
            serialized = serialize_value(original)
            deserialized = deserialize_value(serialized)
            
            assert deserialized == original
            assert isinstance(deserialized, float)
    
    def test_bytes_serialization(self):
        """測試位元組序列化"""
        test_cases = [
            b"hello",
            b"",
            b"\x00\x01\x02\x03",
            b"binary \xff\xfe\xfd data",
            "測試中文".encode('utf-8'),
        ]
        
        for original in test_cases:
            serialized = serialize_value(original)
            deserialized = deserialize_value(serialized)
            
            assert deserialized == original
            assert isinstance(deserialized, bytes)
    
    def test_dict_serialization(self):
        """測試字典序列化"""
        test_cases = [
            {},
            {"key": "value"},
            {"中文鍵": "中文值"},
            {"nested": {"dict": {"value": 123}}},
            {"mixed": [1, "two", 3.0, True, None]},
            {"numbers": 42, "text": "hello", "flag": True},
        ]
        
        for original in test_cases:
            serialized = serialize_value(original)
            deserialized = deserialize_value(serialized)
            
            assert deserialized == original
            assert isinstance(deserialized, dict)
    
    def test_list_serialization(self):
        """測試列表序列化"""
        test_cases = [
            [],
            [1, 2, 3],
            ["a", "b", "c"],
            [1, "two", 3.0, True, None],
            [[1, 2], {"nested": "dict"}],
            [{"user": "alice"}, {"user": "bob"}],
        ]
        
        for original in test_cases:
            serialized = serialize_value(original)
            deserialized = deserialize_value(serialized)
            
            assert deserialized == original
            assert isinstance(deserialized, list)
    
    def test_none_serialization(self):
        """測試 None 序列化"""
        original = None
        serialized = serialize_value(original)
        deserialized = deserialize_value(serialized)
        
        assert deserialized is None


class TestComplexSerialization:
    """複雜資料結構序列化測試"""
    
    def test_nested_structures(self):
        """測試巢狀結構"""
        complex_data = {
            "users": [
                {"id": 1, "name": "Alice", "active": True, "score": 95.5},
                {"id": 2, "name": "Bob", "active": False, "score": 87.2},
            ],
            "metadata": {
                "version": "1.0",
                "created": "2024-01-01",
                "settings": {
                    "debug": False,
                    "features": ["feature1", "feature2"],
                    "limits": {"max_users": 1000, "timeout": 30.0}
                }
            },
            "tags": ["important", "production", "v1.0"]
        }
        
        serialized = serialize_value(complex_data)
        deserialized = deserialize_value(serialized)
        
        assert deserialized == complex_data
        assert isinstance(deserialized, dict)
    
    def test_unicode_handling(self):
        """測試 Unicode 處理"""
        unicode_data = {
            "中文": "測試中文字符",
            "emoji": "🚀🌟💻",
            "mixed": "English 中文 🎉",
            "special": "\\n\\t\\r special chars",
            "list": ["項目一", "項目二", "🎯"]
        }
        
        serialized = serialize_value(unicode_data)
        deserialized = deserialize_value(serialized)
        
        assert deserialized == unicode_data
    
    def test_edge_cases(self):
        """測試邊界情況"""
        edge_cases = [
            {"": ""},  # 空鍵空值
            {"key": ""},  # 空值
            {"": "value"},  # 空鍵
            {str(i): i for i in range(100)},  # 大量鍵值對
            {"large_string": "x" * 10000},  # 大字串
            {"deep_nesting": {"a": {"b": {"c": {"d": "deep"}}}}},  # 深度巢狀
        ]
        
        for original in edge_cases:
            serialized = serialize_value(original)
            deserialized = deserialize_value(serialized)
            assert deserialized == original


class TestNumpySerialization:
    """Numpy 序列化測試（如果有安裝）"""
    
    def test_numpy_arrays(self):
        """測試 Numpy 陣列序列化"""
        try:
            import numpy as np
        except ImportError:
            pytest.skip("Numpy 未安裝，跳過測試")
        
        test_arrays = [
            np.array([1, 2, 3, 4, 5]),
            np.array([[1, 2], [3, 4], [5, 6]]),
            np.array([1.1, 2.2, 3.3], dtype=np.float32),
            np.array([True, False, True], dtype=bool),
            np.array([], dtype=int),  # 空陣列
        ]
        
        for original in test_arrays:
            serialized = serialize_value(original)
            deserialized = deserialize_value(serialized)
            
            assert np.array_equal(original, deserialized)
            assert original.shape == deserialized.shape
            assert original.dtype == deserialized.dtype
    
    def test_numpy_large_arrays(self):
        """測試大型 Numpy 陣列"""
        try:
            import numpy as np
        except ImportError:
            pytest.skip("Numpy 未安裝，跳過測試")
        
        # 測試大型陣列
        large_array = np.random.rand(1000, 100).astype(np.float32)
        
        serialized = serialize_value(large_array)
        deserialized = deserialize_value(serialized)
        
        assert np.array_equal(large_array, deserialized)
        assert large_array.shape == deserialized.shape
        assert large_array.dtype == deserialized.dtype


class TestSerializationErrors:
    """序列化錯誤測試"""
    
    def test_unserializable_objects(self):
        """測試無法序列化的物件"""
        
        # 函數物件
        def test_function():
            return "test"
        
        with pytest.raises(SerializationError):
            serialize_value(test_function)
        
        # 類別實例（沒有 __dict__ 或無法 JSON 序列化）
        class CustomClass:
            def __init__(self):
                self.func = lambda x: x
        
        custom_obj = CustomClass()
        with pytest.raises(SerializationError):
            serialize_value(custom_obj)
    
    def test_circular_references(self):
        """測試循環引用"""
        # 建立循環引用
        data = {"self": None}
        data["self"] = data
        
        with pytest.raises(SerializationError):
            serialize_value(data)


class TestSerializationRoundTrip:
    """序列化往返測試"""
    
    def test_multiple_rounds(self):
        """測試多次序列化往返"""
        original = {"test": "multiple rounds", "count": 0}
        
        current = original
        for i in range(5):
            current["count"] = i
            serialized = serialize_value(current)
            current = deserialize_value(serialized)
        
        assert current["test"] == original["test"]
        assert current["count"] == 4
    
    def test_type_preservation(self):
        """測試類型保持"""
        test_data = {
            "string": "test",
            "integer": 42,
            "float": 3.14,
            "boolean": True,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
            "none": None,
        }
        
        serialized = serialize_value(test_data)
        deserialized = deserialize_value(serialized)
        
        # 檢查每個值的類型
        assert isinstance(deserialized["string"], str)
        assert isinstance(deserialized["integer"], int)
        assert isinstance(deserialized["float"], float)
        assert isinstance(deserialized["boolean"], bool)
        assert isinstance(deserialized["list"], list)
        assert isinstance(deserialized["dict"], dict)
        assert deserialized["none"] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])