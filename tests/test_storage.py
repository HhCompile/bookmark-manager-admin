#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Storage 服务单元测试
"""

import pytest
import json
import os
import tempfile
import shutil
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.bookmark import Bookmark
from app.services.storage_service import Storage


class TestStorage:
    """Storage 服务测试类"""
    
    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # 清理
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def storage(self, temp_dir):
        """创建 Storage 实例"""
        file_path = os.path.join(temp_dir, "test_bookmarks.json")
        return Storage(file_path=file_path)
    
    @pytest.fixture
    def sample_bookmarks(self):
        """创建示例书签列表"""
        return [
            Bookmark(url="https://site1.com", title="Site 1", tags=["a"], category="Tech"),
            Bookmark(url="https://site2.com", title="Site 2", tags=["b"], category="News"),
        ]
    
    def test_save_and_load_bookmarks(self, storage, sample_bookmarks):
        """测试保存和加载书签"""
        # 保存书签
        storage.save_bookmarks(sample_bookmarks)
        
        # 加载书签
        loaded = storage.load_bookmarks()
        
        assert len(loaded) == 2
        assert loaded[0].url == "https://site1.com"
        assert loaded[1].url == "https://site2.com"
    
    def test_load_bookmarks_empty_file(self, storage):
        """测试加载空文件"""
        loaded = storage.load_bookmarks()
        
        assert loaded == []
    
    def test_load_bookmarks_non_existing_file(self, temp_dir):
        """测试加载不存在的文件"""
        file_path = os.path.join(temp_dir, "non_existing.json")
        storage = Storage(file_path=file_path)
        
        loaded = storage.load_bookmarks()
        
        assert loaded == []
    
    def test_save_creates_file(self, storage, sample_bookmarks):
        """测试保存创建文件"""
        assert not os.path.exists(storage.file_path)
        
        storage.save_bookmarks(sample_bookmarks)
        
        assert os.path.exists(storage.file_path)
    
    def test_save_file_content(self, storage, sample_bookmarks):
        """测试保存的文件内容"""
        storage.save_bookmarks(sample_bookmarks)
        
        with open(storage.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert len(data) == 2
        assert data[0]["url"] == "https://site1.com"
        assert data[0]["title"] == "Site 1"
        assert data[0]["tags"] == ["a"]
        assert data[0]["category"] == "Tech"
    
    def test_update_existing_bookmarks(self, storage):
        """测试更新现有书签"""
        # 初始保存
        bookmarks1 = [Bookmark(url="https://site1.com", title="Old Title")]
        storage.save_bookmarks(bookmarks1)
        
        # 更新
        bookmarks2 = [Bookmark(url="https://site1.com", title="New Title")]
        storage.save_bookmarks(bookmarks2)
        
        # 加载验证
        loaded = storage.load_bookmarks()
        assert loaded[0].title == "New Title"
    
    def test_save_empty_list(self, storage):
        """测试保存空列表"""
        storage.save_bookmarks([])
        
        loaded = storage.load_bookmarks()
        assert loaded == []
    
    def test_bookmark_with_special_characters(self, storage):
        """测试包含特殊字符的书签"""
        bookmark = Bookmark(
            url="https://example.com/path?query=1&other=2",
            title="标题 with émojis 🎉",
            tags=["标签", "test"],
            category="分类"
        )
        
        storage.save_bookmarks([bookmark])
        loaded = storage.load_bookmarks()
        
        assert len(loaded) == 1
        assert loaded[0].url == "https://example.com/path?query=1&other=2"
        assert loaded[0].title == "标题 with émojis 🎉"
        assert loaded[0].tags == ["标签", "test"]
        assert loaded[0].category == "分类"
    
    def test_multiple_save_operations(self, storage):
        """测试多次保存操作"""
        for i in range(5):
            bookmark = Bookmark(url=f"https://site{i}.com", title=f"Site {i}")
            storage.save_bookmarks([bookmark])
        
        loaded = storage.load_bookmarks()
        
        # 只保留最后一次保存的内容
        assert len(loaded) == 1
        assert loaded[0].url == "https://site4.com"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
