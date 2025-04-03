import os
from dotenv import load_dotenv

load_dotenv()

class BotConfig:
    """Конфигурация бота"""
    TOKEN = os.getenv('BOT_TOKEN', '')
    ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS', '').split(',')))
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///shop_bot.db')
    LANGUAGES = ['uk', 'en']
    DEFAULT_LANGUAGE = 'uk'