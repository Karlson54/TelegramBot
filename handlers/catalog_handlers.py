from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from services.catalog_service import CatalogService
from services.user_service import UserService
from keyboards.inline_keyboards import get_catalog_keyboard, get_product_detail_keyboard
from utils.helpers import get_message
from config.logging_config import setup_logger

logger = setup_logger()
catalog_service = CatalogService()
user_service = UserService()

def register_catalog_handlers(bot: TeleBot):
    """Регистрация обработчиков каталога"""
    
    @bot.message_handler(commands=['catalog'])
    def handle_catalog(message: Message):
        """Обработка команды /catalog"""
        user_id = message.from_user.id
        language = user_service.get_language(user_id)
        
        # Получаем все товары
        products = catalog_service.get_all_products()
        
        if not products:
            bot.send_message(
                user_id,
                get_message('empty_catalog', language)
            )
            return
        
        # Отправляем сообщение с каталогом
        bot.send_message(
            user_id,
            get_message('catalog_title', language),
            reply_markup=get_catalog_keyboard(products, language)
        )
        
        logger.info(f"User {user_id} opened catalog")
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('product_'))
    def handle_product_selection(call: CallbackQuery):
        """Обработка выбора товара из каталога"""
        user_id = call.from_user.id
        language = user_service.get_language(user_id)
        
        # Получаем ID товара
        product_id = int(call.data.split('_')[1])
        
        # Получаем информацию о товаре
        product = catalog_service.get_product(product_id)
        
        if not product:
            bot.answer_callback_query(call.id, get_message('product_not_found', language))
            return
        
        # Формируем сообщение с информацией о товаре
        product_info = (
            f"*{product.name}*\n\n"
            f"{product.description}\n\n"
            f"_{get_message('price_label', language)}: {product.price} грн_"
        )
        
        # Отправляем сообщение с информацией о товаре
        if product.image_url:
            bot.send_photo(
                user_id,
                product.image_url,
                caption=product_info,
                parse_mode='Markdown',
                reply_markup=get_product_detail_keyboard(product_id, language)
            )
        else:
            bot.send_message(
                user_id,
                product_info,
                parse_mode='Markdown',
                reply_markup=get_product_detail_keyboard(product_id, language)
            )
        
        logger.info(f"User {user_id} viewed product {product_id}")
    
    @bot.callback_query_handler(func=lambda call: call.data == 'back_to_catalog')
    def handle_back_to_catalog(call: CallbackQuery):
        """Обработка возврата к каталогу"""
        user_id = call.from_user.id
        language = user_service.get_language(user_id)
        
        # Получаем все товары
        products = catalog_service.get_all_products()
        
        # Обновляем сообщение с каталогом
        bot.edit_message_text(
            get_message('catalog_title', language),
            user_id,
            call.message.message_id,
            reply_markup=get_catalog_keyboard(products, language)
        )
        
        logger.info(f"User {user_id} returned to catalog")
    
    # Обработчик для текстовых сообщений соответствующих кнопкам
    @bot.message_handler(func=lambda message: message.text == get_message('catalog_btn', user_service.get_language(message.from_user.id)))
    def handle_catalog_button(message: Message):
        handle_catalog(message)