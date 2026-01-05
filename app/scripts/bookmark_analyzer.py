#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
书签数据智能分析与建议生成工具

功能：
1. 数据解析：读取并解析书签JSON数据
2. 别名建议：生成2-3个简洁、有意义的别名
3. 归类建议：分析主题类别
4. 分组建议：建议归属的分组名称
5. 输出格式：支持JSON、CSV和格式化文本输出

使用方法：
python bookmark_analyzer.py <input_file> [output_file] [output_format]

参数：
  input_file: 输入的书签JSON文件路径
  output_file: 输出文件路径（可选，默认：bookmark_suggestions.json）
  output_format: 输出格式（可选，支持：json, csv, text，默认：json）

依赖：
- 无外部依赖，使用Python标准库
"""

import os
import sys
import json
import csv
import logging
import random
from datetime import datetime
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [analyzer] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('analyzer')


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


class AIClassifier(ABC):
    """
    AI分类器抽象基类，定义AI分类接口
    """
    
    @abstractmethod
    def classify(self, text: str, url: str) -> List[str]:
        """
        分类方法，返回类别列表
        
        Args:
            text: 文本内容
            url: URL地址
        
        Returns:
            类别列表
        """
        pass


class MockAIClassifier(AIClassifier):
    """
    模拟AI分类器，用于演示AI分类功能
    
    实际使用时可以替换为真实的AI API集成，如OpenAI、百度AI、阿里云AI等
    """
    
    def __init__(self, available_categories: List[str]):
        """
        初始化模拟AI分类器
        
        Args:
            available_categories: 可用的类别列表
        """
        self.available_categories = available_categories
    
    def classify(self, text: str, url: str) -> List[str]:
        """
        模拟AI分类
        
        Args:
            text: 文本内容
            url: URL地址
        
        Returns:
            类别列表
        """
        categories = []
        
        # 模拟基于关键词的AI分类逻辑
        # 这里可以替换为真实的AI API调用
        
        # 检查文本中的关键词
        text_lower = text.lower()
        url_lower = url.lower()
        
        # 基于文本特征的分类
        if any(keyword in text_lower or keyword in url_lower for keyword in ['ai', '人工智能', 'chatgpt', 'gpt']):
            categories.append('AI工具')
        
        if any(keyword in text_lower or keyword in url_lower for keyword in ['react', 'vue', 'js', 'javascript', 'typescript']):
            categories.append('前端开发')
        
        if 'github' in url_lower or '开源' in text_lower:
            categories.append('开源项目')
        
        if any(keyword in text_lower or keyword in url_lower for keyword in ['ui', '设计', '图标', '组件']):
            categories.append('UI设计')
        
        if any(keyword in text_lower or keyword in url_lower for keyword in ['blog', '教程', '文章']):
            categories.append('技术博客')
        
        if 'docs' in url_lower or '文档' in text_lower:
            categories.append('文档')
        
        if any(keyword in text_lower or keyword in url_lower for keyword in ['命令', 'cli', 'terminal', 'git']):
            categories.append('命令工具')
        
        if 'nas' in text_lower or '群晖' in text_lower:
            categories.append('NAS')
        
        # 模拟AI模型的置信度评分，随机选择1-2个额外类别
        if len(categories) < 3:
            remaining_categories = [cat for cat in self.available_categories if cat not in categories]
            if remaining_categories:
                # 随机选择0-1个额外类别，模拟AI的不确定性
                extra_categories = random.sample(remaining_categories, k=random.randint(0, 1))
                categories.extend(extra_categories)
        
        return categories[:3]  # 限制最多3个类别


class BookmarkAnalyzer(ScriptInterface):
    """
    书签分析器类，用于生成书签建议，实现ScriptInterface接口
    """
    
    def __init__(self):
        super().__init__()
        self.name = "analyzer"
        self.description = "AI智能书签分析器，生成别名、分类和分组建议"
        self.version = "1.0.0"
        self.author = "自动生成"
        
        # 配置参数
        self.config = {
            'use_ai_classification': True,  # 是否使用AI分类
            'ai_confidence_threshold': 0.7,  # AI分类置信度阈值
            'hybrid_classification': True,  # 是否使用混合分类（AI + 规则）
            'max_suggestions': 3,  # 每个类型的最大建议数量
            'output_format': 'json'  # 默认输出格式
        }
        
        # 预定义的分类关键词映射
        self.category_keywords = {
            'AI工具': ['ai', '人工智能', 'chatgpt', 'gpt', '大模型', '机器学习'],
            '开发工具': ['dev', '工具', '开发', 'editor', 'ide', '编译器'],
            'UI设计': ['ui', '设计', '图标', '插图', '组件', '框架'],
            '前端开发': ['前端', 'react', 'vue', 'js', 'javascript', 'typescript'],
            '后端开发': ['后端', 'server', 'api', 'database', '数据库', '服务器'],
            '移动开发': ['移动', 'android', 'ios', 'flutter', 'react native'],
            '开源项目': ['github', '开源', 'repository', '仓库', '项目'],
            '技术博客': ['博客', 'blog', '教程', '文章', '指南'],
            '文档': ['docs', '文档', 'api', '参考', '手册'],
            '云服务': ['云', 'cloud', 'aws', 'azure', '阿里云', '腾讯云'],
            'NAS': ['nas', '群晖', '存储', '服务器'],
            '命令工具': ['命令', 'cli', 'terminal', '终端', 'git', 'linux']
        }
        
        # 预定义的分组建议映射
        self.group_suggestions = {
            'AI工具': ['AI工具', '人工智能', 'AI'],
            '开发工具': ['开发工具', '工具集', '开发资源'],
            'UI设计': ['UI设计', '设计资源', 'UI组件'],
            '前端开发': ['前端开发', '前端框架', 'Web开发'],
            '后端开发': ['后端开发', '服务器', '数据库'],
            '移动开发': ['移动开发', 'APP开发'],
            '开源项目': ['开源项目', 'GitHub项目'],
            '技术博客': ['技术博客', '学习资源', '教程'],
            '文档': ['技术文档', 'API文档'],
            '云服务': ['云服务', '云计算'],
            'NAS': ['NAS', '存储'],
            '命令工具': ['命令工具', '终端工具', 'Git工具']
        }
        
        # 初始化AI分类器
        self.available_categories = list(self.category_keywords.keys())
        self.ai_classifier = MockAIClassifier(self.available_categories)
    
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
                    "usage": "python bookmark_analyzer.py <input_file> [output_file] [output_format]"
                }
            
            # 解析位置参数
            input_file = args[0]
            
            # 解析可选参数
            output_file = 'bookmark_suggestions.json'
            output_format = self.config['output_format']
            
            # 处理命令行参数
            for i in range(1, len(args)):
                arg = args[i]
                if arg.startswith('--'):
                    # 处理标志参数
                    if arg == '--no-ai':
                        self.config['use_ai_classification'] = False
                    elif arg == '--no-hybrid':
                        self.config['hybrid_classification'] = False
                elif '.' in arg:
                    # 处理文件路径参数
                    if arg.lower().endswith('.json') or arg.lower().endswith('.csv') or arg.lower().endswith('.txt'):
                        output_file = arg
                    else:
                        output_format = arg.lower()
                else:
                    # 处理输出格式参数
                    output_format = arg.lower()
            
            # 验证输出格式
            if output_format not in ['json', 'csv', 'text']:
                return {
                    "status": "error",
                    "message": f"不支持的输出格式: {output_format}",
                    "data": {"supported_formats": ['json', 'csv', 'text']}
                }
            
            # 更新配置
            self.config['output_format'] = output_format
            
            logger.info(f"使用配置: AI分类={self.config['use_ai_classification']}, 混合分类={self.config['hybrid_classification']}")
            
            # 加载书签
            bookmarks = self.load_bookmarks(input_file)
            if not bookmarks:
                return {
                    "status": "error",
                    "message": "未加载到书签数据",
                    "data": {"input_file": input_file}
                }
            
            # 分析书签
            results = self.analyze_bookmarks(bookmarks)
            
            # 写入输出
            if output_format == 'json':
                self.write_json_output(results, output_file)
            elif output_format == 'csv':
                # 确保输出文件以.csv结尾
                if not output_file.lower().endswith('.csv'):
                    output_file = output_file + '.csv'
                self.write_csv_output(results, output_file)
            elif output_format == 'text':
                # 确保输出文件以.txt结尾
                if not output_file.lower().endswith('.txt'):
                    output_file = output_file + '.txt'
                self.write_text_output(results, output_file)
            
            logger.info("书签分析完成！")
            
            return {
                "status": "success",
                "message": "书签分析成功",
                "data": {
                    "input_file": input_file,
                    "output_file": output_file,
                    "output_format": output_format,
                    "bookmark_count": len(bookmarks),
                    "suggestion_count": len(results),
                    "output_path": os.path.abspath(output_file)
                }
            }
            
        except FileNotFoundError as e:
            error_msg = f"文件未找到: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg
            }
        except json.JSONDecodeError as e:
            error_msg = f"JSON解析错误: {str(e)}"
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
    
    def load_bookmarks(self, file_path: str) -> List[Dict[str, Any]]:
        """
        加载书签JSON文件
        
        Args:
            file_path: JSON文件路径
        
        Returns:
            书签数据列表
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                bookmarks = json.load(f)
            logger.info(f"成功加载 {len(bookmarks)} 个书签")
            return bookmarks
        except FileNotFoundError:
            logger.error(f"文件未找到: {file_path}")
            return []
        except json.JSONDecodeError:
            logger.error(f"JSON解析错误: {file_path}")
            return []
        except Exception as e:
            logger.error(f"加载文件失败: {str(e)}")
            return []
    
    def generate_alias_suggestions(self, bookmark: Dict[str, Any]) -> List[str]:
        """
        生成别名建议
        
        Args:
            bookmark: 书签数据
        
        Returns:
            别名建议列表
        """
        title = bookmark.get('title', '')
        url = bookmark.get('url', '')
        alias_suggestions = []
        
        # 方法1：使用标题的简洁版本
        clean_title = self._clean_title(title)
        if clean_title and clean_title != title:
            alias_suggestions.append(clean_title)
        
        # 方法2：使用URL域名或路径的关键部分
        domain_part = self._extract_domain_keyword(url)
        if domain_part and domain_part not in alias_suggestions:
            alias_suggestions.append(domain_part)
        
        # 方法3：使用标题的核心关键词组合
        keyword_alias = self._extract_keyword_alias(title)
        if keyword_alias and keyword_alias not in alias_suggestions:
            alias_suggestions.append(keyword_alias)
        
        # 确保生成2-3个别名
        while len(alias_suggestions) < 2:
            # 如果不足，生成默认别名
            default_alias = f"{clean_title or '书签'}_{len(alias_suggestions) + 1}"
            alias_suggestions.append(default_alias)
        
        # 限制最多3个别名
        return alias_suggestions[:3]
    
    def _clean_title(self, title: str) -> str:
        """
        清理标题，生成简洁版本
        
        Args:
            title: 原始标题
        
        Returns:
            简洁标题
        """
        # 移除括号及内容
        import re
        clean = re.sub(r'\[.*?\]|\(.*?\)|\{.*?\}|【.*?】|（.*?）', '', title)
        # 移除特殊符号和多余空格
        clean = re.sub(r'[|_|+|@|#|!|?|,|;|:|\*|/]', ' ', clean)
        clean = re.sub(r'\s+', ' ', clean).strip()
        # 限制长度
        if len(clean) > 20:
            clean = clean[:20] + '...'
        return clean
    
    def _extract_domain_keyword(self, url: str) -> str:
        """
        从URL中提取域名关键词
        
        Args:
            url: 原始URL
        
        Returns:
            域名关键词
        """
        from urllib.parse import urlparse
        try:
            parsed = urlparse(url)
            # 获取域名
            domain = parsed.netloc
            # 移除www.和.com等后缀
            domain_parts = domain.split('.')
            if len(domain_parts) >= 2:
                # 提取核心域名
                if domain_parts[0] == 'www':
                    keyword = domain_parts[1]
                else:
                    keyword = domain_parts[0]
                # 处理特殊情况
                if keyword == 'github':
                    # 从路径中提取项目名
                    path_parts = parsed.path.strip('/').split('/')
                    if len(path_parts) >= 2:
                        keyword = f"{path_parts[0]}_{path_parts[1]}"
                return keyword
            return ''
        except Exception:
            return ''
    
    def _extract_keyword_alias(self, title: str) -> str:
        """
        从标题中提取关键词组合
        
        Args:
            title: 原始标题
        
        Returns:
            关键词组合
        """
        # 提取核心关键词
        import re
        # 移除特殊符号
        clean = re.sub(r'[^\w\u4e00-\u9fa5]', ' ', title)
        words = clean.split()
        # 提取最长的几个关键词
        if len(words) > 3:
            # 选择3个最长的词
            keywords = sorted(words, key=lambda x: len(x), reverse=True)[:3]
            return '_'.join(keywords)
        return ''
    
    def analyze_category(self, bookmark: Dict[str, Any]) -> List[str]:
        """
        分析书签类别，支持AI分类和传统关键词分类的混合模式
        
        Args:
            bookmark: 书签数据
        
        Returns:
            类别列表
        """
        title = bookmark.get('title', '')
        url = bookmark.get('url', '')
        categories = []
        
        # 获取传统关键词分类结果
        traditional_categories = self._traditional_keyword_classification(title, url)
        
        if self.config['use_ai_classification']:
            # 获取AI分类结果
            ai_categories = self._ai_classification(title, url)
            
            if self.config['hybrid_classification']:
                # 混合分类模式：合并AI和传统分类结果，去重
                categories = list(set(traditional_categories + ai_categories))
                logger.debug(f"混合分类结果: {categories}")
            else:
                # 纯AI分类模式
                categories = ai_categories
                logger.debug(f"纯AI分类结果: {categories}")
        else:
            # 纯传统分类模式
            categories = traditional_categories
            logger.debug(f"纯传统分类结果: {categories}")
        
        # 如果没有匹配到类别，添加默认类别
        if not categories:
            categories.append('其他')
        
        return categories[:3]  # 限制最多3个类别
    
    def _traditional_keyword_classification(self, title: str, url: str) -> List[str]:
        """
        传统关键词分类
        
        Args:
            title: 书签标题
            url: 书签URL
        
        Returns:
            类别列表
        """
        title_lower = title.lower()
        url_lower = url.lower()
        categories = []
        
        # 遍历关键词映射，查找匹配的类别
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in title_lower or keyword in url_lower:
                    categories.append(category)
                    break
        
        return categories
    
    def _ai_classification(self, title: str, url: str) -> List[str]:
        """
        AI分类
        
        Args:
            title: 书签标题
            url: 书签URL
        
        Returns:
            类别列表
        """
        try:
            # 调用AI分类器
            ai_categories = self.ai_classifier.classify(title, url)
            logger.debug(f"AI分类器返回: {ai_categories}")
            
            # 验证AI返回的类别是否在可用类别列表中
            valid_categories = [cat for cat in ai_categories if cat in self.available_categories]
            
            return valid_categories
        except Exception as e:
            logger.error(f"AI分类失败: {str(e)}")
            return []
    
    def suggest_groups(self, categories: List[str]) -> List[str]:
        """
        生成分组建议
        
        Args:
            categories: 类别列表
        
        Returns:
            分组建议列表
        """
        groups = []
        
        # 根据类别生成分组建议
        for category in categories:
            if category in self.group_suggestions:
                groups.extend(self.group_suggestions[category])
        
        # 去重
        groups = list(set(groups))
        
        # 如果没有生成分组建议，添加默认建议
        if not groups:
            groups = ['未分类', '其他']
        
        return groups[:3]  # 限制最多3个分组建议
    
    def analyze_bookmarks(self, bookmarks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        分析所有书签，生成建议
        
        Args:
            bookmarks: 书签列表
        
        Returns:
            带建议的书签列表
        """
        results = []
        
        for bookmark in bookmarks:
            # 生成别名建议
            alias_suggestions = self.generate_alias_suggestions(bookmark)
            
            # 分析类别
            categories = self.analyze_category(bookmark)
            
            # 生成分组建议
            group_suggestions = self.suggest_groups(categories)
            
            # 构建结果
            result = {
                'original': bookmark,
                'alias_suggestions': alias_suggestions,
                'category_suggestions': categories,
                'group_suggestions': group_suggestions,
                'analysis_date': datetime.now().isoformat()
            }
            results.append(result)
        
        return results
    
    def write_json_output(self, results: List[Dict[str, Any]], output_file: str):
        """
        写入JSON格式输出
        
        Args:
            results: 分析结果
            output_file: 输出文件路径
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2, sort_keys=True)
            logger.info(f"JSON结果已写入: {output_file}")
        except Exception as e:
            logger.error(f"写入JSON文件失败: {str(e)}")
    
    def write_csv_output(self, results: List[Dict[str, Any]], output_file: str):
        """
        写入CSV格式输出
        
        Args:
            results: 分析结果
            output_file: 输出文件路径
        """
        try:
            with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
                # 定义CSV字段
                fieldnames = [
                    'original_title', 'original_url', 'original_group', 
                    'alias_1', 'alias_2', 'alias_3',
                    'category_1', 'category_2', 'category_3',
                    'group_suggestion_1', 'group_suggestion_2', 'group_suggestion_3'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                # 写入表头
                writer.writeheader()
                
                # 写入数据
                for result in results:
                    original = result['original']
                    alias_suggestions = result['alias_suggestions']
                    category_suggestions = result['category_suggestions']
                    group_suggestions = result['group_suggestions']
                    
                    # 构建行数据
                    row = {
                        'original_title': original.get('title', ''),
                        'original_url': original.get('url', ''),
                        'original_group': original.get('group', ''),
                        'alias_1': alias_suggestions[0] if len(alias_suggestions) > 0 else '',
                        'alias_2': alias_suggestions[1] if len(alias_suggestions) > 1 else '',
                        'alias_3': alias_suggestions[2] if len(alias_suggestions) > 2 else '',
                        'category_1': category_suggestions[0] if len(category_suggestions) > 0 else '',
                        'category_2': category_suggestions[1] if len(category_suggestions) > 1 else '',
                        'category_3': category_suggestions[2] if len(category_suggestions) > 2 else '',
                        'group_suggestion_1': group_suggestions[0] if len(group_suggestions) > 0 else '',
                        'group_suggestion_2': group_suggestions[1] if len(group_suggestions) > 1 else '',
                        'group_suggestion_3': group_suggestions[2] if len(group_suggestions) > 2 else ''
                    }
                    writer.writerow(row)
            logger.info(f"CSV结果已写入: {output_file}")
        except Exception as e:
            logger.error(f"写入CSV文件失败: {str(e)}")
    
    def write_text_output(self, results: List[Dict[str, Any]], output_file: str):
        """
        写入格式化文本输出
        
        Args:
            results: 分析结果
            output_file: 输出文件路径
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for i, result in enumerate(results, 1):
                    original = result['original']
                    f.write(f"\n{'='*50}\n")
                    f.write(f"书签 {i}: {original.get('title', '无标题')}\n")
                    f.write(f"{'='*50}\n")
                    f.write(f"URL: {original.get('url', '无URL')}\n")
                    f.write(f"当前分组: {original.get('group', '无分组')}\n")
                    f.write(f"\n1. 别名建议:\n")
                    for j, alias in enumerate(result['alias_suggestions'], 1):
                        f.write(f"   {j}. {alias}\n")
                    f.write(f"\n2. 分类建议:\n")
                    for j, category in enumerate(result['category_suggestions'], 1):
                        f.write(f"   {j}. {category}\n")
                    f.write(f"\n3. 分组建议:\n")
                    for j, group in enumerate(result['group_suggestions'], 1):
                        f.write(f"   {j}. {group}\n")
            logger.info(f"文本结果已写入: {output_file}")
        except Exception as e:
            logger.error(f"写入文本文件失败: {str(e)}")


def main():
    """
    主函数
    """
    # 初始化分析器
    analyzer = BookmarkAnalyzer()
    
    # 执行脚本，将命令行参数传递给execute方法
    result = analyzer.execute(sys.argv[1:])
    
    # 输出结果
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 根据执行结果设置退出码
    if result.get("status") == "error":
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()