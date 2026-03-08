"""
日志工具
"""
import logging
import sys
from pathlib import Path

def setup_logger(name='stock_screener'):
    """设置日志"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # 文件输出
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    file_handler = logging.FileHandler(log_dir / 'screener.log', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# 全局logger
logger = setup_logger()
