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