# 文档索引

## 项目概述

书签管理器是一个基于Flask的Web应用，用于管理和分类书签，支持自动打标、分类和书签文件导入功能。

## 文档列表

| 文档名称 | 主要内容 | 路径 |
|----------|----------|------|
| README.md | 项目概述、核心功能、快速启动指南 | [README.md](README.md) |
| PROJECT_STRUCTURE.md | 项目结构说明，包括规划和实际结构 | [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) |
| PROJECT_ISSUES_OPTIMIZED.md | 优化后的项目问题分析 | [PROJECT_ISSUES_OPTIMIZED.md](PROJECT_ISSUES_OPTIMIZED.md) |
| REDUNDANT_CODE.md | 冗余或未使用代码记录 | [REDUNDANT_CODE.md](REDUNDANT_CODE.md) |
| INTEGRATION_GUIDE.md | 新功能接入说明文档 | [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) |

## 开发指南

### 快速开始

1. 克隆项目仓库
2. 安装依赖：`pip install -r requirements.txt`
3. 启动应用：`python3 run.py`
4. 访问健康检查端点：http://127.0.0.1:9001/health

### 代码规范

- 采用snake_case命名法
- 类名采用驼峰命名法
- 函数和变量名采用snake_case
- 常量名采用全大写+下划线
- 每个模块、类和函数都应有详细的文档字符串

### 项目结构

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
└── 文档文件...
```

## API文档

### 主要API端点

#### 书签管理
- `GET /bookmarks` - 获取所有书签
- `POST /bookmark` - 添加单个书签
- `POST /bookmarks/batch` - 批量添加书签
- `GET /bookmarks/category/<category>` - 按分类获取书签
- `GET /bookmarks/tag/<tag>` - 按标签获取书签
- `PUT /bookmark/<url>` - 更新书签
- `DELETE /bookmark/<url>` - 删除书签
- `POST /bookmark/upload` - 上传HTML书签文件

#### 脚本管理
- `GET /scripts` - 获取已注册的脚本列表
- `POST /scripts/parse` - 上传HTML书签文件并解析为JSON
- `POST /scripts/analyze` - 分析书签并生成建议
- `POST /scripts/process` - 上传HTML书签文件，解析并分析生成建议

## 常见问题

### 如何添加新功能？

1. 按照项目结构规划，将新功能的代码添加到相应目录
2. 确保遵循代码规范
3. 添加必要的文档
4. 测试新功能
5. 更新相关文档

### 如何运行测试？

目前项目尚未添加测试框架，建议手动测试API端点或使用Postman等工具进行测试。

### 如何部署到生产环境？

1. 确保依赖已安装：`pip install -r requirements.txt`
2. 使用生产级WSGI服务器，如gunicorn：`gunicorn -w 4 -b 0.0.0.0:9001 run:app`
3. 配置Nginx或Apache作为反向代理
4. 添加适当的认证和授权机制
5. 配置日志和监控

## 联系方式

如有问题或建议，请联系开发团队。