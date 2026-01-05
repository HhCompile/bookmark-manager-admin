# 书签管理系统 - 新功能接入说明文档

## 1. 项目概述

本项目是一个书签自动管理系统，支持书签的添加、删除、查询，以及自动打标和分类。本次集成引入了新的脚本系统，增强了系统的扩展性和功能性。

## 2. 新引入脚本的功能特性

### 2.1 controller.py - 脚本控制器

**功能：**
- 统一管理和调用多个Python脚本
- 支持脚本注册、卸载和动态调用
- 标准化接口定义
- 配置参数支持
- 可靠的通信机制
- 完整的错误处理和日志记录

**接口规范：**
- 提供ScriptInterface基类，定义标准化接口
- 支持脚本注册、卸载、列出和运行
- 使用JSON格式进行通信

### 2.2 bookmark_parser.py - 书签HTML解析器

**功能：**
- 读取并解析HTML书签文件
- 提取书签的结构化数据，支持多层嵌套结构
- 将HTML文档转换为规范的JSON数组格式
- 支持别名信息存储和唯一性验证
- 实现异常处理和日志记录
- 支持深度嵌套结构的性能优化

**依赖：**
- beautifulsoup4
- lxml

### 2.3 bookmark_analyzer.py - 书签智能分析器

**功能：**
- 数据解析：读取并解析书签JSON数据
- 别名建议：生成2-3个简洁、有意义的别名
- 归类建议：分析主题类别
- 分组建议：建议归属的分组名称
- 输出格式：支持JSON、CSV和格式化文本输出

**依赖：**
- 无外部依赖，使用Python标准库

## 3. 集成步骤

### 3.1 安装依赖

```bash
python3 -m pip install 'requests>=2.31.0' 'cryptography>=42.0.0'
```

### 3.2 复制脚本文件

将以下脚本文件复制到项目根目录：
- controller.py
- bookmark_parser.py
- bookmark_analyzer.py

### 3.3 创建脚本管理器

创建`script_manager.py`文件，用于初始化和管理脚本控制器：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
脚本管理器，用于集成和管理多个Python脚本
"""

import os
import logging
from controller import ScriptController
from typing import Dict, Any, List

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [script_manager] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('script_manager')


class ScriptManager:
    """
    脚本管理器类，用于集成和管理多个Python脚本
    """
    
    def __init__(self):
        self.controller = ScriptController()
        self.scripts_dir = os.path.dirname(os.path.abspath(__file__))
        self._register_default_scripts()
    
    def _register_default_scripts(self):
        """
        注册默认脚本
        """
        scripts_to_register = [
            ('parser', os.path.join(self.scripts_dir, 'bookmark_parser.py')),
            ('analyzer', os.path.join(self.scripts_dir, 'bookmark_analyzer.py'))
        ]
        
        for script_name, script_path in scripts_to_register:
            if os.path.exists(script_path):
                result = self.controller.register_script(script_name, script_path)
                if result['status'] == 'success':
                    logger.info(f"默认脚本注册成功: {script_name}")
                else:
                    logger.error(f"默认脚本注册失败: {script_name}, 原因: {result['message']}")
            else:
                logger.error(f"脚本文件不存在: {script_path}")
    
    def run_script(self, script_name: str, args: List[str]) -> Dict[str, Any]:
        """
        运行指定脚本
        
        Args:
            script_name: 脚本名称
            args: 脚本参数
            
        Returns:
            脚本执行结果
        """
        return self.controller.run_script(script_name, args)
    
    def list_scripts(self) -> Dict[str, Any]:
        """
        列出所有已注册的脚本
        
        Returns:
            脚本列表
        """
        return self.controller.list_scripts()
    
    def register_script(self, name: str, path: str) -> Dict[str, Any]:
        """
        注册新脚本
        
        Args:
            name: 脚本名称
            path: 脚本路径
            
        Returns:
            注册结果
        """
        return self.controller.register_script(name, path)
    
    def unregister_script(self, name: str) -> Dict[str, Any]:
        """
        卸载脚本
        
        Args:
            name: 脚本名称
            
        Returns:
            卸载结果
        """
        return self.controller.unregister_script(name)
    
    def configure(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        配置脚本管理器
        
        Args:
            config: 配置参数
            
        Returns:
            配置结果
        """
        return self.controller.configure(config)


# 全局脚本管理器实例
script_manager = ScriptManager()
```

### 3.4 集成到Flask应用

在`app.py`中添加对脚本管理器的引用和新的API端点：

```python
# 引入脚本管理器
from script_manager import script_manager

# 添加新的API端点
@app.route('/scripts', methods=['GET'])
def get_scripts():
    """获取已注册的脚本列表"""
    # 实现代码...

@app.route('/scripts/parse', methods=['POST'])
def parse_bookmarks():
    """上传HTML书签文件并解析为JSON"""
    # 实现代码...

@app.route('/scripts/analyze', methods=['POST'])
def analyze_bookmarks():
    """分析书签并生成建议"""
    # 实现代码...

