"""
书签数据结构定义
"""

class Bookmark:
    def __init__(self, url, title, tags=None, category=None):
        self.url = url
        self.title = title
        self.tags = tags or []
        self.category = category
        
    def __str__(self):
        return f"Bookmark(url='{self.url}', title='{self.title}', tags={self.tags}, category='{self.category}')"
        
    def __repr__(self):
        return self.__str__()