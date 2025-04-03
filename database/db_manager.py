from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from config.bot_config import BotConfig

Base = declarative_base()

class DatabaseManager:
    """Класс для управления подключением к базе данных"""
    
    def __init__(self):
        self.engine = create_engine(BotConfig.DATABASE_URL)
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
    
    def create_tables(self):
        """Создать все таблицы"""
        Base.metadata.create_all(self.engine)
    
    def get_session(self):
        """Получить сессию базы данных"""
        return self.Session()
    
    def close_session(self, session):
        """Закрыть сессию базы данных"""
        session.close()
        
# Создание экземпляра менеджера БД
db_manager = DatabaseManager()