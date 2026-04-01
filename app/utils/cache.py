#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存工具模块

功能：
1. 提供简单的内存缓存
2. 支持过期时间
3. 支持最大条目限制

使用方法：
from app.utils.cache import cache

# 设置缓存
cache.set('key', value, expire=3600)  # 1小时后过期

# 获取缓存
value = cache.get('key')

# 删除缓存
cache.delete('key')
"""

import time
import threading
from typing import Any, Optional
from functools import wraps


class MemoryCache:
    """简单的内存缓存实现"""
    
    def __init__(self, max_size=1000, default_expire=3600):
        """初始化缓存
        
        Args:
            max_size: 最大缓存条目数
            default_expire: 默认过期时间（秒）
        """
        self._cache = {}
        self._max_size = max_size
        self._default_expire = default_expire
        self._lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，不存在或已过期返回 None
        """
        with self._lock:
            if key not in self._cache:
                return None
            
            value, expire_time = self._cache[key]
            
            # 检查是否过期
            if expire_time is not None and time.time() > expire_time:
                del self._cache[key]
                return None
            
            return value
    
    def set(self, key: str, value: Any, expire: int = None):
        """设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            expire: 过期时间（秒），None 表示永不过期
        """
        with self._lock:
            # 清理过期条目
            self._cleanup()
            
            # 如果达到最大容量，删除最旧的条目
            if len(self._cache) >= self._max_size and key not in self._cache:
                oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][1] or float('inf'))
                del self._cache[oldest_key]
            
            # 计算过期时间
            if expire is None:
                expire = self._default_expire
            
            expire_time = time.time() + expire if expire > 0 else None
            self._cache[key] = (value, expire_time)
    
    def delete(self, key: str):
        """删除缓存
        
        Args:
            key: 缓存键
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
    
    def clear(self):
        """清空所有缓存"""
        with self._lock:
            self._cache.clear()
    
    def _cleanup(self):
        """清理过期条目"""
        now = time.time()
        expired_keys = [
            key for key, (_, expire_time) in self._cache.items()
            if expire_time is not None and now > expire_time
        ]
        for key in expired_keys:
            del self._cache[key]
    
    def get_stats(self) -> dict:
        """获取缓存统计信息
        
        Returns:
            统计信息字典
        """
        with self._lock:
            self._cleanup()
            return {
                'size': len(self._cache),
                'max_size': self._max_size,
                'usage_percent': round(len(self._cache) / self._max_size * 100, 2)
            }


def cached(cache_instance, expire=3600, key_func=None):
    """缓存装饰器
    
    Args:
        cache_instance: 缓存实例
        expire: 过期时间（秒）
        key_func: 自定义缓存键生成函数
        
    Returns:
        装饰器函数
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # 尝试获取缓存
            result = cache_instance.get(cache_key)
            if result is not None:
                return result
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache_instance.set(cache_key, result, expire)
            return result
        return wrapper
    return decorator


# 全局缓存实例
cache = MemoryCache(max_size=1000, default_expire=3600)
