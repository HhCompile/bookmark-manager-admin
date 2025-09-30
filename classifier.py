"""
自动打标和分类算法
"""

import re
from bookmark import Bookmark

class Classifier:
    def __init__(self):
        # 定义关键词分类规则
        self.category_keywords = {
            '技术': ['python', 'javascript', 'java', '编程', '开发', 'github', 'git', 'linux', 'docker'],
            '新闻': ['新闻', '时事', '政治', '社会', '财经'],
            '娱乐': ['电影', '音乐', '游戏', '娱乐', '视频'],
            '学习': ['教程', '学习', '课程', '教育', '学术'],
            '生活': ['生活', '健康', '美食', '旅行', '家居']
        }
        
        # 定义标签关键词
        self.tag_keywords = {
            '编程': ['python', 'javascript', 'java', 'code', '编程'],
            '开源': ['github', '开源', 'source', 'code'],
            '教程': ['教程', 'guide', 'tutorial', 'howto'],
            '文档': ['文档', 'doc', 'document', '手册']
        }
        
    def classify_bookmark(self, bookmark):
        """对书签进行分类"""
        # 合并标题和URL进行分析
        text = (bookmark.title + bookmark.url).lower()
        
        # 根据关键词匹配分类
        scores = {}
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            scores[category] = score
            
        # 选择得分最高的分类
        if scores:
            best_category = max(scores, key=scores.get)
            if scores[best_category] > 0:
                bookmark.category = best_category
                
        return bookmark
        
    def tag_bookmark(self, bookmark):
        """为书签打标签"""
        # 合并标题和URL进行分析
        text = (bookmark.title + bookmark.url).lower()
        
        # 根据关键词匹配标签
        tags = []
        for tag, keywords in self.tag_keywords.items():
            if any(keyword in text for keyword in keywords):
                tags.append(tag)
                
        # 提取URL中的域名作为标签
        domain_match = re.search(r'https?://(?:www\.)?([^/]+)', bookmark.url)
        if domain_match:
            domain = domain_match.group(1).replace('www.', '')
            # 移除常见的顶级域名
            domain = re.sub(r'\.(com|org|net|edu|gov|cn|io)$', '', domain)
            if domain and domain not in tags:
                tags.append(domain)
                
        bookmark.tags = tags
        return bookmark