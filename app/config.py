#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用配置模块

功能：
1. 集中管理应用配置
2. 支持环境变量覆盖
3. 提供配置默认值

使用方法：
from app.config import config

# 访问配置
port = config.PORT
upload_folder = config.UPLOAD_FOLDER
"""

import os
from typing import Optional


class Config:
    """应用配置类"""
    
    # 应用信息
    APP_NAME = "Bookmark Manager"
    APP_VERSION = "1.0.0"
    API_VERSION = "v1"
    
    # 服务器配置
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 9001))
    DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')
    
    # 文件上传配置
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    ALLOWED_EXTENSIONS = {'html', 'htm'}
    
    # 数据存储配置
    DATA_FILE = os.environ.get('DATA_FILE', 'bookmarks.json')
    MAX_BACKUP_COUNT = int(os.environ.get('MAX_BACKUP_COUNT', 5))
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', None)  # None 表示只输出到控制台
    LOG_MAX_BYTES = int(os.environ.get('LOG_MAX_BYTES', 10 * 1024 * 1024))  # 10MB
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', 5))
    
    # 安全配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # CORS 配置
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # 性能配置
    MAX_BOOKMARKS_PER_BATCH = int(os.environ.get('MAX_BOOKMARKS_PER_BATCH', 1000))
    
    @classmethod
    def init_app(cls, app):
        """初始化 Flask 应用配置
        
        Args:
            app: Flask 应用实例
        """
        app.config['UPLOAD_FOLDER'] = cls.UPLOAD_FOLDER
        app.config['MAX_CONTENT_LENGTH'] = cls.MAX_CONTENT_LENGTH
        app.config['SECRET_KEY'] = cls.SECRET_KEY


# 全局配置实例
config = Config()


def get_api_prefix() -> str:
    """获取 API 版本前缀
    
    Returns:
        str: API 前缀，如 '/v1'
    """
    return f"/{config.API_VERSION}"


def get_full_api_path(endpoint: str) -> str:
    """获取完整的 API 路径
    
    Args:
        endpoint: 端点路径，如 '/bookmarks'
        
    Returns:
        str: 完整路径，如 '/v1/bookmarks'
    """
    prefix = get_api_prefix()
    if endpoint.startswith('/'):
        return f"{prefix}{endpoint}"
    return f"{prefix}/{endpoint}"
