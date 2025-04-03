import json
import os

def load_locale(language):
    """Загрузить локализацию для выбранного языка"""
    locale_path = os.path.join('locales', f"{language}.json")
    
    try:
        with open(locale_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Возвращаем локализацию по умолчанию
        with open(os.path.join('locales', 'uk.json'), 'r', encoding='utf-8') as f:
            return json.load(f)

def get_message(key, language='uk'):
    """Получить сообщение по ключу и языку"""
    locale = load_locale(language)
    return locale.get(key, locale.get('default_message', 'Message not found'))