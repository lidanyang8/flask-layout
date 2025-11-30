# 安全功能实现文档

## 概述

本文档说明已实现的安全功能，涵盖访问控制、输入验证、数据处理、输出安全等方面。

## ✅ 已实现的安全功能

### 1. 访问限制

#### 1.1 API速率限制

- **实现方式**: Flask-Limiter
- **功能**:
    - 防止DDoS攻击
    - 防止暴力破解
    - 防止批量爬取
- **配置**:
    - 认证接口: 登录5次/分钟，注册3次/小时
    - API接口: 读取200次/小时，写入50次/小时
    - 默认限制: 200次/天，50次/小时

#### 1.2 HTTPS和HSTS

- **实现方式**: 安全响应头中间件
- **功能**:
    - 自动检测HTTPS连接
    - 添加HSTS头（Strict-Transport-Security）
    - 包含子域名和预加载

#### 1.3 目录列表保护

- **实现方式**: Flask配置
- **说明**: 默认关闭目录列表，需要时通过Nginx配置

### 2. 输入验证

#### 2.1 HTTP方法验证

- **实现方式**: `validate_http_method` 装饰器
- **功能**:
    - 验证请求方法是否允许
    - 返回405 Method Not Allowed

#### 2.2 Content-Type验证

- **实现方式**: `validate_content_type` 中间件
- **功能**:
    - 验证请求Content-Type
    - 支持: application/json, application/x-www-form-urlencoded, multipart/form-data
    - 返回406 Not Acceptable

#### 2.3 输入清理

- **实现方式**: `sanitize_input` 函数
- **功能**:
    - 使用bleach清理HTML标签
    - 防止XSS攻击
    - 支持字符串、字典、列表递归清理

#### 2.4 SQL注入防护

- **实现方式**:
    - 使用ORM（SQLAlchemy）自动防护
    - `prevent_sql_injection` 函数作为额外检查
- **功能**: 检测常见SQL注入模式

#### 2.5 数据验证

- **实现方式**: 验证函数
- **功能**:
    - 邮箱格式验证
    - URL格式验证
    - 字符串长度验证

### 3. 处理安全

#### 3.1 身份认证检查

- **实现方式**: `@jwt_required()` 装饰器
- **功能**: 所有API接口都需要JWT认证

#### 3.2 权限检查

- **实现方式**:
    - `check_resource_ownership` - 检查资源所有权
    - `check_resource_access` - 检查资源访问权限
    - `require_permission` - 要求特定权限（预留）
- **功能**: 防止横向越权攻击

#### 3.3 UUID支持

- **实现方式**: `GUID` 类型和 `uuid_mixin`
- **功能**:
    - 支持使用UUID替代自增ID
    - 兼容PostgreSQL和SQLite

#### 3.4 DEBUG模式控制

- **实现方式**: 配置文件
- **功能**:
    - 生产环境强制关闭DEBUG
    - 开发环境可开启

### 4. 输出安全

#### 4.1 安全响应头

- **实现方式**: `add_security_headers` 中间件
- **功能**:
    - `X-Content-Type-Options: nosniff` - 防止MIME类型嗅探
    - `X-Frame-Options: DENY` - 防止点击劫持
    - `Content-Security-Policy` - 内容安全策略
    - `X-XSS-Protection` - XSS保护
    - `Referrer-Policy` - 控制referrer信息
    - `Permissions-Policy` - 控制浏览器功能
    - `Strict-Transport-Security` - HSTS

#### 4.2 移除指纹头

- **实现方式**: `remove_sensitive_headers` 中间件
- **功能**: 移除X-Powered-By、Server等指纹头

#### 4.3 数据脱敏

- **实现方式**: `data_masking` 模块
- **功能**:
    - 邮箱脱敏: `u***@example.com`
    - 手机号脱敏: `138****1234`
    - 身份证脱敏: `110101****1234`
    - 银行卡脱敏: `1234****5678`
    - 用户名脱敏: `u***r`
