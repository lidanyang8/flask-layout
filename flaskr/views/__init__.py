"""
视图模块
统一导入所有视图
"""
from flaskr.views import auth, users, health, common

__all__ = ['auth', 'users', 'health', 'common']

