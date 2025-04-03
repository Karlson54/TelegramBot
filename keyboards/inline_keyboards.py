from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_catalog_keyboard(products, language='uk'):
    """Клавиатура для каталога товаров"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    for product in products:
        button_text = f"{product.name} - {product.price} грн"
        keyboard.add(InlineKeyboardButton(
            text=button_text,
            callback_data=f"product_{product.id}"
        ))
    
    return keyboard

def get_product_detail_keyboard(product_id, language='uk'):
    """Клавиатура для деталей товара"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # Загружаем локализацию
    from utils.helpers import get_message
    
    keyboard.add(
        InlineKeyboardButton(
            text=get_message('add_to_cart_btn', language),
            callback_data=f"add_to_cart_{product_id}"
        ),
        InlineKeyboardButton(
            text=get_message('back_to_catalog_btn', language),
            callback_data="back_to_catalog"
        )
    )
    
    return keyboard

def get_cart_keyboard(language='uk'):
    """Клавиатура для корзины"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # Загружаем локализацию
    from utils.helpers import get_message
    
    keyboard.add(
        InlineKeyboardButton(
            text=get_message('checkout_btn', language),
            callback_data="checkout"
        ),
        InlineKeyboardButton(
            text=get_message('clear_cart_btn', language),
            callback_data="clear_cart"
        )
    )
    
    keyboard.add(
        InlineKeyboardButton(
            text=get_message('continue_shopping_btn', language),
            callback_data="back_to_catalog"
        )
    )
    
    return keyboard

def get_order_confirmation_keyboard(language='uk'):
    """Клавиатура для подтверждения заказа"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # Загружаем локализацию
    from utils.helpers import get_message
    
    keyboard.add(
        InlineKeyboardButton(
            text=get_message('confirm_order_btn', language),
            callback_data="confirm_order"
        ),
        InlineKeyboardButton(
            text=get_message('cancel_order_btn', language),
            callback_data="cancel_order"
        )
    )
    
    return keyboard

def get_payment_methods_keyboard(order_id, language='uk'):
    """Клавиатура для выбора метода оплаты"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    # Загружаем локализацию
    from utils.helpers import get_message
    
    keyboard.add(
        InlineKeyboardButton(
            text=get_message('card_payment_btn', language),
            callback_data=f"pay_card_{order_id}"
        ),
        InlineKeyboardButton(
            text=get_message('cash_payment_btn', language),
            callback_data=f"pay_cash_{order_id}"
        )
    )
    
    return keyboard

def get_language_keyboard():
    """Клавиатура для выбора языка"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton(
            text="🇺🇦 Українська",
            callback_data="language_uk"
        ),
        InlineKeyboardButton(
            text="🇬🇧 English",
            callback_data="language_en"
        )
    )
    
    return keyboard