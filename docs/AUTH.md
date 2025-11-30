# 身份认证系统文档

## 概述

本项目实现了基于JWT（JSON Web Token）的身份认证系统，遵循安全最佳实践。

## 安全特性

### ✅ 已实现的安全功能

1. **JWT认证**：使用Flask-JWT-Extended标准库
2. **密码加密**：使用bcrypt标准库，12轮加密
3. **密码错误次数限制**：默认5次失败后锁定账号30分钟
4. **账号冻结功能**：自动锁定和释放
5. **模糊错误提示**：防止暴力破解攻击
6. **Token过期时间**：Access Token 15分钟，Refresh Token 7天
7. **随机JWT密钥**：生产环境强制使用复杂密钥
8. **敏感数据加密**：密码使用bcrypt加密存储

## API端点

### 认证相关

#### 1. 用户注册
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123"
}
```

**响应：**
```json
{
  "success": true,
  "message": "success",
  "data": {
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com",
      "is_active": true
    },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "random_refresh_token_string"
  }
}
```

#### 2. 用户登录
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "testuser",
  "password": "password123"
}
```

**响应：**
```json
{
  "success": true,
  "message": "success",
  "data": {
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com"
    },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "random_refresh_token_string"
  }
}
```

**错误响应（模糊提示）：**
```json
{
  "success": false,
  "message": "用户名或密码错误",
  "errors": null
}
```

#### 3. 刷新Token
```http
POST /api/auth/refresh
Authorization: Bearer <refresh_token>
```

**响应：**
```json
{
  "success": true,
  "message": "success",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

#### 4. 获取当前用户信息
```http
GET /api/auth/me
Authorization: Bearer <access_token>
```

#### 5. 登出
```http
POST /api/auth/logout
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "refresh_token": "refresh_token_string"
}
```

### 用户相关（需要认证）

#### 获取用户列表
```http
GET /api/users?page=1&per_page=10
Authorization: Bearer <access_token>
```

#### 获取单个用户
```http
GET /api/users/1
Authorization: Bearer <access_token>
```

#### 更新用户信息
```http
PUT /api/users/1
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "email": "newemail@example.com",
  "password": "newpassword123"
}
```

#### 删除用户（软删除）
```http
DELETE /api/users/1
Authorization: Bearer <access_token>
```

## 使用示例

### Python示例

```python
import requests

BASE_URL = "http://localhost:5000/api"

# 1. 注册
register_data = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
}
response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
result = response.json()
access_token = result['data']['access_token']
refresh_token = result['data']['refresh_token']

# 2. 登录
login_data = {
    "username": "testuser",
    "password": "password123"
}
response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
result = response.json()
access_token = result['data']['access_token']

# 3. 使用Token访问受保护资源
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get(f"{BASE_URL}/users", headers=headers)
users = response.json()

# 4. 刷新Token
headers = {"Authorization": f"Bearer {refresh_token}"}
response = requests.post(f"{BASE_URL}/auth/refresh", headers=headers)
result = response.json()
new_access_token = result['data']['access_token']
```

### JavaScript示例

```javascript
const BASE_URL = 'http://localhost:5000/api';

// 1. 登录
async function login(username, password) {
  const response = await fetch(`${BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  });
  const data = await response.json();
  localStorage.setItem('access_token', data.data.access_token);
  localStorage.setItem('refresh_token', data.data.refresh_token);
  return data;
}

// 2. 使用Token访问受保护资源
async function getUsers() {
  const token = localStorage.getItem('access_token');
  const response = await fetch(`${BASE_URL}/users`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  return await response.json();
}

// 3. 刷新Token
async function refreshToken() {
  const refreshToken = localStorage.getItem('refresh_token');
  const response = await fetch(`${BASE_URL}/auth/refresh`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${refreshToken}`,
    },
  });
  const data = await response.json();
  localStorage.setItem('access_token', data.data.access_token);
  return data;
}
```

## 配置说明

### 环境变量

```bash
# 必需（生产环境）
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here  # 建议使用随机生成的64字符以上密钥

# 可选
MAX_LOGIN_ATTEMPTS=5                    # 最大登录尝试次数，默认5
LOCKOUT_DURATION_MINUTES=30              # 锁定持续时间（分钟），默认30
JWT_ALGORITHM=HS256                     # JWT算法，默认HS256（生产环境建议RS256）
```

### 生成JWT密钥

```python
import secrets

# 生成随机密钥
jwt_secret = secrets.token_urlsafe(64)
print(jwt_secret)
```

## 安全机制

### 1. 密码错误次数限制

- 默认允许5次失败尝试
- 超过限制后账号锁定30分钟
- 锁定期间无法登录
- 登录成功后自动重置失败次数

### 2. 账号冻结

- 自动检测并锁定账号
- 锁定时间到期后自动解除
- 支持手动重置（需要管理员权限）

### 3. 模糊错误提示

所有登录相关的错误都返回相同的模糊提示：
- "用户名或密码错误"（无论用户名不存在还是密码错误）
- 防止攻击者通过错误信息判断用户名是否存在

### 4. Token管理

- **Access Token**：15分钟过期，用于API访问
- **Refresh Token**：7天过期，用于刷新Access Token
- Refresh Token存储在数据库中，支持撤销
- Token过期后需要重新登录或使用Refresh Token刷新

## 数据库模型

### User（用户）
- `id`: 用户ID
- `username`: 用户名（唯一）
- `email`: 邮箱（唯一）
- `password_hash`: 密码哈希（bcrypt加密）
- `is_active`: 是否激活
- `last_login`: 最后登录时间

### LoginAttempt（登录尝试记录）
- `username`: 尝试登录的用户名
- `ip_address`: IP地址
- `user_agent`: 用户代理
- `success`: 是否成功
- `attempted_at`: 尝试时间

### UserLockout（账号锁定）
- `user_id`: 用户ID
- `failed_attempts`: 失败尝试次数
- `locked_until`: 锁定到期时间

### RefreshToken（刷新Token）
- `user_id`: 用户ID
- `token`: Token字符串
- `expires_at`: 过期时间
- `revoked`: 是否已撤销

## 装饰器

### @jwt_required()
基本JWT认证装饰器，验证Token是否有效。

### @active_user_required
活跃用户装饰器，验证用户是否激活且未被锁定。

### @admin_required
管理员权限装饰器（预留，可根据需要实现）。

## 最佳实践

1. **Token存储**：
   - 前端：使用HttpOnly Cookie存储（推荐）或localStorage
   - 移动端：使用安全存储

2. **Token刷新**：
   - Access Token过期前自动刷新
   - 使用Refresh Token获取新的Access Token

3. **错误处理**：
   - Token过期：使用Refresh Token刷新
   - Refresh Token过期：重新登录

4. **安全建议**：
   - 生产环境使用HTTPS
   - 定期更换JWT密钥
   - 监控登录尝试记录
   - 实施IP限制（可选）

## 故障排查

### Token过期
```json
{
  "success": false,
  "message": "Token已过期",
  "errors": null
}
```
**解决方案**：使用Refresh Token刷新Access Token

### 账号被锁定
```json
{
  "success": false,
  "message": "账号已被锁定，请稍后再试",
  "errors": null
}
```
**解决方案**：等待锁定时间到期或联系管理员

### 无效Token
```json
{
  "success": false,
  "message": "无效的Token",
  "errors": null
}
```
**解决方案**：重新登录获取新Token

