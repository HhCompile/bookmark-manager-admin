#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
书签管理系统控制器

功能：
1. 统一管理和调用多个Python脚本
2. 支持脚本注册、卸载和动态调用
3. 标准化接口定义
4. 配置参数支持
5. 可靠的通信机制
6. 完整的错误处理和日志记录

使用方法：
python3 controller.py <command> [args]

命令列表：
  register <script_name> <script_path>: 注册脚本
  unregister <script_name>: 卸载脚本
  list: 列出所有已注册的脚本
  run <script_name> <args>: 运行指定脚本
  help: 显示帮助信息

示例：
python3 controller.py register parser bookmark_parser.py
python3 controller.py register analyzer bookmark_analyzer.py
python3 controller.py run parser bookmarks_2026_1_2.html parsed.json
python3 controller.py run analyzer parsed.json suggestions.json
"""

import os
import sys
import importlib.util
import logging
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(name)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('controller')


class ScriptInterface:
    """
    脚本接口基类，定义标准化接口
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
    
    def execute(self, args: List[str]) -> Dict[str, Any]:
        """
        执行脚本
        
        Args:
            args: 命令行参数
        
        Returns:
            Dict: 执行结果，包含status和data字段
        """
        return {"status": "success", "data": {}}
    
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


class ScriptController:
    """
    脚本控制器，负责管理和调用脚本
    """
    
    def __init__(self):
        self.scripts: Dict[str, Any] = {}
        self.config: Dict[str, Any] = {
            "log_level": "INFO",
            "default_output": "output.json",
            "max_script_count": 10
        }
    
    def register_script(self, name: str, script_path: str) -> Dict[str, Any]:
        """
        注册脚本
        
        Args:
            name: 脚本名称
            script_path: 脚本路径
        
        Returns:
            Dict: 注册结果
        """
        try:
            # 检查脚本文件是否存在
            if not os.path.exists(script_path):
                return {
                    "status": "error",
                    "message": f"脚本文件不存在: {script_path}"
                }
            
            # 检查脚本是否已注册
            if name in self.scripts:
                return {
                    "status": "error",
                    "message": f"脚本已注册: {name}"
                }
            
            # 动态导入脚本
            spec = importlib.util.spec_from_file_location(name, script_path)
            if spec is None:
                return {
                    "status": "error",
                    "message": f"无法加载脚本: {script_path}"
                }
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 查找脚本类
            script_class = None
            
            # 检查每个类，看它是否实现了ScriptInterface的关键方法
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type):
                    # 检查是否是类，并且不是ScriptInterface本身
                    if attr.__name__ != 'ScriptInterface':
                        # 检查是否实现了ScriptInterface的所有关键方法
                        has_configure = hasattr(attr, 'configure') and callable(getattr(attr, 'configure'))
                        has_execute = hasattr(attr, 'execute') and callable(getattr(attr, 'execute'))
                        has_get_info = hasattr(attr, 'get_info') and callable(getattr(attr, 'get_info'))
                        
                        if has_configure and has_execute and has_get_info:
                            # 找到一个实现了ScriptInterface关键方法的类
                            script_class = attr
                            break
            
            if script_class is None:
                return {
                    "status": "error",
                    "message": f"脚本未实现ScriptInterface接口: {script_path}"
                }
            
            # 创建脚本实例
            script_instance = script_class()
            
            # 注册脚本
            self.scripts[name] = {
                "instance": script_instance,
                "path": script_path,
                "registered_at": datetime.now().isoformat()
            }
            
            logger.info(f"脚本注册成功: {name} -> {script_path}")
            return {
                "status": "success",
                "message": f"脚本注册成功: {name}",
                "data": script_instance.get_info()
            }
            
        except Exception as e:
            logger.error(f"脚本注册失败: {str(e)}")
            return {
                "status": "error",
                "message": f"脚本注册失败: {str(e)}"
            }
    
    def unregister_script(self, name: str) -> Dict[str, Any]:
        """
        卸载脚本
        
        Args:
            name: 脚本名称
        
        Returns:
            Dict: 卸载结果
        """
        try:
            if name not in self.scripts:
                return {
                    "status": "error",
                    "message": f"脚本未注册: {name}"
                }
            
            del self.scripts[name]
            logger.info(f"脚本卸载成功: {name}")
            return {
                "status": "success",
                "message": f"脚本卸载成功: {name}"
            }
        except Exception as e:
            logger.error(f"脚本卸载失败: {str(e)}")
            return {
                "status": "error",
                "message": f"脚本卸载失败: {str(e)}"
            }
    
    def list_scripts(self) -> Dict[str, Any]:
        """
        列出所有已注册的脚本
        
        Returns:
            Dict: 脚本列表
        """
        try:
            scripts_list = []
            for name, script_data in self.scripts.items():
                script_info = script_data["instance"].get_info()
                script_info.update({
                    "path": script_data["path"],
                    "registered_at": script_data["registered_at"]
                })
                scripts_list.append(script_info)
            
            return {
                "status": "success",
                "data": {
                    "scripts": scripts_list,
                    "total": len(scripts_list)
                }
            }
        except Exception as e:
            logger.error(f"列出脚本失败: {str(e)}")
            return {
                "status": "error",
                "message": f"列出脚本失败: {str(e)}"
            }
    
    def run_script(self, name: str, args: List[str]) -> Dict[str, Any]:
        """
        运行指定脚本
        
        Args:
            name: 脚本名称
            args: 命令行参数
        
        Returns:
            Dict: 执行结果
        """
        try:
            if name not in self.scripts:
                return {
                    "status": "error",
                    "message": f"脚本未注册: {name}"
                }
            
            script_instance = self.scripts[name]["instance"]
            
            logger.info(f"开始执行脚本: {name}，参数: {args}")
            result = script_instance.execute(args)
            
            logger.info(f"脚本执行完成: {name}，结果: {result.get('status')}")
            return result
        except Exception as e:
            logger.error(f"脚本执行失败: {str(e)}")
            return {
                "status": "error",
                "message": f"脚本执行失败: {str(e)}"
            }
    
    def configure(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        配置控制器
        
        Args:
            config: 配置参数
        
        Returns:
            Dict: 配置结果
        """
        try:
            self.config.update(config)
            # 更新日志级别
            if "log_level" in config:
                logger.setLevel(config["log_level"])
            
            logger.info(f"控制器配置更新: {list(config.keys())}")
            return {
                "status": "success",
                "message": "控制器配置更新成功"
            }
        except Exception as e:
            logger.error(f"配置控制器失败: {str(e)}")
            return {
                "status": "error",
                "message": f"配置控制器失败: {str(e)}"
            }


def main():
    """
    主函数
    """
    controller = ScriptController()
    
    # 解析命令行参数
    if len(sys.argv) < 2:
        print("使用方法: python3 controller.py <command> [args]")
        print("命令列表:")
        print("  register <script_name> <script_path>: 注册脚本")
        print("  unregister <script_name>: 卸载脚本")
        print("  list: 列出所有已注册的脚本")
        print("  run <script_name> <args>: 运行指定脚本")
        print("  help: 显示帮助信息")
        sys.exit(0)
    
    command = sys.argv[1].lower()
    
    if command == "register":
        if len(sys.argv) < 4:
            print("使用方法: python3 controller.py register <script_name> <script_path>")
            sys.exit(1)
        name = sys.argv[2]
        path = sys.argv[3]
        result = controller.register_script(name, path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == "unregister":
        if len(sys.argv) < 3:
            print("使用方法: python3 controller.py unregister <script_name>")
            sys.exit(1)
        name = sys.argv[2]
        result = controller.unregister_script(name)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == "list":
        result = controller.list_scripts()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == "run":
        if len(sys.argv) < 3:
            print("使用方法: python3 controller.py run <script_name> [args]")
            sys.exit(1)
        name = sys.argv[2]
        args = sys.argv[3:]
        result = controller.run_script(name, args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == "help":
        print("书签管理系统控制器")
        print("使用方法: python3 controller.py <command> [args]")
        print("命令列表:")
        print("  register <script_name> <script_path>: 注册脚本")
        print("  unregister <script_name>: 卸载脚本")
        print("  list: 列出所有已注册的脚本")
        print("  run <script_name> <args>: 运行指定脚本")
        print("  help: 显示帮助信息")
    
    else:
        print(f"未知命令: {command}")
        print("使用 'python3 controller.py help' 查看帮助")
        sys.exit(1)


if __name__ == "__main__":
    main()