# 项目结构规划

## 1. 文件命名规范

### 1.1 命名规则
- 采用 **snake_case** 命名法，所有字母小写，单词之间用下划线分隔
- 文件名应清晰反映文件的功能和职责
- 避免使用缩写，除非是广为人知的缩写（如api、db、ui等）
- 模块文件使用单数形式，如 `bookmark.py` 而不是 `bookmarks.py`
- 工具类文件以 `_utils.py` 结尾，如 `script_utils.py`
- 配置文件使用 `config.py` 或特定功能前缀，如 `database_config.py`

### 1.2 示例
| 旧文件名 | 新文件名 | 说明 |
|---------|---------|------|
| bookmark.py | bookmark.py | 保持不变，符合规范 |
| bookmark_manager.py | bookmark_controller.py | 更清晰地反映其控制器职责 |
| classifier.py | classifier_service.py | 明确其服务层定位 |
| storage.py | storage_service.py | 明确其服务层定位 |
| app.py | api_app.py | 明确其API应用定位 |

## 2. 目录结构设计

### 2.1 整体架构
采用分层架构，将不同功能模块分离，便于维护和扩展：

```
bookmark-manager-admin/
├── app/                      # 主应用目录
│   ├── models/               # 数据模型层
│   ├── controllers/          # 业务控制层
│   ├── services/             # 业务服务层
│   ├── scripts/              # 脚本工具层
│   ├── api/                  # API接口层
│   └── utils/                # 工具函数层
├── run.py                    # 应用入口
├── requirements.txt          # 项目依赖
├── README.md                 # 项目说明
├── openapi.yaml              # API文档
└── INTEGRATION_GUIDE.md      # 集成指南
```

### 2.2 目录职责说明

| 目录 | 职责 | 包含文件 |
|------|------|----------|
| `models/` | 数据模型定义，封装数据结构和属性 | bookmark.py |
| `controllers/` | 业务逻辑控制，处理请求和响应 | bookmark_controller.py |
| `services/` | 核心业务逻辑，提供服务接口 | classifier_service.py, storage_service.py |
| `scripts/` | 辅助脚本工具，如解析器、分析器等 | controller.py, bookmark_parser.py, bookmark_analyzer.py |
| `api/` | API接口定义，处理HTTP请求 | api_app.py |
| `utils/` | 通用工具函数，提供共享功能 | script_manager.py |

## 3. 文件迁移计划

### 3.1 文件归类表

| 旧文件路径 | 新文件路径 | 说明 |
|-----------|-----------|------|
| bookmark.py | app/models/bookmark.py | 数据模型 |
| bookmark_manager.py | app/controllers/bookmark_controller.py | 书签控制器 |
| classifier.py | app/services/classifier_service.py | 分类服务 |
| storage.py | app/services/storage_service.py | 存储服务 |
| app.py | app/api/api_app.py | API应用 |
| main.py | run.py | 应用入口 |
| script_manager.py | app/utils/script_manager.py | 脚本管理工具 |
| controller.py | app/scripts/controller.py | 脚本控制器 |
| bookmark_parser.py | app/scripts/bookmark_parser.py | 书签解析器 |
| bookmark_analyzer.py | app/scripts/bookmark_analyzer.py | 书签分析器 |

### 3.2 导入路径修改
所有文件中的导入语句需要相应修改，例如：
- 旧：`from bookmark import Bookmark`
- 新：`from app.models.bookmark import Bookmark`

## 4. 实施步骤

1. 创建新的目录结构
2. 修改所有文件中的导入语句
3. 将文件按照新结构移动到相应目录
4. 重命名不符合规范的文件
5. 更新应用入口文件
6. 测试应用，确保所有功能正常
7. 更新文档

## 5. 预期效果

- **结构清晰**：各模块职责明确，便于维护和扩展
- **命名规范**：统一的命名规则，提高代码可读性
- **易于扩展**：分层架构便于添加新功能
- **便于测试**：模块化设计便于单元测试和集成测试

## 6. 后续建议

1. **严格遵循规范**：所有新文件都应遵循此命名规范和目录结构
2. **定期审查**：定期检查项目结构，确保符合规范
3. **文档更新**：文件结构变化时及时更新相关文档
4. **自动化工具**：考虑使用lint工具检查命名规范
