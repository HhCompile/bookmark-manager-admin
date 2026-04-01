#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证和授权模块

功能：
1. 简单的 API Key 认证
2. 多用户隔离支持
3. 审计日志记录

使用方法：
from app.utils.auth import require_auth, get_current_user

@app.route('/v1/bookmarks')
@require_auth
def get_bookmarks():
    user = get_current_user()
    # 获取该用户的书签...
"""

import os
import functools
import secrets
from flask import request, jsonify, g
import logging

# 配置
API_KEYS = {
    # 'api_key': 'user_id',
    os.environ.get('API_KEY', 'dev-key'): 'default_user'
}

# 审计日志
audit_logger = logging.getLogger('audit')


def generate_api_key() -> str:
    """生成新的 API Key
    
    Returns:
        API Key 字符串
    """
    return secrets.token_urlsafe(32)


def verify_api_key(api_key: str) -> str:
    """验证 API Key
    
    Args:
        api_key: API Key
        
    Returns:
        用户 ID，验证失败返回 None
    """
    return API_KEYS.get(api_key)


def require_auth(f):
    """认证装饰器
    
    需要 API Key 认证的端点使用该装饰器
    """
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        # 开发模式可以跳过认证
        if os.environ.get('DEBUG', 'False').lower() == 'true':
            g.user_id = 'dev_user'
            return f(*args, **kwargs)
        
        # 从请求头获取 API Key
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({'error': 'API Key is required'}), 401
        
        user_id = verify_api_key(api_key)
        
        if not user_id:
            return jsonify({'error': 'Invalid API Key'}), 401
        
        # 设置当前用户
        g.user_id = user_id
        
        # 记录审计日志
        audit_logger.info(
            f"User: {user_id}, "
            f"Method: {request.method}, "
            f"Path: {request.path}, "
            f"IP: {request.remote_addr}"
        )
        
        return f(*args, **kwargs)
    return decorated


def get_current_user() -> str:
    """获取当前用户 ID
    
    Returns:
        用户 ID
    """
    return getattr(g, 'user_id', 'anonymous')


def get_user_data_path(user_id: str) -> str:
    """获取用户数据文件路径
    
    Args:
        user_id: 用户 ID
        
    Returns:
        数据文件路径
    """
    # 用户数据存储在 user_data/{user_id}/bookmarks.json
    base_dir = 'user_data'
    user_dir = os.path.join(base_dir, user_id)
    
    # 确保目录存在
    os.makedirs(user_dir, exist_ok=True)
    
    return os.path.join(user_dir, 'bookmarks.json')
