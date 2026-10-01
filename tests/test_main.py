import pytest
from httpx import AsyncClient, ASGITransport
from homework.main import app
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from homework.database import Base, get_session

BASE_URL = "http://test"
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_recipes.db"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

async_session_maker = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# @pytest.fixture(scope="session", autouse=True)
@pytest.fixture(scope="module")
async def init_test_db():
    """
    Инициализирует тестовую схему БД перед запуском всех тестов.

    - Создаёт все таблицы (Base.metadata.create_all).
    - После завершения тестовой сессии можно было бы удалить таблицы,
      но для SQLite‑файла это опционально (можно просто удалить файл).
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.fixture
async def db_session():
    """
    Создаёт новую асинхронную сессию для каждого теста.

    - Сессия привязана к тестовому движку.
    - После теста сессия закрывается.
    - Изменения не откатываются автоматически, но так как БД отдельная,
      это не влияет на основную базу.
    """
    async with async_session_maker() as session:
        yield session
        await session.close()


@pytest.fixture
async def client(db_session):
    """
    Создаёт асинхронный тестовый клиент FastAPI.

    - Переопределяет зависимость get_session в приложении:
      вместо реальной БД используется тестовая сессия db_session.
    - После завершения тестов очищает dependency_overrides.
    """

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_add_recipe(client, init_test_db):
    """Тест создания рецепта."""
    recipe_data = {
        "name_dish": "Тестовый рецепт",
        "views": 0,
        "cooking_time": 30,
        "ingredients": "Ингредиент 1, Ингредиент 2",
        "description": "Описание тестового рецепта",
    }

    response = await client.post("/add_recipe", json=recipe_data)

    assert response.status_code == 200
    data = response.json()
    assert data["name_dish"] == "Тестовый рецепт"
    assert data["cooking_time"] == 30
    assert "id" in data


@pytest.mark.anyio
async def test_get_all_recipes(client, init_test_db):
    """Тест получения всех рецептов."""
    response = await client.get("/recipes")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
