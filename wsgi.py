"""
WSGI入口文件
用于生产环境部署
"""
import os

from flaskr import create_app

# 从环境变量获取配置，默认为production
config_name = os.getenv('FLASK_ENV', 'production')
app = create_app(config_name)

if __name__ == '__main__':
    app.run()
