#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
书签数据结构定义
"""


class Bookmark:
    """书签数据模型"""
    
    def __init__(self, url, title, tags=None, category=None):
        """初始化书签
        
        Args:
            url: 书签URL（字符串）
            title: 书签标题（字符串）
            tags: 标签列表（可选，默认为空列表）
            category: 分类（可选）
        """
        # 确保 url 和 title 是字符串类型
        self.url = str(url) if url is not None else ''
        self.title = str(title) if title is not None else ''
        self.tags = tags or []
        self.category = category
    
    def __str__(self):
        """字符串表示"""
        return f"Bookmark(url='{self.url}', title='{self.title}', tags={self.tags}, category='{self.category}')"
    
    def __repr__(self):
        """对象表示"""
        return self.__str__()
    
    def __eq__(self, other):
        """相等比较（基于 URL）
        
        Args:
            other: 另一个 Bookmark 对象
            
        Returns:
            bool: URL 相同则视为相等
        """
        if not isinstance(other, Bookmark):
            return False
        return self.url == other.url
    
    def __hash__(self):
        """哈希值（基于 URL）
        
        Returns:
            int: URL 的哈希值
        """
        return hash(self.url)