import re
from functools import wraps

def validate_price(price_str):
    """Валидация цены"""
    try:
        price = float(price_str)
        if price <= 0:
            return False, "Цена должна быть положительным числом"
        return True, price
    except ValueError:
        return False, "Некорректный формат цены. Используйте числа, например 9.99"

def validate_phone(phone_str):
    """Валидация номера телефона"""
    # Простая проверка на формат телефона
    phone_pattern = re.compile(r'^\+?[0-9]{10,15}$')
    if phone_pattern.match(phone_str):
        return True, phone_str
    return False, "Некорректный формат номера телефона. Используйте формат +380XXXXXXXXX"

def admin_required(func):
    """Декоратор для проверки прав администратора"""
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        from config.bot_config import BotConfig
        if message.from_user.id not in BotConfig.ADMIN_IDS:
            return message.reply("У вас нет прав для выполнения этой команды.")
        return func(message, *args, **kwargs)
    return wrapper