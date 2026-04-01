#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国际化（i18n）支持模块

功能：
1. 多语言错误消息支持
2. 自动根据请求头选择语言

使用方法：
from app.utils.i18n import gettext as _, get_locale

# 获取翻译
error_msg = _('Bookmark not found')

# 设置语言
set_locale('zh')
"""

from flask import request


# 翻译字典
TRANSLATIONS = {
    'zh': {
        'Bookmark not found': '书签未找到',
        'Bookmark already exists': '书签已存在',
        'Invalid URL format': '无效的 URL 格式',
        'URL is required': 'URL 是必需的',
        'Failed to read parsed data': '读取解析数据失败',
        'Failed to analyze bookmarks': '分析书签失败',
        'Failed to process bookmarks': '处理书签失败',
        'Too many bookmarks': '书签数量过多',
        'Bookmarks must be an array': '书签必须是数组',
        'No file provided': '未提供文件',
        'No file selected': '未选择文件',
        'Invalid file type': '无效的文件类型',
        'File too large': '文件太大',
        'Parsing failed': '解析失败',
        'Analysis failed': '分析失败',
        'Bookmark processed successfully': '书签处理成功',
        'Bookmark deleted successfully': '书签删除成功',
        'Bookmark updated successfully': '书签更新成功',
    },
    'en': {
        # 默认英语，无需翻译
    }
}

# 默认语言
DEFAULT_LOCALE = 'en'
_current_locale = DEFAULT_LOCALE


def set_locale(locale: str):
    """设置当前语言
    
    Args:
        locale: 语言代码（如 'zh', 'en'）
    """
    global _current_locale
    _current_locale = locale if locale in TRANSLATIONS else DEFAULT_LOCALE


def get_locale() -> str:
    """获取当前语言
    
    Returns:
        语言代码
    """
    # 尝试从请求头获取语言
    try:
        from flask import request
        if request:
            # 从 Accept-Language 头获取
            accept_lang = request.headers.get('Accept-Language', '')
            if 'zh' in accept_lang:
                return 'zh'
    except:
        pass
    
    return _current_locale


def gettext(message: str) -> str:
    """获取翻译后的消息
    
    Args:
        message: 原始消息
        
    Returns:
        翻译后的消息，如果没有翻译则返回原始消息
    """
    locale = get_locale()
    if locale == DEFAULT_LOCALE:
        return message
    
    return TRANSLATIONS.get(locale, {}).get(message, message)


# 简写
_ = gettext
