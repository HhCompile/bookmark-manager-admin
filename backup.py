#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据备份脚本

功能：
1. 自动备份书签数据文件
2. 支持保留指定数量的备份
3. 可配置为定时任务运行

使用方法：
    python backup.py              # 立即执行备份
    python backup.py --schedule   # 启动定时备份服务

定时任务配置（crontab）：
    # 每小时备份一次
    0 * * * * cd /path/to/project && python backup.py >> backup.log 2>&1
"""

import os
import sys
import shutil
import argparse
import logging
from datetime import datetime
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('backup.log', encoding='utf-8')
    ]
)
logger = logging.getLogger('backup')

# 配置
DATA_FILE = 'bookmarks.json'
BACKUP_DIR = 'backups'
MAX_BACKUPS = 10  # 保留的最大备份数量


def ensure_backup_dir():
    """确保备份目录存在"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        logger.info(f"创建备份目录: {BACKUP_DIR}")


def create_backup():
    """创建数据备份
    
    Returns:
        str: 备份文件路径，失败返回 None
    """
    if not os.path.exists(DATA_FILE):
        logger.error(f"数据文件不存在: {DATA_FILE}")
        return None
    
    ensure_backup_dir()
    
    # 生成备份文件名（带时间戳）
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"bookmarks_{timestamp}.json"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    
    try:
        shutil.copy2(DATA_FILE, backup_path)
        logger.info(f"备份成功: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"备份失败: {e}")
        return None


def cleanup_old_backups():
    """清理旧的备份文件，只保留最近的 MAX_BACKUPS 个"""
    ensure_backup_dir()
    
    # 获取所有备份文件
    backup_files = [
        f for f in os.listdir(BACKUP_DIR)
        if f.startswith('bookmarks_') and f.endswith('.json')
    ]
    
    # 按修改时间排序
    backup_files.sort(key=lambda f: os.path.getmtime(os.path.join(BACKUP_DIR, f)))
    
    # 删除多余的旧备份
    if len(backup_files) > MAX_BACKUPS:
        files_to_delete = backup_files[:-MAX_BACKUPS]
        for filename in files_to_delete:
            filepath = os.path.join(BACKUP_DIR, filename)
            try:
                os.remove(filepath)
                logger.info(f"删除旧备份: {filepath}")
            except Exception as e:
                logger.warning(f"删除旧备份失败 {filepath}: {e}")


def list_backups():
    """列出所有备份文件"""
    ensure_backup_dir()
    
    backup_files = [
        f for f in os.listdir(BACKUP_DIR)
        if f.startswith('bookmarks_') and f.endswith('.json')
    ]
    
    if not backup_files:
        print("没有找到备份文件")
        return
    
    backup_files.sort(key=lambda f: os.path.getmtime(os.path.join(BACKUP_DIR, f)), reverse=True)
    
    print(f"\n找到 {len(backup_files)} 个备份文件:\n")
    print(f"{'序号':<6}{'文件名':<30}{'大小':<15}{'修改时间'}")
    print("-" * 70)
    
    for i, filename in enumerate(backup_files, 1):
        filepath = os.path.join(BACKUP_DIR, filename)
        size = os.path.getsize(filepath)
        mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
        
        # 格式化大小
        if size < 1024:
            size_str = f"{size} B"
        elif size < 1024 * 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size / (1024 * 1024):.1f} MB"
        
        print(f"{i:<6}{filename:<30}{size_str:<15}{mtime.strftime('%Y-%m-%d %H:%M:%S')}")


def restore_backup(backup_file):
    """从备份文件恢复数据
    
    Args:
        backup_file: 备份文件路径或序号
    """
    ensure_backup_dir()
    
    # 如果是序号，查找对应的文件
    if backup_file.isdigit():
        index = int(backup_file) - 1
        backup_files = [
            f for f in os.listdir(BACKUP_DIR)
            if f.startswith('bookmarks_') and f.endswith('.json')
        ]
        backup_files.sort(key=lambda f: os.path.getmtime(os.path.join(BACKUP_DIR, f)), reverse=True)
        
        if index < 0 or index >= len(backup_files):
            logger.error(f"无效的备份序号: {backup_file}")
            return False
        
        backup_path = os.path.join(BACKUP_DIR, backup_files[index])
    else:
        # 直接是文件名
        if os.path.exists(backup_file):
            backup_path = backup_file
        else:
            backup_path = os.path.join(BACKUP_DIR, backup_file)
    
    if not os.path.exists(backup_path):
        logger.error(f"备份文件不存在: {backup_path}")
        return False
    
    # 备份当前数据
    if os.path.exists(DATA_FILE):
        backup_current = f"{DATA_FILE}.before_restore.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(DATA_FILE, backup_current)
        logger.info(f"当前数据已备份到: {backup_current}")
    
    # 恢复数据
    try:
        shutil.copy2(backup_path, DATA_FILE)
        logger.info(f"数据恢复成功: {backup_path} -> {DATA_FILE}")
        return True
    except Exception as e:
        logger.error(f"数据恢复失败: {e}")
        return False


def run_schedule():
    """运行定时备份服务"""
    import time
    import schedule
    
    # 每小时备份一次
    schedule.every().hour.do(lambda: (create_backup(), cleanup_old_backups()))
    
    logger.info("定时备份服务已启动（每小时备份一次）")
    
    while True:
        schedule.run_pending()
        time.sleep(60)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='书签数据备份工具')
    parser.add_argument('--list', '-l', action='store_true', help='列出所有备份')
    parser.add_argument('--restore', '-r', metavar='BACKUP', help='恢复指定备份（序号或文件名）')
    parser.add_argument('--schedule', '-s', action='store_true', help='启动定时备份服务')
    parser.add_argument('--cleanup', '-c', action='store_true', help='只清理旧备份')
    
    args = parser.parse_args()
    
    if args.list:
        list_backups()
    elif args.restore:
        restore_backup(args.restore)
    elif args.schedule:
        run_schedule()
    elif args.cleanup:
        cleanup_old_backups()
    else:
        # 默认执行备份
        backup_path = create_backup()
        if backup_path:
            cleanup_old_backups()
            print(f"\n备份完成: {backup_path}")


if __name__ == '__main__':
    main()
