import pytest
from httpx import AsyncClient
from app.main import app
from app.database import AsyncSessionLocal, init_db, engine
from sqlalchemy import text


@pytest.fixture(scope="function", autouse=True)
async def setup_database():
    await init_db()
    
    async with engine.begin() as conn:
        await conn.execute(text("DELETE FROM users"))
        await conn.execute(text("DELETE FROM articles"))
        await conn.execute(text("DELETE FROM tags"))
        await conn.execute(text("DELETE FROM article_tags"))
        await conn.execute(text("DELETE FROM questions"))
        await conn.execute(text("DELETE FROM question_abilities"))
        await conn.execute(text("DELETE FROM ability_dimensions"))
        await conn.execute(text("DELETE FROM user_progresses"))
        await conn.execute(text("DELETE FROM question_answers"))
        await conn.execute(text("DELETE FROM check_ins"))
        await conn.execute(text("DELETE FROM badges"))
        await conn.execute(text("DELETE FROM user_badges"))
        await conn.execute(text("DELETE FROM user_abilities"))
    
    yield
    pass


@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def db_session():
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
