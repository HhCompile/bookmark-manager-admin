#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
程序入口文件（演示用途）

功能：
1. 演示书签管理系统的基本功能
2. 展示如何创建书签、自动打标和分类
3. 用于快速验证系统功能

注意：实际 Web 服务入口是 run.py
"""

import sys
import os

# 将项目根目录添加到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.bookmark import Bookmark
from app.controllers.bookmark_controller import BookmarkManager
from app.services.storage_service import Storage
from app.services.classifier_service import Classifier


def main():
    """主函数 - 演示书签管理功能"""
    # 创建书签管理器
    manager = BookmarkManager()
    
    # 创建分类器
    classifier = Classifier()
    
    # 创建存储接口
    storage = Storage('bookmarks.json')
    
    # 添加示例书签
    sample_bookmarks = [
        Bookmark('https://github.com/python/cpython', 'Python官方源码仓库'),
        Bookmark('https://www.python.org/doc/', 'Python官方文档'),
        Bookmark('https://news.ycombinator.com', 'Hacker News技术新闻'),
        Bookmark('https://www.youtube.com/watch?v=dQw4w9WgXcQ', '搞笑视频合集'),
    ]
    
    # 处理书签
    for bookmark in sample_bookmarks:
        # 自动打标
        classifier.tag_bookmark(bookmark)
        # 自动分类
        classifier.classify_bookmark(bookmark)
        # 添加到管理器
        manager.add_bookmark(bookmark)
    
    # 保存书签
    storage.save_bookmarks(manager.get_bookmarks())
    
    # 显示结果
    print("处理后的书签:")
    for bookmark in manager.get_bookmarks():
        print(f"- {bookmark}")


if __name__ == '__main__':
    main()
