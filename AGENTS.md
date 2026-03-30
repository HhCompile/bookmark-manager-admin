# AGENTS.md - AI Coding Agent Guide

> This file contains project-specific information for AI coding agents. It is written in Chinese to match the project's primary language in comments and documentation.

## 项目概述

这是一个基于 Flask 的书签管理器 Web 应用，用于管理和分类浏览器书签，支持自动打标、智能分类和书签文件导入功能。项目采用分层架构设计，具有良好的扩展性和可维护性。

### 核心功能

1. **书签管理**：添加、删除、查询、更新书签，支持批量操作
2. **智能功能**：基于关键词的自动打标和分类
3. **导入导出**：支持从浏览器导出的 HTML 书签文件导入
4. **脚本系统**：支持动态注册和管理功能脚本
5. **RESTful API**：完整的 API 接口设计

## 技术栈

| 技术/框架 | 版本 | 用途 |
|-----------|------|------|
| Python | 3.9+ | 开发语言 |
| Flask | 2.3.2 | Web 框架 |
| BeautifulSoup4 | 4.12.2 | HTML 解析 |
| JSON | - | 数据存储格式 |

## 项目结构

```
bookmark-manager-admin/
├── app/                          # 主应用目录
│   ├── api/                      # API 层，处理 HTTP 请求
│   │   ├── __init__.py
│   │   └── api_app.py            # Flask 应用实例和 API 路由
│   ├── controllers/              # 控制器层，处理业务逻辑
│   │   ├── __init__.py
│   │   └── bookmark_controller.py  # 书签管理控制器
│   ├── models/                   # 模型层，定义数据结构
│   │   ├── __init__.py
│   │   └── bookmark.py           # 书签数据模型
│   ├── scripts/                  # 脚本模块，处理特定功能
│   │   ├── __init__.py
│   │   ├── bookmark_analyzer.py  # 书签分析脚本
│   │   ├── bookmark_parser.py    # 书签解析脚本
│   │   └── controller.py         # 脚本控制器
│   ├── services/                 # 服务层，提供核心功能
│   │   ├── __init__.py
│   │   ├── classifier_service.py  # 自动分类服务
│   │   └── storage_service.py    # 存储服务
│   ├── utils/                    # 工具类，提供通用功能
│   │   ├── __init__.py
│   │   └── script_manager.py     # 脚本管理器
│   └── __init__.py
├── docs/                         # 文档目录
│   ├── DOCUMENTATION.md          # 文档索引
│   ├── INTEGRATION_GUIDE.md      # 新功能接入说明
│   ├── PROJECT_ISSUES_OPTIMIZED.md  # 优化后的项目问题分析
│   ├── PROJECT_STRUCTURE.md      # 完整的项目结构说明
│   └── REDUNDANT_CODE.md         # 冗余或未使用代码记录
├── uploads/                      # 上传文件目录
├── bookmarks.json                # 书签数据文件
├── openapi.yaml                  # API 文档 (OpenAPI 3.0)
├── requirements.txt              # 项目依赖
├── run.py                        # 应用入口
└── README.md                     # 项目概述
```

## 启动命令

### 开发环境

```bash
# 创建虚拟环境（推荐）
python3 -m venv venv_new

# 激活虚拟环境（Linux/macOS）
source venv_new/bin/activate

# 激活虚拟环境（Windows）
venv_new\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动应用
python3 run.py
```

应用将在 `http://127.0.0.1:9001` 启动。

### 生产部署

```bash
# 使用 Gunicorn 作为 WSGI 服务器
gunicorn -w 4 -b 0.0.0.0:9001 run:app
```

## 代码规范

### 文件命名规范

- 采用 **snake_case** 命名法，所有字母小写，单词之间用下划线分隔
- 文件名应清晰反映文件的功能和职责
- 避免使用缩写，除非是广为人知的缩写（如 api、db、ui 等）
- 模块文件使用单数形式，如 `bookmark.py` 而不是 `bookmarks.py`
- 工具类文件以 `_utils.py` 结尾
- 配置文件使用 `config.py` 或特定功能前缀

### 代码风格

- 使用 4 空格缩进
- 文件头部包含编码声明：`# -*- coding: utf-8 -*-`
- 类和方法使用中文文档字符串说明功能
- 导入顺序：标准库 → 第三方库 → 本地模块

