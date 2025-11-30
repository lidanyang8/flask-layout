"""
开发环境配置
"""
import os
from config.base import Config


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///dev.db'
    
    # 开发环境特定配置
    SQLALCHEMY_ECHO = True  # 打印SQL语句

