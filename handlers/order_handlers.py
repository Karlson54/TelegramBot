from typing import List, Dict

# Класс, описывающий заказ
class Order:
    def __init__(self, order_id: int, items: List[str], total: float):
        self.order_id = order_id
        self.items = items
        self.total = total

# "База данных" заказов в виде словаря
orders_db: Dict[int, Order] = {}

def create_order(order_id: int, items: List[str], total: float) -> Order:
    """
    Создает новый заказ.
    :param order_id: Идентификатор заказа.
    :param items: Список товаров в заказе.
    :param total: Итоговая стоимость заказа.
    :return: Объект Order.
    :raises ValueError: Если заказ с таким идентификатором уже существует.
    """
    if order_id in orders_db:
        raise ValueError("Заказ с данным идентификатором уже существует.")
    order = Order(order_id, items, total)
    orders_db[order_id] = order
    return order

def get_order(order_id: int) -> Order:
    """
    Возвращает заказ по идентификатору.
    :param order_id: Идентификатор заказа.
    :return: Объект Order или None, если заказ не найден.
    """
    return orders_db.get(order_id)

def list_orders() -> List[Order]:
    """
    Возвращает список всех заказов.
    """
    return list(orders_db.values())

def cancel_order(order_id: int) -> bool:
    """
    Отменяет заказ по идентификатору.
    :param order_id: Идентификатор заказа.
    :return: True, если заказ успешно удален, иначе False.
    """
    if order_id in orders_db:
        del orders_db[order_id]
        return True
    return False

if __name__ == "__main__":
    # Пример тестирования функций
    try:
        order = create_order(1, ["Товар 1", "Товар 2"], 1500.00)
        print("Создан заказ:", order.__dict__)
    except ValueError as e:
        print(e)

    all_orders = list_orders()
    print("Список заказов:")
    for o in all_orders:
        print(o.__dict__)

    # Получение конкретного заказа
    order = get_order(1)
    print("Полученный заказ:", order.__dict__ if order else "Заказ не найден")

    # Отмена заказа
    if cancel_order(1):
        print("Заказ успешно отменен.")
    else:
        print("Не удалось отменить заказ.")
