import pytest
import asyncio
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Text, Boolean, String
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
from sqlalchemy import select


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


# Create a separate Base for testing to avoid importing from app.database
TestBase = declarative_base()


class User(TestBase):
    """用户表（测试用）"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    openid = Column(String, unique=True, nullable=False)
    nickname = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # 关系
    progresses = None

    def __repr__(self):
        return f"<User(id={self.id}, nickname={self.nickname})>"


class Article(TestBase):
    """文章表（测试用）"""

    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    word_count = Column(Integer, nullable=False)
    reading_time = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # 关系
    questions = None
    progresses = None

    def __repr__(self):
        return f"<Article(id={self.id}, title={self.title})>"


class Question(TestBase):
    """题目表（测试用）"""

    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(
        Integer,
        ForeignKey("articles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # 关系
    article = None
    answers = None

    def __repr__(self):
        return f"<Question(id={self.id}, type={self.type})>"


class UserProgress(TestBase):
    """用户阅读进度表（测试用）"""

    __tablename__ = "user_progresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    article_id = Column(
        Integer,
        ForeignKey("articles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # 成绩
    score = Column(Integer, nullable=True)
    correct_count = Column(Integer, default=0)
    total_count = Column(Integer, default=0)

    # 用时
    time_spent = Column(Integer, nullable=True)

    # 状态
    completed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # 关系
    user = None
    article = None
    answers = None

    def __repr__(self):
        return f"<UserProgress(id={self.id}, user_id={self.user_id}, article_id={self.article_id})>"


class QuestionAnswer(TestBase):
    """用户答题记录表（测试用）"""

    __tablename__ = "question_answers"

    id = Column(Integer, primary_key=True, index=True)
    progress_id = Column(
        Integer,
        ForeignKey("user_progresses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id = Column(
        Integer,
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # 用户答案
    user_answer = Column(Text, nullable=True)
    is_correct = Column(Boolean, nullable=True)

    # 简答题 AI 评分（可选）
    ai_score = Column(Integer, nullable=True)
    ai_feedback = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # 关系
    progress = None
    question = None

    def __repr__(self):
        return f"<QuestionAnswer(id={self.id}, is_correct={self.is_correct})>"


@pytest.fixture
async def test_engine():
    """创建测试用的异步引擎"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(TestBase.metadata.create_all)
        await conn.run_sync(
            lambda sync_conn: sync_conn.execute(
                sqlalchemy.text("PRAGMA foreign_keys = ON")
            )
        )
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


@pytest.fixture
async def sample_user(test_session: AsyncSession):
    """创建测试用户"""
    user = User(openid="test_user_123", nickname="测试用户")
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest.fixture
async def sample_article(test_session: AsyncSession):
    """创建测试文章"""
    article = Article(
        title="测试文章", content="测试内容", word_count=100, reading_time=1
    )
    test_session.add(article)
    await test_session.commit()
    await test_session.refresh(article)
    return article


@pytest.fixture
async def sample_question(test_session: AsyncSession, sample_article: Article):
    """创建测试题目"""
    question = Question(
        article_id=sample_article.id, type="choice", content="测试题目", answer="A"
    )
    test_session.add(question)
    await test_session.commit()
    await test_session.refresh(question)
    return question


@pytest.mark.asyncio
async def test_create_user_progress_with_all_fields(
    test_session: AsyncSession, sample_user: User, sample_article: Article
):
    """测试创建包含所有字段的学习进度"""
    progress = UserProgress(
        user_id=sample_user.id,
        article_id=sample_article.id,
        score=85,
        correct_count=4,
        total_count=5,
        time_spent=120,
        completed_at=datetime.now(timezone.utc),
    )

    test_session.add(progress)
    await test_session.commit()
    await test_session.refresh(progress)

    assert progress.id is not None
    assert progress.user_id == sample_user.id
    assert progress.article_id == sample_article.id
    assert progress.score == 85
    assert progress.correct_count == 4
    assert progress.total_count == 5
    assert progress.time_spent == 120
    assert progress.completed_at is not None
    assert progress.created_at is not None


