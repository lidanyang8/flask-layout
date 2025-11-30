"""
权限检查工具
防止横向越权攻击
"""
from functools import wraps

from flask import request
from flask_jwt_extended import get_jwt_identity

from flaskr.models.user import User
from flaskr.utils.response import error_response


def check_resource_ownership(resource_id_param='user_id', allow_admin=True):
    """
    检查资源所有权（防止横向越权）
    
    Args:
        resource_id_param: URL参数中的资源ID参数名
        allow_admin: 是否允许管理员访问
        
    Returns:
        装饰器函数
    """

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()

            if not current_user_id:
                return error_response('未授权访问', 401)

            # 获取资源ID
            resource_id = kwargs.get(resource_id_param) or request.view_args.get(resource_id_param)

            if not resource_id:
                return error_response('资源ID不能为空', 400)

            # 获取当前用户
            current_user = User.query.get(current_user_id)
            if not current_user:
                return error_response('用户不存在', 404)

            # 检查是否是管理员（如果允许）
            # is_admin = getattr(current_user, 'is_admin', False)
            # if allow_admin and is_admin:
            #     return f(*args, **kwargs)

            # 检查资源所有权
            if str(resource_id) != str(current_user_id):
                return error_response('无权访问此资源', 403)

            return f(*args, **kwargs)

        return wrapper

    return decorator


def check_resource_access(resource_model, resource_id_param='id', user_id_field='user_id'):
    """
    检查资源访问权限
    
    Args:
        resource_model: 资源模型类
        resource_id_param: URL参数中的资源ID参数名
        user_id_field: 资源模型中的用户ID字段名
        
    Returns:
        装饰器函数
    """

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()

            if not current_user_id:
                return error_response('未授权访问', 401)

            # 获取资源ID
            resource_id = kwargs.get(resource_id_param) or request.view_args.get(resource_id_param)

            if not resource_id:
                return error_response('资源ID不能为空', 400)

            # 查询资源
            resource = resource_model.query.get(resource_id)
            if not resource:
                return error_response('资源不存在', 404)

            # 检查资源所有权
            resource_user_id = getattr(resource, user_id_field)
            if str(resource_user_id) != str(current_user_id):
                return error_response('无权访问此资源', 403)

            return f(*args, **kwargs)

        return wrapper

    return decorator


def require_permission(permission_name):
    """
    要求特定权限（预留，用于RBAC）
    
    Args:
        permission_name: 权限名称
        
    Returns:
        装饰器函数
    """

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()

            if not current_user_id:
                return error_response('未授权访问', 401)

            # 这里可以实现权限检查逻辑
            # user = User.query.get(current_user_id)
            # if not user.has_permission(permission_name):
            #     return error_response('权限不足', 403)

            return f(*args, **kwargs)

        return wrapper

    return decorator
