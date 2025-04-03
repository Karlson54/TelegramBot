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