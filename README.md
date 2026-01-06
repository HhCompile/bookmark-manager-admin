# 书签管理器

## 项目概述

书签管理器是一个基于Flask的Web应用，用于管理和分类书签，支持自动打标、分类和书签文件导入功能。该项目采用分层架构设计，具有良好的扩展性和可维护性，同时提供了丰富的API接口，方便与其他系统集成。

### 技术栈

| 技术/框架 | 版本 | 用途 |
|-----------|------|------|
| Python | 3.9+ | 开发语言 |
| Flask | 2.3.2 | Web框架 |
| BeautifulSoup4 | 4.12.2 | HTML解析 |
| JSON | - | 数据存储格式 |
| RESTful API | - | 接口设计风格 |

## 核心功能

### 1. 书签管理
- **基本操作**：添加、删除、查询和更新书签
- **批量处理**：支持批量添加书签
- **分类管理**：按分类组织书签
- **标签系统**：支持多标签管理和按标签查询

### 2. 智能功能
- **自动打标**：基于书签内容自动生成标签
- **智能分类**：自动将书签分类到合适的类别
- **智能分析**：分析书签内容，生成优化建议

### 3. 导入导出
- **HTML书签导入**：支持从浏览器导出的HTML书签文件导入
- **JSON解析**：将HTML书签转换为结构化JSON格式
- **批量处理**：支持大规模书签的高效处理

### 4. 脚本系统
- **动态注册**：支持脚本的动态注册和管理
- **脚本执行**：支持运行各种功能脚本
- **扩展机制**：方便添加新的脚本功能

### 5. API设计
- **RESTful风格**：遵循RESTful API设计原则
- **丰富端点**：提供完整的书签管理和脚本管理API
- **易于集成**：方便与其他系统集成

## 快速启动

### 1. 环境准备

#### 1.1 系统要求
- Python 3.9或更高版本
- pip 20.0或更高版本

#### 1.2 安装依赖

```bash
# 创建虚拟环境（推荐）
python3 -m venv venv_new

# 激活虚拟环境（Linux/macOS）
source venv_new/bin/activate

# 激活虚拟环境（Windows）
venv_new\Scripts\activate

# 安装项目依赖
pip install -r requirements.txt
```

### 2. 启动应用

```bash
# 运行应用
python3 run.py
```

应用将在 `http://127.0.0.1:9001` 启动。

### 3. 验证启动

打开浏览器或使用curl工具访问健康检查端点，确认应用正常运行：

```bash
curl http://127.0.0.1:9001/health
```

预期响应：
```json
{"status": "ok"}
```

## 项目结构

```
bookmark-manager-admin/
├── app/                          # 主应用目录
│   ├── api/                      # API层，处理HTTP请求
│   │   ├── __init__.py
│   │   └── api_app.py            # Flask应用实例和API路由
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
├── venv_new/                     # 虚拟环境
├── bookmarks.json                # 书签数据文件
├── openapi.yaml                  # API文档
├── requirements.txt              # 项目依赖
├── run.py                        # 应用入口
└── README.md                     # 项目概述
```

## 主要API端点

### 1. 书签管理

#### 1.1 获取所有书签
- **URL**: `GET /bookmarks`
- **功能**: 获取所有书签
- **响应示例**:
  ```json
  {
    "bookmarks": [
      {
        "url": "https://github.com",
        "title": "GitHub",
        "tags": ["开发", "代码托管"],
        "category": "技术"
      }
    ]
  }
  ```

#### 1.2 添加单个书签
- **URL**: `POST /bookmark`
- **功能**: 添加单个书签
- **请求示例**:
  ```json
  {
    "url": "https://python.org",
    "title": "Python官方网站"
  }
  ```
- **响应示例**:
  ```json
  {
    "message": "Bookmark processed successfully",
    "bookmark": {
      "url": "https://python.org",
      "title": "Python官方网站",
      "tags": ["开发", "编程语言"],
      "category": "技术"
    }
  }
  ```

#### 1.3 批量添加书签
- **URL**: `POST /bookmarks/batch`
- **功能**: 批量添加书签
- **请求示例**:
  ```json
  {
    "bookmarks": [
      {
        "url": "https://github.com",
        "title": "GitHub"
      },
      {
        "url": "https://python.org",
        "title": "Python官方网站"
      }
    ]
  }
  ```

