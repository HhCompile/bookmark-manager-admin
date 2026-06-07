#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标签管理服务

提供标签的增删改查、合并、重命名等功能
"""

import os
import json
import threading
from typing import List, Dict, Optional, Any, Tuple
from collections import Counter
from datetime import datetime

from app.models.tag import Tag, TagSynonym
from app.services.storage_service import Storage


class TagExistsError(Exception):
    """标签已存在错误"""
    pass


class TagNotFoundError(Exception):
    """标签不存在错误"""
    pass


class TagManager:
    """标签管理器 - 处理标签的增删改查"""
    
    def __init__(self, storage_path: str = 'tags.json'):
        """
        初始化标签管理器
        
        Args:
            storage_path: 标签存储文件路径
        """
        self.storage = Storage(storage_path)
        self.lock = threading.Lock()
        self._tags: Dict[str, Tag] = {}  # id -> Tag
        self._name_index: Dict[str, str] = {}  # name -> id
        self._synonyms: Dict[str, str] = {}  # synonym -> canonical_name
        
        # 加载已有标签
        self._load_tags()
    
    def _load_tags(self) -> None:
        """从存储加载标签"""
        data = self.storage.load_raw()
        if not data:
            return
        
        try:
            tags_data = json.loads(data) if isinstance(data, str) else data
            
            # 加载标签
            for tag_dict in tags_data.get('tags', []):
                tag = Tag.from_dict(tag_dict)
                self._tags[tag.id] = tag
                self._name_index[tag.name] = tag.id
            
            # 加载同义词
            self._synonyms = tags_data.get('synonyms', {})
            
        except (json.JSONDecodeError, KeyError) as e:
            import logging
            logging.getLogger('tag_manager').error(f'加载标签失败: {e}')
    
    def _save_tags(self) -> None:
        """保存标签到存储"""
        data = {
            'version': '1.0',
            'tags': [tag.to_dict() for tag in self._tags.values()],
            'synonyms': self._synonyms,
        }
        self.storage.save_raw(json.dumps(data, ensure_ascii=False, indent=2))
    
    # ==================== CRUD 操作 ====================
    
    def create_tag(
        self,
        name: str,
        color: Optional[str] = None,
        description: Optional[str] = None,
        parent_id: Optional[str] = None,
        is_system: bool = False,
        is_ai_generated: bool = False
    ) -> Tag:
        """
        创建新标签
        
        Args:
            name: 标签名称
            color: 标签颜色（可选）
            description: 标签描述（可选）
            parent_id: 父标签 ID（可选）
            is_system: 是否为系统标签
            is_ai_generated: 是否 AI 生成
        
        Returns:
            Tag: 创建的标签对象
        
        Raises:
            TagExistsError: 标签已存在
        """
        normalized_name = name.strip().lower()
        
        with self.lock:
            # 检查是否已存在
            if normalized_name in self._name_index:
                raise TagExistsError(f"标签 '{name}' 已存在")
            
            # 检查同义词
            if normalized_name in self._synonyms:
                canonical = self._synonyms[normalized_name]
                raise TagExistsError(f"标签 '{name}' 是 '{canonical}' 的同义词")
            
            # 验证父标签存在
            if parent_id and parent_id not in self._tags:
                raise TagNotFoundError(f"父标签 '{parent_id}' 不存在")
            
            # 创建标签
            tag = Tag(
                name=name,
                color=color,
                description=description,
                parent_id=parent_id,
                is_system=is_system,
                is_ai_generated=is_ai_generated
            )
            
            # 保存
            self._tags[tag.id] = tag
            self._name_index[tag.name] = tag.id
            self._save_tags()
            
            return tag
    
    def get_tag(self, tag_id: str) -> Optional[Tag]:
        """根据 ID 获取标签"""
        return self._tags.get(tag_id)
    
    def get_tag_by_name(self, name: str) -> Optional[Tag]:
        """根据名称获取标签"""
        normalized_name = name.strip().lower()
        
        # 直接匹配
        if normalized_name in self._name_index:
            tag_id = self._name_index[normalized_name]
            return self._tags.get(tag_id)
        
        # 同义词匹配
        if normalized_name in self._synonyms:
            canonical_name = self._synonyms[normalized_name]
            if canonical_name in self._name_index:
                tag_id = self._name_index[canonical_name]
                return self._tags.get(tag_id)
        
        return None
    
    def get_all_tags(
        self,
        parent_id: Optional[str] = None,
        include_system: bool = True
    ) -> List[Tag]:
        """
        获取所有标签
        
        Args:
            parent_id: 筛选指定父标签的子标签（None 表示顶级标签）
            include_system: 是否包含系统标签
        
        Returns:
            List[Tag]: 标签列表
        """
        tags = []
        for tag in self._tags.values():
            if parent_id is not None and tag.parent_id != parent_id:
                continue
            if not include_system and tag.is_system:
                continue
            tags.append(tag)
        return tags
    
    def update_tag(self, tag_id: str, **kwargs) -> Tag:
        """
        更新标签
        
        Args:
            tag_id: 标签 ID
            **kwargs: 要更新的字段
        
        Returns:
            Tag: 更新后的标签
        
        Raises:
            TagNotFoundError: 标签不存在
            TagExistsError: 新名称与其他标签冲突
        """
        with self.lock:
            tag = self._tags.get(tag_id)
            if not tag:
                raise TagNotFoundError(f"标签 '{tag_id}' 不存在")
            
            # 如果修改名称，检查冲突
            if 'name' in kwargs:
                new_name = kwargs['name'].strip().lower()
                if new_name != tag.name and new_name in self._name_index:
                    raise TagExistsError(f"标签名称 '{kwargs['name']}' 已被使用")
                # 更新索引
                del self._name_index[tag.name]
                self._name_index[new_name] = tag_id
            
            tag.update(**kwargs)
            self._save_tags()
            return tag
    
    def delete_tag(self, tag_id: str, migrate_to: Optional[str] = None) -> None:
        """
        删除标签
        
        Args:
            tag_id: 要删除的标签 ID
            migrate_to: 迁移到的目标标签 ID（可选）
        
        Raises:
            TagNotFoundError: 标签不存在
        """
        with self.lock:
            tag = self._tags.get(tag_id)
            if not tag:
                raise TagNotFoundError(f"标签 '{tag_id}' 不存在")
            
            # 如果指定了迁移目标，验证目标存在
            if migrate_to and migrate_to not in self._tags:
                raise TagNotFoundError(f"迁移目标标签 '{migrate_to}' 不存在")
            
            # 更新子标签的父标签引用
            for t in self._tags.values():
                if t.parent_id == tag_id:
                    t.parent_id = migrate_to
            
            # 删除标签
            del self._tags[tag_id]
            del self._name_index[tag.name]
            self._save_tags()
    
    # ==================== 高级操作 ====================
    
    def merge_tags(self, source_tag_id: str, target_tag_id: str) -> Tag:
        """
        合并标签
        
        将源标签合并到目标标签，所有使用源标签的书签将改为使用目标标签
        
        Args:
            source_tag_id: 源标签 ID
            target_tag_id: 目标标签 ID
        
        Returns:
            Tag: 目标标签
        """
        with self.lock:
            source = self._tags.get(source_tag_id)
            target = self._tags.get(target_tag_id)
            
            if not source:
                raise TagNotFoundError(f"源标签 '{source_tag_id}' 不存在")
            if not target:
                raise TagNotFoundError(f"目标标签 '{target_tag_id}' 不存在")
            
            # 添加同义词映射
            self._synonyms[source.name] = target.name
            
            # 更新目标标签使用计数
            target.increment_usage(source.usage_count)
            
            # 删除源标签
            self.delete_tag(source_tag_id, migrate_to=target_tag_id)
            
            self._save_tags()
            return target
    
    def rename_tag(self, tag_id: str, new_name: str) -> Tag:
        """
        重命名标签
        
        Args:
            tag_id: 标签 ID
            new_name: 新名称
        
        Returns:
            Tag: 重命名后的标签
        """
        return self.update_tag(tag_id, name=new_name)
    
    def add_synonym(self, synonym: str, canonical_name: str) -> None:
        """
        添加同义词映射
        
        Args:
            synonym: 同义词
            canonical_name: 标准标签名
        """
        with self.lock:
            self._synonyms[synonym.strip().lower()] = canonical_name.strip().lower()
            self._save_tags()
    
    def get_tag_hierarchy(self) -> List[Dict[str, Any]]:
        """
        获取标签层级结构
        
        Returns:
            List[Dict]: 树形结构的标签列表
        """
        def build_tree(parent_id: Optional[str] = None) -> List[Dict[str, Any]]:
            nodes = []
            for tag in self._tags.values():
                if tag.parent_id == parent_id:
                    node = tag.to_dict()
                    node['children'] = build_tree(tag.id)
                    nodes.append(node)
            return nodes
        
        return build_tree()
    
    def search_tags(
        self,
        query: str,
        limit: int = 10
    ) -> List[Tag]:
        """
        搜索标签
        
        Args:
            query: 搜索关键词
            limit: 返回数量限制
        
        Returns:
            List[Tag]: 匹配的标签列表
        """
        query = query.lower().strip()
        matches = []
        
        for tag in self._tags.values():
            score = 0
            # 名称完全匹配
            if tag.name == query:
                score = 100
            # 名称包含
            elif query in tag.name:
                score = 80
            # 描述包含
            elif tag.description and query in tag.description.lower():
                score = 40
            
            if score > 0:
                matches.append((score, tag))
        
        # 按分数排序并返回
        matches.sort(key=lambda x: x[0], reverse=True)
        return [tag for _, tag in matches[:limit]]
    
    def get_related_tags(self, tag_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取相关标签
        
        基于共现频率计算相关标签
        
        Args:
            tag_id: 标签 ID
            limit: 返回数量限制
        
        Returns:
            List[Dict]: 相关标签列表（含相关度）
        """
        # 这里需要与 BookmarkManager 协作
        # 暂时返回空列表，实际实现时需要注入 BookmarkManager
        return []
    
    def get_or_create(self, name: str, **kwargs) -> Tuple[Tag, bool]:
        """
        获取或创建标签
        
        Args:
            name: 标签名称
            **kwargs: 创建时的其他参数
        
        Returns:
            Tuple[Tag, bool]: (标签, 是否新创建)
        """
        tag = self.get_tag_by_name(name)
        if tag:
            return tag, False
        
        try:
            tag = self.create_tag(name, **kwargs)
            return tag, True
        except TagExistsError:
            # 可能已被其他线程创建
            return self.get_tag_by_name(name), False
    
    def increment_usage(self, tag_id: str, count: int = 1) -> None:
        """增加标签使用计数"""
        with self.lock:
            tag = self._tags.get(tag_id)
            if tag:
                tag.increment_usage(count)
                self._save_tags()
    
    def decrement_usage(self, tag_id: str, count: int = 1) -> None:
        """减少标签使用计数"""
        with self.lock:
            tag = self._tags.get(tag_id)
            if tag:
                tag.decrement_usage(count)
                self._save_tags()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取标签统计信息"""
        total = len(self._tags)
        system_tags = sum(1 for t in self._tags.values() if t.is_system)
        ai_generated = sum(1 for t in self._tags.values() if t.is_ai_generated)
        total_usage = sum(t.usage_count for t in self._tags.values())
        
        return {
            'total': total,
            'system': system_tags,
            'ai_generated': ai_generated,
            'user_created': total - system_tags - ai_generated,
            'total_usage': total_usage,
            'synonyms': len(self._synonyms),
        }
