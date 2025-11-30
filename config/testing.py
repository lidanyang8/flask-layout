"""
测试环境配置
"""
from config.base import Config


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    
    # 测试环境特定配置
    SECRET_KEY = 'test-secret-key'
    SQLALCHEMY_ECHO = False

