#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用入口文件

功能：
1. 启动Flask Web应用
2. 初始化应用配置
3. 处理命令行参数

使用方法：
    python run.py
    
或设置环境变量：
    DEBUG=False PORT=8080 python run.py
"""

import sys
import os

# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.api.api_app import app, config, logger

if __name__ == '__main__':
    logger.info(f"启动 {config.APP_NAME} v{config.APP_VERSION}")
    logger.info(f"API 版本: {config.API_VERSION}")
    logger.info(f"数据文件: {config.DATA_FILE}")
    logger.info(f"访问地址: http://{config.HOST}:{config.PORT}")
    
    app.run(
        debug=config.DEBUG,
        host=config.HOST,
        port=config.PORT
    )
