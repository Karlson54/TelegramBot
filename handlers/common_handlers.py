from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from services.user_service import UserService
from keyboards.reply_keyboards import get_main_keyboard, get_admin_keyboard
from keyboards.inline_keyboards import get_language_keyboard
from utils.helpers import get_message
from config.logging_config import setup_logger

logger = setup_logger()
user_service = UserService()

def register_common_handlers(bot: TeleBot):
    """Регистрация обработчиков общих команд"""
    
    @bot.message_handler(commands=['start'])
    def handle_start(message: Message):
        """Обработка команды /start"""
        user_id = message.from_user.id
        user = user_service.get_user(
            telegram_id=user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        
        language = user_service.get_language(user_id)
        
        # Приветственное сообщение
        bot.send_message(
            user_id,
            get_message('welcome_message', language),
            reply_markup=get_language_keyboard()
        )
        
        logger.info(f"User {user_id} started the bot")
    
    @bot.message_handler(commands=['help'])
    def handle_help(message: Message):
        """Обработка команды /help"""
        user_id = message.from_user.id
        language = user_service.get_language(user_id)
        
        bot.send_message(
            user_id,
            get_message('help_message', language),
            parse_mode='Markdown'
        )
        
        logger.info(f"User {user_id} requested help")
    
    @bot.message_handler(commands=['info'])
    def handle_info(message: Message):
        """Обработка команды /info"""
        user_id = message.from_user.id
        language = user_service.get_language(user_id)
        
        bot.send_message(
            user_id,
            get_message('info_message', language),
            parse_mode='Markdown'
        )
        
        logger.info(f"User {user_id} requested info")
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('language_'))
    def handle_language_selection(call: CallbackQuery):
        """Обработка выбора языка"""
        user_id = call.from_user.id
        language = call.data.split('_')[1]
        
        # Обновляем язык пользователя
        user_service.set_language(user_id, language)
        
        # Отправляем сообщение на выбранном языке
        bot.answer_callback_query(call.id, get_message('language_changed', language))
        
        # Отправляем главное меню
        if user_service.is_admin(user_id):
            keyboard = get_admin_keyboard(language)
        else:
            keyboard = get_main_keyboard(language)
        
        bot.edit_message_text(
            get_message('language_selected_message', language),
            user_id,
            call.message.message_id,
            reply_markup=None
        )
        
        bot.send_message(
            user_id,
            get_message('main_menu_message', language),
            reply_markup=keyboard
        )
        
        logger.info(f"User {user_id} selected language: {language}")
    
    # Обработчик для текстовых сообщений соответствующих кнопкам
    @bot.message_handler(func=lambda message: message.text == get_message('help_btn', user_service.get_language(message.from_user.id)))
    def handle_help_button(message: Message):
        handle_help(message)
    
    @bot.message_handler(func=lambda message: message.text == get_message('info_btn', user_service.get_language(message.from_user.id)))
    def handle_info_button(message: Message):
        handle_info(message)