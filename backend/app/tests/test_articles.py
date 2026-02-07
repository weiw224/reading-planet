import pytest
from httpx import AsyncClient
from sqlalchemy import select
from app.models.article import Article, ArticleStatusEnum, DifficultyEnum, ArticleTag
from app.models.tag import Tag, TagCategoryEnum
from app.models.user import User, GradeEnum
from app.models.question import Question, QuestionTypeEnum, QuestionAbility
from app.models.progress import UserProgress
from app.models.user_ability import UserAbility
from app.models.ability import AbilityDimension
from datetime import date


@pytest.mark.asyncio
async def test_get_article_list_empty(async_client: AsyncClient):
    """获取空的文章列表"""
    response = await async_client.get("/api/v1/articles/")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["items"] == []
    assert data["data"]["total"] == 0


@pytest.mark.asyncio
async def test_get_article_list_with_articles(async_client: AsyncClient, db_session):
    """获取包含文章的列表"""
    article1 = Article(
        title="测试文章1",
        content="内容1",
        word_count=100,
        reading_time=1,
        status=ArticleStatusEnum.PUBLISHED,
        article_difficulty=DifficultyEnum.EASY
    )
    article2 = Article(
        title="测试文章2",
        content="内容2",
        word_count=200,
        reading_time=2,
        status=ArticleStatusEnum.PUBLISHED,
        article_difficulty=DifficultyEnum.MEDIUM
    )
    db_session.add(article1)
    db_session.add(article2)
    await db_session.commit()
    
    response = await async_client.get("/api/v1/articles/")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["total"] == 2
    assert len(data["data"]["items"]) == 2
    assert data["data"]["items"][0]["title"] == "测试文章1"
    assert data["data"]["items"][1]["title"] == "测试文章2"


@pytest.mark.asyncio
async def test_get_article_list_with_difficulty_filter(async_client: AsyncClient, db_session):
    """按难度筛选文章"""
    article1 = Article(
        title="简单文章",
        content="内容",
        word_count=100,
        reading_time=1,
        status=ArticleStatusEnum.PUBLISHED,
        article_difficulty=DifficultyEnum.EASY
    )
    article2 = Article(
        title="中等文章",
        content="内容",
        word_count=200,
        reading_time=2,
        status=ArticleStatusEnum.PUBLISHED,
        article_difficulty=DifficultyEnum.MEDIUM
    )
    db_session.add(article1)
    db_session.add(article2)
    await db_session.commit()
    
    response = await async_client.get("/api/v1/articles/?difficulty=1")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["total"] == 1
    assert data["data"]["items"][0]["title"] == "简单文章"


@pytest.mark.asyncio
async def test_get_article_list_with_grade_filter(async_client: AsyncClient, db_session):
    """按年级筛选文章"""
    article = Article(
        title="三年级文章",
        content="内容",
        word_count=100,
        reading_time=1,
        status=ArticleStatusEnum.PUBLISHED,
        article_difficulty=DifficultyEnum.EASY
    )
    db_session.add(article)
    await db_session.commit()
    
    tag = Tag(
        name="3年级",
        category=TagCategoryEnum.GRADE
    )
    db_session.add(tag)
    await db_session.commit()
    await db_session.refresh(article)
    await db_session.refresh(tag)
    
    article_tag = ArticleTag(article_id=article.id, tag_id=tag.id)
    db_session.add(article_tag)
    await db_session.commit()
    
    response = await async_client.get("/api/v1/articles/?grade=3年级")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["total"] == 1
    assert data["data"]["items"][0]["title"] == "三年级文章"


