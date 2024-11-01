import os
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from .models import Base

# Создаем движок SQLAlchemy
engine = create_async_engine(os.getenv('DB_LITE'), echo=True)  # echo=True для вывода SQL-запросов в консоль, удобно для отладки

# Создаем фабрику сессий
session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Функция для инициализации базы данных
async def create_db():
    # Создание таблиц в базе данных (если их еще нет)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Функция для удаления базы данных
async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# # Вызов init_db() при запуске скрипта, чтобы гарантировать, что таблицы созданы
# if __name__ == "__main__":
#     init_db()
