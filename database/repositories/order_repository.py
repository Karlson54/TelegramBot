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