import enum

import pytest
from datetime import datetime, timezone
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import UniqueConstraint, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


TestBase = declarative_base()


class TagCategoryEnum(enum.Enum):
    """标签分类枚举"""

    GRADE = "grade"
    GENRE = "genre"
    SOURCE = "source"
    THEME = "theme"
    CULTURE = "culture"
    ADAPTATION = "adaptation"


class Article(TestBase):
    """文章表（简化版，用于测试）"""

    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(String, nullable=False)
    word_count = Column(Integer, nullable=False)
    reading_time = Column(Integer, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    questions = None
    tags = None
    progresses = None


class ArticleTag(TestBase):
    """文章-标签关联表（简化版，用于测试）"""

    __tablename__ = "article_tags"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(
        Integer,
        ForeignKey("articles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tag_id = Column(
        Integer, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False, index=True
    )

    article = None
    tag = None

    __table_args__ = (UniqueConstraint("article_id", "tag_id", name="uq_article_tag"),)


class Tag(TestBase):
    """标签表"""

    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, comment="标签名称")
    category = Column(
        SQLEnum(TagCategoryEnum), nullable=False, index=True, comment="标签分类"
    )
    description = Column(String(200), nullable=True, comment="标签描述")
    display_order = Column(Integer, default=0, comment="显示顺序")

    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), comment="创建时间"
    )

    article_tags = None

    __table_args__ = (
        UniqueConstraint("name", "category", name="uq_tag_name_category"),
    )

    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name}, category={self.category})>"


