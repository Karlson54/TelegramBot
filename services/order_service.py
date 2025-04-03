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