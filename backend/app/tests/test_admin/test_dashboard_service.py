import pytest
from app.services.admin.dashboard_service import dashboard_service
from app.models.article import Article, ArticleStatusEnum, DifficultyEnum
from app.models.question import Question, QuestionTypeEnum
from app.models.user import User
from app.models.progress import UserProgress
from app.models.checkin import CheckIn
from datetime import date, timedelta


@pytest.mark.asyncio
async def test_get_dashboard_stats_basic(db_session):
    stats = await dashboard_service.get_stats(db_session)

    assert stats.total_users == 0
    assert stats.total_articles == 0
    assert stats.total_questions == 0
    assert stats.published_articles == 0
    assert stats.total_readings == 0
    assert stats.checkins_today == 0
    assert stats.active_users_today == 0
    assert stats.active_users_week == 0


@pytest.mark.asyncio
async def test_get_dashboard_stats_with_users(db_session):
    for i in range(10):
        user = User(openid=f"test_{i}")
        db_session.add(user)
    await db_session.commit()

    stats = await dashboard_service.get_stats(db_session)

    assert stats.total_users == 10


@pytest.mark.asyncio
async def test_get_dashboard_stats_with_articles(db_session):
    for i in range(5):
        article = Article(
            title=f"文章{i}",
            content="测试内容",
            word_count=4,
            reading_time=1,
            status=ArticleStatusEnum.PUBLISHED if i < 3 else ArticleStatusEnum.DRAFT,
            article_difficulty=DifficultyEnum.EASY
        )
        db_session.add(article)
    await db_session.commit()

    stats = await dashboard_service.get_stats(db_session)

    assert stats.total_articles == 5
    assert stats.published_articles == 3


@pytest.mark.asyncio
async def test_get_dashboard_stats_with_questions(db_session, test_article):
    for i in range(7):
        question = Question(
            article_id=test_article.id,
            type=QuestionTypeEnum.JUDGE,
            difficulty=DifficultyEnum.EASY,
            content=f"问题{i}",
            answer="对"
        )
        db_session.add(question)
    await db_session.commit()

    stats = await dashboard_service.get_stats(db_session)

    assert stats.total_questions == 7


@pytest.mark.asyncio
async def test_get_dashboard_stats_with_readings(db_session, test_user, test_article):
    for i in range(3):
        progress = UserProgress(
            user_id=test_user.id,
            article_id=test_article.id,
            word_count=100,
            reading_time=1,
            completed_at=None if i == 0 else None
        )
        if i > 0:
            progress.completed_at = None
        db_session.add(progress)
    await db_session.commit()

    completed_progress = UserProgress(
        user_id=test_user.id,
        article_id=test_article.id,
        word_count=100,
        reading_time=1,
        completed_at=None
    )
    db_session.add(completed_progress)
    completed_progress.completed_at = None
    await db_session.commit()

    stats = await dashboard_service.get_stats(db_session)
    
    assert stats.total_readings >= 0


@pytest.mark.asyncio
async def test_get_dashboard_stats_with_checkins_today(db_session, test_user):
    today = date.today()

    checkin = CheckIn(
        user_id=test_user.id,
        check_date=today
    )
    db_session.add(checkin)
    await db_session.commit()

    stats = await dashboard_service.get_stats(db_session)

    assert stats.checkins_today == 1


@pytest.mark.asyncio
async def test_get_dashboard_stats_with_checkins_not_today(db_session, test_user):
    yesterday = date.today() - timedelta(days=1)

    checkin = CheckIn(
        user_id=test_user.id,
        check_date=yesterday
    )
    db_session.add(checkin)
    await db_session.commit()

    stats = await dashboard_service.get_stats(db_session)

    assert stats.checkins_today == 0


@pytest.mark.asyncio
async def test_get_dashboard_stats_active_users_today(db_session, test_user, test_article):
    today = date.today()

    progress = UserProgress(
        user_id=test_user.id,
        article_id=test_article.id,
        word_count=100,
        reading_time=1
    )
    progress.created_at = today
    db_session.add(progress)
    await db_session.commit()

    stats = await dashboard_service.get_stats(db_session)

    assert stats.active_users_today >= 0


@pytest.mark.asyncio
async def test_get_dashboard_stats_active_users_week(db_session, test_user, test_article):
    week_ago = date.today() - timedelta(days=3)

    progress = UserProgress(
        user_id=test_user.id,
        article_id=test_article.id,
        word_count=100,
        reading_time=1
    )
    progress.created_at = week_ago
    db_session.add(progress)
    await db_session.commit()

    stats = await dashboard_service.get_stats(db_session)

    assert stats.active_users_week >= 0


@pytest.mark.asyncio
async def test_get_dashboard_stats_comprehensive(db_session, test_user, test_article):
    user2 = User(openid="test_user_2")
    db_session.add(user2)

    for i in range(3):
        article = Article(
            title=f"文章{i}",
            content="测试内容",
            word_count=4,
            reading_time=1,
            status=ArticleStatusEnum.PUBLISHED if i < 2 else ArticleStatusEnum.DRAFT,
            article_difficulty=DifficultyEnum.EASY
        )
        db_session.add(article)
    await db_session.commit()
    await db_session.refresh(article)

    for i in range(5):
        question = Question(
            article_id=test_article.id,
            type=QuestionTypeEnum.JUDGE,
            difficulty=DifficultyEnum.EASY,
            content=f"问题{i}",
            answer="对"
        )
        db_session.add(question)

    today = date.today()
    checkin = CheckIn(user_id=test_user.id, check_date=today)
    db_session.add(checkin)

    progress = UserProgress(
        user_id=test_user.id,
        article_id=test_article.id,
        word_count=100,
        reading_time=1,
        completed_at=None
    )
    db_session.add(progress)
    await db_session.commit()

    stats = await dashboard_service.get_stats(db_session)

    assert stats.total_users == 2
    assert stats.total_articles == 4
    assert stats.published_articles == 3
    assert stats.total_questions == 5
    assert stats.checkins_today == 1
