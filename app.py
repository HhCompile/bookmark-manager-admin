"""
Flask Web应用入口文件
"""

from flask import Flask, request, jsonify
from bookmark import Bookmark
from bookmark_manager import BookmarkManager
from storage import Storage
from classifier import Classifier
import os
from werkzeug.utils import secure_filename
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 确保上传文件夹存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 初始化组件
manager = BookmarkManager()
classifier = Classifier()
storage = Storage('bookmarks.json')

# 在启动时加载已有书签
manager.bookmarks = storage.load_bookmarks()

def parse_and_process_bookmarks(file_path):
    """解析并处理书签文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        bookmarks = []
        
        # 查找所有书签链接
        links = soup.find_all('a', href=True)
        
        for link in links:
            url = link['href']
            title = link.get_text(strip=True)
            
            # 创建书签对象
            bookmark = Bookmark(
                url=url,
                title=title,
                tags=[],
                category=None
            )
            
            # 自动打标和分类
            classifier.tag_bookmark(bookmark)
            classifier.classify_bookmark(bookmark)
            
            # 添加到管理器
            manager.add_bookmark(bookmark)
            bookmarks.append(bookmark)
        
        # 保存到文件
        storage.save_bookmarks(manager.get_bookmarks())
        
        return len(bookmarks)
    except Exception as e:
        print(f"Error processing bookmarks file: {e}")
        return 0

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({'status': 'ok'})

@app.route('/bookmark', methods=['POST'])
def add_bookmark():
    """添加单个书签并自动处理"""
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400
    
    # 创建书签对象
    bookmark = Bookmark(
        url=data['url'],
        title=data.get('title', ''),
        tags=data.get('tags', []),
        category=data.get('category')
    )
    
    # 自动打标和分类
    classifier.tag_bookmark(bookmark)
    classifier.classify_bookmark(bookmark)
    
    # 添加到管理器
    manager.add_bookmark(bookmark)
    
    # 保存到文件
    storage.save_bookmarks(manager.get_bookmarks())
    
    return jsonify({
        'message': 'Bookmark processed successfully',
        'bookmark': {
            'url': bookmark.url,
            'title': bookmark.title,
            'tags': bookmark.tags,
            'category': bookmark.category
        }
    }), 201

@app.route('/bookmarks/batch', methods=['POST'])
def add_bookmarks_batch():
    """批量添加书签并自动处理"""
    data = request.get_json()
    
    if not data or 'bookmarks' not in data:
        return jsonify({'error': 'Bookmarks array is required'}), 400
    
    processed_bookmarks = []
    
    for item in data['bookmarks']:
        # 创建书签对象
        bookmark = Bookmark(
            url=item['url'],
            title=item.get('title', ''),
            tags=item.get('tags', []),
            category=item.get('category')
        )
        
        # 自动打标和分类
        classifier.tag_bookmark(bookmark)
        classifier.classify_bookmark(bookmark)
        
        # 添加到管理器
        manager.add_bookmark(bookmark)
        
        # 添加到结果列表
        processed_bookmarks.append({
            'url': bookmark.url,
            'title': bookmark.title,
            'tags': bookmark.tags,
            'category': bookmark.category
        })
    
    # 保存到文件
    storage.save_bookmarks(manager.get_bookmarks())
    
    return jsonify({
        'message': f'Successfully processed {len(processed_bookmarks)} bookmarks',
        'bookmarks': processed_bookmarks
    }), 201

@app.route('/bookmarks', methods=['GET'])
def get_bookmarks():
    """获取所有书签"""
    bookmarks = manager.get_bookmarks()
    result = []
    
    for bookmark in bookmarks:
        result.append({
            'url': bookmark.url,
            'title': bookmark.title,
            'tags': bookmark.tags,
            'category': bookmark.category
        })
        
    return jsonify({'bookmarks': result})

@app.route('/bookmarks/category/<category>', methods=['GET'])
def get_bookmarks_by_category(category):
    """根据分类获取书签"""
    bookmarks = manager.get_bookmarks_by_category(category)
    result = []
    
    for bookmark in bookmarks:
        result.append({
            'url': bookmark.url,
            'title': bookmark.title,
            'tags': bookmark.tags,
            'category': bookmark.category
        })
        
    return jsonify({'bookmarks': result})

@app.route('/bookmarks/tag/<tag>', methods=['GET'])
def get_bookmarks_by_tag(tag):
    """根据标签获取书签"""
    bookmarks = manager.get_bookmarks_by_tag(tag)
    result = []
    
    for bookmark in bookmarks:
        result.append({
            'url': bookmark.url,
            'title': bookmark.title,
            'tags': bookmark.tags,
            'category': bookmark.category
        })
        
    return jsonify({'bookmarks': result})

@app.route('/bookmark/<path:url>', methods=['DELETE'])
def delete_bookmark(url):
    """根据URL删除书签"""
    original_count = len(manager.get_bookmarks())
    manager.remove_bookmark(url)
    
    # 保存到文件
    storage.save_bookmarks(manager.get_bookmarks())
    
    new_count = len(manager.get_bookmarks())
    
    if new_count < original_count:
        return jsonify({'message': 'Bookmark deleted successfully'}), 200
    else:
        return jsonify({'message': 'Bookmark not found'}), 404

@app.route('/bookmark/<path:url>', methods=['PUT'])
def update_bookmark(url):
    """根据URL更新书签"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body is required'}), 400
    
    # 查找现有书签
    bookmarks = manager.get_bookmarks()
    bookmark = None
    for b in bookmarks:
        if b.url == url:
            bookmark = b
            break
    
    if not bookmark:
        return jsonify({'error': 'Bookmark not found'}), 404
    
    # 更新书签属性
    if 'title' in data:
        bookmark.title = data['title']
    if 'tags' in data:
        bookmark.tags = data['tags']
    if 'category' in data:
        bookmark.category = data['category']
    
    # 如果需要重新处理分类和标签
    if data.get('reprocess', False):
        classifier.tag_bookmark(bookmark)
        classifier.classify_bookmark(bookmark)
    
    # 保存到文件
    storage.save_bookmarks(manager.get_bookmarks())
    
    return jsonify({
        'message': 'Bookmark updated successfully',
        'bookmark': {
            'url': bookmark.url,
            'title': bookmark.title,
            'tags': bookmark.tags,
            'category': bookmark.category
        }
    }), 200

@app.route('/bookmark/upload', methods=['POST'])
def upload_bookmark_file():
    """上传书签文件并处理"""
    # 检查是否有文件上传
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    # 检查文件名
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # 检查文件类型
    if not file.filename.endswith('.html'):
        return jsonify({'error': 'Invalid file type. Only HTML files are allowed.'}), 400
    
    # 保存文件
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    # 解析并处理书签文件
    processed_count = parse_and_process_bookmarks(file_path)
    
    return jsonify({
        'message': f'File uploaded and processed successfully. {processed_count} bookmarks added.',
        'filename': filename,
        'file_path': file_path,
        'processed_count': processed_count
    }), 201

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9001)