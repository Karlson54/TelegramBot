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