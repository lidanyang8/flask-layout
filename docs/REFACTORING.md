# 项目重构说明

## 重构内容

### 1. 配置分离

配置已从单个 `config.py` 文件分离到 `config/` 目录中，便于管理和维护。

#### 新的配置结构

```
config/
├── __init__.py          # 配置模块入口，导出配置字典
├── base.py              # 基础配置（所有环境共享）
├── development.py       # 开发环境配置
├── testing.py           # 测试环境配置
└── production.py        # 生产环境配置
```

#### 配置使用方式

```python
# 方式1：通过配置名称（推荐）
from flaskr import create_app

app = create_app('development')  # 或 'testing', 'production'

# 方式2：通过配置类
from config.development import DevelopmentConfig
from flaskr import create_app

app = create_app(config_class=DevelopmentConfig)

# 方式3：通过环境变量
import os

app = create_app(os.getenv('FLASK_ENV', 'default'))
```

#### 向后兼容

原有的 `config.py` 文件已保留，用于向后兼容，它会导入新的配置结构。

### 2. 路由和视图分离

路由和业务逻辑已分离，遵循 MVC 架构模式。

#### 新的目录结构

```
app/
├── api/
│   ├── __init__.py      # 蓝图定义
│   ├── routes.py        # 路由定义（只负责URL映射）
│   └── views.py         # 视图逻辑（业务逻辑处理）
└── main/
    ├── __init__.py      # 蓝图定义
    ├── routes.py        # 路由定义
    └── views.py         # 视图逻辑
```

#### 代码示例

**路由文件（routes.py）** - 只负责路由定义：

```python
from flaskr.api import bp
from flaskr.api.views import get_users, create_user


@bp.route('/users', methods=['GET'])
def get_users_route():
    """获取用户列表路由"""
    return get_users()


@bp.route('/users', methods=['POST'])
def create_user_route():
    """创建用户路由"""
    return create_user()
```

**视图文件（views.py）** - 包含业务逻辑：

```python
from flask import request
from flaskr import db
from flaskr.models.user import User
from flaskr.utils.response import success_response, error_response


def get_users():
    """获取用户列表视图"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    pagination = User.query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return success_response({
        'users': [user.to_dict() for user in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })


def create_user():
    """创建用户视图"""
    # 业务逻辑处理
    ...
```

## 优势

### 配置分离的优势

1. **可维护性**：每个环境的配置独立文件，易于阅读和维护
2. **可扩展性**：新增环境配置只需添加新文件
3. **清晰性**：配置内容按环境分类，结构清晰
4. **向后兼容**：保留原有 `config.py`，不影响现有代码

### 路由和视图分离的优势

1. **关注点分离**：路由只负责URL映射，视图负责业务逻辑
2. **可测试性**：视图函数可以独立测试，不依赖Flask路由
3. **可重用性**：视图函数可以在不同路由中重用
4. **代码组织**：业务逻辑集中管理，便于维护
5. **团队协作**：前端开发者关注路由，后端开发者关注视图逻辑

## 迁移指南

### 对于现有代码

如果您的代码中直接导入了配置类，无需修改，因为 `config.py` 已保留并导入新配置。

如果您的代码中使用了路由函数，需要：

1. 将业务逻辑提取到 `views.py`
2. 在 `routes.py` 中只保留路由装饰器和视图函数调用

### 示例迁移

**迁移前：**

```python
# routes.py
@bp.route('/users', methods=['GET'])
def get_users():
    page = request.args.get('page', 1, type=int)
    # ... 业务逻辑 ...
    return success_response(data)
```

**迁移后：**

```python
# routes.py
from flaskr.api.views import get_users


@bp.route('/users', methods=['GET'])
def get_users_route():
    return get_users()


# views.py
def get_users():
    page = request.args.get('page', 1, type=int)
    # ... 业务逻辑 ...
    return success_response(data)
```

## 最佳实践

1. **路由文件**：保持简洁，只包含路由装饰器和视图函数调用
2. **视图文件**：包含所有业务逻辑，可以调用服务层或模型层
3. **配置管理**：每个环境配置只包含该环境特有的配置项
4. **基础配置**：共享配置放在 `base.py` 中

