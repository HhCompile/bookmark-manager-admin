"""
书签管理器核心逻辑
"""

from bookmark import Bookmark

class BookmarkManager:
    def __init__(self):
        self.bookmarks = []
        
    def add_bookmark(self, bookmark):
        """添加书签"""
        self.bookmarks.append(bookmark)
        
    def remove_bookmark(self, url):
        """根据URL删除书签"""
        self.bookmarks = [b for b in self.bookmarks if b.url != url]
        
    def get_bookmarks(self):
        """获取所有书签"""
        return self.bookmarks
        
    def get_bookmarks_by_category(self, category):
        """根据分类获取书签"""
        return [b for b in self.bookmarks if b.category == category]
        
    def get_bookmarks_by_tag(self, tag):
        """根据标签获取书签"""
        return [b for b in self.bookmarks if tag in b.tags]