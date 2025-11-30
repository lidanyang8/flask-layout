"""
输入验证中间件
统一使用utils中的验证函数，避免重复代码
"""
from flaskr.utils.input_validation import validate_content_type

__all__ = ['validate_content_type']
