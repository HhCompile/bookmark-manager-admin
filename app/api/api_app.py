#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask Web应用入口文件
"""

import os
import sys
import json
import logging
import threading
import uuid
import atexit
import time
import psutil
import fcntl
from datetime import datetime
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename
from bs4 import BeautifulSoup
import pytz

# 将项目根目录添加到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.models.bookmark import Bookmark
from app.controllers.bookmark_controller import BookmarkManager
from app.services.storage_service import Storage
from app.services.classifier_service import Classifier
from app.utils.script_manager import script_manager
from app.utils.serializers import bookmark_to_dict, bookmarks_to_dict_list
from app.config import config

# ==================== 日志配置 ====================
def setup_logging():
    """配置日志系统"""
    log_handlers = [logging.StreamHandler()]
    
    # 如果配置了日志文件，添加文件处理器（带轮转）
    if config.LOG_FILE:
        file_handler = RotatingFileHandler(
            config.LOG_FILE,
            maxBytes=config.LOG_MAX_BYTES,
            backupCount=config.LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(name)s] %(message)s'
        ))
        log_handlers.append(file_handler)
    
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL.upper(), logging.INFO),
        format='%(asctime)s - %(levelname)s - [%(name)s] %(message)s',
        handlers=log_handlers
    )
    return logging.getLogger('api')

logger = setup_logging()

# ==================== Flask 应用配置 ====================
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH
app.config['JSON_SORT_KEYS'] = False
app.config['SECRET_KEY'] = config.SECRET_KEY

# 启用 CORS
CORS(app, resources={
    r"/health": {"origins": config.CORS_ORIGINS},
    r"/v1/*": {"origins": config.CORS_ORIGINS},
})

# 配置限流器
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["1000 per hour", "100 per minute"],
    storage_uri="memory://",
)

# 确保上传文件夹存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 审计日志
audit_logger = logging.getLogger('audit')
audit_logger.setLevel(logging.INFO)
if config.LOG_FILE:
    audit_handler = RotatingFileHandler(
        config.LOG_FILE.replace('.log', '_audit.log'),
        maxBytes=config.LOG_MAX_BYTES,
        backupCount=config.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    audit_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(message)s'
    ))
    audit_logger.addHandler(audit_handler)

# ==================== 请求追踪中间件 ====================
@app.before_request
def before_request():
    """在每个请求前执行：记录请求开始时间和请求 ID"""
    g.start_time = time.time()
    # 获取或生成请求 ID
    g.request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())[:8]
    logger.info(f"[{g.request_id}] {request.method} {request.path} - Started")


@app.after_request
def after_request(response):
    """在每个请求后执行：记录响应时间和状态码"""
    if hasattr(g, 'start_time'):
        duration = time.time() - g.start_time
        status_code = response.status_code
        logger.info(f"[{g.request_id}] {request.method} {request.path} - "
                   f"Completed {status_code} in {duration:.3f}s")
        # 添加请求 ID 到响应头
        response.headers['X-Request-ID'] = g.request_id
    return response


# API 版本前缀
API_PREFIX = f"/{config.API_VERSION}"

# ==================== 线程安全锁 ====================
# 用于保护共享状态（书签数据）
bookmarks_lock = threading.Lock()

# ==================== 初始化组件 ====================
manager = BookmarkManager()
classifier = Classifier()
storage = Storage(config.DATA_FILE)

# 在启动时加载已有书签
manager.bookmarks = storage.load_bookmarks()
logger.info(f"应用启动（版本 {config.APP_VERSION}），已加载 {len(manager.bookmarks)} 个书签")

def parse_and_process_bookmarks(file_path):
    """解析并处理书签文件（线程安全）"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'lxml')
        bookmarks = []
        
        # 查找所有书签链接
        links = soup.find_all('a', href=True)
        
        with bookmarks_lock:
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
                
                # 添加到管理器（自动检查重复）
                if not manager.has_bookmark(url):
                    manager.add_bookmark(bookmark)
                    bookmarks.append(bookmark)
            
            # 保存到文件
            storage.save_bookmarks(manager.get_bookmarks())
        
        logger.info(f"成功处理 {len(bookmarks)} 个书签")
        return len(bookmarks)
    except Exception as e:
        logger.error(f"处理书签文件出错: {e}")
        return 0

