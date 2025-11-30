"""
安全响应头中间件
"""
from flask import request


def add_security_headers(response):
    """
    添加安全响应头
    
    Args:
        response: Flask响应对象
        
    Returns:
        添加了安全头的响应对象
    """
    # X-Content-Type-Options: 防止MIME类型嗅探
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # X-Frame-Options: 防止点击劫持
    response.headers['X-Frame-Options'] = 'DENY'
    
    # Content-Security-Policy: 内容安全策略
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "connect-src 'self'; "
        "frame-ancestors 'none';"
    )
    response.headers['Content-Security-Policy'] = csp
    
    # X-XSS-Protection: XSS保护
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Referrer-Policy: 控制referrer信息
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Permissions-Policy: 控制浏览器功能
    response.headers['Permissions-Policy'] = (
        'geolocation=(), '
        'microphone=(), '
        'camera=(), '
        'payment=()'
    )
    
    # Strict-Transport-Security: HSTS（仅在HTTPS时添加）
    if request.is_secure or request.headers.get('X-Forwarded-Proto') == 'https':
        response.headers['Strict-Transport-Security'] = (
            'max-age=31536000; '
            'includeSubDomains; '
            'preload'
        )
    
    # 删除指纹头
    response.headers.pop('X-Powered-By', None)
    response.headers.pop('Server', None)
    
    return response


def remove_sensitive_headers(response):
    """
    移除敏感响应头
    
    Args:
        response: Flask响应对象
        
    Returns:
        移除敏感头的响应对象
    """
    sensitive_headers = [
        'X-Powered-By',
        'Server',
        'X-AspNet-Version',
        'X-AspNetMvc-Version',
        'X-Runtime',
        'X-Version'
    ]
    
    for header in sensitive_headers:
        response.headers.pop(header, None)
    
    return response

