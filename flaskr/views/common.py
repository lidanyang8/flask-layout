"""
通用视图（首页、文档等）
"""
from flask import jsonify


def index():
    """首页视图"""
    return jsonify({
        'message': '欢迎使用Flask API',
        'version': '1.0.0'
    })


def docs():
    """API文档视图"""
    return jsonify({
        'api_docs': '/api/health - 健康检查',
        'endpoints': {
            'GET /api/users': '获取用户列表',
            'GET /api/users/<id>': '获取单个用户',
            'POST /api/users': '创建用户'
        }
    })

