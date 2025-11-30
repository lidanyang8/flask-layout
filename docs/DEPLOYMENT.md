# 生产环境部署指南

本文档说明如何在生产环境中部署Flask Layout应用。

## 前置要求

1. Python 3.8+
2. 已安装项目依赖（`pip install -r requirements.txt`）
3. 数据库已配置并运行
4. 必要的环境变量已设置

## 目录结构准备

创建必要的日志和运行目录：

```bash
sudo mkdir -p /var/log/flask-layout
sudo mkdir -p /var/run/flask-layout
sudo chown -R www-data:www-data /var/log/flask-layout
sudo chown -R www-data:www-data /var/run/flask-layout
```

## 环境变量配置

创建 `.env` 文件或设置系统环境变量：

```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key-here
export DATABASE_URL=postgresql://user:password@localhost/dbname
export GUNICORN_BIND=0.0.0.0:5000
export GUNICORN_WORKERS=4
```

## 方式一：使用 Supervisor

### 1. 安装 Supervisor

```bash
# Ubuntu/Debian
sudo apt-get install supervisor

# CentOS/RHEL
sudo yum install supervisor
```

### 2. 配置 Supervisor

1. 复制配置文件到 Supervisor 配置目录：

```bash
sudo cp supervisor.conf /etc/supervisor/conf.d/flask-layout.conf
```

2. 编辑配置文件，修改以下路径：

```bash
sudo nano /etc/supervisor/conf.d/flask-layout.conf
```

需要修改的配置项：

- `command`: Gunicorn 命令的完整路径
- `directory`: 项目实际路径
- `user`: 运行用户（如 www-data, nginx 等）
- `environment`: 环境变量和 PYTHONPATH

3. 重新加载 Supervisor 配置：

```bash
sudo supervisorctl reread
sudo supervisorctl update
```

4. 启动服务：

```bash
sudo supervisorctl start flask-layout
```

5. 查看状态：

```bash
sudo supervisorctl status flask-layout
```

### 3. 常用 Supervisor 命令

```bash
# 启动服务
sudo supervisorctl start flask-layout

# 停止服务
sudo supervisorctl stop flask-layout

# 重启服务
sudo supervisorctl restart flask-layout

# 查看日志
sudo supervisorctl tail -f flask-layout

# 重新加载配置
sudo supervisorctl reread
sudo supervisorctl update
```

## 方式二：使用 Systemd

### 1. 配置 Systemd Service

1. 复制服务文件到 Systemd 目录：

```bash
sudo cp flask-layout.service /etc/systemd/system/flask-layout.service
```

2. 编辑服务文件，修改以下路径：

```bash
sudo nano /etc/systemd/system/flask-layout.service
```

需要修改的配置项：

- `WorkingDirectory`: 项目实际路径
- `ExecStart`: Gunicorn 命令的完整路径
- `User` 和 `Group`: 运行用户和组
- `Environment`: 环境变量和 PYTHONPATH

3. 重新加载 Systemd 配置：

```bash
sudo systemctl daemon-reload
```

4. 启动服务：

```bash
sudo systemctl start flask-layout
```

5. 设置开机自启：

```bash
sudo systemctl enable flask-layout
```

6. 查看状态：

```bash
sudo systemctl status flask-layout
```

### 2. 常用 Systemd 命令

```bash
# 启动服务
sudo systemctl start flask-layout

# 停止服务
sudo systemctl stop flask-layout

# 重启服务
sudo systemctl restart flask-layout

# 查看状态
sudo systemctl status flask-layout

# 查看日志
sudo journalctl -u flask-layout -f

# 设置开机自启
sudo systemctl enable flask-layout

# 取消开机自启
sudo systemctl disable flask-layout
```

## 直接使用 Gunicorn（测试用）

如果只是测试，可以直接运行：

```bash
gunicorn --config gunicorn.conf.py wsgi:flaskr
```

或者使用命令行参数：

```bash
gunicorn -w 4 -b 0.0.0.0:5000 --access-logfile /var/log/flask-layout/access.log --error-logfile /var/log/flask-layout/error.log wsgi:flaskr
```

## Nginx 反向代理配置（推荐）

在生产环境中，建议使用 Nginx 作为反向代理：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持（如果需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 静态文件
    location /static {
        alias /path/to/flask-layout/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

## 性能调优

### Gunicorn 工作进程数

推荐公式：`(2 × CPU核心数) + 1`

可以通过环境变量调整：

```bash
export GUNICORN_WORKERS=4
```

### 工作模式

- `sync`: 同步模式，适合CPU密集型任务
- `gevent`: 异步模式，适合I/O密集型任务
- `eventlet`: 异步模式，适合I/O密集型任务

修改 `gunicorn.conf.py` 中的 `worker_class` 或通过环境变量：

```bash
export GUNICORN_WORKER_CLASS=gevent
```

如果使用 gevent 或 eventlet，需要安装相应依赖：

```bash
pip install gevent
# 或
pip install eventlet
```

## 日志管理

日志文件位置：

- 访问日志：`/var/log/flask-layout/access.log`
- 错误日志：`/var/log/flask-layout/error.log`
- Supervisor日志：`/var/log/flask-layout/supervisor_*.log`

建议配置日志轮转（logrotate）：

```bash
sudo nano /etc/logrotate.d/flask-layout
```

内容：

```
/var/log/flask-layout/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    missingok
    create 0640 www-data www-data
    sharedscripts
    postrotate
        supervisorctl restart flask-layout > /dev/null 2>&1 || true
    endscript
}
```

## 安全建议

1. **防火墙配置**：只开放必要的端口
2. **使用HTTPS**：配置SSL证书
3. **环境变量**：敏感信息通过环境变量传递，不要硬编码
4. **用户权限**：使用非root用户运行应用
5. **文件权限**：确保配置文件权限正确

## 故障排查

### 查看日志

```bash
# Gunicorn日志
tail -f /var/log/flask-layout/error.log

# Supervisor日志
sudo supervisorctl tail -f flask-layout stderr

# Systemd日志
sudo journalctl -u flask-layout -f
```

### 检查进程

```bash
ps aux | grep gunicorn
```

### 检查端口

```bash
netstat -tlnp | grep 5000
# 或
ss -tlnp | grep 5000
```

## 更新部署

1. 拉取最新代码
2. 安装/更新依赖：`pip install -r requirements.txt`
3. 运行数据库迁移：`flask db upgrade`
4. 重启服务：

```bash
# Supervisor
sudo supervisorctl restart flask-layout

# Systemd
sudo systemctl restart flask-layout
```

