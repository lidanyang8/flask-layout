"""
基础配置
所有环境共享的配置
"""
import os
from datetime import timedelta


class Config:
    """基础配置"""
    # 应用配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///flaskr.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    # 使用HS256算法（生产环境建议使用RS256）
    JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')
    # Access Token过期时间尽量短（15分钟）
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    # Refresh Token过期时间（7天）
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    # Token在header中的位置
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'

    # 认证安全配置
    MAX_LOGIN_ATTEMPTS = int(os.environ.get('MAX_LOGIN_ATTEMPTS', '5'))
    LOCKOUT_DURATION_MINUTES = int(os.environ.get('LOCKOUT_DURATION_MINUTES', '30'))

    # 分页配置
    POSTS_PER_PAGE = 10

    # CORS配置
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')

    # 日志配置
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
