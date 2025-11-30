"""
响应工具
"""
from flask import jsonify


def success_response(data=None, status_code=200, message='success'):
    """
    成功响应
    
    Args:
        data: 响应数据
        status_code: HTTP状态码
        message: 响应消息
        
    Returns:
        JSON响应
    """
    response = {
        'success': True,
        'message': message,
        'data': data
    }
    return jsonify(response), status_code


def error_response(message='error', status_code=400, errors=None):
    """
    错误响应
    
    Args:
        message: 错误消息
        status_code: HTTP状态码
        errors: 详细错误信息
        
    Returns:
        JSON响应
    """
    response = {
        'success': False,
        'message': message,
        'errors': errors
    }
    return jsonify(response), status_code

