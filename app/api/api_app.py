"""
Flask Web应用入口文件
"""

from flask import Flask, request, jsonify
from app.models.bookmark import Bookmark
from app.controllers.bookmark_controller import BookmarkManager
from app.services.storage_service import Storage
from app.services.classifier_service import Classifier
import os
import json
from werkzeug.utils import secure_filename
from bs4 import BeautifulSoup
from app.utils.script_manager import script_manager

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

# ------------------------------
# 新添加的API端点：脚本管理和新功能
# ------------------------------

@app.route('/scripts', methods=['GET'])
def get_scripts():
    """获取已注册的脚本列表"""
    result = script_manager.list_scripts()
    if result['status'] == 'success':
        return jsonify(result['data']), 200
    else:
        return jsonify({'error': result['message']}), 500

@app.route('/scripts/parse', methods=['POST'])
def parse_bookmarks():
    """上传HTML书签文件并解析为JSON"""
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
    
    # 生成输出文件名
    output_filename = f"parsed_{filename.replace('.html', '.json')}"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    
    # 运行解析器脚本
    result = script_manager.run_script('parser', [file_path, output_path])
    
    if result['status'] == 'success':
        # 读取解析结果
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                parsed_data = json.load(f)
            
            return jsonify({
                'message': 'Bookmarks parsed successfully',
                'filename': filename,
                'output_filename': output_filename,
                'parsed_count': result['data']['bookmark_count'],
                'parsed_data': parsed_data
            }), 201
        except Exception as e:
            return jsonify({'error': f'Failed to read parsed data: {str(e)}'}), 500
    else:
        return jsonify({'error': result['message']}), 500

@app.route('/scripts/analyze', methods=['POST'])
def analyze_bookmarks():
    """分析书签并生成建议"""
    data = request.get_json()
    
    if not data or 'bookmarks' not in data:
        return jsonify({'error': 'Bookmarks data is required'}), 400
    
    # 保存临时文件
    temp_input = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_bookmarks.json')
    with open(temp_input, 'w', encoding='utf-8') as f:
        json.dump(data['bookmarks'], f, ensure_ascii=False, indent=2)
    
    # 生成输出文件名
    temp_output = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_suggestions.json')
    
    # 运行分析器脚本
    result = script_manager.run_script('analyzer', [temp_input, temp_output])
    
    if result['status'] == 'success':
        # 读取分析结果
        try:
            with open(temp_output, 'r', encoding='utf-8') as f:
                suggestions = json.load(f)
            
            # 删除临时文件
            os.remove(temp_input)
            os.remove(temp_output)
            
            return jsonify({
                'message': 'Bookmarks analyzed successfully',
                'suggestion_count': result['data']['suggestion_count'],
                'suggestions': suggestions
            }), 200
        except Exception as e:
            return jsonify({'error': f'Failed to read analysis results: {str(e)}'}), 500
    else:
        # 删除临时文件
        if os.path.exists(temp_input):
            os.remove(temp_input)
        if os.path.exists(temp_output):
            os.remove(temp_output)
        
        return jsonify({'error': result['message']}), 500

@app.route('/scripts/process', methods=['POST'])
def process_bookmarks():
    """上传HTML书签文件，解析并分析生成建议"""
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
    
    # 生成中间文件名
    parsed_filename = f"parsed_{filename.replace('.html', '.json')}"
    parsed_path = os.path.join(app.config['UPLOAD_FOLDER'], parsed_filename)
    suggestions_filename = f"suggestions_{filename.replace('.html', '.json')}"
    suggestions_path = os.path.join(app.config['UPLOAD_FOLDER'], suggestions_filename)
    
    # 运行解析器脚本
    parse_result = script_manager.run_script('parser', [file_path, parsed_path])
    
    if parse_result['status'] != 'success':
        return jsonify({'error': f'Parsing failed: {parse_result["message"]}'}), 500
    
    # 运行分析器脚本
    analyze_result = script_manager.run_script('analyzer', [parsed_path, suggestions_path])
    
    if analyze_result['status'] != 'success':
        # 删除解析结果文件
        if os.path.exists(parsed_path):
            os.remove(parsed_path)
        return jsonify({'error': f'Analysis failed: {analyze_result["message"]}'}), 500
    
    # 读取最终结果
    try:
        with open(suggestions_path, 'r', encoding='utf-8') as f:
            suggestions = json.load(f)
        
        # 删除临时文件
        os.remove(parsed_path)
        os.remove(suggestions_path)
        
        return jsonify({
            'message': 'Bookmarks processed successfully',
            'filename': filename,
            'parsed_count': parse_result['data']['bookmark_count'],
            'suggestion_count': analyze_result['data']['suggestion_count'],
            'suggestions': suggestions
        }), 201
    except Exception as e:
        # 清理临时文件
        if os.path.exists(parsed_path):
            os.remove(parsed_path)
        if os.path.exists(suggestions_path):
            os.remove(suggestions_path)
        return jsonify({'error': f'Failed to read final results: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9001)