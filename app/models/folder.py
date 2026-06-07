#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件夹数据结构定义
"""


class Folder:
    """文件夹数据模型"""
    
    def __init__(self, id=None, name=None, parent_id=None, children=None):
        """初始化文件夹
        
        Args:
            id: 文件夹唯一标识
            name: 文件夹名称
            parent_id: 父文件夹ID（None 表示根目录）
            children: 子文件夹ID列表
        """
        self.id = id or self._generate_id()
        self.name = str(name) if name else ''
        self.parent_id = parent_id
        self.children = children or []
    
    def _generate_id(self):
        """生成唯一ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def __str__(self):
        """字符串表示"""
        return f"Folder(id='{self.id}', name='{self.name}', parent_id='{self.parent_id}')"
    
    def __repr__(self):
        """对象表示"""
        return self.__str__()
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'parentId': self.parent_id,
            'children': self.children
        }
