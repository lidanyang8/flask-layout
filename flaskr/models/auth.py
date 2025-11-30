"""
认证相关模型
"""
import secrets
from datetime import datetime, timedelta

from flaskr.extensions import db


class LoginAttempt(db.Model):
    """登录尝试记录"""
    __tablename__ = 'login_attempts'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, index=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    success = db.Column(db.Boolean, default=False)
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<LoginAttempt {self.username} {self.attempted_at}>'


class UserLockout(db.Model):
    """用户账号锁定记录"""
    __tablename__ = 'user_lockouts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True, index=True)
    failed_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('lockout', uselist=False))

    def is_locked(self):
        """检查账号是否被锁定"""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until

    def increment_failed_attempts(self, max_attempts=5, lockout_duration_minutes=30):
        """增加失败尝试次数，如果超过限制则锁定账号"""
        self.failed_attempts += 1
        self.updated_at = datetime.utcnow()

        if self.failed_attempts >= max_attempts:
            self.locked_until = datetime.utcnow() + timedelta(minutes=lockout_duration_minutes)

        return self.is_locked()

    def reset_failed_attempts(self):
        """重置失败尝试次数"""
        self.failed_attempts = 0
        self.locked_until = None
        self.updated_at = datetime.utcnow()

    def __repr__(self):
        return f'<UserLockout user_id={self.user_id} attempts={self.failed_attempts}>'


class RefreshToken(db.Model):
    """刷新Token记录"""
    __tablename__ = 'refresh_tokens'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    revoked = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref=db.backref('refresh_tokens', lazy='dynamic'))

    def is_expired(self):
        """检查token是否过期"""
        return datetime.utcnow() > self.expires_at

    def is_valid(self):
        """检查token是否有效"""
        return not self.revoked and not self.is_expired()

    @staticmethod
    def generate_token():
        """生成随机token"""
        return secrets.token_urlsafe(64)

    def __repr__(self):
        return f'<RefreshToken user_id={self.user_id} expires_at={self.expires_at}>'
