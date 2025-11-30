"""
认证视图
处理登录、注册、token刷新等
"""
from flask import request
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required
)

from flaskr.core.auth import AuthService
from flaskr.core.token import TokenService
from flaskr.utils.response import success_response, error_response


def register():
    """用户注册视图"""
    data = request.get_json()

    # 验证必填字段
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data or not data[field]:
            return error_response('用户名或密码错误', 400)  # 模糊提示

    # 验证密码强度（至少8位）
    if len(data['password']) < 8:
        return error_response('用户名或密码错误', 400)  # 模糊提示

    # 注册用户
    user, error = AuthService.register(
        username=data['username'],
        email=data['email'],
        password=data['password']
    )

    if error:
        return error_response(error, 400)

    # 生成JWT token
    access_token = create_access_token(identity=user.id)
    refresh_token_obj = TokenService.create_refresh_token(user.id)

    return success_response({
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token_obj.token
    }, 201)


def login():
    """用户登录视图"""
    data = request.get_json()

    # 验证必填字段
    if 'username' not in data or 'password' not in data:
        return error_response('用户名或密码错误', 400)  # 模糊提示

    # 登录验证
    user, error, is_locked = AuthService.login(
        username_or_email=data['username'],
        password=data['password']
    )

    if error:
        return error_response(error, 401)

    # 生成JWT token
    access_token = create_access_token(identity=user.id)
    refresh_token_obj = TokenService.create_refresh_token(user.id)

    return success_response({
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token_obj.token
    })


@jwt_required(refresh=True)
def refresh():
    """刷新Access Token视图"""
    user_id = get_jwt_identity()

    # 验证用户是否存在且激活
    from flaskr.models.user import User
    user = User.query.get(user_id)

    if not user or not user.is_active:
        return error_response('用户不存在或已被禁用', 401)

    # 生成新的access token
    access_token = create_access_token(identity=user_id)

    return success_response({
        'access_token': access_token
    })


@jwt_required()
def logout():
    """登出视图"""
    # 获取refresh token（如果提供）
    data = request.get_json() or {}
    refresh_token = data.get('refresh_token')

    if refresh_token:
        TokenService.revoke_refresh_token(refresh_token)

    return success_response({'message': '登出成功'})


@jwt_required()
def me():
    """获取当前用户信息视图"""
    user_id = get_jwt_identity()

    from flaskr.models.user import User
    from flaskr.utils.data_masking import mask_user_data

    user = User.query.get(user_id)

    if not user:
        return error_response('用户不存在', 404)

    # 返回数据前进行脱敏处理
    user_data = user.to_dict(include_sensitive=True)
    masked_data = mask_user_data(user_data)

    return success_response({
        'user': masked_data
    })