#### 1.4 按分类获取书签
- **URL**: `GET /bookmarks/category/<category>`
- **功能**: 根据分类获取书签
- **示例**: `GET /bookmarks/category/技术`

#### 1.5 按标签获取书签
- **URL**: `GET /bookmarks/tag/<tag>`
- **功能**: 根据标签获取书签
- **示例**: `GET /bookmarks/tag/开发`

#### 1.6 更新书签
- **URL**: `PUT /bookmark/<url>`
- **功能**: 更新书签信息
- **请求示例**:
  ```json
  {
    "title": "GitHub - 代码托管平台",
    "tags": ["开发", "代码托管", "开源"],
    "reprocess": true
  }
  ```

#### 1.7 删除书签
- **URL**: `DELETE /bookmark/<url>`
- **功能**: 根据URL删除书签

#### 1.8 上传HTML书签文件
- **URL**: `POST /bookmark/upload`
- **功能**: 上传HTML书签文件并导入
- **请求**: `multipart/form-data` 格式，包含 `file` 字段

### 2. 脚本管理

#### 2.1 获取脚本列表
- **URL**: `GET /scripts`
- **功能**: 获取已注册的脚本列表

#### 2.2 解析HTML书签
- **URL**: `POST /scripts/parse`
- **功能**: 上传HTML书签文件并解析为JSON

#### 2.3 分析书签
- **URL**: `POST /scripts/analyze`
- **功能**: 分析书签并生成建议
- **请求示例**:
  ```json
  {
    "bookmarks": [
      {
        "url": "https://github.com",
        "title": "GitHub"
      }
    ]
  }
  ```

#### 2.4 处理书签
- **URL**: `POST /scripts/process`
- **功能**: 上传HTML书签文件，解析并分析生成建议

## 配置选项

### 1. 应用配置

在 `run.py` 文件中可以配置以下选项：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| debug | True | 是否启用调试模式 |
| host | 0.0.0.0 | 监听地址 |
| port | 9001 | 监听端口 |

### 2. 数据存储

- **数据文件**: `bookmarks.json`
- **存储格式**: JSON数组
- **位置**: 项目根目录

### 3. 上传配置

- **上传目录**: `uploads/`
- **最大文件大小**: 16MB
- **支持的文件类型**: HTML

## 常见问题解答

### 1. 如何添加新的脚本？

1. 创建一个新的Python文件，实现 `ScriptInterface` 接口
2. 在脚本中实现 `configure`、`execute` 和 `get_info` 方法
3. 将脚本文件放在 `app/scripts/` 目录下
4. 重启应用，脚本将自动注册

### 2. 如何修改日志级别？

可以在 `app/utils/script_manager.py` 和 `app/scripts/controller.py` 文件中修改日志配置：

```python
logging.basicConfig(
    level=logging.INFO,  # 修改此处的日志级别
    format='%(asctime)s - %(levelname)s - [%(name)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
```

### 3. 如何扩展自动分类功能？

可以修改 `app/services/classifier_service.py` 文件中的 `Classifier` 类，实现更复杂的分类逻辑。

### 4. 如何部署到生产环境？

1. 确保已安装所有依赖
2. 使用生产级WSGI服务器，如Gunicorn：
   ```bash
   gunicorn -w 4 -b 0.0.0.0:9001 run:app
   ```
3. 配置Nginx或Apache作为反向代理
4. 添加适当的认证和授权机制
5. 配置日志和监控

## 文档

- [项目结构说明](docs/PROJECT_STRUCTURE.md)
- [优化后的项目问题分析](docs/PROJECT_ISSUES_OPTIMIZED.md)
- [冗余或未使用代码记录](docs/REDUNDANT_CODE.md)
- [新功能接入说明文档](docs/INTEGRATION_GUIDE.md)
- [文档索引](docs/DOCUMENTATION.md)

## 贡献指南

1. Fork 项目仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证。详情请查看 [LICENSE](LICENSE) 文件。

## 联系方式

如有问题或建议，请联系开发团队。

---

**版本**: 1.0.0
**发布日期**: 2026-01-06
**适用环境**: Python 3.9+，Flask 2.3.2+