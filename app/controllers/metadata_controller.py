#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
书签元数据管理器
管理用户的个性化设置
"""

import hashlib
from app.models.bookmark_metadata import BookmarkMetadata


class MetadataManager:
    """
    元数据管理器
    
    负责管理书签的元数据（别名、文件夹归类等），不管理书签内容
    """
    
    def __init__(self):
        self.metadata = {}  # url_hash -> BookmarkMetadata
    
    @staticmethod
    def hash_url(url):
        """
        计算URL的哈希值
        
        Args:
            url: 书签URL
            
        Returns:
            str: URL的MD5哈希值
        """
        return hashlib.md5(url.encode('utf-8')).hexdigest()
    
    def get_metadata(self, url):
        """
        获取书签的元数据
        
        Args:
            url: 书签URL
            
        Returns:
            BookmarkMetadata or None
        """
        url_hash = self.hash_url(url)
        return self.metadata.get(url_hash)
    
    def set_metadata(self, url, **kwargs):
        """
        设置书签的元数据
        
        Args:
            url: 书签URL
            **kwargs: 元数据字段
            
        Returns:
            BookmarkMetadata: 更新后的元数据
        """
        url_hash = self.hash_url(url)
        
        if url_hash in self.metadata:
            self.metadata[url_hash].update(**kwargs)
        else:
            self.metadata[url_hash] = BookmarkMetadata(url_hash=url_hash, **kwargs)
        
        return self.metadata[url_hash]
    
    def get_or_create(self, url):
        """
        获取或创建元数据
        
        Args:
            url: 书签URL
            
        Returns:
            BookmarkMetadata
        """
        url_hash = self.hash_url(url)
        
        if url_hash not in self.metadata:
            self.metadata[url_hash] = BookmarkMetadata(url_hash=url_hash)
        
        return self.metadata[url_hash]
    
    def delete_metadata(self, url):
        """
        删除书签的元数据
        
        Args:
            url: 书签URL
            
        Returns:
            bool: 是否成功删除
        """
        url_hash = self.hash_url(url)
        if url_hash in self.metadata:
            del self.metadata[url_hash]
            return True
        return False
    
    def get_all_metadata(self):
        """
        获取所有元数据
        
        Returns:
            dict: url_hash -> BookmarkMetadata
        """
        return self.metadata.copy()
    
    def get_by_folder(self, folder_id):
        """
        获取指定文件夹下的所有元数据
        
        Args:
            folder_id: 文件夹ID
            
        Returns:
            list: BookmarkMetadata 列表
        """
        return [m for m in self.metadata.values() if m.folder_id == folder_id]
    
    def get_favorites(self):
        """
        获取所有收藏的书签元数据
        
        Returns:
            list: BookmarkMetadata 列表
        """
        return [m for m in self.metadata.values() if m.is_favorite]
    
    def to_dict_list(self):
        """
        将所有元数据转换为字典列表
        
        Returns:
            list: 元数据字典列表
        """
        return [m.to_dict() for m in self.metadata.values()]
    
    def load_from_dict_list(self, dict_list):
        """
        从字典列表加载元数据
        
        Args:
            dict_list: 元数据字典列表
        """
        self.metadata = {}
        for data in dict_list:
            metadata = BookmarkMetadata.from_dict(data)
            self.metadata[metadata.url_hash] = metadata
