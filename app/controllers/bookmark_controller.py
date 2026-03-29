#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
书签管理器核心逻辑
"""

from app.models.bookmark import Bookmark


class BookmarkManager:
    """书签管理器，负责书签的增删改查操作"""
    
    def __init__(self):
        self.bookmarks = []
        
    def add_bookmark(self, bookmark):
        """添加书签
        
        Args:
            bookmark: Bookmark 对象
        """
        self.bookmarks.append(bookmark)
        
    def has_bookmark(self, url):
        """检查是否已存在相同 URL 的书签
        
        Args:
            url: 要检查的 URL
            
        Returns:
            bool: 是否存在
        """
        return any(b.url == url for b in self.bookmarks)
        
    def remove_bookmark(self, url):
        """根据URL删除书签
        
        Args:
            url: 要删除的书签URL
        """
        self.bookmarks = [b for b in self.bookmarks if b.url != url]
        
    def get_bookmarks(self):
        """获取所有书签
        
        Returns:
            list: Bookmark 对象列表
        """
        return self.bookmarks
        
    def get_bookmarks_by_category(self, category):
        """根据分类获取书签
        
        Args:
            category: 分类名称
            
        Returns:
            list: 该分类下的 Bookmark 对象列表
        """
        return [b for b in self.bookmarks if b.category == category]
        
    def get_bookmarks_by_tag(self, tag):
        """根据标签获取书签
        
        Args:
            tag: 标签名称
            
        Returns:
            list: 包含该标签的 Bookmark 对象列表
        """
        return [b for b in self.bookmarks if tag in b.tags]