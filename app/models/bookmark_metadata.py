#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
书签元数据模型
存储用户的个性化设置，不存储书签内容本身
"""

from datetime import datetime


class BookmarkMetadata:
    """
    书签元数据
    
    注意：此类只存储用户的个性化设置，不存储书签内容（URL、标题等）
    书签内容存储在原始书签文件中
    """
    
    def __init__(self, url_hash, alias=None, folder_id=None, custom_tags=None, 
                 notes=None, is_favorite=False, display_order=0):
        """
        初始化书签元数据
        
        Args:
            url_hash: URL的哈希值（唯一标识）
            alias: 用户自定义别名
            folder_id: 所属文件夹ID
            custom_tags: 用户自定义标签列表
            notes: 用户备注
            is_favorite: 是否收藏
            display_order: 显示顺序
        """
        self.url_hash = url_hash
        self.alias = alias or ''
        self.folder_id = folder_id
        self.custom_tags = custom_tags or []
        self.notes = notes or ''
        self.is_favorite = is_favorite
        self.display_order = display_order
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self):
        """转换为字典"""
        return {
            'url_hash': self.url_hash,
            'alias': self.alias,
            'folder_id': self.folder_id,
            'custom_tags': self.custom_tags,
            'notes': self.notes,
            'is_favorite': self.is_favorite,
            'display_order': self.display_order,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建实例"""
        metadata = cls(
            url_hash=data.get('url_hash', ''),
            alias=data.get('alias', ''),
            folder_id=data.get('folder_id'),
            custom_tags=data.get('custom_tags', []),
            notes=data.get('notes', ''),
            is_favorite=data.get('is_favorite', False),
            display_order=data.get('display_order', 0)
        )
        metadata.created_at = data.get('created_at', datetime.now().isoformat())
        metadata.updated_at = data.get('updated_at', datetime.now().isoformat())
        return metadata
    
    def update(self, **kwargs):
        """更新元数据"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now().isoformat()
