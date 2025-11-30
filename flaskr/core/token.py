"""
Token核心功能
整合所有JWT和Token相关的功能
"""
from datetime import datetime, timedelta
import secrets

from flask import current_app

from flaskr.extensions import db
from flaskr.models.auth import RefreshToken
from flaskr.utils.response import error_response


class TokenService:
    """Token服务类"""

    @staticmethod
    def create_refresh_token(user_id):
        """
        创建刷新Token
        
        Args:
            user_id: 用户ID
            
        Returns:
            RefreshToken对象
        """
        # 生成token
        token = RefreshToken.generate_token()

        # 创建刷新token记录
        refresh_expires = current_app.config.get('JWT_REFRESH_TOKEN_EXPIRES', timedelta(days=7))
        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=datetime.utcnow() + refresh_expires
        )

        db.session.add(refresh_token)
        db.session.commit()

        return refresh_token

    @staticmethod
    def revoke_refresh_token(token):
        """
        撤销刷新Token
        
        Args:
            token: 刷新token字符串
        """
        refresh_token = RefreshToken.query.filter_by(token=token).first()
        if refresh_token:
            refresh_token.revoked = True
            db.session.commit()

    @staticmethod
    def validate_refresh_token(token):
        """
        验证刷新Token
        
        Args:
            token: 刷新token字符串
            
        Returns:
            (RefreshToken对象, error_message)
        """
        refresh_token = RefreshToken.query.filter_by(token=token).first()

        if not refresh_token:
            return None, '无效的刷新token'

        if not refresh_token.is_valid():
            return None, '刷新token已过期或已被撤销'

        return refresh_token, None

    @staticmethod
    def cleanup_expired_tokens():
        """清理过期的刷新token"""
        expired_tokens = RefreshToken.query.filter(
            RefreshToken.expires_at < datetime.utcnow()
        ).all()

        for token in expired_tokens:
            db.session.delete(token)

        db.session.commit()


def configure_jwt_handlers(jwt):
    """配置JWT错误处理"""

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """Token过期处理"""
        return error_response('Token已过期', 401)

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        """无效Token处理"""
        return error_response('无效的Token', 401)

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        """缺少Token处理"""
        return error_response('缺少认证Token', 401)

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        """需要新的Token处理"""
        return error_response('Token需要刷新', 401)

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        """Token已被撤销处理"""
        return error_response('Token已被撤销', 401)