@app.route(f'{API_PREFIX}/health', methods=['GET'])
@limiter.exempt  # 健康检查不受限流限制
def health_check():
    """健康检查接口
    
    返回应用状态、书签数量、存储状态、系统资源等信息
    """
    with bookmarks_lock:
        bookmark_count = len(manager.get_bookmarks())
    
    # 检查存储文件状态
    storage_exists = os.path.exists(config.DATA_FILE)
    storage_size = os.path.getsize(config.DATA_FILE) if storage_exists else 0
    
    # 检查磁盘空间
    disk = psutil.disk_usage(os.path.dirname(config.DATA_FILE) or '.')
    disk_free_percent = (disk.free / disk.total) * 100
    
    # 检查内存使用
    memory = psutil.virtual_memory()
    
    return jsonify({
        'status': 'ok',
        'version': config.APP_VERSION,
        'api_version': config.API_VERSION,
        'bookmarks': {
            'count': bookmark_count,
            'storage_exists': storage_exists,
            'storage_size_bytes': storage_size
        },
        'system': {
            'disk': {
                'total_gb': round(disk.total / (1024**3), 2),
                'free_gb': round(disk.free / (1024**3), 2),
                'free_percent': round(disk_free_percent, 2),
                'healthy': disk_free_percent > 10  # 磁盘空间低于10%为不健康
            },
            'memory': {
                'total_gb': round(memory.total / (1024**3), 2),
                'available_gb': round(memory.available / (1024**3), 2),
                'percent': memory.percent
            }
        },
        'config': {
            'upload_folder': app.config['UPLOAD_FOLDER'],
            'max_content_length_mb': app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024)
        }
    })

@app.route(f'{API_PREFIX}/bookmark', methods=['POST'])
def add_bookmark():
    """添加单个书签并自动处理（线程安全）"""
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400
    
    url = data['url']
    
    # 验证 URL 格式
    if not _is_valid_url(url):
        return jsonify({'error': 'Invalid URL format'}), 400
    
    # 验证和清理输入数据
    title = _sanitize_string(data.get('title', ''), max_length=Constants.MAX_TITLE_LENGTH)
    tags = _sanitize_tags(data.get('tags', []))
    category = _sanitize_string(data.get('category'), max_length=Constants.MAX_CATEGORY_LENGTH) if data.get('category') else None
    
    with bookmarks_lock:
        # 检查重复
        if manager.has_bookmark(url):
            return jsonify({
                'error': 'Bookmark already exists',
                'url': url
            }), 409
        
        # 创建书签对象
        bookmark = Bookmark(
            url=url,
            title=title,
            tags=tags,
            category=category
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
        'bookmark': bookmark_to_dict(bookmark)
    }), 201

def _process_bookmark_item(item, manager, classifier):
    """处理单个书签条目（内部函数，不持有锁）
    
    Args:
        item: 书签数据字典
        manager: BookmarkManager 实例
        classifier: Classifier 实例
        
    Returns:
        tuple: (success: bool, result: dict or None)
    """
    # 验证条目类型
    if not isinstance(item, dict):
        return False, None
    
    url = item.get('url', '')
    
    # 验证 URL
    if not url or not _is_valid_url(url):
        return False, None
    
    # 检查重复
    if manager.has_bookmark(url):
        return False, None
    
    # 清理输入数据
    title = _sanitize_string(item.get('title', ''), max_length=200)
    tags = _sanitize_tags(item.get('tags', []))
    category = _sanitize_string(item.get('category'), max_length=50) if item.get('category') else None
    
    # 创建书签对象
    bookmark = Bookmark(
        url=url,
        title=title,
        tags=tags,
        category=category
    )
    
    # 自动打标和分类
    classifier.tag_bookmark(bookmark)
    classifier.classify_bookmark(bookmark)
    
    # 添加到管理器
    manager.add_bookmark(bookmark)
    
    return True, bookmark_to_dict(bookmark)


@app.route(f'{API_PREFIX}/bookmarks/batch', methods=['POST'])
def add_bookmarks_batch():
    """批量添加书签并自动处理（线程安全）"""
    data = request.get_json()
    
    if not data or 'bookmarks' not in data:
        return jsonify({'error': 'Bookmarks array is required'}), 400
    
    # 验证 bookmarks 是列表类型
    bookmarks_list = data['bookmarks']
    if not isinstance(bookmarks_list, list):
        return jsonify({'error': 'Bookmarks must be an array'}), 400
    
    # 限制批量处理数量（防止过大请求）
    if len(bookmarks_list) > Constants.MAX_BOOKMARKS_PER_BATCH:
        return jsonify({'error': f'Too many bookmarks. Maximum is {Constants.MAX_BOOKMARKS_PER_BATCH} per request'}), 400
    
    processed_bookmarks = []
    skipped_count = 0
    
    with bookmarks_lock:
        for item in bookmarks_list:
            success, result = _process_bookmark_item(item, manager, classifier)
            if success:
                processed_bookmarks.append(result)
            else:
                skipped_count += 1
        
        # 保存到文件
        storage.save_bookmarks(manager.get_bookmarks())
    
    return jsonify({
        'message': f'Successfully processed {len(processed_bookmarks)} bookmarks, skipped {skipped_count}',
        'processed': len(processed_bookmarks),
        'skipped': skipped_count,
        'bookmarks': processed_bookmarks
    }), 201

