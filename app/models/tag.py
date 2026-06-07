#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标签数据模型

支持标签元数据、层级关系、使用统计
"""

import hashlib
from datetime import datetime
from typing import Optional, List, Dict, Any


class Tag:
    """标签数据模型"""
    
    # 预定义颜色 palette
    COLOR_PALETTE = [
        '#3B82F6',  # 蓝色
        '#8B5CF6',  # 紫色
        '#EC4899',  # 粉色
        '#F59E0B',  # 橙色
        '#10B981',  # 绿色
        '#EF4444',  # 红色
        '#6366F1',  # 靛蓝
        '#14B8A6',  # 青色
        '#F97316',  # 深橙
        '#84CC16',  # 黄绿
    ]
    
    def __init__(
        self,
        name: str,
        id: Optional[str] = None,
        color: Optional[str] = None,
        description: Optional[str] = None,
        parent_id: Optional[str] = None,
        is_system: bool = False,
        is_ai_generated: bool = False,
        usage_count: int = 0,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        **kwargs
    ):
        """
        初始化标签
        
        Args:
            name: 标签名称（必填）
            id: 标签唯一标识（可选，默认自动生成）
            color: 标签颜色（可选，默认根据名称生成）
            description: 标签描述（可选）
            parent_id: 父标签 ID（可选，支持层级）
            is_system: 是否为系统标签（可选）
            is_ai_generated: 是否 AI 生成（可选）
            usage_count: 使用次数（可选）
            created_at: 创建时间（可选）
            updated_at: 更新时间（可选）
        """
        # 规范化标签名（小写、去除首尾空格）
        self.name = name.strip().lower() if name else ''
        
        # 生成或设置 ID
        self.id = id or self._generate_id(self.name)
        
        # 设置颜色（未提供时自动生成）
        self.color = color or self._generate_color(self.name)
        
        # 其他属性
        self.description = description or ''
        self.parent_id = parent_id
        self.is_system = is_system
        self.is_ai_generated = is_ai_generated
        self.usage_count = usage_count
        
        # 时间戳
        now = datetime.now().isoformat()
        self.created_at = created_at or now
        self.updated_at = updated_at or now
    
    def _generate_id(self, name: str) -> str:
        """根据标签名生成唯一 ID"""
        hash_input = f"tag_{name}_{datetime.now().timestamp()}"
        hash_val = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        safe_name = ''.join(c if c.isalnum() else '_' for c in name[:20])
        return f"tag_{safe_name}_{hash_val}"
    
    def _generate_color(self, name: str) -> str:
        """根据标签名生成一致的颜色"""
        if not name:
            return self.COLOR_PALETTE[0]
        hash_val = sum(ord(c) for c in name)
        return self.COLOR_PALETTE[hash_val % len(self.COLOR_PALETTE)]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'description': self.description,
            'parent_id': self.parent_id,
            'is_system': self.is_system,
            'is_ai_generated': self.is_ai_generated,
            'usage_count': self.usage_count,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Tag':
        """从字典创建标签对象"""
        return cls(**data)
    
    def update(self, **kwargs) -> None:
        """更新标签属性"""
        allowed_fields = ['name', 'color', 'description', 'parent_id', 
                         'is_system', 'is_ai_generated']
        for field in allowed_fields:
            if field in kwargs:
                setattr(self, field, kwargs[field])
        self.updated_at = datetime.now().isoformat()
    
    def increment_usage(self, count: int = 1) -> None:
        """增加使用计数"""
        self.usage_count += count
        self.updated_at = datetime.now().isoformat()
    
    def decrement_usage(self, count: int = 1) -> None:
        """减少使用计数"""
        self.usage_count = max(0, self.usage_count - count)
        self.updated_at = datetime.now().isoformat()
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"Tag(id='{self.id}', name='{self.name}', usage={self.usage_count})"
    
    def __repr__(self) -> str:
        """对象表示"""
        return self.__str__()
    
    def __eq__(self, other) -> bool:
        """相等比较（基于 ID 或名称）"""
        if isinstance(other, Tag):
            return self.id == other.id or self.name == other.name
        if isinstance(other, str):
            return self.name == other.lower()
        return False
    
    def __hash__(self) -> int:
        """哈希值（基于 ID）"""
        return hash(self.id)


class TagSynonym:
    """标签同义词映射"""
    
    def __init__(self, synonym: str, canonical_name: str):
        """
        初始化同义词映射
        
        Args:
            synonym: 同义词
            canonical_name: 标准标签名
        """
        self.synonym = synonym.strip().lower()
        self.canonical_name = canonical_name.strip().lower()
    
    def to_dict(self) -> Dict[str, str]:
        """转换为字典"""
        return {
            'synonym': self.synonym,
            'canonical_name': self.canonical_name,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'TagSynonym':
        """从字典创建"""
        return cls(data['synonym'], data['canonical_name'])


class TagRelation:
    """标签关系（用于标签图谱）"""
    
    RELATION_TYPES = ['related', 'parent', 'synonym', 'child']
    
    def __init__(
        self,
        source_tag_id: str,
        target_tag_id: str,
        relation_type: str = 'related',
        weight: float = 0.5
    ):
        """
        初始化标签关系
        
        Args:
            source_tag_id: 源标签 ID
            target_tag_id: 目标标签 ID
            relation_type: 关系类型（related/parent/synonym/child）
            weight: 关系权重（0-1）
        """
        self.source_tag_id = source_tag_id
        self.target_tag_id = target_tag_id
        self.relation_type = relation_type if relation_type in self.RELATION_TYPES else 'related'
        self.weight = max(0.0, min(1.0, weight))
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'source_tag_id': self.source_tag_id,
            'target_tag_id': self.target_tag_id,
            'relation_type': self.relation_type,
            'weight': self.weight,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TagRelation':
        """从字典创建"""
        return cls(**data)
