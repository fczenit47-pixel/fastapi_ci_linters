"""
Модуль Pydantic-схем для валидации данных рецептов.

Этот модуль определяет схемы для создания и чтения рецептов в API.
Используется Pydantic v2 с поддержкой валидации через Field.

Классы:
    RecipeCreate: Схема для создания нового рецепта.
    RecipeRead: Схема для чтения рецепта из базы данных.
"""
from pydantic import BaseModel,Field,ConfigDict

class RecipeCreate(BaseModel):
    """
    Схема для создания нового рецепта.

    Используется в POST-запросах для валидации входящих данных.
    Все поля обязательны, кроме views (по умолчанию 0).
    """

    name_dish :str = Field(..., min_length=1, description="Название блюда")
    views: int = Field(0, ge=0, description="Количество просмотров")
    cooking_time: int = Field(..., gt=0, description="Время приготовления в минутах")
    ingredients: str = Field(..., description="Список ингредиентов")
    description: str = Field(..., description="Описание рецепта")

class RecipeRead(BaseModel):
    """
    Схема для чтения рецепта из базы данных.

    Используется в GET-запросах для сериализации данных из ORM-моделей.
    Включает все поля RecipeCreate плюс автоматический id.
    """
    id : int
    name_dish :str = Field(..., min_length=1, description="Название блюда")
    views: int = Field(0, ge=0, description="Количество просмотров")
    cooking_time: int = Field(..., gt=0, description="Время приготовления в минутах")
    ingredients: str = Field(..., description="Список ингредиентов")
    description: str = Field(..., description="Описание рецепта")

    model_config = ConfigDict(from_attributes=True)