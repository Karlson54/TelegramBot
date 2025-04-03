from sqlalchemy.orm.exc import NoResultFound
from database.models import User, UserLanguage

class UserRepository:
    """Репозиторий для работы с пользователями"""
    
    def __init__(self, session):
        self.session = session
    
    def get_by_telegram_id(self, telegram_id):
        """Получить пользователя по telegram_id"""
        try:
            return self.session.query(User).filter(User.telegram_id == telegram_id).one()
        except NoResultFound:
            return None
    
    def create_user(self, telegram_id, username=None, first_name=None, last_name=None):
        """Создать нового пользователя"""
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        
        # Проверка на админа
        from config.bot_config import BotConfig
        if telegram_id in BotConfig.ADMIN_IDS:
            user.is_admin = True
            
        self.session.add(user)
        self.session.commit()
        return user
    
    def update_language(self, telegram_id, language):
        """Обновить язык пользователя"""
        user = self.get_by_telegram_id(telegram_id)
        if user:
            user.language = UserLanguage(language)
            self.session.commit()
            return True
        return False
    
    def get_all_admins(self):
        """Получить всех админов"""
        return self.session.query(User).filter(User.is_admin == True).all()