@pytest.mark.asyncio
async def test_user_progress_default_values(
    test_session: AsyncSession, sample_user: User, sample_article: Article
):
    """测试学习进度默认值"""
    progress = UserProgress(user_id=sample_user.id, article_id=sample_article.id)

    test_session.add(progress)
    await test_session.commit()
    await test_session.refresh(progress)

    assert progress.score is None
    assert progress.correct_count == 0
    assert progress.total_count == 0
    assert progress.time_spent is None
    assert progress.completed_at is None
    assert progress.created_at is not None


@pytest.mark.asyncio
async def test_user_progress_foreign_key_constraint_user(
    test_session: AsyncSession, sample_article: Article
):
    """测试学习进度用户外键约束"""
    progress = UserProgress(user_id=999, article_id=sample_article.id)  # 不存在的用户ID

    test_session.add(progress)
    with pytest.raises(IntegrityError):
        await test_session.commit()


@pytest.mark.asyncio
async def test_user_progress_foreign_key_constraint_article(
    test_session: AsyncSession, sample_user: User
):
    """测试学习进度文章外键约束"""
    progress = UserProgress(user_id=sample_user.id, article_id=999)  # 不存在的文章ID

    test_session.add(progress)
    with pytest.raises(IntegrityError):
        await test_session.commit()


@pytest.mark.asyncio
async def test_user_progress_cascade_delete_user(
    test_session: AsyncSession, sample_user: User, sample_article: Article
):
    """测试删除用户时级联删除学习进度"""
    progress = UserProgress(
        user_id=sample_user.id, article_id=sample_article.id, score=90
    )

    test_session.add(progress)
    await test_session.commit()
    progress_id = progress.id

    # 删除用户
    await test_session.delete(sample_user)
    await test_session.commit()

    # 验证学习进度已被级联删除
    result = await test_session.execute(
        select(UserProgress).where(UserProgress.id == progress_id)
    )
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_user_progress_cascade_delete_article(
    test_session: AsyncSession, sample_user: User, sample_article: Article
):
    """测试删除文章时级联删除学习进度"""
    progress = UserProgress(
        user_id=sample_user.id, article_id=sample_article.id, score=90
    )

    test_session.add(progress)
    await test_session.commit()
    progress_id = progress.id

    # 删除文章
    await test_session.delete(sample_article)
    await test_session.commit()

    # 验证学习进度已被级联删除
    result = await test_session.execute(
        select(UserProgress).where(UserProgress.id == progress_id)
    )
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_user_progress_relationships_defined(
    test_session: AsyncSession, sample_user: User, sample_article: Article
):
    """测试学习进度关系定义"""
    progress = UserProgress(user_id=sample_user.id, article_id=sample_article.id)

    test_session.add(progress)
    await test_session.commit()
    await test_session.refresh(progress)

    assert hasattr(progress, "user")
    assert hasattr(progress, "article")
    assert hasattr(progress, "answers")


@pytest.mark.asyncio
async def test_user_progress_repr(
    test_session: AsyncSession, sample_user: User, sample_article: Article
):
    """测试学习进度__repr__方法"""
    progress = UserProgress(user_id=sample_user.id, article_id=sample_article.id)

    repr_str = repr(progress)
    assert "UserProgress" in repr_str
    assert str(sample_user.id) in repr_str
    assert str(sample_article.id) in repr_str


@pytest.mark.asyncio
async def test_create_question_answer_with_all_fields(
    test_session: AsyncSession,
    sample_user: User,
    sample_article: Article,
    sample_question: Question,
):
    """测试创建包含所有字段的答题记录"""
    progress = UserProgress(user_id=sample_user.id, article_id=sample_article.id)
    test_session.add(progress)
    await test_session.commit()
    await test_session.refresh(progress)

    answer = QuestionAnswer(
        progress_id=progress.id,
        question_id=sample_question.id,
        user_answer="A",
        is_correct=True,
        ai_score=95,
        ai_feedback="回答正确",
    )

    test_session.add(answer)
    await test_session.commit()
    await test_session.refresh(answer)

    assert answer.id is not None
    assert answer.progress_id == progress.id
    assert answer.question_id == sample_question.id
    assert answer.user_answer == "A"
    assert answer.is_correct is True
    assert answer.ai_score == 95
    assert answer.ai_feedback == "回答正确"
    assert answer.created_at is not None


