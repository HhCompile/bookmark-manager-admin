#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BookmarkManager 控制器单元测试
"""

import pytest
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.controllers.bookmark_controller import BookmarkManager
from app.models.bookmark import Bookmark


class TestBookmarkManager:
    """BookmarkManager 控制器测试类"""
    
    @pytest.fixture
    def manager(self):
        """创建一个新的 BookmarkManager 实例"""
        return BookmarkManager()
    
    @pytest.fixture
    def sample_bookmark(self):
        """创建示例书签"""
        return Bookmark(
            url="https://example.com",
            title="Example Site",
            tags=["test"],
            category="Test"
        )
    
    def test_add_bookmark(self, manager, sample_bookmark):
        """测试添加书签"""
        manager.add_bookmark(sample_bookmark)
        
        assert len(manager.get_bookmarks()) == 1
        assert manager.get_bookmarks()[0] == sample_bookmark
    
    def test_add_multiple_bookmarks(self, manager):
        """测试添加多个书签"""
        bookmark1 = Bookmark(url="https://site1.com", title="Site 1")
        bookmark2 = Bookmark(url="https://site2.com", title="Site 2")
        
        manager.add_bookmark(bookmark1)
        manager.add_bookmark(bookmark2)
        
        assert len(manager.get_bookmarks()) == 2
    
    def test_has_bookmark_existing(self, manager, sample_bookmark):
        """测试检查已存在的书签"""
        manager.add_bookmark(sample_bookmark)
        
        assert manager.has_bookmark("https://example.com") is True
    
    def test_has_bookmark_non_existing(self, manager):
        """测试检查不存在的书签"""
        assert manager.has_bookmark("https://nonexistent.com") is False
    
    def test_remove_bookmark(self, manager, sample_bookmark):
        """测试删除书签"""
        manager.add_bookmark(sample_bookmark)
        assert len(manager.get_bookmarks()) == 1
        
        manager.remove_bookmark("https://example.com")
        assert len(manager.get_bookmarks()) == 0
    
    def test_remove_non_existing_bookmark(self, manager):
        """测试删除不存在的书签"""
        bookmark = Bookmark(url="https://example.com", title="Example")
        manager.add_bookmark(bookmark)
        
        manager.remove_bookmark("https://nonexistent.com")
        assert len(manager.get_bookmarks()) == 1
    
    def test_get_bookmarks_empty(self, manager):
        """测试获取空书签列表"""
        bookmarks = manager.get_bookmarks()
        
        assert bookmarks == []
        assert isinstance(bookmarks, list)
    
    def test_get_bookmarks_by_category(self, manager):
        """测试按分类获取书签"""
        bookmark1 = Bookmark(url="https://site1.com", title="Site 1", category="Tech")
        bookmark2 = Bookmark(url="https://site2.com", title="Site 2", category="Tech")
        bookmark3 = Bookmark(url="https://site3.com", title="Site 3", category="News")
        
        manager.add_bookmark(bookmark1)
        manager.add_bookmark(bookmark2)
        manager.add_bookmark(bookmark3)
        
        tech_bookmarks = manager.get_bookmarks_by_category("Tech")
        
        assert len(tech_bookmarks) == 2
        assert bookmark1 in tech_bookmarks
        assert bookmark2 in tech_bookmarks
        assert bookmark3 not in tech_bookmarks
    
    def test_get_bookmarks_by_category_non_existing(self, manager):
        """测试按不存在的分类获取书签"""
        bookmark = Bookmark(url="https://example.com", title="Example", category="Tech")
        manager.add_bookmark(bookmark)
        
        result = manager.get_bookmarks_by_category("NonExisting")
        assert result == []
    
    def test_get_bookmarks_by_tag(self, manager):
        """测试按标签获取书签"""
        bookmark1 = Bookmark(url="https://site1.com", title="Site 1", tags=["python", "coding"])
        bookmark2 = Bookmark(url="https://site2.com", title="Site 2", tags=["python", "tutorial"])
        bookmark3 = Bookmark(url="https://site3.com", title="Site 3", tags=["javascript"])
        
        manager.add_bookmark(bookmark1)
        manager.add_bookmark(bookmark2)
        manager.add_bookmark(bookmark3)
        
        python_bookmarks = manager.get_bookmarks_by_tag("python")
        
        assert len(python_bookmarks) == 2
        assert bookmark1 in python_bookmarks
        assert bookmark2 in python_bookmarks
        assert bookmark3 not in python_bookmarks
    
    def test_get_bookmarks_by_tag_non_existing(self, manager):
        """测试按不存在的标签获取书签"""
        bookmark = Bookmark(url="https://example.com", title="Example", tags=["python"])
        manager.add_bookmark(bookmark)
        
        result = manager.get_bookmarks_by_tag("javascript")
        assert result == []
    
    def test_bookmark_with_empty_tags(self, manager):
        """测试空标签列表的书签"""
        bookmark = Bookmark(url="https://example.com", title="Example", tags=[])
        manager.add_bookmark(bookmark)
        
        result = manager.get_bookmarks_by_tag("anytag")
        assert result == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
