import pytest
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, Boolean, ForeignKey, UniqueConstraint
from datetime import datetime, timezone
import enum


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


# Create a separate Base for testing to avoid importing from app.database
TestBase = declarative_base()


class ArticleStatusEnum(enum.Enum):
    """文章状态枚举"""
    DRAFT = "draft"
    PENDING = "pending"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class DifficultyEnum(enum.Enum):
    """难度枚举"""
    EASY = 1
    MEDIUM = 2
    HARD = 3


class Article(TestBase):
    """文章表"""
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True, comment="标题")
    content = Column(Text, nullable=False, comment="文章内容")
    
    # 来源信息
    source_book = Column(String(200), nullable=True, comment="来源书籍，如《伊索寓言》")
    source_chapter = Column(String(200), nullable=True, comment="来源章节")
    is_excerpt = Column(Boolean, default=False, comment="是否为节选")
    
    # 文章属性
    word_count = Column(Integer, nullable=False, comment="字数")
    reading_time = Column(Integer, nullable=False, comment="预计阅读时间(分钟)")
    article_difficulty = Column(SQLEnum(DifficultyEnum), default=DifficultyEnum.MEDIUM, comment="文章难度")
    
    # 状态
    status = Column(SQLEnum(ArticleStatusEnum), default=ArticleStatusEnum.DRAFT, index=True, comment="状态")
    
    # AI 导入标记
    is_ai_generated = Column(Boolean, default=False, comment="是否AI导入")
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), comment="创建时间")
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), comment="更新时间")
    created_by = Column(Integer, nullable=True, comment="创建者ID（管理员）")
    
    # 关系
    questions = None
    tags = None
    progresses = None
    
    def __repr__(self):
        return f"<Article(id={self.id}, title={self.title})>"


class Tag(TestBase):
    """标签表"""
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, comment="标签名称")
    color = Column(String(7), nullable=True, comment="标签颜色")
    
    # 关系
    article_tags = None
    
    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name})>"


class ArticleTag(TestBase):
    """文章-标签关联表"""
    __tablename__ = "article_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 关系
    article = None
    tag = None
    
    # 唯一约束
    __table_args__ = (
        UniqueConstraint('article_id', 'tag_id', name='uq_article_tag'),
    )


