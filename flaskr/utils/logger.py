"""
日志工具
"""
import logging
import os
import sys
from logging.handlers import RotatingFileHandler


def setup_logger(app):
    """
    设置日志配置
    
    Args:
        app: Flask应用实例
    """
    # 设置日志级别
    if app.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    app.logger.setLevel(log_level)

    # 控制台日志处理器（所有模式都启用）
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s [in %(pathname)s:%(lineno)d]',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(log_level)
    app.logger.addHandler(console_handler)

    # 文件日志处理器（所有模式都启用）
    # 确保日志目录存在
    log_dir = app.config.get('LOG_DIR', 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # 根据环境设置日志文件名
    log_file = app.config.get('LOG_FILE', f'{log_dir}/flaskr.log')

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10240000,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s [in %(pathname)s:%(lineno)d]',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(log_level)
    app.logger.addHandler(file_handler)

    # 避免重复日志
    app.logger.propagate = False
