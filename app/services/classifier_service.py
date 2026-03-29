#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动打标和分类算法

支持从配置文件加载分类规则
"""

import os
import json
import re
from app.models.bookmark import Bookmark


class Classifier:
    """书签分类器，支持关键词匹配自动分类和打标"""
    
    # 默认分类规则（当配置文件不存在时使用）
    DEFAULT_CATEGORY_KEYWORDS = {
        '技术': ['python', 'javascript', 'java', '编程', '开发', 'github', 'git', 'linux', 'docker'],
        '新闻': ['新闻', '时事', '政治', '社会', '财经'],
        '娱乐': ['电影', '音乐', '游戏', '娱乐', '视频'],
        '学习': ['教程', '学习', '课程', '教育', '学术'],
        '生活': ['生活', '健康', '美食', '旅行', '家居']
    }
    
    # 默认标签规则
    DEFAULT_TAG_KEYWORDS = {
        '编程': ['python', 'javascript', 'java', 'code', '编程'],
        '开源': ['github', '开源', 'source', 'code'],
        '教程': ['教程', 'guide', 'tutorial', 'howto'],
        '文档': ['文档', 'doc', 'document', '手册']
    }
    
    def __init__(self, config_path: str = None):
        """初始化分类器
        
        Args:
            config_path: 配置文件路径（JSON格式），如果为None则使用默认规则
        """
        self.category_keywords = self._load_config(
            config_path, 
            'category_keywords', 
            self.DEFAULT_CATEGORY_KEYWORDS
        )
        self.tag_keywords = self._load_config(
            config_path,
            'tag_keywords',
            self.DEFAULT_TAG_KEYWORDS
        )
    
    def _load_config(self, config_path: str, key: str, default: dict) -> dict:
        """加载配置文件
        
        Args:
            config_path: 配置文件路径
            key: 配置项键名
            default: 默认值
            
        Returns:
            dict: 配置字典
        """
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return config.get(key, default)
            except (json.JSONDecodeError, IOError) as e:
                # 配置加载失败时使用默认值
                import logging
                logging.getLogger('classifier').warning(
                    f'加载配置文件失败，使用默认规则: {e}'
                )
        return default.copy()
    
    def reload_config(self, config_path: str = None):
        """重新加载配置
        
        Args:
            config_path: 配置文件路径
        """
        self.category_keywords = self._load_config(
            config_path,
            'category_keywords',
            self.DEFAULT_CATEGORY_KEYWORDS
        )
        self.tag_keywords = self._load_config(
            config_path,
            'tag_keywords',
            self.DEFAULT_TAG_KEYWORDS
        )
        
    def classify_bookmark(self, bookmark):
        """对书签进行分类"""
        # 合并标题和URL进行分析
        text = (bookmark.title + bookmark.url).lower()
        
        # 根据关键词匹配分类
        scores = {}
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            scores[category] = score
            
        # 选择得分最高的分类
        if scores:
            best_category = max(scores, key=scores.get)
            if scores[best_category] > 0:
                bookmark.category = best_category
                
        return bookmark
        
    def tag_bookmark(self, bookmark):
        """为书签打标签"""
        # 合并标题和URL进行分析
        text = (bookmark.title + bookmark.url).lower()
        
        # 根据关键词匹配标签
        tags = []
        for tag, keywords in self.tag_keywords.items():
            if any(keyword in text for keyword in keywords):
                tags.append(tag)
                
        # 提取URL中的域名作为标签
        domain_match = re.search(r'https?://(?:www\.)?([^/]+)', bookmark.url)
        if domain_match:
            domain = domain_match.group(1).replace('www.', '')
            # 移除常见的顶级域名
            domain = re.sub(r'\.(com|org|net|edu|gov|cn|io)$', '', domain)
            if domain and domain not in tags:
                tags.append(domain)
                
        bookmark.tags = tags
        return bookmark