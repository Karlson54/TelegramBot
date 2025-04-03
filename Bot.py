# Структура проекта
"""
telegram_shop_bot/
│
├── config/
│   ├── __init__.py
│   ├── bot_config.py   # Конфигурация бота
│   └── logging_config.py  # Настройки логирования
│
├── database/
│   ├── __init__.py
│   ├── db_manager.py   # Интерфейс для работы с БД
│   ├── models.py       # Модели данных
│   └── repositories/   # Репозитории для работы с данными
│      ├── __init__.py
│      ├── product_repository.py
│      ├── order_repository.py
│      └── user_repository.py
│
├── handlers/
│   ├── __init__.py
│   ├── admin_handlers.py    # Обработчики для админов
│   ├── catalog_handlers.py  # Обработчики каталога
│   ├── common_handlers.py   # Обработчики общих команд
│   ├── order_handlers.py    # Обработчики заказов
│   └── payment_handlers.py  # Обработчики оплаты
│
├── keyboards/
│   ├── __init__.py
│   ├── inline_keyboards.py  # Инлайн клавиатуры
│   └── reply_keyboards.py   # Reply клавиатуры
│
├── services/
│   ├── __init__.py
│   ├── catalog_service.py   # Бизнес-логика каталога
│   ├── order_service.py     # Бизнес-логика заказов
│   ├── payment_service.py   # Бизнес-логика платежей
│   └── user_service.py      # Бизнес-логика пользователей
│
├── states/
│   ├── __init__.py
│   └── user_states.py       # Пользовательские состояния
│
├── utils/
│   ├── __init__.py
│   ├── validators.py        # Валидаторы данных
│   └── helpers.py           # Вспомогательные функции
│
├── locales/                 # Локализация для мультиязычности
│   ├── en.json
│   └── uk.json
│
├── app.py                   # Точка входа в приложение
├── requirements.txt         # Зависимости
└── README.md                # Документация
"""

# config/bot_config.py
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

# config/logging_config.py
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger():
    """Настройка логгера"""
    if not os.path.exists('logs'):
        os.makedirs('logs')
        
    logger = logging.getLogger('bot_logger')
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

# database/db_manager.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from config.bot_config import BotConfig

Base = declarative_base()

class DatabaseManager:
    """Класс для управления подключением к базе данных"""
    
    def __init__(self):
        self.engine = create_engine(BotConfig.DATABASE_URL)
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
    
    def create_tables(self):
        """Создать все таблицы"""
        Base.metadata.create_all(self.engine)
    
    def get_session(self):
        """Получить сессию базы данных"""
        return self.Session()
    
    def close_session(self, session):
        """Закрыть сессию базы данных"""
        session.close()
        
# Создание экземпляра менеджера БД
db_manager = DatabaseManager()

# database/models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from database.db_manager import Base
import enum
import datetime

class UserLanguage(enum.Enum):
    UK = 'uk'
    EN = 'en'