@app.route(f'{API_PREFIX}/bookmarks', methods=['GET'])
def get_bookmarks():
    """获取所有书签（支持分页）
    
    Query Parameters:
        page: 页码（从1开始，默认1）
        limit: 每页数量（默认20，最大100）
        category: 按分类筛选
        tag: 按标签筛选
    """
    # 获取分页参数
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
    except ValueError:
        return jsonify({'error': 'Invalid pagination parameters'}), 400
    
    # 限制分页范围
    page = max(1, page)
    limit = max(1, min(limit, Constants.MAX_PAGE_SIZE))  # 限制最大页大小
    
    # 获取筛选参数
    filter_category = request.args.get('category')
    filter_tag = request.args.get('tag')
    
    with bookmarks_lock:
        bookmarks = manager.get_bookmarks()
        
        # 应用筛选
        if filter_category:
            bookmarks = [b for b in bookmarks if b.category == filter_category]
        if filter_tag:
            bookmarks = [b for b in bookmarks if filter_tag in b.tags]
        
        total = len(bookmarks)
        
        # 分页
        start = (page - 1) * limit
        end = start + limit
        paginated_bookmarks = bookmarks[start:end]
        
        # 使用序列化工具转换
        result = bookmarks_to_dict_list(paginated_bookmarks)
    
    return jsonify({
        'bookmarks': result,
        'pagination': {
            'page': page,
            'limit': limit,
            'total': total,
            'pages': (total + limit - 1) // limit if limit > 0 else 0
        }
    })

@app.route(f'{API_PREFIX}/bookmarks/category/<category>', methods=['GET'])
def get_bookmarks_by_category(category):
    """根据分类获取书签（线程安全）"""
    with bookmarks_lock:
        bookmarks = manager.get_bookmarks_by_category(category)
        result = bookmarks_to_dict_list(bookmarks)
    return jsonify({'bookmarks': result})


@app.route(f'{API_PREFIX}/bookmarks/tag/<tag>', methods=['GET'])
def get_bookmarks_by_tag(tag):
    """根据标签获取书签（线程安全）"""
    with bookmarks_lock:
        bookmarks = manager.get_bookmarks_by_tag(tag)
        result = bookmarks_to_dict_list(bookmarks)
    return jsonify({'bookmarks': result})

@app.route(f'{API_PREFIX}/bookmark/delete', methods=['POST'])
def delete_bookmark():
    """根据URL删除书签（使用POST请求体，避免URL编码问题）
    
    Request Body:
        url: 要删除的书签URL
    """
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required in request body'}), 400
    
    url = data['url']
    
    with bookmarks_lock:
        original_count = len(manager.get_bookmarks())
        manager.remove_bookmark(url)
        
        # 保存到文件
        storage.save_bookmarks(manager.get_bookmarks())
        
        new_count = len(manager.get_bookmarks())
    
    if new_count < original_count:
        return jsonify({'message': 'Bookmark deleted successfully', 'url': url}), 200
    else:
        return jsonify({'error': 'Bookmark not found', 'url': url}), 404

@app.route(f'{API_PREFIX}/bookmark/update', methods=['POST'])
def update_bookmark():
    """根据URL更新书签（使用POST请求体，避免URL编码问题）
    
    Request Body:
        url: 要更新的书签URL（必需）
        title: 新标题（可选）
        tags: 新标签（可选）
        category: 新分类（可选）
        reprocess: 是否重新自动分类（可选）
    """
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required in request body'}), 400
    
    url = data['url']
    
    with bookmarks_lock:
        # 查找现有书签
        bookmarks = manager.get_bookmarks()
        bookmark = None
        for b in bookmarks:
            if b.url == url:
                bookmark = b
                break
        
        if not bookmark:
            return jsonify({'error': 'Bookmark not found', 'url': url}), 404
        
        # 更新书签属性（使用清理函数）
        if 'title' in data:
            bookmark.title = _sanitize_string(data['title'], max_length=Constants.MAX_TITLE_LENGTH)
        if 'tags' in data:
            bookmark.tags = _sanitize_tags(data['tags'])
        if 'category' in data:
            bookmark.category = _sanitize_string(data['category'], max_length=Constants.MAX_CATEGORY_LENGTH) if data['category'] else None
        
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

