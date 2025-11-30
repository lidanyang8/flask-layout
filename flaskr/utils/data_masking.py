"""
数据脱敏工具
在返回数据前对敏感信息进行脱敏处理
"""


def mask_email(email):
    """
    脱敏邮箱
    
    Args:
        email: 邮箱地址
        
    Returns:
        脱敏后的邮箱
    """
    if not email or '@' not in email:
        return email

    parts = email.split('@')
    username = parts[0]
    domain = parts[1]

    if len(username) <= 2:
        masked_username = '*' * len(username)
    else:
        masked_username = username[0] + '*' * (len(username) - 2) + username[-1]

    return f'{masked_username}@{domain}'


def mask_phone(phone):
    """
    脱敏手机号
    
    Args:
        phone: 手机号
        
    Returns:
        脱敏后的手机号
    """
    if not phone:
        return phone

    phone_str = str(phone)
    if len(phone_str) <= 4:
        return '*' * len(phone_str)

    return phone_str[:3] + '*' * (len(phone_str) - 7) + phone_str[-4:]


def mask_id_card(id_card):
    """
    脱敏身份证号
    
    Args:
        id_card: 身份证号
        
    Returns:
        脱敏后的身份证号
    """
    if not id_card:
        return id_card

    id_str = str(id_card)
    if len(id_str) <= 8:
        return '*' * len(id_str)

    return id_str[:6] + '*' * (len(id_str) - 10) + id_str[-4:]


def mask_bank_card(card_number):
    """
    脱敏银行卡号
    
    Args:
        card_number: 银行卡号
        
    Returns:
        脱敏后的银行卡号
    """
    if not card_number:
        return card_number

    card_str = str(card_number)
    if len(card_str) <= 8:
        return '*' * len(card_str)

    return card_str[:4] + '*' * (len(card_str) - 8) + card_str[-4:]


def mask_username(username):
    """
    脱敏用户名
    
    Args:
        username: 用户名
        
    Returns:
        脱敏后的用户名
    """
    if not username:
        return username

    username_str = str(username)
    if len(username_str) <= 2:
        return '*' * len(username_str)

    return username_str[0] + '*' * (len(username_str) - 2) + username_str[-1]


def mask_data(data, fields_to_mask=None):
    """
    批量脱敏数据
    
    Args:
        data: 数据字典或列表
        fields_to_mask: 需要脱敏的字段列表，格式: {'field_name': 'mask_type'}
                        mask_type: 'email', 'phone', 'id_card', 'bank_card', 'username'
        
    Returns:
        脱敏后的数据
    """
    if fields_to_mask is None:
        fields_to_mask = {}

    mask_functions = {
        'email': mask_email,
        'phone': mask_phone,
        'id_card': mask_id_card,
        'bank_card': mask_bank_card,
        'username': mask_username
    }

    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if key in fields_to_mask:
                mask_type = fields_to_mask[key]
                if mask_type in mask_functions:
                    result[key] = mask_functions[mask_type](value)
                else:
                    result[key] = value
            elif isinstance(value, (dict, list)):
                result[key] = mask_data(value, fields_to_mask)
            else:
                result[key] = value
        return result
    elif isinstance(data, list):
        return [mask_data(item, fields_to_mask) for item in data]
    else:
        return data


def mask_user_data(user_dict):
    """
    脱敏用户数据
    
    Args:
        user_dict: 用户数据字典
        
    Returns:
        脱敏后的用户数据
    """
    fields_to_mask = {
        'email': 'email',
        'phone': 'phone',
        'username': 'username'
    }

    return mask_data(user_dict, fields_to_mask)
