"""
Точка входа FastAPI‑приложения для сервиса рецептов.

Назначение модуля
-----------------
Этот модуль:
- инициализирует FastAPI‑приложение;
- настраивает базу данных при старте (создание таблиц);
- определяет HTTP‑эндпоинты для работы с рецептами:
  - создание нового рецепта;
  - получение списка всех рецептов;
  - получение рецепта по ID с увеличением счётчика просмотров.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_ci_linters.homework.database import Base, engine, get_session
from fastapi_ci_linters.homework.models import RecipesModel
from fastapi_ci_linters.homework.schemas import RecipeCreate, RecipeRead


async def setup_database() -> None:
    """
    Создаёт все таблицы базы данных, если они ещё не существуют.

    Используется движок engine и метаданные Base.metadata.
    Вызывается один раз при старте приложения через событие startup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await setup_database()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Recipes API",
    description="API для управления рецептами блюд: создание, получение списка и деталей.",
)


@app.post(
    "/add_recipe",
    response_model=RecipeRead,
    tags=["Рецепты"],
    summary="Добавить новый рецепт",
)
async def create_recipe(
    recipe: RecipeCreate, db: AsyncSession = Depends(get_session)
) -> RecipesModel:
    """
    Создаёт новый рецепт в базе данных.

    Параметры запроса (тело запроса, JSON):
    - name_dish (str, обязательное): название блюда;
    - views (int, опциональное): начальное количество просмотров (по умолчанию 0);
    - cooking_time (int, обязательное): время приготовления в минутах;
    - ingredients (str | None, опциональное): список ингредиентов;
    - description (str | None, опциональное): текстовое описание рецепта.

    Возвращаемое значение:
    - Созданный объект рецепта в формате RecipeRead (с id и актуальными полями).

        Логика:
    1. Из входящей схемы RecipeCreate создаётся экземпляр RecipesModel.
    2. Объект добавляется в сессию базы данных.
    3. Транзакция фиксируется (commit).
    4. Объект обновляется из БД (refresh), чтобы получить сгенерированный id.
    5. Возвращается созданный рецепт.
    """
    db_recipe = RecipesModel(
        name_dish=recipe.name_dish,
        views=recipe.views,
        cooking_time=recipe.cooking_time,
        ingredients=recipe.ingredients,
        description=recipe.description,
    )

    db.add(db_recipe)

    await db.commit()
    await db.refresh(db_recipe)
    return db_recipe


@app.get(
    "/recipes",
    response_model=list[RecipeRead],
    tags=["Рецепты"],
    summary="Получить все рецепты",
)
async def get_recipes(db: AsyncSession = Depends(get_session)):
    """
    Возвращает список всех рецептов из базы данных.

    Возвращаемое значение:
    - Список объектов рецептов в формате RecipeRead.

        Логика:
    1. Выполняется SELECT * FROM all_recipes через SQLAlchemy.
    2. Все записи извлекаются через scalars().all().
    3. Возвращается список ORM‑объектов, которые автоматически
       сериализуются в JSON согласно response_model=RecipeRead.
    """
    result = await db.execute(select(RecipesModel))
    recipes = result.scalars().all()
    return recipes


@app.get(
    "/recipes/{recipe_id}",
    response_model=RecipeRead,
    tags=["Рецепты"],
    summary="Получить конкретный рецепт",
)
async def get_recipe(recipe_id: int, db: AsyncSession = Depends(get_session)):
    """
    Получает детальную информацию о рецепте по его уникальному идентификатору.

    Параметры пути:
    - recipe_id (int): уникальный идентификатор рецепта.

    Возвращаемое значение:
    - Объект рецепта в формате RecipeRead.

    Ошибки:
    - 404 Not Found, если рецепт с указанным ID не найден.

    Логика:
    1. Выполняется запрос к таблице all_recipes с условием WHERE id = recipe_id.
    2. Если запись не найдена — генерируется HTTPException 404.
    3. Если рецепт найден:
       - увеличивается счётчик просмотров (views += 1);
       - изменения фиксируются в базе (commit);
       - объект обновляется (refresh);
       - возвращается обновлённый рецепт.
    """
    stmt = (
        update(RecipesModel)
        .where(RecipesModel.id == recipe_id)
        .values(views=RecipesModel.views + 1)
    )
    result = await db.execute(stmt)

    if result.rowcount == 0:  # type: ignore[attr-defined]
        raise HTTPException(status_code=404, detail="Рецепт не найден")

    await db.commit()

    select_stmt = select(RecipesModel).where(RecipesModel.id == recipe_id)
    recipe_result = await db.execute(select_stmt)
    recipe = recipe_result.scalar_one()
    return RecipeRead.model_validate(recipe)
