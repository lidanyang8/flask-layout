"""
通用路由（首页、文档等）
"""
from flaskr.routes import bp
from flaskr.views.common import index, docs


@bp.route('/', methods=['GET'])
def index_route():
    """首页路由"""
    return index()


@bp.route('/docs', methods=['GET'])
def docs_route():
    """API文档路由"""
    return docs()

