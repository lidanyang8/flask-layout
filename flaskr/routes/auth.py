"""
认证路由
"""
from flask_jwt_extended import jwt_required

from flaskr.extensions import limiter, RATE_LIMITS
from flaskr.routes import bp
from flaskr.utils.input_validation import validate_json
from flaskr.views.auth import register, login, refresh, logout, me


@bp.route('/api/auth/register', methods=['POST'])
@limiter.limit(RATE_LIMITS['auth']['register'])
@validate_json(['username', 'email', 'password'])
def register_route():
    """用户注册路由"""
    return register()


@bp.route('/api/auth/login', methods=['POST'])
@limiter.limit(RATE_LIMITS['auth']['login'])
@validate_json(['username', 'password'])
def login_route():
    """用户登录路由"""
    return login()


@bp.route('/api/auth/refresh', methods=['POST'])
@limiter.limit(RATE_LIMITS['auth']['refresh'])
def refresh_route():
    """刷新Token路由"""
    return refresh()


@bp.route('/api/auth/logout', methods=['POST'])
@jwt_required()
@limiter.limit(RATE_LIMITS['api']['write'])
def logout_route():
    """登出路由"""
    return logout()


@bp.route('/api/auth/me', methods=['GET'])
@jwt_required()
@limiter.limit(RATE_LIMITS['api']['read'])
def me_route():
    """获取当前用户信息路由"""
    return me()
