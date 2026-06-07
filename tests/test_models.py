#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bookmark 模型单元测试
"""

import pytest
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.bookmark import Bookmark


class TestBookmark:
    """Bookmark 模型测试类"""
    
    def test_bookmark_creation(self):
        """测试书签创建"""
        bookmark = Bookmark(
            url="https://example.com",
            title="Example Site",
            tags=["test", "example"],
            category="Test Category"
        )
        
        assert bookmark.url == "https://example.com"
        assert bookmark.title == "Example Site"
        assert bookmark.tags == ["test", "example"]
        assert bookmark.category == "Test Category"
    
    def test_bookmark_creation_with_defaults(self):
        """测试使用默认值创建书签"""
        bookmark = Bookmark(
            url="https://example.com",
            title="Example"
        )
        
        assert bookmark.url == "https://example.com"
        assert bookmark.title == "Example"
        assert bookmark.tags == []
        assert bookmark.category is None
    
    def test_bookmark_creation_with_none_values(self):
        """测试使用 None 值创建书签"""
        bookmark = Bookmark(
            url=None,
            title=None,
            tags=None,
            category=None
        )
        
        assert bookmark.url == ""
        assert bookmark.title == ""
        assert bookmark.tags == []
        assert bookmark.category is None
    
    def test_bookmark_string_representation(self):
        """测试书签的字符串表示"""
        bookmark = Bookmark(
            url="https://example.com",
            title="Example",
            tags=["tag1"],
            category="Cat"
        )
        
        expected = "Bookmark(url='https://example.com', title='Example', tags=['tag1'], category='Cat')"
        assert str(bookmark) == expected
        assert repr(bookmark) == expected
    
    def test_bookmark_equality(self):
        """测试书签相等性比较"""
        bookmark1 = Bookmark(url="https://example.com", title="Example 1")
        bookmark2 = Bookmark(url="https://example.com", title="Example 2")
        bookmark3 = Bookmark(url="https://other.com", title="Other")
        
        # URL 相同则视为相等
        assert bookmark1 == bookmark2
        assert bookmark1 != bookmark3
        assert bookmark2 != bookmark3
    
    def test_bookmark_equality_with_non_bookmark(self):
        """测试书签与非书签对象比较"""
        bookmark = Bookmark(url="https://example.com", title="Example")
        
        assert bookmark != "https://example.com"
        assert bookmark != 123
        assert bookmark != None
        assert bookmark != {"url": "https://example.com"}
    
    def test_bookmark_hash(self):
        """测试书签哈希值"""
        bookmark1 = Bookmark(url="https://example.com", title="Example 1")
        bookmark2 = Bookmark(url="https://example.com", title="Example 2")
        bookmark3 = Bookmark(url="https://other.com", title="Other")
        
        # URL 相同则哈希值相同
        assert hash(bookmark1) == hash(bookmark2)
        assert hash(bookmark1) != hash(bookmark3)
    
    def test_bookmark_in_set(self):
        """测试书签可以放入集合中"""
        bookmark1 = Bookmark(url="https://example.com", title="Example 1")
        bookmark2 = Bookmark(url="https://example.com", title="Example 2")
        bookmark3 = Bookmark(url="https://other.com", title="Other")
        
        bookmark_set = {bookmark1, bookmark2, bookmark3}
        
        # 由于 bookmark1 和 bookmark2 URL 相同，集合中只会有 2 个元素
        assert len(bookmark_set) == 2
    
    def test_bookmark_url_type_conversion(self):
        """测试 URL 类型转换"""
        bookmark = Bookmark(url=123, title=456)
        
        assert bookmark.url == "123"
        assert bookmark.title == "456"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
