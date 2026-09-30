"""
Модуль с ORM‑моделями базы данных для сервиса рецептов.

Этот модуль содержит единственную ORM‑модель — RecipesModel, которая отображает
таблицу all_recipes в базе данных. Модель интегрируется с FastAPI через SQLAlchemy.

Таблица: all_recipes
--------------------
Хранит информацию о рецептах блюд: название, время приготовления, ингредиенты,
описание и счётчик просмотров.
"""
from sqlalchemy import Integer, String,Text
from sqlalchemy.orm import Mapped, mapped_column
from fastapi_ci_linters.homework.database import Base


class RecipesModel(Base):
    """
    ORM‑модель рецепта блюда.
    Соответствует таблице all_recipes в базе данных.
    Используется для сохранения, загрузки и изменения записей о рецептах.
    """
    __tablename__ = "all_recipes"

    id: Mapped[int] = mapped_column(Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )
    """
    Уникальный идентификатор рецепта.

    - Тип: int
    - Первичный ключ
    - Автоинкремент
    - Индексируется
    """

    name_dish: Mapped[str] = mapped_column(
        String,
        nullable=False,
        comment="Название блюда",
    )
    """
    Название блюда.

    - Тип в БД: VARCHAR (String)
    - Обязательное поле (NOT NULL)
    """

    views: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Количество просмотров",
    )
    """
    Количество просмотров рецепта.

    - Тип в БД: INTEGER
    - Обязательное поле
    - Значение по умолчанию: 0
    """

    cooking_time: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Время приготовления в минутах",
    )
    """
    Время приготовления блюда в минутах.

    - Тип в БД: INTEGER
    - Обязательное поле (NOT NULL)
    """

    ingredients: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        comment="Список ингредиентов ",
    )
    """
    Список ингредиентов в текстовом виде.

    - Тип в БД: TEXT
    - Опциональное поле (может быть NULL)
    """
    description: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        comment="Текстовое описание рецепта",
    )
    """
    Текстовое описание рецепта.

    - Тип в БД: TEXT
    - Опциональное поле (может быть NULL)
    """