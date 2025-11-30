"""
Gunicorn配置文件
生产环境WSGI服务器配置
"""
import os
import multiprocessing

# 服务器socket配置
bind = os.getenv('GUNICORN_BIND', '0.0.0.0:5000')
backlog = 2048

# 工作进程配置
workers = int(os.getenv('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = os.getenv('GUNICORN_WORKER_CLASS', 'sync')
worker_connections = 1000
timeout = 30
keepalive = 2

# 日志配置
accesslog = os.getenv('GUNICORN_ACCESS_LOG', '/var/log/flask-layout/access.log')
errorlog = os.getenv('GUNICORN_ERROR_LOG', '/var/log/flask-layout/error.log')
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 进程命名
proc_name = 'flask-layout'

# 服务器机制
daemon = False
pidfile = os.getenv('GUNICORN_PIDFILE', '/var/run/flask-layout/gunicorn.pid')
umask = 0
user = os.getenv('GUNICORN_USER', None)
group = os.getenv('GUNICORN_GROUP', None)
tmp_redirect = False

# 性能调优
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# SSL配置（如果需要HTTPS）
# keyfile = '/path/to/keyfile'
# certfile = '/path/to/certfile'

def when_ready(server):
    """服务器启动时的回调"""
    server.log.info("服务器已就绪，开始接受连接")

def worker_int(worker):
    """工作进程中断时的回调"""
    worker.log.info("工作进程收到中断信号")

def pre_fork(server, worker):
    """工作进程fork前的回调"""
    pass

def post_fork(server, worker):
    """工作进程fork后的回调"""
    server.log.info("工作进程 %s 已启动", worker.pid)

def post_worker_init(worker):
    """工作进程初始化后的回调"""
    pass

def worker_abort(worker):
    """工作进程异常退出时的回调"""
    worker.log.info("工作进程异常退出")

