#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用入口文件

功能：
1. 启动Flask Web应用
2. 初始化应用配置
3. 处理命令行参数
"""

import sys
import os

# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.api.api_app import app

if __name__ == '__main__':
    # 可以添加命令行参数处理逻辑
    app.run(debug=True, host='0.0.0.0', port=9001)
