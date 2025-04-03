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