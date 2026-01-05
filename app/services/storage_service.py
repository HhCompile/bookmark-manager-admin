"""
数据存储接口
"""

import json
from app.models.bookmark import Bookmark

class Storage:
    def __init__(self, file_path):
        self.file_path = file_path
        
    def save_bookmarks(self, bookmarks):
        """保存书签到文件"""
        data = []
        for bookmark in bookmarks:
            data.append({
                'url': bookmark.url,
                'title': bookmark.title,
                'tags': bookmark.tags,
                'category': bookmark.category
            })
            
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
    def load_bookmarks(self):
        """从文件加载书签"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            bookmarks = []
            for item in data:
                bookmark = Bookmark(
                    url=item['url'],
                    title=item['title'],
                    tags=item['tags'],
                    category=item['category']
                )
                bookmarks.append(bookmark)
                
            return bookmarks
        except FileNotFoundError:
            return []