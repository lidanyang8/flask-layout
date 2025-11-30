"""
生产环境配置
"""
import os
import secrets
from config.base import Config


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False  # 生产环境必须关闭DEBUG
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://user:password@localhost/dbname'
    
    # 生产环境必须设置SECRET_KEY和JWT_SECRET_KEY
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("生产环境必须设置SECRET_KEY环境变量")
    
    # JWT密钥必须使用随机复杂的密钥
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    if not JWT_SECRET_KEY:
        # 如果未设置，生成一个随机密钥（但生产环境应该手动设置）
        JWT_SECRET_KEY = secrets.token_urlsafe(64)
        import warnings
        warnings.warn("JWT_SECRET_KEY未设置，已生成随机密钥。生产环境请手动设置！")
    
    # 生产环境使用HS256算法（建议使用RS256）
    JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')
    
    # 速率限制配置
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')
    RATELIMIT_STRATEGY = os.environ.get('RATELIMIT_STRATEGY', 'fixed-window')
    
    # HTTPS和HSTS配置（由Nginx或负载均衡器处理）
    # 应用层通过security_headers中间件添加HSTS头
    
    # 生产环境特定配置
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }
    
    # 安全配置
    SESSION_COOKIE_SECURE = True  # 仅HTTPS传输
    SESSION_COOKIE_HTTPONLY = True  # 防止XSS
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF保护

