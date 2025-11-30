"""
用户相关路由
"""
from flask_jwt_extended import jwt_required

from flaskr.extensions import limiter, RATE_LIMITS
from flaskr.routes import bp
from flaskr.core.auth import active_user_required
from flaskr.utils.permission_check import check_resource_ownership
from flaskr.views.users import get_users, get_user, update_user, delete_user


@bp.route('/api/users', methods=['GET'])
@jwt_required()
@limiter.limit(RATE_LIMITS['api']['read'])
def get_users_route():
    """获取用户列表路由（需要认证）"""
    return get_users()


@bp.route('/api/users/<int:user_id>', methods=['GET'])
@jwt_required()
@limiter.limit(RATE_LIMITS['api']['read'])
def get_user_route(user_id):
    """获取单个用户路由（需要认证）"""
    return get_user(user_id)


@bp.route('/api/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@active_user_required
@limiter.limit(RATE_LIMITS['api']['write'])
@check_resource_ownership('user_id')
def update_user_route(user_id):
    """更新用户路由（需要认证且为活跃用户，防止横向越权）"""
    return update_user(user_id)


@bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@active_user_required
@limiter.limit(RATE_LIMITS['api']['write'])
@check_resource_ownership('user_id')
def delete_user_route(user_id):
    """删除用户路由（需要认证且为活跃用户，防止横向越权）"""
    return delete_user(user_id)
