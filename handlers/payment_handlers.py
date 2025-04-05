import uuid
from typing import Optional

# Класс, описывающий платеж
class Payment:
    def __init__(self, payment_id: str, order_id: int, amount: float, status: str = "pending"):
        self.payment_id = payment_id
        self.order_id = order_id
        self.amount = amount
        self.status = status

# "База данных" платежей в виде словаря
payments_db = {}

def initiate_payment(order_id: int, amount: float) -> Payment:
    """
    Инициирует платеж для заказа.
    :param order_id: Идентификатор заказа.
    :param amount: Сумма платежа.
    :return: Объект Payment.
    """
    payment_id = str(uuid.uuid4())
    payment = Payment(payment_id, order_id, amount)
    payments_db[payment_id] = payment
    return payment

def confirm_payment(payment_id: str) -> Optional[Payment]:
    """
    Подтверждает платеж, переводя его в статус "completed".
    :param payment_id: Идентификатор платежа.
    :return: Обновленный объект Payment или None, если платеж не найден.
    """
    payment = payments_db.get(payment_id)
    if payment:
        payment.status = "completed"
        return payment
    return None

def cancel_payment(payment_id: str) -> Optional[Payment]:
    """
    Отменяет платеж, переводя его в статус "cancelled".
    :param payment_id: Идентификатор платежа.
    :return: Обновленный объект Payment или None, если платеж не найден.
    """
    payment = payments_db.get(payment_id)
    if payment:
        payment.status = "cancelled"
        return payment
    return None

if __name__ == "__main__":
    # Пример тестирования функций
    payment = initiate_payment(1, 1500.00)
    print("Инициирован платеж:", payment.__dict__)

    confirmed = confirm_payment(payment.payment_id)
    print("Подтвержденный платеж:", confirmed.__dict__ if confirmed else "Платеж не найден")

    # Для демонстрации отмены платежа, инициируем новый платеж
    payment2 = initiate_payment(2, 2500.00)
    cancelled = cancel_payment(payment2.payment_id)
    print("Отмененный платеж:", cancelled.__dict__ if cancelled else "Платеж не найден")
