"""
路由模块
统一导入所有路由
"""
from flask import Blueprint

# 创建主蓝图
bp = Blueprint('main', __name__)

# 导入所有路由
from flaskr.routes import auth, users, health, common

__all__ = ['bp', 'auth', 'users', 'health', 'common']