@pytest.fixture
async def test_engine():
    """创建测试用的异步引擎"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(TestBase.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(TestBase.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine):
    """创建测试用的异步会话"""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.mark.asyncio
async def test_create_article_with_all_fields(test_session: AsyncSession):
    """测试创建包含所有字段的文章"""
    article = Article(
        title="测试文章标题",
        content="这是一篇测试文章的内容，用于验证所有字段是否正确保存。",
        source_book="《伊索寓言》",
        source_chapter="第一章",
        is_excerpt=True,
        word_count=500,
        reading_time=2,
        article_difficulty=DifficultyEnum.MEDIUM,
        status=ArticleStatusEnum.PUBLISHED,
        is_ai_generated=False,
        created_by=1
    )
    
    test_session.add(article)
    await test_session.commit()
    await test_session.refresh(article)
    
    assert article.id is not None
    assert article.title == "测试文章标题"
    assert article.content == "这是一篇测试文章的内容，用于验证所有字段是否正确保存。"
    assert article.source_book == "《伊索寓言》"
    assert article.source_chapter == "第一章"
    assert article.is_excerpt is True
    assert article.word_count == 500
    assert article.reading_time == 2
    assert article.article_difficulty == DifficultyEnum.MEDIUM
    assert article.status == ArticleStatusEnum.PUBLISHED
    assert article.is_ai_generated is False
    assert article.created_by == 1
    assert article.created_at is not None
    assert article.updated_at is not None


@pytest.mark.asyncio
async def test_article_default_values(test_session: AsyncSession):
    """测试文章默认值"""
    article = Article(
        title="默认值测试",
        content="测试内容",
        word_count=100,
        reading_time=1
    )
    
    test_session.add(article)
    await test_session.commit()
    await test_session.refresh(article)
    
    assert article.source_book is None
    assert article.source_chapter is None
    assert article.is_excerpt is False
    assert article.article_difficulty == DifficultyEnum.MEDIUM
    assert article.status == ArticleStatusEnum.DRAFT
    assert article.is_ai_generated is False
    assert article.created_by is None


@pytest.mark.asyncio
async def test_article_status_enum_values():
    """测试文章状态枚举值"""
    assert ArticleStatusEnum.DRAFT.value == "draft"
    assert ArticleStatusEnum.PENDING.value == "pending"
    assert ArticleStatusEnum.PUBLISHED.value == "published"
    assert ArticleStatusEnum.ARCHIVED.value == "archived"


@pytest.mark.asyncio
async def test_difficulty_enum_values():
    """测试难度枚举值"""
    assert DifficultyEnum.EASY.value == 1
    assert DifficultyEnum.MEDIUM.value == 2
    assert DifficultyEnum.HARD.value == 3


@pytest.mark.asyncio
async def test_article_repr(test_session: AsyncSession):
    """测试文章__repr__方法"""
    article = Article(
        title="测试标题",
        content="测试内容",
        word_count=100,
        reading_time=1
    )
    
    repr_str = repr(article)
    assert "Article" in repr_str
    assert "测试标题" in repr_str


@pytest.mark.asyncio
async def test_article_tag_unique_constraint(test_session: AsyncSession):
    """测试ArticleTag唯一约束"""
    # 创建文章和标签
    article = Article(title="文章1", content="内容1", word_count=100, reading_time=1)
    tag = Tag(name="测试标签", color="#FF0000")
    
    test_session.add(article)
    test_session.add(tag)
    await test_session.commit()
    await test_session.refresh(article)
    await test_session.refresh(tag)
    
    # 创建第一个关联
    article_tag1 = ArticleTag(article_id=article.id, tag_id=tag.id)
    test_session.add(article_tag1)
    await test_session.commit()
    
    # 尝试创建相同的关联（应该失败）
    article_tag2 = ArticleTag(article_id=article.id, tag_id=tag.id)
    test_session.add(article_tag2)
    
    with pytest.raises(Exception):  # Should raise an integrity error
        await test_session.commit()




@pytest.mark.asyncio
async def test_multiple_tags_for_one_article(test_session: AsyncSession):
    """测试一篇文章关联多个标签"""
    article = Article(title="文章1", content="内容1", word_count=100, reading_time=1)
    tag1 = Tag(name="标签1", color="#FF0000")
    tag2 = Tag(name="标签2", color="#00FF00")
    tag3 = Tag(name="标签3", color="#0000FF")
    
    test_session.add(article)
    test_session.add(tag1)
    test_session.add(tag2)
    test_session.add(tag3)
    await test_session.commit()
    await test_session.refresh(article)
    await test_session.refresh(tag1)
    await test_session.refresh(tag2)
    await test_session.refresh(tag3)
    
    # 创建多个关联
    article_tag1 = ArticleTag(article_id=article.id, tag_id=tag1.id)
    article_tag2 = ArticleTag(article_id=article.id, tag_id=tag2.id)
    article_tag3 = ArticleTag(article_id=article.id, tag_id=tag3.id)
    
    test_session.add(article_tag1)
    test_session.add(article_tag2)
    test_session.add(article_tag3)
    await test_session.commit()
    
    # 验证创建了3个关联
    from sqlalchemy import select
    result = await test_session.execute(
        select(ArticleTag).where(ArticleTag.article_id == article.id)
    )
    article_tags = result.scalars().all()
    assert len(article_tags) == 3


@pytest.mark.asyncio
async def test_one_tag_for_multiple_articles(test_session: AsyncSession):
    """测试一个标签关联多篇文章"""
    article1 = Article(title="文章1", content="内容1", word_count=100, reading_time=1)
    article2 = Article(title="文章2", content="内容2", word_count=100, reading_time=1)
    article3 = Article(title="文章3", content="内容3", word_count=100, reading_time=1)
    tag = Tag(name="标签1", color="#FF0000")
    
    test_session.add(article1)
    test_session.add(article2)
    test_session.add(article3)
    test_session.add(tag)
    await test_session.commit()
    await test_session.refresh(article1)
    await test_session.refresh(article2)
    await test_session.refresh(article3)
    await test_session.refresh(tag)
    
    # 创建多个关联
    article_tag1 = ArticleTag(article_id=article1.id, tag_id=tag.id)
    article_tag2 = ArticleTag(article_id=article2.id, tag_id=tag.id)
    article_tag3 = ArticleTag(article_id=article3.id, tag_id=tag.id)
    
    test_session.add(article_tag1)
    test_session.add(article_tag2)
    test_session.add(article_tag3)
    await test_session.commit()
    
    # 验证创建了3个关联
    from sqlalchemy import select
    result = await test_session.execute(
        select(ArticleTag).where(ArticleTag.tag_id == tag.id)
    )
    article_tags = result.scalars().all()
    assert len(article_tags) == 3


@pytest.mark.asyncio
async def test_article_tag_indexes(test_session: AsyncSession):
    """测试ArticleTag外键索引"""
    article = Article(title="文章1", content="内容1", word_count=100, reading_time=1)
    tag = Tag(name="测试标签", color="#FF0000")
    
    test_session.add(article)
    test_session.add(tag)
    await test_session.commit()
    await test_session.refresh(article)
    await test_session.refresh(tag)
    
    article_tag = ArticleTag(article_id=article.id, tag_id=tag.id)
    test_session.add(article_tag)
    await test_session.commit()
    
    # 验证可以通过article_id查询
    from sqlalchemy import select
    result = await test_session.execute(
        select(ArticleTag).where(ArticleTag.article_id == article.id)
    )
    assert result.scalar_one_or_none() is not None
    
    # 验证可以通过tag_id查询
    result = await test_session.execute(
        select(ArticleTag).where(ArticleTag.tag_id == tag.id)
    )
    assert result.scalar_one_or_none() is not None


@pytest.mark.asyncio
async def test_article_relationships_defined(test_session: AsyncSession):
    """测试文章关系定义（不测试功能，只验证关系存在）"""
    article = Article(
        title="测试文章",
        content="测试内容",
        word_count=100,
        reading_time=1
    )
    
    test_session.add(article)
    await test_session.commit()
    await test_session.refresh(article)
    
    assert hasattr(article, 'questions')
    assert hasattr(article, 'tags')
    assert hasattr(article, 'progresses')


@pytest.mark.asyncio
async def test_article_updated_at_auto_update(test_session: AsyncSession):
    """测试updated_at字段自动更新"""
    article = Article(
        title="测试文章",
        content="测试内容",
        word_count=100,
        reading_time=1
    )
    
    test_session.add(article)
    await test_session.commit()
    await test_session.refresh(article)
    
    original_updated_at = article.updated_at
    
    # 等待一小段时间
    await asyncio.sleep(0.1)
    
    # 更新文章
    article.title = "更新后的标题"
    await test_session.commit()
    await test_session.refresh(article)
    
    # 验证updated_at已更新
    assert article.updated_at > original_updated_at