@pytest.fixture
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(TestBase.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(TestBase.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine):
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.mark.asyncio
async def test_tag_category_enum_values():
    assert TagCategoryEnum.GRADE.value == "grade"
    assert TagCategoryEnum.GENRE.value == "genre"
    assert TagCategoryEnum.SOURCE.value == "source"
    assert TagCategoryEnum.THEME.value == "theme"
    assert TagCategoryEnum.CULTURE.value == "culture"
    assert TagCategoryEnum.ADAPTATION.value == "adaptation"


@pytest.mark.asyncio
async def test_create_tag_with_all_fields(test_session: AsyncSession):
    tag = Tag(
        name="五年级",
        category=TagCategoryEnum.GRADE,
        description="适合五年级学生阅读的文章",
        display_order=5,
    )

    test_session.add(tag)
    await test_session.commit()
    await test_session.refresh(tag)

    assert tag.id is not None
    assert tag.name == "五年级"
    assert tag.category == TagCategoryEnum.GRADE
    assert tag.description == "适合五年级学生阅读的文章"
    assert tag.display_order == 5
    assert tag.created_at is not None


@pytest.mark.asyncio
async def test_tag_default_values(test_session: AsyncSession):
    tag = Tag(name="寓言", category=TagCategoryEnum.GENRE)

    test_session.add(tag)
    await test_session.commit()
    await test_session.refresh(tag)

    assert tag.description is None
    assert tag.display_order == 0
    assert tag.created_at is not None


@pytest.mark.asyncio
async def test_tag_unique_constraint_same_name_and_category(test_session: AsyncSession):
    tag1 = Tag(name="五年级", category=TagCategoryEnum.GRADE)

    test_session.add(tag1)
    await test_session.commit()

    tag2 = Tag(name="五年级", category=TagCategoryEnum.GRADE)

    test_session.add(tag2)

    with pytest.raises(IntegrityError):
        await test_session.commit()


@pytest.mark.asyncio
async def test_tag_unique_constraint_allows_same_name_different_category(
    test_session: AsyncSession,
):
    tag1 = Tag(name="五年级", category=TagCategoryEnum.GRADE)

    tag2 = Tag(name="五年级", category=TagCategoryEnum.GENRE)

    test_session.add(tag1)
    test_session.add(tag2)

    await test_session.commit()
    await test_session.refresh(tag1)
    await test_session.refresh(tag2)

    assert tag1.id is not None
    assert tag2.id is not None
    assert tag1.id != tag2.id


@pytest.mark.asyncio
async def test_tag_repr(test_session: AsyncSession):
    tag = Tag(name="神话", category=TagCategoryEnum.CULTURE)

    repr_str = repr(tag)
    assert "Tag" in repr_str
    assert "神话" in repr_str
    assert "CULTURE" in repr_str


@pytest.mark.asyncio
async def test_tag_name_not_nullable(test_session: AsyncSession):
    tag = Tag(category=TagCategoryEnum.GRADE)

    test_session.add(tag)

    with pytest.raises(IntegrityError):
        await test_session.commit()


@pytest.mark.asyncio
async def test_tag_category_not_nullable(test_session: AsyncSession):
    tag = Tag(name="测试标签")

    test_session.add(tag)

    with pytest.raises(IntegrityError):
        await test_session.commit()


@pytest.mark.asyncio
async def test_tag_category_indexed(test_session: AsyncSession):
    tag1 = Tag(name="标签1", category=TagCategoryEnum.GRADE)
    tag2 = Tag(name="标签2", category=TagCategoryEnum.GRADE)
    tag3 = Tag(name="标签3", category=TagCategoryEnum.GENRE)

    test_session.add(tag1)
    test_session.add(tag2)
    test_session.add(tag3)
    await test_session.commit()

    result = await test_session.execute(
        select(Tag).where(Tag.category == TagCategoryEnum.GRADE)
    )
    grade_tags = result.scalars().all()
    assert len(grade_tags) == 2


@pytest.mark.asyncio
async def test_tag_article_tag_relationship(test_session: AsyncSession):
    tag = Tag(name="五年级", category=TagCategoryEnum.GRADE)

    article = Article(
        title="测试文章", content="测试内容", word_count=100, reading_time=1
    )

    test_session.add(tag)
    test_session.add(article)
    await test_session.commit()
    await test_session.refresh(tag)
    await test_session.refresh(article)

    article_tag = ArticleTag(article_id=article.id, tag_id=tag.id)

    test_session.add(article_tag)
    await test_session.commit()

    assert article_tag.id is not None
    assert article_tag.tag_id == tag.id


@pytest.mark.asyncio
async def test_multiple_articles_same_tag(test_session: AsyncSession):
    tag = Tag(name="寓言", category=TagCategoryEnum.GENRE)

    article1 = Article(title="文章1", content="内容1", word_count=100, reading_time=1)
    article2 = Article(title="文章2", content="内容2", word_count=100, reading_time=1)

    test_session.add(tag)
    test_session.add(article1)
    test_session.add(article2)
    await test_session.commit()
    await test_session.refresh(tag)
    await test_session.refresh(article1)
    await test_session.refresh(article2)

    article_tag1 = ArticleTag(article_id=article1.id, tag_id=tag.id)
    article_tag2 = ArticleTag(article_id=article2.id, tag_id=tag.id)

    test_session.add(article_tag1)
    test_session.add(article_tag2)
    await test_session.commit()

    result = await test_session.execute(
        select(ArticleTag).where(ArticleTag.tag_id == tag.id)
    )
    article_tags = result.scalars().all()
    assert len(article_tags) == 2


@pytest.mark.asyncio
async def test_tag_display_order(test_session: AsyncSession):
    tag1 = Tag(name="一年级", category=TagCategoryEnum.GRADE, display_order=1)
    tag2 = Tag(name="二年级", category=TagCategoryEnum.GRADE, display_order=2)
    tag3 = Tag(name="三年级", category=TagCategoryEnum.GRADE, display_order=3)

    test_session.add(tag1)
    test_session.add(tag2)
    test_session.add(tag3)
    await test_session.commit()
    await test_session.refresh(tag1)
    await test_session.refresh(tag2)
    await test_session.refresh(tag3)

    assert tag1.display_order == 1
    assert tag2.display_order == 2
    assert tag3.display_order == 3

    result = await test_session.execute(
        select(Tag)
        .where(Tag.category == TagCategoryEnum.GRADE)
        .order_by(Tag.display_order)
    )
    ordered_tags = result.scalars().all()

    assert ordered_tags[0].name == "一年级"
    assert ordered_tags[1].name == "二年级"
    assert ordered_tags[2].name == "三年级"


@pytest.mark.asyncio
async def test_tag_description_max_length(test_session: AsyncSession):
    long_description = "a" * 200
    tag = Tag(
        name="测试标签", category=TagCategoryEnum.GRADE, description=long_description
    )

    test_session.add(tag)
    await test_session.commit()
    await test_session.refresh(tag)

    assert len(tag.description) == 200


@pytest.mark.asyncio
async def test_tag_name_max_length(test_session: AsyncSession):
    long_name = "a" * 50
    tag = Tag(name=long_name, category=TagCategoryEnum.GRADE)

    test_session.add(tag)
    await test_session.commit()
    await test_session.refresh(tag)

    assert len(tag.name) == 50
