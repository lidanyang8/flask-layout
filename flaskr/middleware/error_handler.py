"""
错误处理中间件
"""
import logging
from flask import request
from werkzeug.exceptions import HTTPException
from flaskr.utils.response import error_response

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """
    注册错误处理器
    
    Args:
        app: Flask应用实例
    """
    @app.errorhandler(400)
    def bad_request(error):
        """400 Bad Request"""
        logger.warning(f"Bad Request: {request.url} - {error}")
        return error_response('请求参数错误', 400)
    
    @app.errorhandler(401)
    def unauthorized(error):
        """401 Unauthorized"""
        logger.warning(f"Unauthorized: {request.url}")
        return error_response('未授权访问', 401)
    
    @app.errorhandler(403)
    def forbidden(error):
        """403 Forbidden"""
        logger.warning(f"Forbidden: {request.url}")
        return error_response('无权访问', 403)
    
    @app.errorhandler(404)
    def not_found(error):
        """404 Not Found"""
        logger.info(f"Not Found: {request.url}")
        return error_response('资源不存在', 404)
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """405 Method Not Allowed"""
        logger.warning(f"Method Not Allowed: {request.method} {request.url}")
        return error_response('不允许的HTTP方法', 405)
    
    @app.errorhandler(406)
    def not_acceptable(error):
        """406 Not Acceptable"""
        logger.warning(f"Not Acceptable: {request.url}")
        return error_response('不支持的Content-Type', 406)
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        """429 Too Many Requests"""
        logger.warning(f"Rate Limit Exceeded: {request.remote_addr} - {request.url}")
        return error_response('请求过于频繁，请稍后再试', 429)
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """500 Internal Server Error"""
        logger.error(f"Internal Server Error: {request.url} - {error}", exc_info=True)
        if app.config.get('DEBUG', False):
            return error_response(f'服务器内部错误: {str(error)}', 500)
        else:
            return error_response('服务器内部错误', 500)
    
    @app.errorhandler(HTTPException)
    def http_exception_handler(error):
        """处理HTTP异常"""
        logger.warning(f"HTTP Exception: {error.code} - {request.url}")
        return error_response(error.description or '请求错误', error.code)
    
    @app.errorhandler(Exception)
    def general_exception_handler(error):
        """处理所有未捕获的异常"""
        logger.error(f"Unhandled Exception: {request.url} - {error}", exc_info=True)
        if app.config.get('DEBUG', False):
            return error_response(f'服务器错误: {str(error)}', 500)
        else:
            return error_response('服务器错误', 500)