@app.route(f'{API_PREFIX}/bookmark/upload', methods=['POST'])
def upload_bookmark_file():
    """上传书签文件并处理（自动清理上传文件）"""
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
    
    # 检查文件大小（手动检查，因为 MAX_CONTENT_LENGTH 已经在 Flask 层面处理）
    try:
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # 重置文件指针
    except (OSError, IOError):
        # 如果文件不支持 seek 操作，尝试从 content_length 获取
        file_size = request.content_length or 0
    
    if file_size > app.config['MAX_CONTENT_LENGTH']:
        return jsonify({'error': f'File too large. Maximum size is {app.config["MAX_CONTENT_LENGTH"] // (1024*1024)}MB'}), 413
    
    # 使用唯一文件名保存，避免冲突
    filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        file.save(file_path)
        
        # 解析并处理书签文件
        processed_count = parse_and_process_bookmarks(file_path)
        
        return jsonify({
            'message': f'File uploaded and processed successfully. {processed_count} bookmarks added.',
            'filename': filename,
            'processed_count': processed_count
        }), 201
    finally:
        # 确保上传文件被清理
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.warning(f'Failed to remove uploaded file: {e}')

# ------------------------------
# 新添加的API端点：脚本管理和新功能
# ------------------------------

@app.route(f'{API_PREFIX}/scripts', methods=['GET'])
def get_scripts():
    """获取已注册的脚本列表"""
    result = script_manager.list_scripts()
    if result['status'] == 'success':
        return jsonify(result['data']), 200
    else:
        return jsonify({'error': result['message']}), 500

@app.route(f'{API_PREFIX}/scripts/parse', methods=['POST'])
def parse_bookmarks():
    """上传HTML书签文件并解析为JSON（自动清理临时文件）"""
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
    
    # 使用唯一文件名，避免并发冲突
    unique_id = uuid.uuid4().hex
    filename = f"{unique_id}_{secure_filename(file.filename)}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    output_filename = f"parsed_{unique_id}.json"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    
    try:
        # 保存文件
        file.save(file_path)
        
        # 运行解析器脚本
        result = script_manager.run_script('parser', [file_path, output_path])
        
        if result['status'] == 'success':
            # 读取解析结果
            try:
                with open(output_path, 'r', encoding='utf-8') as f:
                    parsed_data = json.load(f)
                
                return jsonify({
                    'message': 'Bookmarks parsed successfully',
                    'parsed_count': result['data']['bookmark_count'],
                    'parsed_data': parsed_data
                }), 201
            except Exception:
                logger.exception('Failed to read parsed data')
                return jsonify({'error': 'Failed to read parsed data'}), 500
        else:
            return jsonify({'error': result['message']}), 500
    finally:
        # 清理临时文件
        for path in [file_path, output_path]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as e:
                    logger.warning(f'Failed to remove temp file: {e}')

@app.route(f'{API_PREFIX}/scripts/analyze', methods=['POST'])
def analyze_bookmarks():
    """分析书签并生成建议（使用唯一临时文件名，自动清理）"""
    data = request.get_json()
    
    if not data or 'bookmarks' not in data:
        return jsonify({'error': 'Bookmarks data is required'}), 400
    
    # 使用唯一文件名，避免并发冲突
    unique_id = uuid.uuid4().hex
    temp_input = os.path.join(app.config['UPLOAD_FOLDER'], f'temp_bookmarks_{unique_id}.json')
    temp_output = os.path.join(app.config['UPLOAD_FOLDER'], f'temp_suggestions_{unique_id}.json')
    
    try:
        # 保存临时文件
        with open(temp_input, 'w', encoding='utf-8') as f:
            json.dump(data['bookmarks'], f, ensure_ascii=False, indent=2)
        
        # 运行分析器脚本
        result = script_manager.run_script('analyzer', [temp_input, temp_output])
        
        if result['status'] == 'success':
            # 读取分析结果
            with open(temp_output, 'r', encoding='utf-8') as f:
                suggestions = json.load(f)
            
            return jsonify({
                'message': 'Bookmarks analyzed successfully',
                'suggestion_count': result['data']['suggestion_count'],
                'suggestions': suggestions
            }), 200
        else:
            return jsonify({'error': result['message']}), 500
    except Exception:
        logger.exception('Analysis failed')
        return jsonify({'error': 'Failed to analyze bookmarks'}), 500
    finally:
        # 确保临时文件被清理
        for path in [temp_input, temp_output]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as e:
                    logger.warning(f'Failed to remove temp file: {e}')

