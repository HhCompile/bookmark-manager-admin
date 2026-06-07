#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序列化工具单元测试
"""

import pytest
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.bookmark import Bookmark
from app.utils.serializers import (
    bookmark_to_dict,
    bookmarks_to_dict_list,
    dict_to_bookmark,
    dict_list_to_bookmarks
)


class TestSerializers:
    """序列化工具测试类"""
    
    @pytest.fixture
    def sample_bookmark(self):
        """创建示例书签"""
        return Bookmark(
            url="https://example.com",
            title="Example Site",
            tags=["test", "example"],
            category="Test Category"
        )
    
    @pytest.fixture
    def sample_dict(self):
        """创建示例字典"""
        return {
            "url": "https://example.com",
            "title": "Example Site",
            "tags": ["test", "example"],
            "category": "Test Category"
        }
    
    def test_bookmark_to_dict(self, sample_bookmark):
        """测试书签转字典"""
        result = bookmark_to_dict(sample_bookmark)
        
        expected = {
            "url": "https://example.com",
            "title": "Example Site",
            "tags": ["test", "example"],
            "category": "Test Category"
        }
        
        assert result == expected
    
    def test_bookmark_to_dict_empty_tags(self):
        """测试空标签书签转字典"""
        bookmark = Bookmark(url="https://example.com", title="Example")
        result = bookmark_to_dict(bookmark)
        
        assert result["tags"] == []
        assert result["category"] is None
    
    def test_bookmarks_to_dict_list(self):
        """测试书签列表转字典列表"""
        bookmarks = [
            Bookmark(url="https://site1.com", title="Site 1", tags=["a"]),
            Bookmark(url="https://site2.com", title="Site 2", tags=["b"]),
        ]
        
        result = bookmarks_to_dict_list(bookmarks)
        
        assert len(result) == 2
        assert result[0]["url"] == "https://site1.com"
        assert result[1]["url"] == "https://site2.com"
    
    def test_bookmarks_to_dict_list_empty(self):
        """测试空书签列表转字典列表"""
        result = bookmarks_to_dict_list([])
        
        assert result == []
    
    def test_dict_to_bookmark(self, sample_dict):
        """测试字典转书签"""
        result = dict_to_bookmark(sample_dict)
        
        assert isinstance(result, Bookmark)
        assert result.url == "https://example.com"
        assert result.title == "Example Site"
        assert result.tags == ["test", "example"]
        assert result.category == "Test Category"
    
    def test_dict_to_bookmark_partial(self):
        """测试部分字典转书签"""
        data = {"url": "https://example.com"}
        result = dict_to_bookmark(data)
        
        assert result.url == "https://example.com"
        assert result.title == ""  # 默认值
        assert result.tags == []  # 默认值
        assert result.category is None  # 默认值
    
    def test_dict_to_bookmark_empty_dict(self):
        """测试空字典转书签"""
        result = dict_to_bookmark({})
        
        assert result.url == ""
        assert result.title == ""
        assert result.tags == []
        assert result.category is None
    
    def test_dict_list_to_bookmarks(self):
        """测试字典列表转书签列表"""
        dict_list = [
            {"url": "https://site1.com", "title": "Site 1"},
            {"url": "https://site2.com", "title": "Site 2"},
        ]
        
        result = dict_list_to_bookmarks(dict_list)
        
        assert len(result) == 2
        assert all(isinstance(b, Bookmark) for b in result)
        assert result[0].url == "https://site1.com"
        assert result[1].url == "https://site2.com"
    
    def test_dict_list_to_bookmarks_empty(self):
        """测试空字典列表转书签列表"""
        result = dict_list_to_bookmarks([])
        
        assert result == []
    
    def test_roundtrip_conversion(self, sample_bookmark):
        """测试往返转换（书签 -> 字典 -> 书签）"""
        # 书签转字典
        dict_data = bookmark_to_dict(sample_bookmark)
        # 字典转书签
        result = dict_to_bookmark(dict_data)
        
        assert result == sample_bookmark
        assert result.url == sample_bookmark.url
        assert result.title == sample_bookmark.title


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
