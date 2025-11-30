"""
Flask应用工厂
"""
import logging
import os

from flask import Flask

from config import config as config_dict

# 创建基础logger
logger = logging.getLogger(__name__)


def create_app(config_name=None):
    """
    应用工厂函数
    
    Args:
        config_name: 配置名称 ('development', 'testing', 'production')

    Returns:
        Flask应用实例
    """
    app = Flask(__name__)

    # 设置基础日志
    setup_basic_logging()

    # 加载配置
    setup_config(app, config_name)

    # 初始化日志系统
    setup_logging(app)

    # 初始化扩展
    setup_extensions(app)

    # 注册中间件
    setup_middlewares(app)

    # 注册蓝图
    setup_blueprints(app)

    app.logger.info("应用初始化完成")
    return app


def setup_config(app, config_name):
    """
    设置应用配置
    
    Args:
        app: Flask应用实例
        config_name: 配置名称
        
    Returns:
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')

    config_class = config_dict.get(config_name, config_dict['default'])
    app.config.from_object(config_class)
    logger.info(f"配置加载成功: {config_class}")


def setup_basic_logging():
    """设置基础日志（在应用创建前使用）"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def setup_logging(app):
    from flaskr.utils.logger import setup_logger
    setup_logger(app)


def setup_extensions(app):
    from flaskr.extensions import (
        db,
        migrate,
        cors,
        jwt,
        limiter
    )
    from flaskr.core.token import configure_jwt_handlers

    # 初始化数据库
    db.init_app(app)

    cors.init_app(app)

    limiter.init_app(app)

    jwt.init_app(app)
    # 配置JWT错误处理
    configure_jwt_handlers(jwt)

    logger.info("扩展初始化成功")


def setup_blueprints(app):
    from flaskr.routes import bp
    app.register_blueprint(bp)
    logger.info("路由注册成功")


def setup_middlewares(app):
    from flaskr.middleware import (
        add_security_headers,
        remove_sensitive_headers,
        validate_content_type,
        register_error_handlers
    )

    app.after_request(add_security_headers)
    app.after_request(remove_sensitive_headers)

    @app.before_request
    def validate_request():
        is_valid, error = validate_content_type()
        if not is_valid:
            return error

    register_error_handlers(app)
    logger.info("中间件注册成功")