@app.route(f'{API_PREFIX}/scripts/process', methods=['POST'])
def process_bookmarks():
    """上传HTML书签文件，解析并分析生成建议（自动清理所有临时文件）"""
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
    
    # 使用唯一文件名，避免并发冲突
    unique_id = uuid.uuid4().hex
    filename = f"{unique_id}_{secure_filename(file.filename)}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    parsed_path = os.path.join(app.config['UPLOAD_FOLDER'], f'parsed_{unique_id}.json')
    suggestions_path = os.path.join(app.config['UPLOAD_FOLDER'], f'suggestions_{unique_id}.json')
    
    try:
        # 保存文件
        file.save(file_path)
        
        # 运行解析器脚本
        parse_result = script_manager.run_script('parser', [file_path, parsed_path])
        
        if parse_result['status'] != 'success':
            return jsonify({'error': f'Parsing failed: {parse_result["message"]}'}), 500
        
        # 运行分析器脚本
        analyze_result = script_manager.run_script('analyzer', [parsed_path, suggestions_path])
        
        if analyze_result['status'] != 'success':
            return jsonify({'error': f'Analysis failed: {analyze_result["message"]}'}), 500
        
        # 读取最终结果
        with open(suggestions_path, 'r', encoding='utf-8') as f:
            suggestions = json.load(f)
        
        return jsonify({
            'message': 'Bookmarks processed successfully',
            'parsed_count': parse_result['data']['bookmark_count'],
            'suggestion_count': analyze_result['data']['suggestion_count'],
            'suggestions': suggestions
        }), 201
        
    except Exception:
        logger.exception('Processing failed')
        return jsonify({'error': 'Failed to process bookmarks'}), 500
    finally:
        # 确保所有临时文件被清理
        for path in [file_path, parsed_path, suggestions_path]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as e:
                    logger.warning(f'Failed to remove temp file: {e}')

def _is_valid_url(url):
    """验证 URL 格式是否有效
    
    Args:
        url: 要验证的 URL
        
    Returns:
        bool: 是否有效
    """
    if not url or not isinstance(url, str):
        return False
    url = url.strip()
    return url.startswith(('http://', 'https://', 'chrome://'))


def _sanitize_string(value, max_length=100):
    """清理字符串输入
    
    Args:
        value: 输入值
        max_length: 最大长度
        
    Returns:
        str: 清理后的字符串
    """
    if not isinstance(value, str):
        value = str(value) if value else ''
    value = value.strip()
    return value[:max_length] if value else ''


def _sanitize_tags(tags):
    """清理标签数组
    
    Args:
        tags: 标签数组
        
    Returns:
        list: 清理后的标签列表
    """
    if not isinstance(tags, list):
        return []
    # 限制标签数量
    if len(tags) > Constants.MAX_TAG_COUNT:
        tags = tags[:Constants.MAX_TAG_COUNT]
    # 过滤非字符串元素，清理并去重
    result = []
    seen = set()
    for tag in tags:
        if isinstance(tag, str):
            cleaned = tag.strip()[:Constants.MAX_TAG_LENGTH]  # 限制单个标签长度
            if cleaned and cleaned not in seen:
                result.append(cleaned)
                seen.add(cleaned)
    return result


def _save_on_exit():
    """应用退出时保存数据"""
    try:
        with bookmarks_lock:
            storage.save_bookmarks(manager.get_bookmarks())
            logger.info(f"应用退出，已保存 {len(manager.get_bookmarks())} 个书签")
    except Exception as e:
        logger.error(f"退出保存失败: {e}")


# 注册退出处理器
atexit.register(_save_on_exit)


# 常量定义
class Constants:
    """API 常量定义"""
    # 批量处理限制
    MAX_BOOKMARKS_PER_BATCH = 1000
    
    # 分页限制
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # 字符串长度限制
    MAX_TITLE_LENGTH = 200
    MAX_TAG_LENGTH = 50
    MAX_CATEGORY_LENGTH = 50
    MAX_TAG_COUNT = 100


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9001)