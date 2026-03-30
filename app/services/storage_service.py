#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据存储接口

功能：
1. 保存和加载书签数据
2. 自动备份机制（写入前先备份原文件）
3. 原子写入（使用临时文件 + 重命名）
4. 限制备份文件数量
"""

import os
import json
import shutil
import glob
from datetime import datetime
from app.models.bookmark import Bookmark


class Storage:
    """存储服务，负责书签数据的持久化"""
    
    # 最大备份文件数量
    MAX_BACKUP_COUNT = 5
    
    def __init__(self, file_path):
        self.file_path = file_path
        
    def save_bookmarks(self, bookmarks):
        """保存书签到文件（原子写入 + 备份）
        
        Args:
            bookmarks: Bookmark 对象列表
        """
        # 构建数据
        data = []
        for bookmark in bookmarks:
            data.append({
                'url': bookmark.url,
                'title': bookmark.title,
                'tags': bookmark.tags,
                'category': bookmark.category
            })
        
        # 如果原文件存在，先创建备份
        if os.path.exists(self.file_path):
            self._create_backup()
            self._cleanup_old_backups()
        
        # 使用临时文件 + 重命名的方式实现原子写入
        temp_file = self.file_path + '.tmp'
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 原子重命名
            os.replace(temp_file, self.file_path)
        except Exception:
            # 如果失败，清理临时文件
            if os.path.exists(temp_file):
                os.remove(temp_file)
            raise
            
    def _create_backup(self):
        """创建带时间戳的备份文件"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f"{self.file_path}.{timestamp}.backup"
        try:
            shutil.copy2(self.file_path, backup_path)
        except Exception:
            # 备份失败不影响主流程
            pass
    
    def _cleanup_old_backups(self):
        """清理旧的备份文件，只保留最近的 MAX_BACKUP_COUNT 个"""
        try:
            # 查找所有备份文件
            pattern = f"{self.file_path}.*.backup"
            backup_files = glob.glob(pattern)
            
            # 如果备份文件数量超过限制，删除最旧的
            if len(backup_files) > self.MAX_BACKUP_COUNT:
                # 按修改时间排序
                backup_files.sort(key=os.path.getmtime)
                # 删除多余的旧备份
                for old_file in backup_files[:-self.MAX_BACKUP_COUNT]:
                    try:
                        os.remove(old_file)
                    except Exception:
                        pass
        except Exception:
            # 清理失败不影响主流程
            pass
            
    def load_bookmarks(self):
        """从文件加载书签
        
        Returns:
            list: Bookmark 对象列表
        """
        # 如果主文件不存在，尝试从备份恢复
        if not os.path.exists(self.file_path):
            backup_path = self.file_path + '.backup'
            if os.path.exists(backup_path):
                try:
                    shutil.copy2(backup_path, self.file_path)
                except Exception:
                    return []
            else:
                return []
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            bookmarks = []
            for item in data:
                bookmark = Bookmark(
                    url=item.get('url', ''),
                    title=item.get('title', ''),
                    tags=item.get('tags', []),
                    category=item.get('category')
                )
                bookmarks.append(bookmark)
                
            return bookmarks
        except (FileNotFoundError, json.JSONDecodeError):
            # 如果文件损坏，尝试从备份恢复
            backup_path = self.file_path + '.backup'
            if os.path.exists(backup_path):
                try:
                    with open(backup_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    bookmarks = []
                    for item in data:
                        bookmark = Bookmark(
                            url=item.get('url', ''),
                            title=item.get('title', ''),
                            tags=item.get('tags', []),
                            category=item.get('category')
                        )
                        bookmarks.append(bookmark)
                    
                    # 恢复主文件
                    shutil.copy2(backup_path, self.file_path)
                    return bookmarks
                except Exception:
                    return []
            return []