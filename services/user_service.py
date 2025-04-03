from database.repositories.user_repository import UserRepository
from database.db_manager import db_manager
from utils.helpers import load_locale

class UserService:
    """Сервис для работы с пользователями"""
    
    def get_user(self, telegram_id, create_if_not_exists=True, **user_data):
        """Получить пользователя по telegram_id"""
        session = db_manager.get_session()
        try:
            user_repo = UserRepository(session)
            user = user_repo.get_by_telegram_id(telegram_id)
            
            if not user and create_if_not_exists:
                user = user_repo.create_user(
                    telegram_id=telegram_id,
                    username=user_data.get('username'),
                    first_name=user_data.get('first_name'),
                    last_name=user_data.get('last_name')
                )
            
            return user
        finally:
            db_manager.close_session(session)
    
    def set_language(self, telegram_id, language):
        """Установить язык пользователя"""
        session = db_manager.get_session()
        try:
            user_repo = UserRepository(session)
            return user_repo.update_language(telegram_id, language)
        finally:
            db_manager.close_session(session)
    
    def get_language(self, telegram_id):
        """Получить язык пользователя"""
        user = self.get_user(telegram_id)
        if user:
            return user.language.value
        return 'uk'  # язык по умолчанию
    
    def is_admin(self, telegram_id):
        """Проверить, является ли пользователь админом"""
        user = self.get_user(telegram_id)
        return user and user.is_admin
    
    def get_all_admins(self):
        """Получить всех админов"""
        session = db_manager.get_session()
        try:
            user_repo = UserRepository(session)
            return user_repo.get_all_admins()
        finally:
            db_manager.close_session(session)