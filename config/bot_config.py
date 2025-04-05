import os
from dotenv import load_dotenv

load_dotenv()

class BotConfig:
    """Конфигурация бота"""
    TOKEN = os.getenv('7574595805:AAFjrdshTQuwK4TZrZc_KCfkEs0QmzjmF_Y', '')
    ADMIN_IDS = list(map(int, os.getenv('1', '').split(',')))
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///shop_bot.db')
    LANGUAGES = ['uk', 'en']
    DEFAULT_LANGUAGE = 'uk'