@pytest.mark.asyncio
async def test_question_answer_default_values(
    test_session: AsyncSession,
    sample_user: User,
    sample_article: Article,
    sample_question: Question,
):
    """测试答题记录默认值"""
    progress = UserProgress(user_id=sample_user.id, article_id=sample_article.id)
    test_session.add(progress)
    await test_session.commit()
    await test_session.refresh(progress)

    answer = QuestionAnswer(progress_id=progress.id, question_id=sample_question.id)

    test_session.add(answer)
    await test_session.commit()
    await test_session.refresh(answer)

    assert answer.user_answer is None
    assert answer.is_correct is None
    assert answer.ai_score is None
    assert answer.ai_feedback is None
    assert answer.created_at is not None


@pytest.mark.asyncio
async def test_question_answer_foreign_key_constraint_progress(
    test_session: AsyncSession, sample_question: Question
):
    """测试答题记录进度外键约束"""
    answer = QuestionAnswer(
        progress_id=999, question_id=sample_question.id  # 不存在的进度ID
    )

    test_session.add(answer)
    with pytest.raises(IntegrityError):
        await test_session.commit()


@pytest.mark.asyncio
async def test_question_answer_foreign_key_constraint_question(
    test_session: AsyncSession, sample_user: User, sample_article: Article
):
    """测试答题记录题目外键约束"""
    progress = UserProgress(user_id=sample_user.id, article_id=sample_article.id)
    test_session.add(progress)
    await test_session.commit()
    await test_session.refresh(progress)

    answer = QuestionAnswer(progress_id=progress.id, question_id=999)  # 不存在的题目ID

    test_session.add(answer)
    with pytest.raises(IntegrityError):
        await test_session.commit()


@pytest.mark.asyncio
async def test_question_answer_cascade_delete_progress(
    test_session: AsyncSession,
    sample_user: User,
    sample_article: Article,
    sample_question: Question,
):
    """测试删除进度时级联删除答题记录"""
    progress = UserProgress(user_id=sample_user.id, article_id=sample_article.id)
    test_session.add(progress)
    await test_session.commit()
    await test_session.refresh(progress)

    answer = QuestionAnswer(
        progress_id=progress.id,
        question_id=sample_question.id,
        user_answer="A",
        is_correct=True,
    )
    test_session.add(answer)
    await test_session.commit()
    answer_id = answer.id

    # 删除进度
    await test_session.delete(progress)
    await test_session.commit()

    # 验证答题记录已被级联删除
    result = await test_session.execute(
        select(QuestionAnswer).where(QuestionAnswer.id == answer_id)
    )
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_question_answer_cascade_delete_question(
    test_session: AsyncSession,
    sample_user: User,
    sample_article: Article,
    sample_question: Question,
):
    """测试删除题目时级联删除答题记录"""
    progress = UserProgress(user_id=sample_user.id, article_id=sample_article.id)
    test_session.add(progress)
    await test_session.commit()
    await test_session.refresh(progress)

    answer = QuestionAnswer(
        progress_id=progress.id,
        question_id=sample_question.id,
        user_answer="A",
        is_correct=True,
    )
    test_session.add(answer)
    await test_session.commit()
    answer_id = answer.id

    # 删除题目
    await test_session.delete(sample_question)
    await test_session.commit()

    # 验证答题记录已被级联删除
    result = await test_session.execute(
        select(QuestionAnswer).where(QuestionAnswer.id == answer_id)
    )
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_multiple_answers_for_one_progress(
    test_session: AsyncSession,
    sample_user: User,
    sample_article: Article,
    sample_question: Question,
):
    """测试一个进度关联多个答题记录"""
    progress = UserProgress(user_id=sample_user.id, article_id=sample_article.id)
    test_session.add(progress)
    await test_session.commit()
    await test_session.refresh(progress)

    # 创建第二个题目
    question2 = Question(
        article_id=sample_article.id, type="choice", content="测试题目2", answer="B"
    )
    test_session.add(question2)
    await test_session.commit()
    await test_session.refresh(question2)

    # 创建多个答题记录
    answer1 = QuestionAnswer(
        progress_id=progress.id,
        question_id=sample_question.id,
        user_answer="A",
        is_correct=True,
    )
    answer2 = QuestionAnswer(
        progress_id=progress.id,
        question_id=question2.id,
        user_answer="B",
        is_correct=True,
    )

    test_session.add(answer1)
    test_session.add(answer2)
    await test_session.commit()

    # 验证创建了2个答题记录
    result = await test_session.execute(
        select(QuestionAnswer).where(QuestionAnswer.progress_id == progress.id)
    )
    answers = result.scalars().all()
    assert len(answers) == 2


