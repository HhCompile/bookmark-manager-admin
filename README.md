# 书签管理器

## 项目概述

书签管理器是一个基于Flask的Web应用，用于管理和分类书签，支持自动打标、分类和书签文件导入功能。

## 核心功能

- 书签的添加、删除、查询和更新
- 自动打标和分类
- HTML书签文件导入和解析
- 书签智能分析和建议生成
- RESTful API设计
- 脚本管理系统，支持动态脚本注册和执行

## 快速启动

### 1. 安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv_new

# 激活虚拟环境
source venv_new/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 启动应用

```bash
python3 run.py
```

### 3. 访问应用

应用启动后，可以通过以下地址访问：
- 健康检查：http://127.0.0.1:9001/health

## 主要API端点

### 书签管理
- `GET /bookmarks` - 获取所有书签
- `POST /bookmark` - 添加单个书签
- `POST /bookmarks/batch` - 批量添加书签
- `GET /bookmarks/category/<category>` - 按分类获取书签
- `GET /bookmarks/tag/<tag>` - 按标签获取书签
- `PUT /bookmark/<url>` - 更新书签
- `DELETE /bookmark/<url>` - 删除书签
- `POST /bookmark/upload` - 上传HTML书签文件

### 脚本管理
- `GET /scripts` - 获取已注册的脚本列表
- `POST /scripts/parse` - 上传HTML书签文件并解析为JSON
- `POST /scripts/analyze` - 分析书签并生成建议
- `POST /scripts/process` - 上传HTML书签文件，解析并分析生成建议

## 项目结构

```
bookmark-manager-admin/
├── app/                          # 主应用目录
│   ├── api/                      # API层，处理HTTP请求
│   ├── controllers/              # 控制器层，处理业务逻辑
│   ├── models/                   # 模型层，定义数据结构
│   ├── scripts/                  # 脚本模块，处理特定功能
│   ├── services/                 # 服务层，提供核心功能
│   └── utils/                    # 工具类，提供通用功能
├── uploads/                      # 上传文件目录
├── venv_new/                     # 虚拟环境
├── bookmarks.json                # 书签数据文件
├── openapi.yaml                  # API文档
├── requirements.txt              # 项目依赖
├── run.py                        # 应用入口
├── PROJECT_STRUCTURE.md          # 项目结构说明
└── README.md                     # 项目概述
```

## 文档

- [项目结构说明](docs/PROJECT_STRUCTURE.md)
- [优化后的项目问题分析](docs/PROJECT_ISSUES_OPTIMIZED.md)
- [冗余或未使用代码记录](docs/REDUNDANT_CODE.md)
- [新功能接入说明文档](docs/INTEGRATION_GUIDE.md)
- [文档索引](docs/DOCUMENTATION.md)