class User(Base):
    """Модель пользователя"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    language = Column(Enum(UserLanguage), default=UserLanguage.UK)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Отношения
    orders = relationship("Order", back_populates="user")
    feedback = relationship("Feedback", back_populates="user")

class Product(Base):
    """Модель товара"""
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    image_url = Column(String(1024), nullable=True)
    available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Отношения
    order_items = relationship("OrderItem", back_populates="product")

class OrderStatus(enum.Enum):
    NEW = 'new'
    PENDING_PAYMENT = 'pending_payment'
    PAID = 'paid'
    PROCESSING = 'processing'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'

class Order(Base):
    """Модель заказа"""
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.NEW)
    total_amount = Column(Float, default=0.0)
    shipping_address = Column(Text, nullable=True)
    contact_phone = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Отношения
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    payments = relationship("Payment", back_populates="order")

class OrderItem(Base):
    """Модель элемента заказа"""
    __tablename__ = 'order_items'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, default=1)
    price = Column(Float, nullable=False)
    
    # Отношения
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

class PaymentStatus(enum.Enum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    REFUNDED = 'refunded'

class Payment(Base):
    """Модель платежа"""
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_method = Column(String(100), nullable=True)
    transaction_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Отношения
    order = relationship("Order", back_populates="payments")

class Feedback(Base):
    """Модель обратной связи"""
    __tablename__ = 'feedback'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Отношения
    user = relationship("User", back_populates="feedback")

# database/repositories/user_repository.py
from sqlalchemy.orm.exc import NoResultFound
from database.models import User, UserLanguage

class UserRepository:
    """Репозиторий для работы с пользователями"""
    
    def __init__(self, session):
        self.session = session
    
    def get_by_telegram_id(self, telegram_id):
        """Получить пользователя по telegram_id"""
        try:
            return self.session.query(User).filter(User.telegram_id == telegram_id).one()
        except NoResultFound:
            return None
    
    def create_user(self, telegram_id, username=None, first_name=None, last_name=None):
        """Создать нового пользователя"""
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        
        # Проверка на админа
        from config.bot_config import BotConfig
        if telegram_id in BotConfig.ADMIN_IDS:
            user.is_admin = True
            
        self.session.add(user)
        self.session.commit()
        return user
    
    def update_language(self, telegram_id, language):
        """Обновить язык пользователя"""
        user = self.get_by_telegram_id(telegram_id)
        if user:
            user.language = UserLanguage(language)
            self.session.commit()
            return True
        return False
    
    def get_all_admins(self):
        """Получить всех админов"""
        return self.session.query(User).filter(User.is_admin == True).all()

# database/repositories/product_repository.py
from sqlalchemy.orm.exc import NoResultFound
from database.models import Product

class ProductRepository:
    """Репозиторий для работы с товарами"""
    
    def __init__(self, session):
        self.session = session
    
    def get_all_products(self, available_only=True):
        """Получить все товары"""
        query = self.session.query(Product)
        if available_only:
            query = query.filter(Product.available == True)
        return query.all()
    
    def get_by_id(self, product_id):
        """Получить товар по ID"""
        try:
            return self.session.query(Product).filter(Product.id == product_id).one()
        except NoResultFound:
            return None
    
    def create_product(self, name, price, description=None, image_url=None):
        """Создать новый товар"""
        product = Product(
            name=name,
            description=description,
            price=price,
            image_url=image_url
        )
        self.session.add(product)
        self.session.commit()
        return product
    
    def update_product(self, product_id, **kwargs):
        """Обновить товар"""
        product = self.get_by_id(product_id)
        if product:
            for key, value in kwargs.items():
                if hasattr(product, key):
                    setattr(product, key, value)
            self.session.commit()
            return product
        return None
    
    def delete_product(self, product_id):
        """Удалить товар (установить available=False)"""
        product = self.get_by_id(product_id)
        if product:
            product.available = False
            self.session.commit()
            return True
        return False

# database/repositories/order_repository.py
from sqlalchemy.orm.exc import NoResultFound
from database.models import Order, OrderItem, OrderStatus

class OrderRepository:
    """Репозиторий для работы с заказами"""
    
    def __init__(self, session):
        self.session = session
    
    def get_all_orders(self):
        """Получить все заказы"""
        return self.session.query(Order).all()
    
    def get_by_id(self, order_id):
        """Получить заказ по ID"""
        try:
            return self.session.query(Order).filter(Order.id == order_id).one()
        except NoResultFound:
            return None
    
    def get_user_orders(self, user_id):
        """Получить заказы пользователя"""
        return self.session.query(Order).filter(Order.user_id == user_id).all()
    
    def create_order(self, user_id):
        """Создать новый заказ"""
        order = Order(
            user_id=user_id,
            status=OrderStatus.NEW
        )
        self.session.add(order)
        self.session.commit()
        return order
    
    def add_item_to_order(self, order_id, product_id, quantity, price):
        """Добавить товар к заказу"""
        order_item = OrderItem(
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            price=price
        )
        self.session.add(order_item)
        self.session.commit()
        
        # Обновление общей суммы заказа
        self._update_order_total(order_id)
        return order_item
    
    def update_order_status(self, order_id, status):
        """Обновить статус заказа"""
        order = self.get_by_id(order_id)
        if order:
            order.status = OrderStatus(status)
            self.session.commit()
            return order
        return None
    
    def _update_order_total(self, order_id):
        """Обновить общую сумму заказа"""
        order = self.get_by_id(order_id)
        if order:
            total = sum(item.price * item.quantity for item in order.items)
            order.total_amount = total
            self.session.commit()

# utils/validators.py
import re
from functools import wraps

def validate_price(price_str):
    """Валидация цены"""
    try:
        price = float(price_str)
        if price <= 0:
            return False, "Цена должна быть положительным числом"
        return True, price
    except ValueError:
        return False, "Некорректный формат цены. Используйте числа, например 9.99"

def validate_phone(phone_str):
    """Валидация номера телефона"""
    # Простая проверка на формат телефона
    phone_pattern = re.compile(r'^\+?[0-9]{10,15}$')
    if phone_pattern.match(phone_str):
        return True, phone_str
    return False, "Некорректный формат номера телефона. Используйте формат +380XXXXXXXXX"

def admin_required(func):
    """Декоратор для проверки прав администратора"""
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        from config.bot_config import BotConfig
        if message.from_user.id not in BotConfig.ADMIN_IDS:
            return message.reply("У вас нет прав для выполнения этой команды.")
        return func(message, *args, **kwargs)
    return wrapper

# utils/helpers.py
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

# states/user_states.py
from telebot.handler_backends import State, StatesGroup

class AdminProductStates(StatesGroup):
    """Состояния для админа при работе с товарами"""
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_price = State()
    waiting_for_image = State()
    waiting_for_confirm = State()
    waiting_for_product_id = State()

class OrderStates(StatesGroup):
    """Состояния для оформления заказа"""
    selecting_products = State()
    entering_shipping_address = State()
    entering_phone = State()
    confirming_order = State()
    waiting_for_payment = State()

class FeedbackStates(StatesGroup):
    """Состояния для обратной связи"""
    waiting_for_message = State()

# keyboards/reply_keyboards.py
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

# keyboards/inline_keyboards.py
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

# services/user_service.py
from database.repositories.user_repository import UserRepository
from database.db_manager import db_manager
from utils.helpers import load_locale

class UserService:
    """Сервис для работы с пользователями"""
    
    def get_user(self, telegram_id, create_if_not_exists=True, **user_data):
        """Получить пользователя по telegram_id"""
        session = db_manager.get_session()
        try:
            user_repo = UserRepository(session)
            user = user_repo.get_by_telegram_id(telegram_id)
            
            if not user and create_if_not_exists:
                user = user_repo.create_user(
                    telegram_id=telegram_id,
                    username=user_data.get('username'),
                    first_name=user_data.get('first_name'),
                    last_name=user_data.get('last_name')
                )
            
            return user
        finally:
            db_manager.close_session(session)
    
    def set_language(self, telegram_id, language):
        """Установить язык пользователя"""
        session = db_manager.get_session()
        try:
            user_repo = UserRepository(session)
            return user_repo.update_language(telegram_id, language)
        finally:
            db_manager.close_session(session)
    
    def get_language(self, telegram_id):
        """Получить язык пользователя"""
        user = self.get_user(telegram_id)
        if user:
            return user.language.value
        return 'uk'  # язык по умолчанию
    
    def is_admin(self, telegram_id):
        """Проверить, является ли пользователь админом"""
        user = self.get_user(telegram_id)
        return user and user.is_admin
    
    def get_all_admins(self):
        """Получить всех админов"""
        session = db_manager.get_session()
        try:
            user_repo = UserRepository(session)
            return user_repo.get_all_admins()
        finally:
            db_manager.close_session(session)

# services/catalog_service.py
from database.repositories.product_repository import ProductRepository
from database.db_manager import db_manager

class CatalogService:
    """Сервис для работы с каталогом товаров"""
    
    def get_all_products(self, available_only=True):
        """Получить все товары"""
        session = db_manager.get_session()
        try:
            product_repo = ProductRepository(session)
            return product_repo.get_all_products(available_only)
        finally:
            db_manager.close_session(session)
    
    def get_product(self, product_id):
        """Получить товар по ID"""
        session = db_manager.get_session()
        try:
            product_repo = ProductRepository(session)
            return product_repo.get_by_id(product_id)
        finally:
            db_manager.close_session(session)
    
    def create_product(self, name, price, description=None, image_url=None):
        """Создать новый товар"""
        session = db_manager.get_session()
        try:
            product_repo = ProductRepository(session)
            return product_repo.create_product(
                name=name,
                price=price,
                description=description,
                image_url=image_url
            )
        finally:
            db_manager.close_session(session)
    
    def update_product(self, product_id, **kwargs):
        """Обновить товар"""
        session = db_manager.get_session()
        try:
            product_repo = ProductRepository(session)
            return product_repo.update_product(product_id, **kwargs)
        finally:
            db_manager.close_session(session)
    
    def delete_product(self, product_id):
        """Удалить товар"""
        session = db_manager.get_session()
        try:
            product_repo = ProductRepository(session)
            return product_repo.delete_product(product_id)
        finally:
            db_manager.close_session(session)

# services/order_service.py
from database.repositories.order_repository import OrderRepository
from database.db_manager import db_manager
from database.models import OrderStatus

class OrderService:
    """Сервис для работы с заказами"""
    
    def create_order(self, user_id):
        """Создать новый заказ"""
        session = db_manager.get_session()
        try:
            order_repo = OrderRepository(session)
            return order_repo.create_order(user_id)
        finally:
            db_manager.close_session(session)
    
    def add_product_to_order(self, order_id, product_id, quantity, price):
        """Добавить товар к заказу"""
        session = db_manager.get_session()
        try:
            order_repo = OrderRepository(session)
            return order_repo.add_item_to_order(
                order_id=order_id,
                product_id=product_id,
                quantity=quantity,
                price=price
            )
        finally:
            db_manager.close_session(session)
    
    def update_order_status(self, order_id, status):
        """Обновить статус заказа"""
        session = db_manager.get_session()
        try:
            order_repo = OrderRepository(session)
            return order_repo.update_order_status(order_id, status)
        finally:
            db_manager.close_session(session)
    
# services/order_service.py (продолжение)
    def get_order(self, order_id):
        """Получить заказ по ID"""
        session = db_manager.get_session()
        try:
            order_repo = OrderRepository(session)
            return order_repo.get_by_id(order_id)
        finally:
            db_manager.close_session(session)
    
    def get_user_orders(self, user_id):
        """Получить заказы пользователя"""
        session = db_manager.get_session()
        try:
            order_repo = OrderRepository(session)
            return order_repo.get_user_orders(user_id)
        finally:
            db_manager.close_session(session)
    
    def get_all_orders(self):
        """Получить все заказы"""
        session = db_manager.get_session()
        try:
            order_repo = OrderRepository(session)
            return order_repo.get_all_orders()
        finally:
            db_manager.close_session(session)

# services/payment_service.py
from database.db_manager import db_manager
from database.models import Payment, PaymentStatus, OrderStatus

class PaymentService:
    """Сервис для работы с платежами"""
    
    def create_payment(self, order_id, amount, payment_method):
        """Создать новый платеж"""
        session = db_manager.get_session()
        try:
            payment = Payment(
                order_id=order_id,
                amount=amount,
                payment_method=payment_method,
                status=PaymentStatus.PENDING
            )
            session.add(payment)
            session.commit()
            return payment
        finally:
            db_manager.close_session(session)
    
    def update_payment_status(self, payment_id, status):
        """Обновить статус платежа"""
        session = db_manager.get_session()
        try:
            payment = session.query(Payment).filter(Payment.id == payment_id).first()
            if payment:
                payment.status = PaymentStatus(status)
                session.commit()
                
                # Если платеж выполнен, то обновляем статус заказа
                if status == PaymentStatus.COMPLETED.value:
                    order = payment.order
                    order.status = OrderStatus.PAID
                    session.commit()
                
                return payment
            return None
        finally:
            db_manager.close_session(session)
    
    def get_payment(self, payment_id):
        """Получить платеж по ID"""
        session = db_manager.get_session()
        try:
            return session.query(Payment).filter(Payment.id == payment_id).first()
        finally:
            db_manager.close_session(session)
    
    def get_order_payments(self, order_id):
        """Получить платежи по заказу"""
        session = db_manager.get_session()
        try:
            return session.query(Payment).filter(Payment.order_id == order_id).all()
        finally:
            db_manager.close_session(session)

# handlers/common_handlers.py
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

# handlers/catalog_handlers.py
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

# handlers/admin_handlers.py
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

# handlers/order_handlers.py
from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from services.user_service import UserService
from services.catalog_service import CatalogService
from services.order_service import OrderService
from services.payment_service import PaymentService
from keyboards.inline_keyboards import get_cart_keyboard, get_order_confirmation_keyboard, get_payment_methods_keyboard
from keyboards.reply_keyboards import get_main_keyboard, get_cancel_keyboard
from utils.helpers import get_message
from utils.validators import validate_phone
from states.user_states import OrderStates
from config.logging_config import setup_logger
from database.models import OrderStatus

logger = setup_logger()
user_service = UserService()
catalog_service = CatalogService()
order_service = OrderService()
payment_service = PaymentService()

# Временное хранилище корзин пользователей
# В реальном проекте лучше использовать Redis или другое хранилище
user_carts = {}

def register_order_handlers(bot: TeleBot):
    """Регистрация обработчиков заказов"""
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('add_to_cart_'))
    def handle_add_to_cart(call: CallbackQuery):
        """Обработка добавления товара в корзину"""
        user_id = call.from_user.id
        language = user_service.get_language(user_id)
        
        # Получаем ID товара
        product_id = int(call.data.split('_')[-1])
        
        # Получаем информацию о товаре
        product = catalog_service.get_product(product_id)
        
        if not product:
            bot.answer_callback_query(call.id, get_message('product_not_found', language))
            return
        
        # Добавляем товар в корзину
        if user_id not in user_carts:
            user_carts[user_id] = []
        
        # Проверяем, есть ли товар уже в корзине
        for item in user_carts[user_id]:
            if item['product_id'] == product_id:
                item['quantity'] += 1
                break
        else:
            # Добавляем новый товар
            user_carts[user_id].append({
                'product_id': product_id,
                'name': product.name,
                'price': product.price,
                'quantity': 1
            })
        
        # Отвечаем пользователю
        bot.answer_callback_query