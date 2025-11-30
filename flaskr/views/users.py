"""
用户相关视图
业务逻辑处理
"""
from flask import request
from flask_jwt_extended import get_jwt_identity

from flaskr.extensions import db
from flaskr.models.user import User
from flaskr.utils.response import success_response, error_response


def get_users():
    """获取用户列表视图"""
    from flaskr.utils.data_masking import mask_user_data

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    pagination = User.query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    # 对用户数据进行脱敏
    users_data = [mask_user_data(user.to_dict()) for user in pagination.items]

    return success_response({
        'users': users_data,
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })


def get_user(user_id):
    """获取单个用户视图"""
    from flaskr.utils.data_masking import mask_user_data

    user = User.query.get_or_404(user_id)
    # 对用户数据进行脱敏
    user_data = mask_user_data(user.to_dict())
    return success_response(user_data)


def update_user(user_id):
    """更新用户视图"""
    current_user_id = get_jwt_identity()

    # 只能更新自己的信息（除非是管理员）
    if int(current_user_id) != user_id:
        return error_response('无权访问', 403)

    user = User.query.get_or_404(user_id)
    data = request.get_json()

    # 更新允许的字段
    if 'email' in data:
        # 检查邮箱是否已被其他用户使用
        existing_user = User.query.filter(
            User.email == data['email'],
            User.id != user_id
        ).first()
        if existing_user:
            return error_response('邮箱已被使用', 400)
        user.email = data['email']

    if 'password' in data:
        # 更新密码
        if len(data['password']) < 8:
            return error_response('密码长度至少8位', 400)
        user.set_password(data['password'])

    try:
        db.session.commit()
        return success_response(user.to_dict())
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新失败: {str(e)}', 500)


def delete_user(user_id):
    """删除用户视图"""
    current_user_id = get_jwt_identity()

    # 只能删除自己的账号（除非是管理员）
    if int(current_user_id) != user_id:
        return error_response('无权访问', 403)

    user = User.query.get_or_404(user_id)

    try:
        # 软删除：设置为非激活状态
        user.is_active = False
        db.session.commit()
        return success_response({'message': '账号已删除'})
    except Exception as e:
        db.session.rollback()
        return error_response(f'删除失败: {str(e)}', 500)
