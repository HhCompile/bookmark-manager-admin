#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件夹管理器核心逻辑
"""

from app.models.folder import Folder


class FolderManager:
    """文件夹管理器，负责文件夹的增删改查操作"""
    
    def __init__(self):
        self.folders = []
        self._default_folders = [
            {'id': '1', 'name': '书签栏', 'parentId': None, 'children': []},
            {'id': '2', 'name': '其他书签', 'parentId': None, 'children': []},
        ]
        self._init_default_folders()
    
    def _init_default_folders(self):
        """初始化默认文件夹"""
        for folder_data in self._default_folders:
            folder = Folder(
                id=folder_data['id'],
                name=folder_data['name'],
                parent_id=folder_data['parentId'],
                children=folder_data['children']
            )
            self.folders.append(folder)
    
    def add_folder(self, folder):
        """添加文件夹
        
        Args:
            folder: Folder 对象
            
        Returns:
            Folder: 添加的文件夹
        """
        self.folders.append(folder)
        
        # 如果有父文件夹，更新父文件夹的 children
        if folder.parent_id:
            parent = self.get_folder_by_id(folder.parent_id)
            if parent and folder.id not in parent.children:
                parent.children.append(folder.id)
        
        return folder
    
    def has_folder(self, folder_id):
        """检查是否存在指定ID的文件夹
        
        Args:
            folder_id: 文件夹ID
            
        Returns:
            bool: 是否存在
        """
        return any(f.id == folder_id for f in self.folders)
    
    def has_folder_by_name(self, name, parent_id=None):
        """检查是否存在同名文件夹
        
        Args:
            name: 文件夹名称
            parent_id: 父文件夹ID（可选）
            
        Returns:
            bool: 是否存在
        """
        for folder in self.folders:
            if folder.name == name and folder.parent_id == parent_id:
                return True
        return False
    
    def remove_folder(self, folder_id):
        """根据ID删除文件夹
        
        Args:
            folder_id: 要删除的文件夹ID
            
        Returns:
            bool: 是否成功删除
        """
        folder = self.get_folder_by_id(folder_id)
        if not folder:
            return False
        
        # 从父文件夹的 children 中移除
        if folder.parent_id:
            parent = self.get_folder_by_id(folder.parent_id)
            if parent and folder_id in parent.children:
                parent.children.remove(folder_id)
        
        # 递归删除子文件夹
        for child_id in folder.children[:]:  # 使用切片复制列表
            self.remove_folder(child_id)
        
        # 删除自身
        self.folders = [f for f in self.folders if f.id != folder_id]
        return True
    
    def get_folders(self):
        """获取所有文件夹
        
        Returns:
            list: Folder 对象列表
        """
        return self.folders
    
    def get_folder_by_id(self, folder_id):
        """根据ID获取文件夹
        
        Args:
            folder_id: 文件夹ID
            
        Returns:
            Folder or None: 找到的文件夹，未找到返回 None
        """
        for folder in self.folders:
            if folder.id == folder_id:
                return folder
        return None
    
    def get_root_folders(self):
        """获取根级文件夹（没有父文件夹的）
        
        Returns:
            list: 根级 Folder 对象列表
        """
        return [f for f in self.folders if f.parent_id is None]
    
    def get_child_folders(self, parent_id):
        """获取指定父文件夹下的子文件夹
        
        Args:
            parent_id: 父文件夹ID
            
        Returns:
            list: 子 Folder 对象列表
        """
        return [f for f in self.folders if f.parent_id == parent_id]
    
    def update_folder(self, folder_id, **kwargs):
        """更新文件夹
        
        Args:
            folder_id: 要更新的文件夹ID
            **kwargs: 要更新的字段 (name, parent_id)
            
        Returns:
            Folder or None: 更新后的文件夹，未找到返回 None
        """
        folder = self.get_folder_by_id(folder_id)
        if not folder:
            return None
        
        # 处理 parent_id 变更
        new_parent_id = kwargs.get('parent_id')
        if new_parent_id is not None and new_parent_id != folder.parent_id:
            # 从旧父文件夹移除
            if folder.parent_id:
                old_parent = self.get_folder_by_id(folder.parent_id)
                if old_parent and folder_id in old_parent.children:
                    old_parent.children.remove(folder_id)
            
            # 添加到新父文件夹
            if new_parent_id:
                new_parent = self.get_folder_by_id(new_parent_id)
                if new_parent and folder_id not in new_parent.children:
                    new_parent.children.append(folder_id)
            
            folder.parent_id = new_parent_id
        
        # 更新名称
        if 'name' in kwargs:
            folder.name = kwargs['name']
        
        return folder
    
    def to_dict_list(self):
        """将所有文件夹转换为字典列表
        
        Returns:
            list: 文件夹字典列表
        """
        return [f.to_dict() for f in self.folders]