### 文件头示例

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块功能说明
"""

import os
import sys
from flask import Flask
from app.models.bookmark import Bookmark


class BookmarkManager:
    """
    书签管理器核心逻辑
    """
    
    def add_bookmark(self, bookmark):
        """添加书签"""
        pass
```

### 脚本接口实现示例

```python
from app.scripts.interface import ScriptInterface

class MyScript(ScriptInterface):
    def __init__(self):
        super().__init__()
        self.name = "my_script"
        self.description = "脚本描述"
        
    def execute(self, args):
        # 实现脚本逻辑
        return {"status": "success", "data": {}}
```

## 架构说明

### 分层架构

| 层级 | 目录 | 职责 |
|------|------|------|
| API 层 | `app/api/` | 处理 HTTP 请求和响应，定义路由 |
| 控制器层 | `app/controllers/` | 业务逻辑控制，协调服务和模型 |
| 服务层 | `app/services/` | 核心业务逻辑实现 |
| 模型层 | `app/models/` | 数据结构和实体定义 |
| 脚本层 | `app/scripts/` | 独立功能脚本，可动态注册 |
| 工具层 | `app/utils/` | 通用工具函数和辅助类 |

### 核心类说明

#### Bookmark (app/models/bookmark.py)
数据模型，包含 url、title、tags、category 属性。

#### BookmarkManager (app/controllers/bookmark_controller.py)
控制器类，管理书签的增删改查，支持按分类和标签查询。

#### Classifier (app/services/classifier_service.py)
分类服务，基于关键词匹配实现自动打标和分类功能。

#### Storage (app/services/storage_service.py)
存储服务，负责书签数据的 JSON 文件持久化。

#### ScriptController (app/scripts/controller.py)
脚本控制器，支持脚本的动态注册、卸载和执行。

#### ScriptManager (app/utils/script_manager.py)
脚本管理器，封装 ScriptController，提供统一的脚本管理接口。

## API 端点

### 书签管理

| 方法 | 端点 | 功能 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/bookmarks` | 获取所有书签（支持分页和筛选） |
| POST | `/bookmark` | 添加单个书签（自动检查重复） |
| POST | `/bookmarks/batch` | 批量添加书签 |
| GET | `/bookmarks/category/<category>` | 按分类获取书签 |
| GET | `/bookmarks/tag/<tag>` | 按标签获取书签 |
| POST | `/bookmark/update` | 更新书签（新） |
| POST | `/bookmark/delete` | 删除书签（新） |
| POST | `/bookmark/upload` | 上传 HTML 书签文件 |

### 查询参数

- `/bookmarks` 支持以下查询参数：
  - `page`: 页码（默认 1）
  - `limit`: 每页数量（默认 20，最大 100）
  - `category`: 按分类筛选
  - `tag`: 按标签筛选

### 脚本管理

| 方法 | 端点 | 功能 |
|------|------|------|
| GET | `/scripts` | 获取已注册的脚本列表 |
| POST | `/scripts/parse` | 上传 HTML 书签文件并解析为 JSON |
| POST | `/scripts/analyze` | 分析书签并生成建议 |
| POST | `/scripts/process` | 上传 HTML 书签文件，解析并分析生成建议 |

## 脚本接口规范

新脚本需要实现 `ScriptInterface` 接口：

```python
class ScriptInterface:
    def __init__(self):
        self.name = ""
        self.description = ""
        self.version = "1.0.0"
        self.author = ""
    
    def configure(self, config: Dict[str, Any]) -> bool:
        """配置脚本"""
        return True
    
    def execute(self, args: List[str]) -> Dict[str, Any]:
        """执行脚本，返回 {"status": "success|error", "data": {...}}"""
        return {"status": "success", "data": {}}
    
    def get_info(self) -> Dict[str, Any]:
        """获取脚本信息"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author
        }
