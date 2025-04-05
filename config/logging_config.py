import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger():
    """Настройка логгера"""
    if not os.path.exists('logs'):
        os.makedirs('logs')
        
    logger = logging.getLogger('bot_logger')
    
    # Проверяем, были ли уже добавлены обработчики к логгеру
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Лог в файл
        file_handler = RotatingFileHandler(
            'logs/bot.log', 
            maxBytes=1024*1024*5,  # 5 MB
            backupCount=3
        )
        file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_format)
        
        # Лог в консоль
        console_handler = logging.StreamHandler()
        console_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_format)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger