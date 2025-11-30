"""
扩展实例
所有Flask扩展的实例定义
"""
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# 数据库
db = SQLAlchemy()

# 数据库迁移
migrate = Migrate()

# CORS
cors = CORS()

# JWT
jwt = JWTManager()

# limiter
limiter = Limiter(auto_check=False, key_func=get_remote_address)
# 速率限制预设
RATE_LIMITS = {
    # 认证相关接口 - 更严格的限制
    'auth': {
        'login': "5 per minute",
        'register': "3 per hour",
        'refresh': "10 per minute",
    },
    # API接口 - 中等限制
    'api': {
        'default': "100 per hour",
        'read': "200 per hour",
        'write': "50 per hour",
    },
    # 公共接口 - 宽松限制
    'public': {
        'default': "1000 per hour",
    }
}
