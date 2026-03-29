#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
脚本接口定义模块

功能：
1. 定义 ScriptInterface 基类
2. 提供标准化的脚本接口规范
3. 供所有脚本实现时继承使用
"""

from typing import Dict, Any, List
from abc import ABC, abstractmethod


class ScriptInterface(ABC):
    """
    脚本接口基类，定义标准化接口
    
    所有脚本都应继承此类并实现其抽象方法
    """
    
    def __init__(self):
        self.name = ""
        self.description = ""
        self.version = "1.0.0"
        self.author = ""
    
    def configure(self, config: Dict[str, Any]) -> bool:
        """
        配置脚本
        
        Args:
            config: 配置参数
        
        Returns:
            bool: 配置是否成功
        """
        return True
    
    @abstractmethod
    def execute(self, args: List[str]) -> Dict[str, Any]:
        """
        执行脚本
        
        Args:
            args: 命令行参数
        
        Returns:
            Dict: 执行结果，包含status和data字段
        """
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """
        获取脚本信息
        
        Returns:
            Dict: 脚本信息
        """
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author
        }
