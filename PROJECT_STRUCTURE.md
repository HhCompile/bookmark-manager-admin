# 书签管理器项目结构说明

## 1. 项目概述

书签管理器是一个基于Flask的Web应用，用于管理和分类书签，支持自动打标、分类和书签文件导入功能。

## 2. 目录结构

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
├── uploads/                      # 上传文件目录
├── venv_new/                     # 虚拟环境
├── bookmarks.json                # 书签数据文件
├── openapi.yaml                  # API文档
├── requirements.txt              # 项目依赖
├── run.py                        # 应用入口
├── PROJECT_STRUCTURE.md          # 项目结构说明
└── README.md                     # 项目概述
```

## 3. 文件命名规范

- **采用snake_case命名法**：所有文件名和目录名均使用小写字母和下划线组合
- **功能清晰**：文件名应准确反映文件的功能和职责
- **模块化设计**：按功能模块划分文件，每个文件负责特定功能
- **避免缩写**：除非是通用缩写，否则尽量使用完整单词

## 4. 模块说明

### 4.1 API层 (app/api/)

- **api_app.py**：Flask应用实例，定义所有API路由，处理HTTP请求和响应

### 4.2 控制器层 (app/controllers/)

- **bookmark_controller.py**：书签管理控制器，处理书签的增删改查、分类和标签管理

### 4.3 模型层 (app/models/)

- **bookmark.py**：书签数据模型，定义书签的属性和方法

### 4.4 脚本模块 (app/scripts/)

- **bookmark_parser.py**：HTML书签文件解析器，将HTML书签转换为JSON格式
- **bookmark_analyzer.py**：书签分析器，对书签进行分析并生成建议
- **controller.py**：脚本控制器，负责管理和执行各种脚本

### 4.5 服务层 (app/services/)

- **classifier_service.py**：自动分类服务，为书签提供自动打标和分类功能
- **storage_service.py**：存储服务，处理书签数据的持久化存储

### 4.6 工具类 (app/utils/)

- **script_manager.py**：脚本管理器，负责脚本的注册、加载和执行

## 5. 应用入口

- **run.py**：应用的主要入口文件，用于启动Flask Web服务器

## 6. 配置和依赖

- **requirements.txt**：项目依赖列表，包含所有必要的Python包
- **openapi.yaml**：API文档，定义了所有可用的API端点

## 7. 数据存储

- **bookmarks.json**：存储书签数据的JSON文件
- **uploads/**：存放用户上传的书签文件和临时文件

## 8. 核心功能流程

1. **书签导入**：用户上传HTML书签文件 → bookmark_parser.py解析 → 生成书签对象 → 存入数据库
2. **自动分类**：书签对象创建后 → classifier_service.py自动打标和分类 → 更新书签属性
3. **API访问**：客户端发送HTTP请求 → api_app.py路由处理 → 调用相应控制器 → 返回JSON响应
4. **脚本执行**：API请求触发脚本执行 → script_manager.py调用相应脚本 → 返回执行结果

## 9. 代码规范

- **Python版本**：使用Python 3.9+
- **命名规范**：
  - 类名：采用驼峰命名法 (如：BookmarkManager)
  - 函数名：采用snake_case (如：get_bookmarks)
  - 变量名：采用snake_case (如：bookmark_list)
  - 常量名：采用全大写+下划线 (如：MAX_CONTENT_LENGTH)
- **注释规范**：
  - 每个模块、类和函数都应有详细的文档字符串
  - 复杂逻辑应有单行注释说明

## 10. 开发和部署

### 10.1 开发环境设置

```bash
# 创建虚拟环境
python3 -m venv venv_new

# 激活虚拟环境
source venv_new/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
python3 run.py
```

### 10.2 访问应用

应用启动后，可以通过以下地址访问：
- 主页：http://127.0.0.1:9001
- 健康检查：http://127.0.0.1:9001/health

## 11. API端点

### 11.1 书签管理

- `GET /bookmarks` - 获取所有书签
- `POST /bookmark` - 添加单个书签
- `POST /bookmarks/batch` - 批量添加书签
- `GET /bookmarks/category/<category>` - 按分类获取书签
- `GET /bookmarks/tag/<tag>` - 按标签获取书签
- `PUT /bookmark/<url>` - 更新书签
- `DELETE /bookmark/<url>` - 删除书签
- `POST /bookmark/upload` - 上传HTML书签文件

### 11.2 脚本管理

- `GET /scripts` - 获取已注册的脚本列表
- `POST /scripts/parse` - 上传HTML书签文件并解析为JSON
- `POST /scripts/analyze` - 分析书签并生成建议
- `POST /scripts/process` - 上传HTML书签文件，解析并分析生成建议

## 12. 总结

本项目采用了清晰的分层架构，遵循了模块化设计原则，代码结构清晰，易于维护和扩展。通过合理的目录结构和命名规范，使项目具有良好的可读性和可扩展性。

项目的核心功能包括书签管理、自动分类、脚本管理等，通过RESTful API提供服务，方便与其他系统集成。