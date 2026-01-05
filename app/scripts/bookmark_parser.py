#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
书签HTML解析器

功能：
1. 读取并解析HTML书签文件
2. 提取书签的结构化数据，支持多层嵌套结构
3. 将HTML文档转换为规范的JSON数组格式
4. 支持别名信息存储和唯一性验证
5. 实现异常处理和日志记录
6. 支持深度嵌套结构的性能优化

使用方法：
python bookmark_parser.py <input_file> [output_file]

参数：
  input_file: 输入的HTML书签文件路径
  output_file: 输出的JSON文件路径（可选，默认：bookmarks.json）

依赖：
- beautifulsoup4
- lxml

配置项：
- MAX_NESTING_DEPTH: 最大嵌套深度限制，防止过深嵌套导致栈溢出
- MAX_ALIAS_LENGTH: 别名最大长度限制
- ALLOW_DUPLICATE_ALIASES: 是否允许重复别名

字段说明：
- title: 书签标题文本内容
- url: 书签链接地址
- date: 书签添加时间戳（ISO格式）
- tags: 书签所属文件夹路径（完整层级）
- group: 书签所属直接分组（最后一级文件夹）
- alias: 书签别名（可选，支持唯一性验证）
- description: 书签描述文本
"""

import os
import sys
import json
import logging
from datetime import datetime
from bs4 import BeautifulSoup
from typing import List, Dict, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [parser] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('parser')


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


class BookmarkParser(ScriptInterface):
    """
    书签HTML解析器类，实现ScriptInterface接口
    """
    
    def __init__(self):
        super().__init__()
        self.name = "parser"
        self.description = "HTML书签解析器，将HTML书签转换为JSON格式"
        self.version = "1.0.0"
        self.author = "自动生成"
        
        # 配置项
        self.config = {
            "MAX_NESTING_DEPTH": 20,  # 最大嵌套深度限制
            "MAX_ALIAS_LENGTH": 100,  # 别名最大长度限制
            "ALLOW_DUPLICATE_ALIASES": False,  # 是否允许重复别名
            "MAX_FILE_SIZE": 10 * 1024 * 1024  # 最大文件大小限制（10MB）
        }
    
    def configure(self, config: Dict[str, Any]) -> bool:
        """
        配置脚本
        
        Args:
            config: 配置参数
        
        Returns:
            bool: 配置是否成功
        """
        try:
            self.config.update(config)
            logger.info(f"配置更新: {list(config.keys())}")
            return True
        except Exception as e:
            logger.error(f"配置失败: {str(e)}")
            return False
    
    def execute(self, args: List[str]) -> Dict[str, Any]:
        """
        执行脚本
        
        Args:
            args: 命令行参数
        
        Returns:
            Dict: 执行结果，包含status和data字段
        """
        try:
            # 解析命令行参数
            if len(args) < 1:
                return {
                    "status": "error",
                    "message": "缺少输入文件参数",
                    "usage": "python bookmark_parser.py <input_file> [output_file]"
                }
            
            input_file = args[0]
            output_file = args[1] if len(args) > 1 else 'bookmarks.json'
            
            # 验证输入文件存在且为HTML文件
            if not os.path.exists(input_file):
                return {
                    "status": "error",
                    "message": f"输入文件不存在: {input_file}"
                }
            
            if not input_file.lower().endswith('.html'):
                logger.warning(f"输入文件不是HTML格式: {input_file}")
            
            # 读取HTML文件，限制文件大小以提高安全性
            with open(input_file, 'r', encoding='utf-8') as f:
                html_content = f.read(self.config["MAX_FILE_SIZE"])
                if len(html_content) == self.config["MAX_FILE_SIZE"]:
                    logger.warning(f"输入文件超过最大限制 {self.config['MAX_FILE_SIZE']} bytes，可能被截断")
            logger.info(f"成功读取文件: {input_file}")
            
            # 解析书签
            bookmarks = self.parse_bookmarks(html_content)
            
            # 写入JSON输出
            self.write_json_output(bookmarks, output_file)
            
            logger.info("书签解析完成")
            
            return {
                "status": "success",
                "message": "书签解析成功",
                "data": {
                    "input_file": input_file,
                    "output_file": output_file,
                    "bookmark_count": len(bookmarks),
                    "output_path": os.path.abspath(output_file)
                }
            }
            
        except FileNotFoundError:
            error_msg = f"文件未找到: {args[0] if args else '未知文件'}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg
            }
        except UnicodeDecodeError:
            error_msg = f"文件编码错误，请确保是UTF-8编码: {args[0] if args else '未知文件'}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg
            }
        except Exception as e:
            error_msg = f"程序执行失败: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg
            }
    
    def parse_bookmarks(self, html_content):
        """
        解析HTML书签内容
        
        Args:
            html_content (str): HTML书签文件内容
        
        Returns:
            list: 解析后的书签数组
        """
        try:
            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(html_content, 'lxml')
            logger.info("HTML内容解析成功")
            
            # 查找根目录的DL标签
            root_dl = soup.find('dl')
            if not root_dl:
                logger.error("未找到书签根目录DL标签")
                return []
            
            # 解析书签结构
            bookmarks = []
            self.parse_dl_element(root_dl, bookmarks, [], 0)
            
            # 验证别名唯一性
            if not self.config["ALLOW_DUPLICATE_ALIASES"]:
                self.validate_alias_uniqueness(bookmarks)
            
            logger.info(f"成功解析 {len(bookmarks)} 个书签")
            return bookmarks
            
        except RecursionError:
            logger.error(f"解析失败：书签嵌套深度超过最大限制 {self.config['MAX_NESTING_DEPTH']}")
            return []
        except Exception as e:
            logger.error(f"解析HTML内容失败: {str(e)}")
            return []

    def parse_dl_element(self, dl_element, bookmarks, current_tags, current_depth):
        """
        递归解析DL元素，提取书签和文件夹
        
        Args:
            dl_element (bs4.element.Tag): DL标签元素
            bookmarks (list): 书签数组
            current_tags (list): 当前文件夹路径
            current_depth (int): 当前嵌套深度
        """
        # 检查嵌套深度限制
        if current_depth > self.config["MAX_NESTING_DEPTH"]:
            logger.warning(f"跳过深度为 {current_depth} 的文件夹，超过最大限制")
            return
        
        # 遍历所有子元素
        for child in dl_element.children:
            # 跳过文本节点和空节点
            if child.name is None:
                continue
            
            # 处理文件夹节点 <DT><H3>...</H3></DT>
            if child.name == 'dt':
                h3_tag = child.find('h3')
                if h3_tag:
                    # 获取文件夹名称和属性
                    folder_name = h3_tag.get_text(strip=True)
                    new_tags = current_tags.copy()
                    new_tags.append(folder_name)
                    
                    # 查找文件夹下的DL子元素
                    next_dl = child.find_next_sibling('dl')
                    if next_dl:
                        # 递归处理子文件夹，深度+1
                        self.parse_dl_element(next_dl, bookmarks, new_tags, current_depth + 1)
            
            # 处理书签节点 <DT><A>...</A></DT>
            a_tag = child.find('a')
            if a_tag:
                bookmark = self.parse_bookmark_element(a_tag, current_tags)
                if bookmark:
                    bookmarks.append(bookmark)

    def parse_bookmark_element(self, a_tag, tags):
        """
        解析单个书签元素
        
        Args:
            a_tag (bs4.element.Tag): A标签元素
            tags (list): 书签所属文件夹路径
        
        Returns:
            dict: 解析后的书签对象
        """
        try:
            # 确定书签所属分组
            # 如果tags不为空，group为最后一个标签（直接父文件夹）
            # 否则group为空字符串
            group = tags[-1] if tags else ""
            
            # 提取别名信息
            # 检查是否有别名属性或内容
            alias = a_tag.get('alias', '')
            if not alias:
                # 尝试从title属性或其他可能的字段中提取别名
                # 这里可以根据实际HTML格式扩展
                alias = ""
            
            # 验证别名长度
            if len(alias) > self.config["MAX_ALIAS_LENGTH"]:
                logger.warning(f"书签别名过长，已截断: {alias[:20]}...")
                alias = alias[:self.config["MAX_ALIAS_LENGTH"]]
            
            # 提取核心字段
            bookmark = {
                'title': a_tag.get_text(strip=True),
                'url': a_tag.get('href', ''),
                'date': self.parse_timestamp(a_tag.get('add_date')),
                'tags': tags.copy(),
                'group': group,
                'alias': alias,
                'description': a_tag.get('description', '')
            }
            
            # 验证必填字段
            if not bookmark['title'] and not bookmark['url']:
                logger.warning("跳过无效书签: 标题和URL都为空")
                return None
            
            # 验证URL格式（简单验证）
            if bookmark['url'] and not (bookmark['url'].startswith('http://') or 
                                       bookmark['url'].startswith('https://') or 
                                       bookmark['url'].startswith('chrome://')):
                logger.warning(f"书签URL格式可能无效: {bookmark['url']}")
            
            return bookmark
            
        except Exception as e:
            logger.error(f"解析书签元素失败: {str(e)}")
            return None

    def parse_timestamp(self, timestamp_str):
        """
        解析时间戳字符串
        
        Args:
            timestamp_str (str): 时间戳字符串
        
        Returns:
            str: 格式化后的时间字符串，或空字符串
        """
        if not timestamp_str:
            return ''
        
        try:
            # 将Unix时间戳转换为ISO格式
            timestamp = int(timestamp_str)
            dt = datetime.fromtimestamp(timestamp)
            return dt.isoformat()
        except ValueError:
            logger.warning(f"无效的时间戳: {timestamp_str}")
            return ''

    def validate_alias_uniqueness(self, bookmarks):
        """
        验证书签别名的唯一性
        
        Args:
            bookmarks (list): 书签数组
        """
        alias_set = set()
        for bookmark in bookmarks:
            alias = bookmark.get('alias', '')
            if alias:
                if alias in alias_set:
                    logger.warning(f"发现重复别名: {alias}")
                else:
                    alias_set.add(alias)

    def write_json_output(self, data, output_file):
        """
        将数据写入JSON文件
        
        Args:
            data (list): 书签数据
            output_file (str): 输出文件路径
        """
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                # 使用更高效的JSON序列化，禁用ensure_ascii以支持中文
                json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
            logger.info(f"JSON数据已成功写入: {output_file}")
        except PermissionError:
            raise PermissionError(f"写入文件失败：没有写入权限 {output_file}")
        except Exception as e:
            raise Exception(f"写入JSON文件失败: {str(e)}")


# 用于直接执行的主函数
if __name__ == "__main__":
    parser = BookmarkParser()
    result = parser.execute(sys.argv[1:])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 根据执行结果设置退出码
    if result["status"] == "error":
        sys.exit(1)
    sys.exit(0)