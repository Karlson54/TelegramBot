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