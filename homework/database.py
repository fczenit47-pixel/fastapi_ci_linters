"""
Модуль настройки асинхронной базы данных для FastAPI.

Этот модуль создаёт асинхронный движок SQLAlchemy и фабрику сессий
для работы с SQLite через aiosqlite. Предоставляет генератор сессии
для использования в зависимостях FastAPI и функцию корректного
закрытия движка при завершении приложения.

Атрибуты:
    engine: Асинхронный движок SQLAlchemy для подключения к SQLite.
    async_session_maker: Фабрика для создания асинхронных сессий.

Функции:
    get_session: Генератор сессий для dependency injection в FastAPI.
    close_db: Функция для закрытия всех соединений с БД.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import DeclarativeBase

# Создание асинхронного движка
engine = create_async_engine("sqlite+aiosqlite:///my_recipes.db")

# Фабрика асинхронных сессий
async_session_maker = async_sessionmaker(
    engine,
    expire_on_commit=False,  # Не истекать объекты после commit
    autoflush=False,  # Отключить авто-flush
    autocommit=False,  # Отключить авто-commit
    class_=AsyncSession,  # Явно указываем класс сессии
)


class Base(DeclarativeBase):
    """Базовый класс для всех ORM-моделей.
        Все модели должны наследоваться от этого класса для регистрации
    метаданных и создания таблиц в базе данных."""


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Генератор сессии для использования в зависимостях FastAPI.
        Создаёт новую асинхронную сессию базы данных для каждого запроса
    и автоматически закрывает её после завершения обработки запроса.
    Используется с FastAPI Depends() для автоматического управления
    жизненным циклом сессии.

    Возвращает:
        AsyncSession: Асинхронная сессия SQLAlchemy для работы с БД."""

    async with async_session_maker() as session:
        yield session


async def close_db():
    """Корректно закрывает все соединения с БД при остановке приложения."""
    await engine.dispose()
