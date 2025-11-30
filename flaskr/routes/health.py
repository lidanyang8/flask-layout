"""
健康检查路由
"""
from flaskr.routes import bp
from flaskr.views.health import health_check


@bp.route('/api/health', methods=['GET'])
def health_check_route():
    """健康检查路由"""
    return health_check()