- **说明**: 所有用户数据在返回前自动脱敏

#### 4.4 统一错误响应

- **实现方式**: `error_handler` 模块
- **功能**:
    - 统一错误格式
    - 生产环境隐藏堆栈信息
    - 返回合适的HTTP状态码

#### 4.5 Content-Type一致性

- **实现方式**: 响应工具
- **功能**: 请求和响应Content-Type保持一致

### 5. 配置安全

#### 5.1 环境变量

- **实现方式**: 配置文件
- **功能**:
    - 所有敏感配置通过环境变量
    - 不硬编码密钥

#### 5.2 Session安全

- **实现方式**: Flask配置
- **功能**:
    - `SESSION_COOKIE_SECURE = True` - 仅HTTPS传输
    - `SESSION_COOKIE_HTTPONLY = True` - 防止XSS
    - `SESSION_COOKIE_SAMESITE = 'Lax'` - CSRF保护

## 使用示例

### 速率限制

```python
from flaskr.utils.rate_limit import limiter, RATE_LIMITS


@bp.route('/api/endpoint', methods=['GET'])
@limiter.limit(RATE_LIMITS['api']['read'])
def endpoint():
    return success_response(data)
```

### 权限检查

```python
from flaskr.utils.permission_check import check_resource_ownership


@bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@check_resource_ownership('user_id')
def update_user(user_id):
    # 只能更新自己的资源
    ...
```

### 数据脱敏

```python
from flaskr.utils.data_masking import mask_user_data

user_data = user.to_dict()
masked_data = mask_user_data(user_data)
return success_response({'user': masked_data})
```

### 输入验证

```python
from flaskr.utils.input_validation import validate_json_structure


@bp.route('/api/endpoint', methods=['POST'])
@validate_json_structure(required_fields=['field1', 'field2'])
def endpoint():
    data = request.get_json()  # 已自动清理
    ...
```

## 配置说明

### 环境变量

```bash
# 速率限制存储（可选，默认使用内存）
RATELIMIT_STORAGE_URL=redis://localhost:6379/0
RATELIMIT_STRATEGY=fixed-window

# 安全配置
DEBUG=False  # 生产环境必须为False
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
```

### Nginx配置（HTTPS和HSTS）

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # HSTS由应用层添加，Nginx可额外配置
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 待实现功能

### 1. IP白名单

- 实现私有API的IP白名单访问控制
- 需要时可通过中间件实现

### 2. API Gateway

- 建议使用Nginx或专业API Gateway（如Kong）
- 实现缓存、限流、动态部署

### 3. 文件上传

- 使用CDN存储上传文件
- 实现文件类型和大小验证

### 4. 队列处理

- 大数据量处理使用队列（Celery + Redis/RabbitMQ）
- 避免阻塞请求

### 5. XML解析保护

- 如需解析XML，关闭实体解析和扩展
- 使用defusedxml库

## 监控建议

### 1. 集中式日志

- 使用ELK Stack或类似方案
- 记录所有请求、错误、响应

### 2. 监控告警

- 监控速率限制触发
- 监控异常登录尝试
- 监控错误率

### 3. IDS/IPS

- 使用入侵检测/防护系统
- 监控API请求模式

## 最佳实践

1. **生产环境**:
    - 使用HTTPS
    - 关闭DEBUG
    - 使用Redis存储速率限制
    - 定期更新依赖

2. **开发环境**:
    - 可开启DEBUG便于调试
    - 使用内存存储速率限制

3. **测试**:
    - 编写安全测试用例
    - 测试速率限制
    - 测试权限检查

## 相关文档

- [AUTH.md](AUTH.md) - 认证系统文档
- [SECURITY_CHECKLIST.md](SECURITY_CHECKLIST.md) - 安全清单
- [DEPLOYMENT.md](DEPLOYMENT.md) - 部署文档

