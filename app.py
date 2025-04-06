import telebot
from telebot import custom_filters
from telebot.storage import StateMemoryStorage

from config.bot_config import BotConfig
from config.logging_config import setup_logger
from database.db_manager import db_manager

# Настройка логгера
logger = setup_logger()

# Инициализация бота
state_storage = StateMemoryStorage()
bot = telebot.TeleBot(BotConfig.TOKEN, state_storage=state_storage)

# Удаляем вебхук перед запуском long polling
bot.remove_webhook()

# Импортируем модели перед созданием таблиц
from database.models import User, Product, Order, OrderItem, Payment, Feedback

# Создание таблиц в БД, если их нет
db_manager.create_tables()

# Импорт обработчиков
from handlers import admin_handlers, catalog_handlers, common_handlers, order_handlers, payment_handlers

if __name__ == '__main__':
    logger.info("Запуск бота магазина...")
    
    # Регистрация фильтров
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    
    # Регистрация обработчиков
    common_handlers.register_common_handlers(bot)
    catalog_handlers.register_catalog_handlers(bot)
    admin_handlers.register_admin_handlers(bot)
    
    # Добавьте регистрацию остальных обработчиков, когда они будут готовы
    order_handlers.register_order_handlers(bot)
    payment_handlers.register_payment_handlers(bot)
    
    logger.info("Бот запущен...")
    
    # Запуск бота
    bot.infinity_polling(skip_pending=True)