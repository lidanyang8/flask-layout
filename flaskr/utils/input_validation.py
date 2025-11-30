"""
输入验证工具
防止XSS、SQL注入等攻击
"""
import re
from functools import wraps

import bleach
from flask import request

from flaskr.utils.response import error_response


def validate_content_type():
    """
    验证Content-Type
    
    Returns:
        (is_valid, error_response)
    """
    if request.method in ['POST', 'PUT', 'PATCH']:
        content_type = request.content_type or ''

        # 允许的Content-Type
        allowed_types = [
            'application/json',
            'application/x-www-form-urlencoded',
            'multipart/form-data'
        ]

        # 检查是否匹配允许的类型
        if not any(content_type.startswith(t) for t in allowed_types):
            return False, error_response(
                '不支持的Content-Type，请使用application/json',
                406  # Not Acceptable
            )

    return True, None


def validate_http_method(allowed_methods):
    """
    验证HTTP方法
    
    Args:
        allowed_methods: 允许的HTTP方法列表
        
    Returns:
        装饰器函数
    """

    def decorator(f):
        def wrapper(*args, **kwargs):
            if request.method not in allowed_methods:
                return error_response(
                    f'不允许的HTTP方法: {request.method}',
                    405  # Method Not Allowed
                )
            return f(*args, **kwargs)

        wrapper.__name__ = f.__name__
        return wrapper

    return decorator


def sanitize_input(data):
    """
    清理输入数据，防止XSS
    
    Args:
        data: 输入数据（可以是字符串、字典、列表）
        
    Returns:
        清理后的数据
    """
    if isinstance(data, str):
        # 使用bleach清理HTML标签
        return bleach.clean(data, tags=[], strip=True)
    elif isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    else:
        return data


def validate_json_structure(required_fields=None, optional_fields=None):
    """
    验证JSON结构
    
    Args:
        required_fields: 必需字段列表
        optional_fields: 可选字段列表
        
    Returns:
        装饰器函数
    """

    def decorator(f):
        def wrapper(*args, **kwargs):
            if request.is_json:
                data = request.get_json() or {}

                # 检查必需字段
                if required_fields:
                    missing = [field for field in required_fields if field not in data]
                    if missing:
                        return error_response(
                            f'缺少必需字段: {", ".join(missing)}',
                            400
                        )

                # 清理输入
                sanitized_data = sanitize_input(data)
                request.json = sanitized_data

            return f(*args, **kwargs)

        wrapper.__name__ = f.__name__
        return wrapper

    return decorator


def validate_string_length(field, min_length=0, max_length=None):
    """
    验证字符串长度
    
    Args:
        field: 字段名
        min_length: 最小长度
        max_length: 最大长度
        
    Returns:
        验证函数
    """

    def validate(value):
        if not isinstance(value, str):
            return False, f'{field}必须是字符串'

        length = len(value)
        if length < min_length:
            return False, f'{field}长度至少{min_length}个字符'

        if max_length and length > max_length:
            return False, f'{field}长度不能超过{max_length}个字符'

        return True, None

    return validate


def validate_email(email):
    """
    验证邮箱格式
    
    Args:
        email: 邮箱地址
        
    Returns:
        (is_valid, error_message)
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, '邮箱格式不正确'
    return True, None


def validate_url(url):
    """
    验证URL格式
    
    Args:
        url: URL地址
        
    Returns:
        (is_valid, error_message)
    """
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    if not re.match(pattern, url):
        return False, 'URL格式不正确'
    return True, None


def prevent_sql_injection(value):
    """
    防止SQL注入（基本检查）
    注意：使用ORM时通常不需要，但可以作为额外保护
    
    Args:
        value: 输入值
        
    Returns:
        (is_safe, error_message)
    """
    if not isinstance(value, str):
        return True, None

    # SQL注入常见模式
    dangerous_patterns = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(--|#|/\*|\*/)",
        r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
        r"('|;|\\)",
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, value, re.IGNORECASE):
            return False, '输入包含不安全的字符'

    return True, None


def validate_json(required_fields):
    """
    验证JSON请求体是否包含必需字段

    Args:
        required_fields: 必需字段列表

    Returns:
        装饰器函数
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return error_response('请求必须是JSON格式', 400)

            data = request.get_json()
            if not data:
                return error_response('请求体不能为空', 400)

            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return error_response(
                    f'缺少必需字段: {", ".join(missing_fields)}',
                    400
                )

            return f(*args, **kwargs)

        return decorated_function

    return decorator