```

## 数据存储

- **数据文件**: `bookmarks.json`
- **存储格式**: JSON 数组
- **位置**: 项目根目录
- **上传目录**: `uploads/`

### 书签数据结构

```json
{
  "url": "https://github.com",
  "title": "GitHub",
  "tags": ["开发", "代码托管"],
  "category": "技术"
}
```

## 测试策略

当前项目没有正式的测试框架配置。建议添加：

1. **单元测试**: 使用 pytest 测试各个模块
2. **集成测试**: 测试 API 端点
3. **端到端测试**: 测试完整业务流程

### 推荐的测试命令（待实现）

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

## 安全注意事项

1. **无认证机制**: 当前 API 没有认证和授权，生产环境需要添加
2. **文件上传限制**: 最大 16MB，仅允许 HTML 文件
3. **文件路径处理**: 使用 `werkzeug.utils.secure_filename` 处理上传文件名
4. **输入验证**: 基本的 URL 和文件类型验证已实现

## 开发建议

1. **日志级别**: 在 `app/utils/script_manager.py` 和 `app/scripts/controller.py` 中修改 `level=logging.INFO` 调整日志级别
2. **分类规则**: 修改 `app/services/classifier_service.py` 中的关键词映射可扩展分类功能
3. **AI 集成**: `app/scripts/bookmark_analyzer.py` 中的 `MockAIClassifier` 可替换为真实的 AI API
4. **数据库存储**: 当前使用 JSON 文件，建议迁移到 PostgreSQL 或 SQLite 以支持更大规模数据

## 已修复的问题

### 第一轮修复
1. ✅ `main.py` - 已修复导入路径
2. ✅ `requirements.txt` - 添加 `lxml` 依赖
3. ✅ `ScriptInterface` - 提取到独立文件，消除重复代码
4. ✅ 日志配置 - 统一由应用入口管理
5. ✅ 重复书签检查 - 添加 `has_bookmark()` 方法
6. ✅ URL 路由问题 - 更新/删除改用 POST 请求体
7. ✅ JSON 存储 - 添加原子写入和备份机制
8. ✅ 分页支持 - 添加分页查询参数
9. ✅ `.gitignore` - 添加 Git 忽略文件

### 第二轮修复
10. ✅ 临时文件命名冲突 - 使用 `uuid.uuid4().hex` 生成唯一文件名
11. ✅ 线程安全问题 - 为所有读取操作（分类/标签查询）添加锁
12. ✅ 文件清理 - 使用 `try/finally` 确保上传文件和临时文件被删除
13. ✅ HTML 文件夹层级解析 - 修复 `find_next_sibling()` 为 `find('dl')`
14. ✅ CORS 支持 - 添加 `flask-cors`，允许前端跨域调用
15. ✅ 异常处理 - 确保临时文件在成功或失败时都被清理
16. ✅ 文件大小检查 - 上传时手动验证文件大小

### 第三轮修复
17. ✅ 安全限制 - 脚本注册添加路径遍历防护，只允许加载项目内的 `.py` 文件
18. ✅ 脚本名称验证 - 只允许字母、数字、下划线、连字符
19. ✅ 代码重复 - 创建 `serializers.py` 统一处理 Bookmark 序列化
20. ✅ 配置硬编码 - `Classifier` 支持从 JSON 配置文件加载规则
21. ✅ 输入验证 - 添加 `_sanitize_string()` 和 `_sanitize_tags()` 清理用户输入
22. ✅ 优雅关闭 - 注册 `atexit` 处理器，确保退出时保存数据
23. ✅ 健康检查增强 - 添加书签数量、存储状态等信息

### 第四轮修复
24. ✅ 批量添加书签 - 添加类型检查（必须是数组）、数量限制（最多1000个）、输入清理
25. ✅ 更新书签端点 - 使用统一的清理函数 `_sanitize_string` 和 `_sanitize_tags`
26. ✅ atexit 导入 - 移到文件顶部与其他导入放在一起
27. ✅ 备份文件管理 - 添加时间戳、数量限制（最多保留5个）、自动清理旧备份
28. ✅ 文件大小检查 - 添加异常处理，防止不支持 seek 的文件对象导致错误
29. ✅ API 文档 - 更新批量添加接口的文档

## 待完成

1. 项目没有配置正式的测试框架
2. 缺少生产环境部署配置（如 Docker、Gunicorn 配置等）

## 相关文档

- `README.md`: 项目概述和快速开始
- `docs/PROJECT_STRUCTURE.md`: 详细的项目结构说明
- `docs/INTEGRATION_GUIDE.md`: 新功能接入指南
- `docs/DOCUMENTATION.md`: 文档索引
- `docs/REDUNDANT_CODE.md`: 冗余代码记录
- `docs/PROJECT_ISSUES_OPTIMIZED.md`: 项目优化问题分析
- `openapi.yaml`: OpenAPI 3.0 API 文档