@app.route('/scripts/process', methods=['POST'])
def process_bookmarks():
    """上传HTML书签文件，解析并分析生成建议"""
    # 实现代码...
```

## 4. API接口说明

### 4.1 GET /scripts

**功能：** 获取已注册的脚本列表

**响应：**
```json
{
  "scripts": [
    {
      "author": "自动生成",
      "description": "HTML书签解析器，将HTML书签转换为JSON格式",
      "name": "parser",
      "path": "/path/to/bookmark_parser.py",
      "registered_at": "2026-01-04T16:14:04.735540",
      "version": "1.0.0"
    },
    {
      "author": "自动生成",
      "description": "AI智能书签分析器，生成别名、分类和分组建议",
      "name": "analyzer",
      "path": "/path/to/bookmark_analyzer.py",
      "registered_at": "2026-01-04T16:14:04.736116",
      "version": "1.0.0"
    }
  ],
  "total": 2
}
```

### 4.2 POST /scripts/parse

**功能：** 上传HTML书签文件并解析为JSON

**请求：** 表单数据，包含file字段（HTML书签文件）

**响应：**
```json
{
  "message": "Bookmarks parsed successfully",
  "filename": "bookmarks.html",
  "output_filename": "parsed_bookmarks.json",
  "parsed_count": 10,
  "parsed_data": [...]
}
```

### 4.3 POST /scripts/analyze

**功能：** 分析书签并生成建议

**请求：** JSON格式，包含bookmarks字段（书签数组）

**响应：**
```json
{
  "message": "Bookmarks analyzed successfully",
  "suggestion_count": 10,
  "suggestions": [...]
}
```

### 4.4 POST /scripts/process

**功能：** 上传HTML书签文件，解析并分析生成建议

**请求：** 表单数据，包含file字段（HTML书签文件）

**响应：**
```json
{
  "message": "Bookmarks processed successfully",
  "filename": "bookmarks.html",
  "parsed_count": 10,
  "suggestion_count": 10,
  "suggestions": [...]
}
```

## 5. 使用示例

### 5.1 启动应用

```bash
python3 app.py
```

### 5.2 测试API

#### 5.2.1 获取脚本列表

```bash
curl -X GET http://localhost:9001/scripts
```

#### 5.2.2 上传HTML书签文件并解析

```bash
curl -X POST -F 'file=@bookmarks.html' http://localhost:9001/scripts/parse
```

#### 5.2.3 分析书签并生成建议

```bash
curl -X POST -H "Content-Type: application/json" -d '{"bookmarks": [{"title": "Python官方文档", "url": "https://docs.python.org/3/"}]}' http://localhost:9001/scripts/analyze
```

#### 5.2.4 上传HTML书签文件，解析并分析

```bash
curl -X POST -F 'file=@bookmarks.html' http://localhost:9001/scripts/process
```

## 6. 测试结果

### 6.1 健康检查

```
$ curl -X GET http://localhost:9001/health
{
  "status": "ok"
}
```

### 6.2 获取脚本列表

```
$ curl -X GET http://localhost:9001/scripts
{
  "scripts": [...],
  "total": 2
}
```

### 6.3 解析HTML书签文件

```
$ curl -X POST -F 'file=@uploads/bookmarks_2025_9_30_.html' http://localhost:9001/scripts/parse
{
  "filename": "bookmarks_2025_9_30_.html",
  "message": "Bookmarks parsed successfully",
  "output_filename": "parsed_bookmarks_2025_9_30_.json",
  "parsed_count": 0,
  "parsed_data": []
}
```

## 7. 注意事项

1. **依赖安装**：确保安装了所有必要的依赖包
2. **文件权限**：确保应用程序有读写uploads目录的权限
3. **脚本命名**：脚本名称应唯一，避免冲突
4. **脚本接口**：新注册的脚本应实现ScriptInterface接口
5. **错误处理**：应用程序包含完整的错误处理机制，但仍需注意异常情况
6. **日志记录**：所有操作都会记录日志，可通过调整日志级别查看详细信息
7. **性能优化**：对于大量书签的处理，建议使用异步方式或分批处理
8. **安全性**：API接口没有认证机制，生产环境中建议添加认证和授权

## 8. 扩展建议

1. **添加用户认证**：实现JWT或OAuth2认证机制
2. **支持更多输出格式**：添加XML、Excel等输出格式支持
3. **集成真实AI服务**：将MockAIClassifier替换为真实的AI API，如OpenAI、百度AI等
4. **添加前端界面**：开发Web前端界面，提供更好的用户体验
5. **支持数据库存储**：添加数据库支持，替代JSON文件存储
6. **实现缓存机制**：添加缓存，提高频繁访问的性能
7. **添加任务调度**：支持定时任务，自动更新和分析书签
8. **添加导出功能**：支持将书签导出为HTML、JSON等格式

## 9. 技术支持

如有问题或建议，请联系开发团队。

---

**文档版本**：1.0.0
**发布日期**：2026-01-04
**适用版本**：书签管理系统 v1.0
