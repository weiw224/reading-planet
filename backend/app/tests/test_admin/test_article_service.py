import pytest
from app.services.admin.article_service import admin_article_service
from app.schemas.admin.article import (
    ArticleCreateRequest,
    ArticleUpdateRequest,
    DifficultyEnum
)
from app.models.article import Article, ArticleStatusEnum, DifficultyEnum as DBDifficultyEnum
from app.models.tag import Tag, TagCategoryEnum


@pytest.mark.asyncio
async def test_create_article(db_session):
    tag = Tag(name="测试标签", category=TagCategoryEnum.GENRE)
    db_session.add(tag)
    await db_session.commit()
    await db_session.refresh(tag)

    data = ArticleCreateRequest(
        title="测试文章",
        content="这是测试内容" * 10,
        source_book="测试书籍",
        article_difficulty=DifficultyEnum.EASY,
        tag_ids=[tag.id]
    )

    result = await admin_article_service.create_article(db_session, data, admin_id=1)

    assert result.id is not None
    assert result.title == "测试文章"
    assert str(result.status) == "draft"
    assert str(result.article_difficulty) == "1"
    assert result.word_count == len("这是测试内容" * 10)
    assert result.reading_time == max(1, len("这是测试内容" * 10) // 300)
    assert len(result.tags) == 1
    assert result.tags[0]["name"] == "测试标签"
    assert result.created_by == 1


@pytest.mark.asyncio
async def test_get_article_list(db_session):
    for i in range(5):
        article = Article(
            title=f"文章{i}",
            content=f"内容{i}" * 20,
            word_count=len(f"内容{i}" * 20),
            reading_time=max(1, len(f"内容{i}" * 20) // 300),
            status=ArticleStatusEnum.PUBLISHED if i < 3 else ArticleStatusEnum.DRAFT,
            article_difficulty=DifficultyEnum.MEDIUM
        )
        db_session.add(article)
    await db_session.commit()

    items, total = await admin_article_service.get_article_list(db_session, page=1, page_size=10)

    assert total == 5
    assert len(items) == 5
    assert items[0].title == "文章4"


@pytest.mark.asyncio
async def test_get_article_list_with_filters(db_session):
    for status in [ArticleStatusEnum.PUBLISHED, ArticleStatusEnum.DRAFT]:
        article = Article(
            title=f"{status.value}文章",
            content="测试内容",
            word_count=4,
            reading_time=1,
            status=status,
            article_difficulty=DifficultyEnum.MEDIUM
        )
        db_session.add(article)
    await db_session.commit()

    items, total = await admin_article_service.get_article_list(
        db_session,
        status="published"
    )

    assert total == 1
    assert len(items) == 1
    assert items[0].status == ArticleStatusEnum.PUBLISHED

    items, total = await admin_article_service.get_article_list(
        db_session,
        keyword="published"
    )

    assert total == 1
    assert items[0].title == "published文章"


@pytest.mark.asyncio
async def test_get_article_detail(db_session):
    tag = Tag(name="测试标签", category=TagCategoryEnum.GENRE)
    db_session.add(tag)
    await db_session.commit()

    article = Article(
        title="测试文章",
        content="测试内容",
        word_count=4,
        reading_time=1,
        status=ArticleStatusEnum.PUBLISHED,
        article_difficulty=DifficultyEnum.MEDIUM
    )
    db_session.add(article)
    await db_session.commit()
    await db_session.refresh(article)

    from app.models.article import ArticleTag
    article_tag = ArticleTag(article_id=article.id, tag_id=tag.id)
    db_session.add(article_tag)
    await db_session.commit()

    result = await admin_article_service.get_article_detail(db_session, article.id)

    assert result is not None
    assert result.id == article.id
    assert result.title == "测试文章"
    assert len(result.tags) == 1
    assert result.tags[0]["name"] == "测试标签"


@pytest.mark.asyncio
async def test_update_article(db_session):
    article = Article(
        title="原标题",
        content="原内容",
        word_count=3,
        reading_time=1,
        status=ArticleStatusEnum.DRAFT,
        article_difficulty=DifficultyEnum.EASY
    )
    db_session.add(article)
    await db_session.commit()
    await db_session.refresh(article)

    data = ArticleUpdateRequest(
        title="新标题",
        status=ArticleStatusEnum.PUBLISHED,
        article_difficulty=DifficultyEnum.HARD
    )

    result = await admin_article_service.update_article(db_session, article.id, data)

    assert result is not None
    assert result.title == "新标题"
    assert result.status == ArticleStatusEnum.PUBLISHED
    assert result.article_difficulty == DifficultyEnum.HARD


@pytest.mark.asyncio
async def test_update_article_with_content(db_session):
    article = Article(
        title="原标题",
        content="短内容",
        word_count=3,
        reading_time=1,
        status=ArticleStatusEnum.DRAFT,
        article_difficulty=DifficultyEnum.EASY
    )
    db_session.add(article)
    await db_session.commit()
    await db_session.refresh(article)

    new_content = "新内容" * 100
    data = ArticleUpdateRequest(content=new_content)

    result = await admin_article_service.update_article(db_session, article.id, data)

    assert result is not None
    assert result.word_count == len(new_content)
    assert result.reading_time == max(1, len(new_content) // 300)


@pytest.mark.asyncio
async def test_update_article_tags(db_session):
    tag1 = Tag(name="标签1", category=TagCategoryEnum.GENRE)
    tag2 = Tag(name="标签2", category=TagCategoryEnum.THEME)
    db_session.add(tag1)
    db_session.add(tag2)
    await db_session.commit()

    article = Article(
        title="测试文章",
        content="测试内容",
        word_count=4,
        reading_time=1,
        status=ArticleStatusEnum.PUBLISHED,
        article_difficulty=DifficultyEnum.MEDIUM
    )
    db_session.add(article)
    await db_session.commit()
    await db_session.refresh(article)

    from app.models.article import ArticleTag
    article_tag = ArticleTag(article_id=article.id, tag_id=tag1.id)
    db_session.add(article_tag)
    await db_session.commit()

    data = ArticleUpdateRequest(tag_ids=[tag2.id])
    result = await admin_article_service.update_article(db_session, article.id, data)

    assert result is not None
    assert len(result.tags) == 1
    assert result.tags[0]["name"] == "标签2"


@pytest.mark.asyncio
async def test_delete_article(db_session):
    article = Article(
        title="测试文章",
        content="测试内容",
        word_count=4,
        reading_time=1,
        status=ArticleStatusEnum.PUBLISHED,
        article_difficulty=DifficultyEnum.MEDIUM
    )
    db_session.add(article)
    await db_session.commit()
    await db_session.refresh(article)

    article_id = article.id
    success = await admin_article_service.delete_article(db_session, article_id)

    assert success is True

    from sqlalchemy import select
    result = await db_session.execute(select(Article).where(Article.id == article_id))
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_publish_article(db_session):
    article = Article(
        title="测试文章",
        content="测试内容",
        word_count=4,
        reading_time=1,
        status=ArticleStatusEnum.DRAFT,
        article_difficulty=DifficultyEnum.MEDIUM
    )
    db_session.add(article)
    await db_session.commit()

    success = await admin_article_service.publish_article(db_session, article.id)

    assert success is True

    await db_session.refresh(article)
    assert article.status == ArticleStatusEnum.PUBLISHED


@pytest.mark.asyncio
async def test_archive_article(db_session):
    article = Article(
        title="测试文章",
        content="测试内容",
        word_count=4,
        reading_time=1,
        status=ArticleStatusEnum.PUBLISHED,
        article_difficulty=DifficultyEnum.MEDIUM
    )
    db_session.add(article)
    await db_session.commit()

    success = await admin_article_service.archive_article(db_session, article.id)

    assert success is True

    await db_session.refresh(article)
    assert article.status == ArticleStatusEnum.ARCHIVED


@pytest.mark.asyncio
async def test_get_article_detail_not_found(db_session):
    result = await admin_article_service.get_article_detail(db_session, 99999)
    assert result is None


@pytest.mark.asyncio
async def test_delete_article_not_found(db_session):
    success = await admin_article_service.delete_article(db_session, 99999)
    assert success is False


@pytest.mark.asyncio
async def test_publish_article_not_found(db_session):
    success = await admin_article_service.publish_article(db_session, 99999)
    assert success is False


@pytest.mark.asyncio
async def test_archive_article_not_found(db_session):
    success = await admin_article_service.archive_article(db_session, 99999)
    assert success is False
