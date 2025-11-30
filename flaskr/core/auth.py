"""
认证核心功能
整合所有认证相关的业务逻辑
"""
from datetime import datetime, timedelta
from functools import wraps

from flask import request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from flaskr.extensions import db
from flaskr.models.auth import LoginAttempt, UserLockout, RefreshToken
from flaskr.models.user import User
from flaskr.utils.response import error_response


class AuthService:
    """认证服务类"""

    @staticmethod
    def register(username, email, password):
        """
        用户注册
        
        Args:
            username: 用户名
            email: 邮箱
            password: 密码
            
        Returns:
            (user, error_message)
        """
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            return None, '用户名或密码错误'  # 模糊提示

        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            return None, '用户名或密码错误'  # 模糊提示

        # 创建新用户
        user = User(
            username=username,
            email=email,
            is_active=True
        )
        user.set_password(password)

        try:
            db.session.add(user)
            db.session.commit()
            return user, None
        except Exception as e:
            db.session.rollback()
            return None, '注册失败，请稍后重试'

    @staticmethod
    def login(username_or_email, password):
        """
        用户登录
        
        Args:
            username_or_email: 用户名或邮箱
            password: 密码
            
        Returns:
            (user, error_message, is_locked)
        """
        # 获取客户端信息
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')

        # 记录登录尝试
        login_attempt = LoginAttempt(
            username=username_or_email,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False
        )

        # 查找用户（支持用户名或邮箱登录）
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()

        # 如果用户不存在，记录失败尝试并返回模糊提示
        if not user:
            login_attempt.success = False
            db.session.add(login_attempt)
            db.session.commit()
            return None, '用户名或密码错误', False

        # 检查账号是否被锁定
        lockout = UserLockout.query.filter_by(user_id=user.id).first()
        if lockout and lockout.is_locked():
            login_attempt.success = False
            db.session.add(login_attempt)
            db.session.commit()
            return None, '账号已被锁定，请稍后再试', True

        # 检查账号是否激活
        if not user.is_active:
            login_attempt.success = False
            db.session.add(login_attempt)
            db.session.commit()
            return None, '用户名或密码错误', False

        # 验证密码
        if not user.check_password(password):
            # 密码错误，增加失败尝试次数
            if not lockout:
                lockout = UserLockout(user_id=user.id, failed_attempts=0)
                db.session.add(lockout)

            is_locked = lockout.increment_failed_attempts(
                max_attempts=current_app.config.get('MAX_LOGIN_ATTEMPTS', 5),
                lockout_duration_minutes=current_app.config.get('LOCKOUT_DURATION_MINUTES', 30)
            )

            login_attempt.success = False
            db.session.add(login_attempt)
            db.session.commit()

            if is_locked:
                return None, '账号已被锁定，请稍后再试', True
            else:
                return None, '用户名或密码错误', False

        # 登录成功
        # 重置失败尝试次数
        if lockout:
            lockout.reset_failed_attempts()

        # 更新最后登录时间
        user.last_login = datetime.utcnow()

        # 记录成功的登录尝试
        login_attempt.success = True
        login_attempt.username = user.username

        db.session.add(login_attempt)
        db.session.commit()

        return user, None, False


def admin_required(f):
    """管理员权限装饰器"""

    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or not user.is_active:
            return error_response('用户不存在或已被禁用', 403)

        # 这里可以添加管理员检查逻辑
        # if not user.is_admin:
        #     return error_response('需要管理员权限', 403)

        return f(*args, **kwargs)

    return decorated_function


def active_user_required(f):
    """活跃用户装饰器（检查用户是否激活且未被锁定）"""

    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return error_response('用户不存在', 404)

        if not user.is_active:
            return error_response('账号已被禁用', 403)

        if user.is_locked():
            return error_response('账号已被锁定，请稍后再试', 403)

        return f(*args, **kwargs)

    return decorated_function

