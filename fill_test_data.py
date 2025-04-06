import datetime
from database.db_manager import db_manager  # или другой объект сессии, если он называется иначе
from database.models import Product

def create_test_products():
    session = db_manager.get_session()
    
    # Пример списка тестовых товаров
    products = [
        Product(
            name="Товар 1",
            description="Описание товара 1",
            price=9.99,
            image_url="https://upload.wikimedia.org/wikipedia/commons/3/3a/Cat03.jpg",
            available=True,
            created_at=datetime.datetime.utcnow()
        ),
        Product(
            name="Товар 2",
            description="Описание товара 2",
            price=19.99,
            image_url="https://cdn.shopify.com/s/files/1/0754/2767/6508/files/what_is_a_jpg_file_480x480.jpg?v=1683282723",
            available=True,
            created_at=datetime.datetime.utcnow()
        ),
        Product(
            name="Товар 3",
            description="Описание товара 3",
            price=29.99,
            image_url="https://example.com/images/product3.jpg",
            available=False,
            created_at=datetime.datetime.utcnow()
        )
    ]
    
    session.add_all(products)
    session.commit()
    session.close()
    print("Тестовые товары успешно созданы!")

if __name__ == "__main__":
    create_test_products()
