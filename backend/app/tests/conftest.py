import pytest
from httpx import AsyncClient
from app.main import app
from app.database import AsyncSessionLocal, init_db, engine
from sqlalchemy import text
from app.models.user import User
from app.models.article import Article, DifficultyEnum, ArticleStatusEnum
from app.models.tag import Tag
from app.models.question import Question, QuestionTypeEnum


@pytest.fixture(scope="function", autouse=True)
async def setup_database():
    await init_db()
    
    async with engine.begin() as conn:
        await conn.execute(text("DELETE FROM user_abilities"))
        await conn.execute(text("DELETE FROM user_badges"))
        await conn.execute(text("DELETE FROM question_answers"))
        await conn.execute(text("DELETE FROM user_progresses"))
        await conn.execute(text("DELETE FROM check_ins"))
        await conn.execute(text("DELETE FROM question_abilities"))
        await conn.execute(text("DELETE FROM questions"))
        await conn.execute(text("DELETE FROM ability_dimensions"))
        await conn.execute(text("DELETE FROM badges"))
        await conn.execute(text("DELETE FROM article_tags"))
        await conn.execute(text("DELETE FROM tags"))
        await conn.execute(text("DELETE FROM articles"))
        await conn.execute(text("DELETE FROM users"))

    
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


@pytest.fixture
async def test_user(db_session):
    user = User(openid="test_openid_123")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def auth_headers(test_user):
    from app.utils.security import create_access_token
    from datetime import timedelta
    token = create_access_token(
        data={"sub": str(test_user.id), "openid": test_user.openid},
        expires_delta=timedelta(days=7)
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def test_article(db_session):
    article = Article(
        title="测试文章",
        content="这是测试内容",
        word_count=100,
        reading_time=1,
        status=ArticleStatusEnum.PUBLISHED,
        article_difficulty=DifficultyEnum.EASY
    )
    db_session.add(article)
    await db_session.commit()
    await db_session.refresh(article)
    return article



@pytest.fixture
async def test_question(test_article, db_session):
    question = Question(
        article_id=test_article.id,
        type=QuestionTypeEnum.CHOICE,
        difficulty=DifficultyEnum.EASY,
        content="测试问题",
        options='{"A": "选项A", "B": "选项B", "C": "选项C", "D": "选项D"}',
        answer="A",
        explanation="测试解析"
    )
    db_session.add(question)
    await db_session.commit()
    await db_session.refresh(question)
    return question

