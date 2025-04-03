from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from services.user_service import UserService
from services.catalog_service import CatalogService
from services.order_service import OrderService
from keyboards.reply_keyboards import get_admin_keyboard, get_cancel_keyboard, get_main_keyboard
from utils.validators import admin_required, validate_price
from utils.helpers import get_message
from states.user_states import AdminProductStates
from config.logging_config import setup_logger
import telebot

logger = setup_logger()
user_service = UserService()
catalog_service = CatalogService()
order_service = OrderService()

def register_admin_handlers(bot: TeleBot):
    """Регистрация обработчиков для администраторов"""
    
    @bot.message_handler(commands=['admin'])
    @admin_required
    def handle_admin(message: Message):
        """Обработка команды /admin"""
        user_id = message.from_user.id
        language = user_service.get_language(user_id)
        
        bot.send_message(
            user_id,
            get_message('admin_welcome', language),
            reply_markup=get_admin_keyboard(language)
        )
        
        logger.info(f"Admin {user_id} opened admin panel")
    
    # Обработчики добавления товара
    @bot.message_handler(commands=['add_item'])
    @admin_required
    def handle_add_item(message: Message):
        """Обработка команды /add_item"""
        user_id = message.from_user.id
        language = user_service.get_language(user_id)
        
        bot.send_message(
            user_id,
            get_message('enter_product_name', language),
            reply_markup=get_cancel_keyboard(language)
        )
        
        bot.set_state(user_id, AdminProductStates.waiting_for_name, message.chat.id)
        
        logger.info(f"Admin {user_id} started adding a new product")
    
    @bot.message_handler(state=AdminProductStates.waiting_for_name)
    def handle_product_name(message: Message):
        """Обработка ввода имени товара"""
        user_id = message.from_user.id
        language = user_service.get_language(user_id)
        
        # Проверка на отмену
        if message.text == get_message('cancel_btn', language):
            bot.delete_state(user_id, message.chat.id)
            bot.send_message(
                user_id,
                get_message('operation_cancelled', language),
                reply_markup=get_admin_keyboard(language)
            )
            return
        
        # Сохраняем имя товара в память
        with bot.retrieve_data(user_id, message.chat.id) as data:
            data['name'] = message.text
        
        # Запрашиваем описание
        bot.send_message(
            user_id,
            get_message('enter_product_description', language),
            reply_markup=get_cancel_keyboard(language)
        )
        
        bot.set_state(user_id, AdminProductStates.waiting_for_description, message.chat.id)
    
    @bot.message_handler(state=AdminProductStates.waiting_for_description)
    def handle_product_description(message: Message):
        """Обработка ввода описания товара"""
        user_id = message.from_user.id
        language = user_service.get_language(user_id)
        
        # Проверка на отмену
        if message.text == get_message('cancel_btn', language):
            bot.delete_state(user_id, message.chat.id)
            bot.send_message(
                user_id,
                get_message('operation_cancelled', language),
                reply_markup=get_admin_keyboard(language)
            )
            return
        
        # Сохраняем описание товара в память
        with bot.retrieve_data(user_id, message.chat.id) as data:
            data['description'] = message.text
        
        # Запрашиваем цену
        bot.send_message(
            user_id,
            get_message('enter_product_price', language),
            reply_markup=get_cancel_keyboard(language)
        )
        
        bot.set_state(user_id, AdminProductStates.waiting_for_price, message.chat.id)
    
    @bot.message_handler(state=AdminProductStates.waiting_for_price)
    def handle_product_price(message: Message):
        """Обработка ввода цены товара"""
        user_id = message.from_user.id
        language = user_service.get_language(user_id)
        
        # Проверка на отмену
        if message.text == get_message('cancel_btn', language):
            bot.delete_state(user_id, message.chat.id)
            bot.send_message(
                user_id,
                get_message('operation_cancelled', language),
                reply_markup=get_admin_keyboard(language)
            )
            return
        
        # Валидация цены
        is_valid, result = validate_price(message.text)
        
        if not is_valid:
            bot.send_message(
                user_id,
                result  # Сообщение об ошибке
            )
            return
        
        # Сохраняем цену товара в память
        with bot.retrieve_data(user_id, message.chat.id) as data:
            data['price'] = result
        
        # Запрашиваем URL изображения (опционально)
        bot.send_message(
            user_id,
            get_message('enter_product_image', language),
            reply_markup=get_cancel_keyboard(language)
        )
        
        bot.set_state(user_id, AdminProductStates.waiting_for_image, message.chat.id)
    
    @bot.message_handler(state=AdminProductStates.waiting_for_image)
    def handle_product_image(message: Message):
        """Обработка ввода URL изображения товара"""
        user_id = message.from_user.id
        language = user_service.get_language(user_id)
        
        # Проверка на отмену
        if message.text == get_message('cancel_btn', language):
            bot.delete_state(user_id, message.chat.id)
            bot.send_message(
                user_id,
                get_message('operation_cancelled', language),
                reply_markup=get_admin_keyboard(language)
            )
            return
        
        # Сохраняем URL изображения в память
        with bot.retrieve_data(user_id, message.chat.id) as data:
            data['image_url'] = message.text if message.text != "-" else None
            
            # Формируем сообщение с информацией о товаре для подтверждения
            product_info = (
                f"*{get_message('product_name', language)}:* {data['name']}\n"
                f"*{get_message('product_description', language)}:* {data['description']}\n"
                f"*{get_message('product_price', language)}:* {data['price']} грн\n"
            )
            
            if data.get('image_url'):
                product_info += f"*{get_message('product_image', language)}:* {data['image_url']}\n"
        
        # Запрашиваем подтверждение
        bot.send_message(
            user_id,
            get_message('confirm_product_info', language) + "\n\n" + product_info,
            parse_mode='Markdown',
            reply_markup=get_cancel_keyboard(language)
        )
        
        bot.set_state(user_id, AdminProductStates.waiting_for_confirm, message.chat.id)
    
    @bot.message_handler(state=AdminProductStates.waiting_for_confirm)
    def handle_product_confirmation(message: Message):
        """Обработка подтверждения добавления товара"""
        user_id = message.from_user.id
        language = user_service.get_language(user_id)
        
        # Проверка на отмену
        if message.text == get_message('cancel_btn', language):
            bot.delete_state(user_id, message.chat.id)
            bot.send_message(
                user_id,
                get_message('operation_cancelled', language),
                reply_markup=get_admin_keyboard(language)
            )
            return
        
        # Если подтверждено
        if message.text.lower() in ['да', 'yes', '+']:
            with bot.retrieve_data(user_id, message.chat.id) as data:
                # Создаем товар
                product = catalog_service.create_product(
                    name=data['name'],
                    price=data['price'],
                    description=data['description'],
                    image_url=data.get('image_url')
                )
            
            bot.send_message(
                user_id,
                get_message('product_added_success', language),
                reply_markup=get_admin_keyboard(language)
            )
            
            logger.info(f"Admin {user_id} added new product ID: {product.id}")
        else:
            bot.send_message(
                user_id,
                get_message('operation_cancelled', language),
                reply_markup=get_admin_keyboard(language)
            )
        
        # Очищаем состояние
        bot.delete_state(user_id, message.chat.id)
    
    # Обработчики удаления товара
    @bot.message_handler(commands=['remove_item'])
    @admin_required
    def handle_remove_item(message: Message):
        """Обработка команды /remove_item"""
        user_id = message.from_user.id
        language = user_service.get_language(user_id)
        
        # Получаем все товары
        products = catalog_service.get_all_products(available_only=False)
        
        if not products:
            bot.send_message(
                user_id,
                get_message('empty_catalog', language),
                reply_markup=get_admin_keyboard(language)
            )
            return
        
        # Формируем список товаров
        product_list = "\n".join([f"{p.id}. {p.name} - {p.price} грн" for p in products])
        
        bot.send_message(
            user_id,
            get_message('select_product_to_remove', language) + "\n\n" + product_list,
            reply_markup=get_cancel_keyboard(language)
        )
        
        bot.set_state(user_id, AdminProductStates.waiting_for_product_id, message.chat.id)
        
        logger.info(f"Admin {user_id} started removing a product")
    
    @bot.message_handler(state=AdminProductStates.waiting_for_product_id)
    def handle_product_id_for_removal(message: Message):
        """Обработка ввода ID товара для удаления"""
        user_id = message.from_user.id
        language = user_service.get_language(user_id)
        
        # Проверка на отмену
        if message.text == get_message('cancel_btn', language):
            bot.delete_state(user_id, message.chat.id)
            bot.send_message(
                user_id,
                get_message('operation_cancelled', language),
                reply_markup=get_admin_keyboard(language)
            )
            return
        
        # Проверка ID товара
        try:
            product_id = int(message.text)
        except ValueError:
            bot.send_message(
                user_id,
                get_message('invalid_product_id', language)
            )
            return
        
        # Удаляем товар
        result = catalog_service.delete_product(product_id)
        
        if result:
            bot.send_message(
                user_id,
                get_message('product_removed_success', language),
                reply_markup=get_admin_keyboard(language)
            )
            
            logger.info(f"Admin {user_id} removed product ID: {product_id}")
        else:
            bot.send_message(
                user_id,
                get_message('product_not_found', language),
                reply_markup=get_admin_keyboard(language)
            )
        
        # Очищаем состояние
        bot.delete_state(user_id, message.chat.id)
    
    # Обработчик просмотра заказов
    @bot.message_handler(commands=['orders'])
    @admin_required
    def handle_orders(message: Message):
        """Обработка команды /orders"""
        user_id = message.from_user.id
        language = user_service.get_language(user_id)
        
        # Получаем все заказы
        orders = order_service.get_all_orders()
        
        if not orders:
            bot.send_message(
                user_id,
                get_message('no_orders', language),
                reply_markup=get_admin_keyboard(language)
            )
            return
        
        # Формируем список заказов
        for order in orders:
            order_info = (
                f"*{get_message('order_id', language)}: {order.id}*\n"
                f"{get_message('order_status', language)}: {order.status.value}\n"
                f"{get_message('order_total', language)}: {order.total_amount} грн\n"
                f"{get_message('order_date', language)}: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
                f"{get_message('order_items', language)}:\n"
            )
            
            for item in order.items:
                order_info += f"- {item.product.name} x{item.quantity} = {item.price * item.quantity} грн\n"
            
            if order.shipping_address:
                order_info += f"\n{get_message('shipping_address', language)}: {order.shipping_address}\n"
            
            if order.contact_phone:
                order_info += f"{get_message('contact_phone', language)}: {order.contact_phone}\n"
            
            # Отправляем информацию о заказе
            bot.send_message(
                user_id,
                order_info,
                parse_mode='Markdown'
            )
        
        # Отправляем клавиатуру админа
        bot.send_message(
            user_id,
            get_message('admin_menu', language),
            reply_markup=get_admin_keyboard(language)
        )
        
        logger.info(f"Admin {user_id} viewed all orders")
    
    # Обработчик для текстовых сообщений соответствующих кнопкам
    @bot.message_handler(func=lambda message: message.text == get_message('admin_products_btn', user_service.get_language(message.from_user.id)))
    @admin_required
    def handle_admin_products(message: Message):
        """Обработка кнопки управления товарами"""
        user_id = message.from_user.id
        language = user_service.get_language(user_id)
        
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        keyboard.add(
            telebot.types.KeyboardButton('/add_item'),
            telebot.types.KeyboardButton('/remove_item'),
            telebot.types.KeyboardButton(get_message('back_btn', language))
        )
        
        bot.send_message(
            user_id,
            get_message('select_product_action', language),
            reply_markup=keyboard
        )
    
    @bot.message_handler(func=lambda message: message.text == get_message('admin_orders_btn', user_service.get_language(message.from_user.id)))
    @admin_required
    def handle_admin_orders(message: Message):
        """Обработка кнопки управления заказами"""
        handle_orders(message)
    
    @bot.message_handler(func=lambda message: message.text == get_message('back_btn', user_service.get_language(message.from_user.id)))
    def handle_back_button(message: Message):
        """Обработка кнопки назад"""
        user_id = message.from_user.id
        language = user_service.get_language(user_id)
        
        if user_service.is_admin(user_id):
            keyboard = get_admin_keyboard(language)
        else:
            keyboard = get_main_keyboard(language)
        
        bot.send_message(
            user_id,
            get_message('main_menu_message', language),
            reply_markup=keyboard
        )