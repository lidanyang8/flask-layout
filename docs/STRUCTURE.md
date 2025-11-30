# 项目结构说明

## 目录结构

```
app/
├── __init__.py              # Flask应用工厂
├── api/                     # API模块
│   ├── __init__.py          # API蓝图定义
│   ├── routes/              # 路由文件夹
│   │   ├── __init__.py      # 路由模块统一导入
│   │   ├── health.py        # 健康检查路由
│   │   └── users.py         # 用户相关路由
│   └── views/               # 视图文件夹
│       ├── __init__.py      # 视图模块统一导入
│       ├── health.py        # 健康检查视图
│       └── users.py         # 用户相关视图
├── common/                  # 通用模块（首页、文档等）
│   ├── __init__.py          # 通用蓝图定义
│   ├── routes/              # 路由文件夹
│   │   ├── __init__.py      # 路由模块统一导入
│   │   └── index.py         # 首页和文档路由
│   └── views/               # 视图文件夹
│       ├── __init__.py      # 视图模块统一导入
│       └── index.py         # 首页和文档视图
├── errors/                  # 错误处理模块
│   ├── __init__.py
│   └── handlers.py
├── models/                  # 数据模型
│   ├── __init__.py
│   └── user.py
└── utils/                   # 工具模块
    ├── __init__.py
    ├── decorators.py
    ├── logger.py
    └── response.py
```

## 设计原则

### 1. 路由和视图分离

- **路由文件** (`routes/`): 只负责URL映射和装饰器
- **视图文件** (`views/`): 包含所有业务逻辑

### 2. 按功能模块组织

每个功能模块（如 users, health）都有独立的路由和视图文件，便于维护和扩展。

### 3. 文件夹结构

使用文件夹而非单文件，避免文件内容过大，提高可读性：

- `routes/` 文件夹：按功能拆分路由文件
- `views/` 文件夹：按功能拆分视图文件

## 添加新功能示例

### 添加新的API端点

1. **创建路由文件** `app/api/routes/posts.py`:

```python
from flaskr.api import bp
from flaskr.api.views.posts import get_posts, create_post


@bp.route('/posts', methods=['GET'])
def get_posts_route():
    return get_posts()


@bp.route('/posts', methods=['POST'])
def create_post_route():
    return create_post()
```

2. **创建视图文件** `app/api/views/posts.py`:

```python
from flask import request
from flaskr import db
from flaskr.models.post import Post
from flaskr.utils.response import success_response


def get_posts():
    """获取文章列表视图"""
    # 业务逻辑
    posts = Post.query.all()
    return success_response([post.to_dict() for post in posts])


def create_post():
    """创建文章视图"""
    data = request.get_json()
    # 业务逻辑
    ...
```

3. **在路由模块中注册** `app/api/routes/__init__.py`:

```python
from flaskr.api.routes import health, users, posts

__all__ = ['health', 'users', 'posts']
```

4. **在API蓝图中导入** `app/api/__init__.py`:

```python
from flaskr.api.routes import health, users, posts
```

## 路由组织

### API路由 (`/api/*`)

- `/api/health` - 健康检查
- `/api/users` - 用户相关接口
- `/api/posts` - 文章相关接口（示例）

### 通用路由 (`/*`)

- `/` - 首页
- `/docs` - API文档

## 优势

1. **可维护性**: 每个功能模块独立，易于定位和修改
2. **可扩展性**: 添加新功能只需创建新文件，不影响现有代码
3. **可读性**: 文件内容精简，结构清晰
4. **可测试性**: 视图函数可独立测试
5. **团队协作**: 不同开发者可以同时开发不同模块，减少冲突