@pytest.mark.asyncio
async def test_get_article_list_with_keyword_search(async_client: AsyncClient, db_session):
    """关键词搜索文章"""
    article1 = Article(
        title="伊索寓言故事",
        content="内容",
        source_book="伊索寓言",
        word_count=100,
        reading_time=1,
        status=ArticleStatusEnum.PUBLISHED,
        article_difficulty=DifficultyEnum.EASY
    )
    article2 = Article(
        title="格林童话",
        content="内容",
        source_book="格林童话",
        word_count=200,
        reading_time=2,
        status=ArticleStatusEnum.PUBLISHED,
        article_difficulty=DifficultyEnum.MEDIUM
    )
    db_session.add(article1)
    db_session.add(article2)
    await db_session.commit()
    
    response = await async_client.get("/api/v1/articles/?keyword=伊索")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["total"] == 1
    assert data["data"]["items"][0]["title"] == "伊索寓言故事"


@pytest.mark.asyncio
async def test_get_article_list_pagination(async_client: AsyncClient, db_session):
    """文章列表分页"""
    for i in range(25):
        article = Article(
            title=f"文章{i}",
            content="内容",
            word_count=100,
            reading_time=1,
            status=ArticleStatusEnum.PUBLISHED,
            article_difficulty=DifficultyEnum.EASY
        )
        db_session.add(article)
    await db_session.commit()
    
    response = await async_client.get("/api/v1/articles/?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["total"] == 25
    assert data["data"]["page"] == 1
    assert data["data"]["page_size"] == 10
    assert len(data["data"]["items"]) == 10
    
    response = await async_client.get("/api/v1/articles/?page=2&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["page"] == 2
    assert len(data["data"]["items"]) == 10


@pytest.mark.asyncio
async def test_get_article_detail(async_client: AsyncClient, db_session):
    """获取文章详情"""
    article = Article(
        title="测试文章",
        content="这是详细内容",
        source_book="测试书籍",
        source_chapter="第一章",
        is_excerpt=True,
        word_count=100,
        reading_time=1,
        status=ArticleStatusEnum.PUBLISHED,
        article_difficulty=DifficultyEnum.EASY
    )
    db_session.add(article)
    await db_session.commit()
    await db_session.refresh(article)
    
    question = Question(
        article_id=article.id,
        type=QuestionTypeEnum.CHOICE,
        content="测试问题",
        answer="A",
        difficulty=DifficultyEnum.EASY
    )
    db_session.add(question)
    await db_session.commit()
    
    response = await async_client.get(f"/api/v1/articles/{article.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["title"] == "测试文章"
    assert data["data"]["content"] == "这是详细内容"
    assert data["data"]["source_book"] == "测试书籍"
    assert data["data"]["source_chapter"] == "第一章"
    assert data["data"]["is_excerpt"] == True
    assert data["data"]["question_count"] == 1


@pytest.mark.asyncio
async def test_get_article_detail_not_found(async_client: AsyncClient):
    """获取不存在的文章详情"""
    response = await async_client.get("/api/v1/articles/999999")
    assert response.status_code == 404
    data = response.json()
    assert "文章不存在" in data["detail"]


@pytest.mark.asyncio
async def test_get_article_detail_unpublished(async_client: AsyncClient, db_session):
    """获取未发布的文章详情"""
    article = Article(
        title="草稿文章",
        content="内容",
        word_count=100,
        reading_time=1,
        status=ArticleStatusEnum.DRAFT,
        article_difficulty=DifficultyEnum.EASY
    )
    db_session.add(article)
    await db_session.commit()
    await db_session.refresh(article)
    
    response = await async_client.get(f"/api/v1/articles/{article.id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_today_recommendation(async_client: AsyncClient, test_user, auth_headers, db_session):
    """获取今日推荐文章"""
    article = Article(
        title="推荐文章",
        content="内容",
        word_count=100,
        reading_time=1,
        status=ArticleStatusEnum.PUBLISHED,
        article_difficulty=DifficultyEnum.EASY
    )
    db_session.add(article)
    await db_session.commit()
    
    response = await async_client.get("/api/v1/articles/today", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["title"] == "推荐文章"


@pytest.mark.asyncio
async def test_get_today_recommendation_unauthenticated(async_client: AsyncClient):
    """未登录获取今日推荐"""
    response = await async_client.get("/api/v1/articles/today")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_today_recommendation_excludes_read_today(async_client: AsyncClient, test_user, auth_headers, db_session):
    """今日推荐排除今天已读过的文章"""
    article1 = Article(
        title="已读文章",
        content="内容1",
        word_count=100,
        reading_time=1,
        status=ArticleStatusEnum.PUBLISHED,
        article_difficulty=DifficultyEnum.EASY
    )
    article2 = Article(
        title="未读文章",
        content="内容2",
        word_count=100,
        reading_time=1,
        status=ArticleStatusEnum.PUBLISHED,
        article_difficulty=DifficultyEnum.EASY
    )
    db_session.add(article1)
    db_session.add(article2)
    await db_session.commit()
    await db_session.refresh(article1)
    
    progress = UserProgress(
        user_id=test_user.id,
        article_id=article1.id,
        score=100,
        correct_count=0,
        total_count=0
    )
    db_session.add(progress)
    await db_session.commit()
    
    response = await async_client.get("/api/v1/articles/today", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["title"] == "未读文章"


@pytest.mark.asyncio
async def test_get_weak_point_recommendation(async_client: AsyncClient, test_user, auth_headers, db_session):
    """获取补弱项推荐文章"""
    from app.models.ability import AbilityCategoryEnum
    ability = AbilityDimension(
        name="细节提取",
        code="detail_extraction",
        category=AbilityCategoryEnum.COMPREHENSION
    )
    db_session.add(ability)
    await db_session.commit()
    await db_session.refresh(ability)
    
    user_ability = UserAbility(
        user_id=test_user.id,
        ability_id=ability.id,
        score=30.0,
        correct_count=3,
        total_count=10
    )
    db_session.add(user_ability)
    await db_session.commit()
    
    from app.models.question import QuestionAbility
    article = Article(
        title="训练细节提取的文章",
        content="内容",
        word_count=100,
        reading_time=1,
        status=ArticleStatusEnum.PUBLISHED,
        article_difficulty=DifficultyEnum.EASY
    )
    db_session.add(article)
    await db_session.commit()
    await db_session.refresh(article)
    
    question = Question(
        article_id=article.id,
        type=QuestionTypeEnum.CHOICE,
        content="问题",
        answer="A",
        difficulty=DifficultyEnum.EASY
    )
    db_session.add(question)
    await db_session.commit()
    await db_session.refresh(question)
    
    question_ability = QuestionAbility(
        question_id=question.id,
        ability_id=ability.id
    )
    db_session.add(question_ability)
    await db_session.commit()
    
    response = await async_client.get("/api/v1/articles/weak-point", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["title"] == "训练细节提取的文章"


@pytest.mark.asyncio
async def test_get_weak_point_recommendation_no_ability_data(async_client: AsyncClient, test_user, auth_headers, db_session):
    """没有能力数据时的补弱项推荐"""
    article = Article(
        title="随机推荐",
        content="内容",
        word_count=100,
        reading_time=1,
        status=ArticleStatusEnum.PUBLISHED,
        article_difficulty=DifficultyEnum.EASY
    )
    db_session.add(article)
    await db_session.commit()
    
    response = await async_client.get("/api/v1/articles/weak-point", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["title"] == "随机推荐"


@pytest.mark.asyncio
async def test_get_article_questions(async_client: AsyncClient, test_user, auth_headers, db_session, test_article):
    """获取文章的题目列表"""
    response = await async_client.get(f"/api/v1/articles/{test_article.id}/questions", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "questions" in data["data"]
    assert data["data"]["article_id"] == test_article.id


@pytest.mark.asyncio
async def test_get_article_questions_unauthenticated(async_client: AsyncClient, test_article):
    """未登录获取文章题目"""
    response = await async_client.get(f"/api/v1/articles/{test_article.id}/questions")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_article_questions_article_not_found(async_client: AsyncClient, auth_headers):
    """获取不存在文章的题目"""
    response = await async_client.get("/api/v1/articles/999999/questions", headers=auth_headers)
    assert response.status_code == 404
