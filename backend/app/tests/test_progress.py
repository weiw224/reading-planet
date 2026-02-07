import pytest
from httpx import AsyncClient
from sqlalchemy import select
from app.models.article import Article, ArticleStatusEnum, DifficultyEnum
from app.models.question import Question, QuestionTypeEnum, QuestionAbility
from app.models.progress import UserProgress, QuestionAnswer
from app.models.ability import AbilityDimension, AbilityCategoryEnum
from app.models.badge import Badge, BadgeConditionTypeEnum, BadgeCategoryEnum
from app.models.user import User


@pytest.mark.asyncio
async def test_start_reading_success(async_client: AsyncClient, auth_headers, test_article):
    """Test starting to read an article"""
    response = await async_client.post(
        "/api/v1/progress/start",
        json={"article_id": test_article.id},
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "progress_id" in data["data"]
    assert data["data"]["article_id"] == test_article.id
    assert data["data"]["article_title"] == test_article.title


@pytest.mark.asyncio
async def test_start_reading_unauthorized(async_client: AsyncClient, test_article):
    """Test starting reading without authentication"""
    response = await async_client.post(
        "/api/v1/progress/start",
        json={"article_id": test_article.id}
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_start_reading_article_not_found(async_client: AsyncClient, auth_headers):
    """Test starting reading with non-existent article"""
    response = await async_client.post(
        "/api/v1/progress/start",
        json={"article_id": 999},
        headers=auth_headers
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_submit_answer_correct(async_client: AsyncClient, auth_headers, test_question, db_session):
    """Test submitting correct answer"""
    progress = UserProgress(
        user_id=1,
        article_id=test_question.article_id,
        total_count=1
    )
    db_session.add(progress)
    await db_session.commit()
    await db_session.refresh(progress)

    response = await async_client.post(
        f"/api/v1/progress/{progress.id}/submit",
        json={"question_id": test_question.id, "user_answer": "A"},
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["is_correct"] is True
    assert data["data"]["correct_answer"] == "A"


@pytest.mark.asyncio
async def test_submit_answer_incorrect(async_client: AsyncClient, auth_headers, test_question, db_session):
    """Test submitting incorrect answer"""
    progress = UserProgress(
        user_id=1,
        article_id=test_question.article_id,
        total_count=1
    )
    db_session.add(progress)
    await db_session.commit()
    await db_session.refresh(progress)

    response = await async_client.post(
        f"/api/v1/progress/{progress.id}/submit",
        json={"question_id": test_question.id, "user_answer": "B"},
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["is_correct"] is False


@pytest.mark.asyncio
async def test_submit_answer_duplicate(async_client: AsyncClient, auth_headers, test_question, db_session):
    """Test submitting duplicate answer"""
    progress = UserProgress(
        user_id=1,
        article_id=test_question.article_id,
        total_count=1
    )
    db_session.add(progress)
    await db_session.commit()
    await db_session.refresh(progress)

    answer = QuestionAnswer(
        progress_id=progress.id,
        question_id=test_question.id,
        user_answer="A",
        is_correct=True
    )
    db_session.add(answer)
    await db_session.commit()

    response = await async_client.post(
        f"/api/v1/progress/{progress.id}/submit",
        json={"question_id": test_question.id, "user_answer": "B"},
        headers=auth_headers
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_complete_reading_success(async_client: AsyncClient, auth_headers, test_article, test_question, db_session):
    """Test completing reading"""
    progress = UserProgress(
        user_id=1,
        article_id=test_article.id,
        total_count=1,
        correct_count=1
    )
    db_session.add(progress)
    await db_session.commit()
    await db_session.refresh(progress)

    answer = QuestionAnswer(
        progress_id=progress.id,
        question_id=test_question.id,
        user_answer="A",
        is_correct=True
    )
    db_session.add(answer)
    await db_session.commit()

    response = await async_client.post(
        f"/api/v1/progress/{progress.id}/complete",
        json={"time_spent": 180},
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["progress_id"] == progress.id
    assert data["data"]["score"] == 100
    assert data["data"]["correct_count"] == 1
    assert data["data"]["total_count"] == 1


@pytest.mark.asyncio
async def test_complete_reading_unauthorized(async_client: AsyncClient, db_session):
    """Test completing reading without authentication"""
    article = Article(
        title="Test Article",
        content="Content",
        word_count=100,
        reading_time=1,
        status=ArticleStatusEnum.PUBLISHED,
        article_difficulty=DifficultyEnum.EASY
    )
    db_session.add(article)
    await db_session.commit()
    await db_session.refresh(article)

    progress = UserProgress(
        user_id=1,
        article_id=article.id,
        total_count=1
    )
    db_session.add(progress)
    await db_session.commit()
    await db_session.refresh(progress)

    response = await async_client.post(
        f"/api/v1/progress/{progress.id}/complete",
        json={"time_spent": 180}
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_complete_reading_invalid_time_spent(async_client: AsyncClient, auth_headers, db_session):
    """Test completing reading with invalid time_spent"""
    article = Article(
        title="Test Article",
        content="Content",
        word_count=100,
        reading_time=1,
        status=ArticleStatusEnum.PUBLISHED,
        article_difficulty=DifficultyEnum.EASY
    )
    db_session.add(article)
    await db_session.commit()
    await db_session.refresh(article)

    progress = UserProgress(
        user_id=1,
        article_id=article.id,
        total_count=1
    )
    db_session.add(progress)
    await db_session.commit()
    await db_session.refresh(progress)

    response = await async_client.post(
        f"/api/v1/progress/{progress.id}/complete",
        json={"time_spent": -1},
        headers=auth_headers
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_progress_detail(async_client: AsyncClient, auth_headers, test_article, test_question, db_session):
    """Test getting progress detail"""
    progress = UserProgress(
        user_id=1,
        article_id=test_article.id,
        total_count=1,
        correct_count=1,
        score=100,
        time_spent=180
    )
    db_session.add(progress)
    await db_session.commit()
    await db_session.refresh(progress)

    answer = QuestionAnswer(
        progress_id=progress.id,
        question_id=test_question.id,
        user_answer="A",
        is_correct=True
    )
    db_session.add(answer)
    await db_session.commit()

    response = await async_client.get(
        f"/api/v1/progress/{progress.id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["id"] == progress.id
    assert data["data"]["article_title"] == test_article.title
    assert len(data["data"]["answers"]) == 1


@pytest.mark.asyncio
async def test_get_progress_detail_not_found(async_client: AsyncClient, auth_headers):
    """Test getting non-existent progress"""
    response = await async_client.get(
        "/api/v1/progress/999",
        headers=auth_headers
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_history_empty(async_client: AsyncClient, auth_headers):
    """Test getting empty reading history"""
    response = await async_client.get(
        "/api/v1/progress/history",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["total"] == 0
    assert len(data["data"]["items"]) == 0


@pytest.mark.asyncio
async def test_get_history_with_items(async_client: AsyncClient, auth_headers, test_article, db_session):
    """Test getting reading history with items"""
    from datetime import datetime

    progress1 = UserProgress(
        user_id=1,
        article_id=test_article.id,
        total_count=1,
        score=80,
        completed_at=datetime.utcnow()
    )
    progress2 = UserProgress(
        user_id=1,
        article_id=test_article.id,
        total_count=1,
        score=90,
        completed_at=datetime.utcnow()
    )
    db_session.add_all([progress1, progress2])
    await db_session.commit()

    response = await async_client.get(
        "/api/v1/progress/history",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["total"] == 2
    assert len(data["data"]["items"]) == 2


@pytest.mark.asyncio
async def test_get_history_pagination(async_client: AsyncClient, auth_headers, test_article, db_session):
    """Test getting reading history with pagination"""
    from datetime import datetime

    for i in range(5):
        progress = UserProgress(
            user_id=1,
            article_id=test_article.id,
            total_count=1,
            score=i * 10,
            completed_at=datetime.utcnow()
        )
        db_session.add(progress)
    await db_session.commit()

    response = await async_client.get(
        "/api/v1/progress/history?page=1&page_size=2",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["total"] == 5
    assert len(data["data"]["items"]) == 2
    assert data["data"]["page"] == 1
    assert data["data"]["page_size"] == 2


@pytest.mark.asyncio
async def test_submit_answer_with_abilities(async_client: AsyncClient, auth_headers, test_question, db_session):
    """Test submitting answer with ability tags"""
    ability = AbilityDimension(
        name="细节提取",
        code="detail",
        category=AbilityCategoryEnum.INFORMATION
    )
    db_session.add(ability)
    await db_session.commit()
    await db_session.refresh(ability)

    question_ability = QuestionAbility(
        question_id=test_question.id,
        ability_id=ability.id
    )
    db_session.add(question_ability)
    await db_session.commit()

    progress = UserProgress(
        user_id=1,
        article_id=test_question.article_id,
        total_count=1
    )
    db_session.add(progress)
    await db_session.commit()
    await db_session.refresh(progress)

    response = await async_client.post(
        f"/api/v1/progress/{progress.id}/submit",
        json={"question_id": test_question.id, "user_answer": "A"},
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "细节提取" in data["data"]["ability_names"]


@pytest.mark.asyncio
async def test_complete_reading_with_badge(async_client: AsyncClient, auth_headers, test_article, db_session, test_user):
    """Test completing reading and earning badge"""
    badge = Badge(
        name="阅读新星",
        description="完成第一次阅读",
        category=BadgeCategoryEnum.READING,
        condition_type=BadgeConditionTypeEnum.FIRST_READING,
        condition_value=1
    )
    db_session.add(badge)
    await db_session.commit()

    progress = UserProgress(
        user_id=test_user.id,
        article_id=test_article.id,
        total_count=0
    )
    db_session.add(progress)
    await db_session.commit()
    await db_session.refresh(progress)

    response = await async_client.post(
        f"/api/v1/progress/{progress.id}/complete",
        json={"time_spent": 180},
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert len(data["data"]["new_badges"]) >= 0


@pytest.mark.asyncio
async def test_submit_answer_case_insensitive_choice(async_client: AsyncClient, auth_headers, test_question, db_session):
    """Test that choice answers are case-insensitive"""
    progress = UserProgress(
        user_id=1,
        article_id=test_question.article_id,
        total_count=1
    )
    db_session.add(progress)
    await db_session.commit()
    await db_session.refresh(progress)

    response = await async_client.post(
        f"/api/v1/progress/{progress.id}/submit",
        json={"question_id": test_question.id, "user_answer": "a"},
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["data"]["is_correct"] is True
