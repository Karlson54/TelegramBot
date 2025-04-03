from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard(language='uk'):
    """Главная клавиатура"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    # Загружаем локализацию
    from utils.helpers import get_message
    
    keyboard.add(
        KeyboardButton(get_message('catalog_btn', language)),
        KeyboardButton(get_message('info_btn', language)),
        KeyboardButton(get_message('feedback_btn', language)),
        KeyboardButton(get_message('help_btn', language))
    )
    
    return keyboard

def get_admin_keyboard(language='uk'):
    """Админская клавиатура"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    # Загружаем локализацию
    from utils.helpers import get_message
    
    # Добавляем обычные кнопки
    keyboard.add(
        KeyboardButton(get_message('catalog_btn', language)),
        KeyboardButton(get_message('info_btn', language))
    )
    
    # Добавляем админские кнопки
    keyboard.add(
        KeyboardButton(get_message('admin_products_btn', language)),
        KeyboardButton(get_message('admin_orders_btn', language))
    )
    
    keyboard.add(KeyboardButton(get_message('help_btn', language)))
    
    return keyboard

def get_cancel_keyboard(language='uk'):
    """Клавиатура отмены"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    
    # Загружаем локализацию
    from utils.helpers import get_message
    
    keyboard.add(KeyboardButton(get_message('cancel_btn', language)))
    
    return keyboard