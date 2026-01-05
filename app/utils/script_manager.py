#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
脚本管理器，用于集成和管理多个Python脚本

功能：
1. 初始化ScriptController
2. 注册和管理脚本
3. 提供统一的调用接口
4. 支持配置管理
"""

import os
import logging
from app.scripts.controller import ScriptController
from typing import Dict, Any, List

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [script_manager] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('script_manager')


class ScriptManager:
    """
    脚本管理器类，用于集成和管理多个Python脚本
    """
    
    def __init__(self):
        self.controller = ScriptController()
        self.scripts_dir = os.path.dirname(os.path.abspath(__file__))
        self._register_default_scripts()
    
    def _register_default_scripts(self):
        """
        注册默认脚本
        """
        # 获取脚本目录路径
        scripts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts')
        
        scripts_to_register = [
            ('parser', os.path.join(scripts_dir, 'bookmark_parser.py')),
            ('analyzer', os.path.join(scripts_dir, 'bookmark_analyzer.py'))
        ]
        
        for script_name, script_path in scripts_to_register:
            if os.path.exists(script_path):
                result = self.controller.register_script(script_name, script_path)
                if result['status'] == 'success':
                    logger.info(f"默认脚本注册成功: {script_name}")
                else:
                    logger.error(f"默认脚本注册失败: {script_name}, 原因: {result['message']}")
            else:
                logger.error(f"脚本文件不存在: {script_path}")
    
    def run_script(self, script_name: str, args: List[str]) -> Dict[str, Any]:
        """
        运行指定脚本
        
        Args:
            script_name: 脚本名称
            args: 脚本参数
            
        Returns:
            脚本执行结果
        """
        return self.controller.run_script(script_name, args)
    
    def list_scripts(self) -> Dict[str, Any]:
        """
        列出所有已注册的脚本
        
        Returns:
            脚本列表
        """
        return self.controller.list_scripts()
    
    def register_script(self, name: str, path: str) -> Dict[str, Any]:
        """
        注册新脚本
        
        Args:
            name: 脚本名称
            path: 脚本路径
            
        Returns:
            注册结果
        """
        return self.controller.register_script(name, path)
    
    def unregister_script(self, name: str) -> Dict[str, Any]:
        """
        卸载脚本
        
        Args:
            name: 脚本名称
            
        Returns:
            卸载结果
        """
        return self.controller.unregister_script(name)
    
    def configure(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        配置脚本管理器
        
        Args:
            config: 配置参数
            
        Returns:
            配置结果
        """
        return self.controller.configure(config)


# 全局脚本管理器实例
script_manager = ScriptManager()