@pytest.mark.asyncio
async def test_question_answer_relationships_defined(
    test_session: AsyncSession,
    sample_user: User,
    sample_article: Article,
    sample_question: Question,
):
    """测试答题记录关系定义"""
    progress = UserProgress(user_id=sample_user.id, article_id=sample_article.id)
    test_session.add(progress)
    await test_session.commit()
    await test_session.refresh(progress)

    answer = QuestionAnswer(progress_id=progress.id, question_id=sample_question.id)
    test_session.add(answer)
    await test_session.commit()
    await test_session.refresh(answer)

    assert hasattr(answer, "progress")
    assert hasattr(answer, "question")


@pytest.mark.asyncio
async def test_question_answer_repr(
    test_session: AsyncSession,
    sample_user: User,
    sample_article: Article,
    sample_question: Question,
):
    """测试答题记录__repr__方法"""
    progress = UserProgress(user_id=sample_user.id, article_id=sample_article.id)
    test_session.add(progress)
    await test_session.commit()
    await test_session.refresh(progress)

    answer = QuestionAnswer(
        progress_id=progress.id, question_id=sample_question.id, is_correct=True
    )

    repr_str = repr(answer)
    assert "QuestionAnswer" in repr_str
    assert "True" in repr_str


@pytest.mark.asyncio
async def test_user_progress_foreign_key_indexes(
    test_session: AsyncSession, sample_user: User, sample_article: Article
):
    """测试学习进度外键索引"""
    progress = UserProgress(user_id=sample_user.id, article_id=sample_article.id)
    test_session.add(progress)
    await test_session.commit()

    # 验证可以通过user_id查询
    result = await test_session.execute(
        select(UserProgress).where(UserProgress.user_id == sample_user.id)
    )
    assert result.scalar_one_or_none() is not None

    # 验证可以通过article_id查询
    result = await test_session.execute(
        select(UserProgress).where(UserProgress.article_id == sample_article.id)
    )
    assert result.scalar_one_or_none() is not None


@pytest.mark.asyncio
async def test_question_answer_foreign_key_indexes(
    test_session: AsyncSession,
    sample_user: User,
    sample_article: Article,
    sample_question: Question,
):
    """测试答题记录外键索引"""
    progress = UserProgress(user_id=sample_user.id, article_id=sample_article.id)
    test_session.add(progress)
    await test_session.commit()
    await test_session.refresh(progress)

    answer = QuestionAnswer(progress_id=progress.id, question_id=sample_question.id)
    test_session.add(answer)
    await test_session.commit()

    # 验证可以通过progress_id查询
    result = await test_session.execute(
        select(QuestionAnswer).where(QuestionAnswer.progress_id == progress.id)
    )
    assert result.scalar_one_or_none() is not None

    # 验证可以通过question_id查询
    result = await test_session.execute(
        select(QuestionAnswer).where(QuestionAnswer.question_id == sample_question.id)
    )
    assert result.scalar_one_or_none() is not None


@pytest.mark.asyncio
async def test_user_progress_created_at_timezone(
    test_session: AsyncSession, sample_user: User, sample_article: Article
):
    """测试学习进度created_at使用UTC时区"""
    progress = UserProgress(user_id=sample_user.id, article_id=sample_article.id)

    test_session.add(progress)
    await test_session.commit()
    await test_session.refresh(progress)

    # 验证created_at已设置且是datetime对象
    assert progress.created_at is not None
    assert isinstance(progress.created_at, datetime)


@pytest.mark.asyncio
async def test_question_answer_created_at_timezone(
    test_session: AsyncSession,
    sample_user: User,
    sample_article: Article,
    sample_question: Question,
):
    """测试答题记录created_at使用UTC时区"""
    progress = UserProgress(user_id=sample_user.id, article_id=sample_article.id)
    test_session.add(progress)
    await test_session.commit()
    await test_session.refresh(progress)

    answer = QuestionAnswer(progress_id=progress.id, question_id=sample_question.id)
    test_session.add(answer)
    await test_session.commit()
    await test_session.refresh(answer)

    # 验证created_at已设置且是datetime对象
    assert answer.created_at is not None
    assert isinstance(answer.created_at, datetime)
