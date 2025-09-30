"""
程序入口文件
"""

from bookmark import Bookmark
from bookmark_manager import BookmarkManager
from storage import Storage
from classifier import Classifier

def main():
    # 创建书签管理器
    manager = BookmarkManager()
    
    # 创建分类器
    classifier = Classifier()
    
    # 创建存储接口
    storage = Storage('bookmarks.json')
    
    # 添加示例书签
    sample_bookmarks = [
        Bookmark('https://github.com/python/cpython', 'Python官方源码仓库'),
        Bookmark('https://www.python.org/doc/', 'Python官方文档'),
        Bookmark('https://news.ycombinator.com', 'Hacker News技术新闻'),
        Bookmark('https://www.youtube.com/watch?v=dQw4w9WgXcQ', '搞笑视频合集'),
    ]
    
    # 处理书签
    for bookmark in sample_bookmarks:
        # 自动打标
        classifier.tag_bookmark(bookmark)
        # 自动分类
        classifier.classify_bookmark(bookmark)
        # 添加到管理器
        manager.add_bookmark(bookmark)
    
    # 保存书签
    storage.save_bookmarks(manager.get_bookmarks())
    
    # 显示结果
    print("处理后的书签:")
    for bookmark in manager.get_bookmarks():
        print(f"- {bookmark}")

if __name__ == '__main__':
    main()