"""
健康检查视图
"""
from flaskr.utils.response import success_response


def health_check():
    """健康检查视图"""
    return success_response({'status': 'healthy'})

