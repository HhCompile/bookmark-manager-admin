#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序列化工具模块

功能：
1. 提供 Bookmark 对象的序列化/反序列化
2. 统一处理数据转换逻辑，避免代码重复
"""

from typing import List, Dict, Any
from app.models.bookmark import Bookmark


def bookmark_to_dict(bookmark: Bookmark) -> Dict[str, Any]:
    """将 Bookmark 对象转换为字典
    
    Args:
        bookmark: Bookmark 对象
        
    Returns:
        dict: 书签字典
    """
    return {
        'url': bookmark.url,
        'title': bookmark.title,
        'tags': bookmark.tags,
        'category': bookmark.category
    }


def bookmarks_to_dict_list(bookmarks: List[Bookmark]) -> List[Dict[str, Any]]:
    """将 Bookmark 对象列表转换为字典列表
    
    Args:
        bookmarks: Bookmark 对象列表
        
    Returns:
        list: 书签字典列表
    """
    return [bookmark_to_dict(b) for b in bookmarks]


def dict_to_bookmark(data: Dict[str, Any]) -> Bookmark:
    """将字典转换为 Bookmark 对象
    
    Args:
        data: 书签字典
        
    Returns:
        Bookmark: 书签对象
    """
    return Bookmark(
        url=data.get('url', ''),
        title=data.get('title', ''),
        tags=data.get('tags', []),
        category=data.get('category')
    )


def dict_list_to_bookmarks(data_list: List[Dict[str, Any]]) -> List[Bookmark]:
    """将字典列表转换为 Bookmark 对象列表
    
    Args:
        data_list: 书签字典列表
        
    Returns:
        list: Bookmark 对象列表
    """
    return [dict_to_bookmark(d) for d in data_list]
