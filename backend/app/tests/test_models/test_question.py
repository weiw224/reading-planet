import enum

import pytest
from datetime import datetime, timezone
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import JSON, Boolean, UniqueConstraint, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


TestBase = declarative_base()


class DifficultyEnum(enum.Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3


class QuestionTypeEnum(enum.Enum):
    CHOICE = "choice"
    JUDGE = "judge"
    FILL = "fill"
    SHORT_ANSWER = "short_answer"


class Article(TestBase):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    word_count = Column(Integer, nullable=False)
    reading_time = Column(Integer, nullable=False)
    article_difficulty = Column(SQLEnum(DifficultyEnum), default=DifficultyEnum.MEDIUM)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    questions = None
    tags = None
    progresses = None


class AbilityDimension(TestBase):
    __tablename__ = "ability_dimensions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)

    question_abilities = None


class Question(TestBase):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(
        Integer,
        ForeignKey("articles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    type = Column(SQLEnum(QuestionTypeEnum), nullable=False, comment="题目类型")
    content = Column(Text, nullable=False, comment="题干内容")

    options = Column(JSON, nullable=True, comment="选项（选择题）")

    answer = Column(Text, nullable=False, comment="正确答案")

    explanation = Column(Text, nullable=True, comment="答案解析")
    hint = Column(String(500), nullable=True, comment="温柔提示")

    difficulty = Column(
        SQLEnum(DifficultyEnum), default=DifficultyEnum.MEDIUM, comment="题目难度"
    )

    display_order = Column(Integer, default=0, comment="题目顺序")

    is_ai_generated = Column(Boolean, default=False, comment="是否AI生成")

    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), comment="创建时间"
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        comment="更新时间",
    )

    article = None
    abilities = None
    answers = None

    def __repr__(self):
        return f"<Question(id={self.id}, type={self.type})>"


class QuestionAbility(TestBase):
    __tablename__ = "question_abilities"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(
        Integer,
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ability_id = Column(
        Integer,
        ForeignKey("ability_dimensions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    weight = Column(Integer, default=1, comment="权重 1-10")

    question = None
    ability = None

    __table_args__ = (
        UniqueConstraint("question_id", "ability_id", name="uq_question_ability"),
    )


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
async def test_question_type_enum_values():
    assert QuestionTypeEnum.CHOICE.value == "choice"
    assert QuestionTypeEnum.JUDGE.value == "judge"
    assert QuestionTypeEnum.FILL.value == "fill"
    assert QuestionTypeEnum.SHORT_ANSWER.value == "short_answer"


@pytest.mark.asyncio
async def test_create_choice_question(test_session: AsyncSession):
    article = Article(
        title="测试文章", content="测试内容", word_count=100, reading_time=1
    )
    test_session.add(article)
    await test_session.commit()
    await test_session.refresh(article)

    question = Question(
        article_id=article.id,
        type=QuestionTypeEnum.CHOICE,
        content="下列哪个是正确的？",
        options=["选项A", "选项B", "选项C", "选项D"],
        answer="A",
        explanation="选项A是正确的，因为...",
        hint="仔细阅读文章",
        difficulty=DifficultyEnum.MEDIUM,
        display_order=1,
        is_ai_generated=False,
    )

    test_session.add(question)
    await test_session.commit()
    await test_session.refresh(question)

    assert question.id is not None
    assert question.type == QuestionTypeEnum.CHOICE
    assert question.content == "下列哪个是正确的？"
    assert question.options == ["选项A", "选项B", "选项C", "选项D"]
    assert question.answer == "A"
    assert question.explanation == "选项A是正确的，因为..."
    assert question.hint == "仔细阅读文章"
    assert question.difficulty == DifficultyEnum.MEDIUM
    assert question.display_order == 1
    assert question.is_ai_generated is False


@pytest.mark.asyncio
async def test_create_judge_question(test_session: AsyncSession):
    article = Article(
        title="测试文章", content="测试内容", word_count=100, reading_time=1
    )
    test_session.add(article)
    await test_session.commit()
    await test_session.refresh(article)

    question = Question(
        article_id=article.id,
        type=QuestionTypeEnum.JUDGE,
        content="判断题：这句话是正确的吗？",
        answer="true",
        explanation="这句话是正确的，因为...",
        difficulty=DifficultyEnum.EASY,
        display_order=2,
    )

    test_session.add(question)
    await test_session.commit()
    await test_session.refresh(question)

    assert question.id is not None
    assert question.type == QuestionTypeEnum.JUDGE
    assert question.content == "判断题：这句话是正确的吗？"
    assert question.options is None
    assert question.answer == "true"
    assert question.explanation == "这句话是正确的，因为..."
    assert question.difficulty == DifficultyEnum.EASY
    assert question.display_order == 2


@pytest.mark.asyncio
async def test_create_fill_question(test_session: AsyncSession):
    article = Article(
        title="测试文章", content="测试内容", word_count=100, reading_time=1
    )
    test_session.add(article)
    await test_session.commit()
    await test_session.refresh(article)

    question = Question(
        article_id=article.id,
        type=QuestionTypeEnum.FILL,
        content="填空题：答案是____",
        answer="正确答案",
        explanation="根据文章第一段...",
        difficulty=DifficultyEnum.HARD,
        display_order=3,
    )

    test_session.add(question)
    await test_session.commit()
    await test_session.refresh(question)

    assert question.id is not None
    assert question.type == QuestionTypeEnum.FILL
    assert question.content == "填空题：答案是____"
    assert question.options is None
    assert question.answer == "正确答案"
    assert question.difficulty == DifficultyEnum.HARD


@pytest.mark.asyncio
async def test_create_short_answer_question(test_session: AsyncSession):
    article = Article(
        title="测试文章", content="测试内容", word_count=100, reading_time=1
    )
    test_session.add(article)
    await test_session.commit()
    await test_session.refresh(article)

    question = Question(
        article_id=article.id,
        type=QuestionTypeEnum.SHORT_ANSWER,
        content="简答题：请概括文章主旨",
        answer="文章主要讲述了...",
        explanation="参考答案要点：1. ... 2. ...",
        hint="注意抓住关键词",
        difficulty=DifficultyEnum.HARD,
        display_order=4,
    )

    test_session.add(question)
    await test_session.commit()
    await test_session.refresh(question)

    assert question.id is not None
    assert question.type == QuestionTypeEnum.SHORT_ANSWER
    assert question.content == "简答题：请概括文章主旨"
    assert question.answer == "文章主要讲述了..."
    assert question.explanation == "参考答案要点：1. ... 2. ..."
    assert question.hint == "注意抓住关键词"
    assert question.difficulty == DifficultyEnum.HARD


@pytest.mark.asyncio
async def test_question_default_values(test_session: AsyncSession):
    article = Article(
        title="测试文章", content="测试内容", word_count=100, reading_time=1
    )
    test_session.add(article)
    await test_session.commit()
    await test_session.refresh(article)

    question = Question(
        article_id=article.id,
        type=QuestionTypeEnum.CHOICE,
        content="测试问题",
        answer="A",
    )

    test_session.add(question)
    await test_session.commit()
    await test_session.refresh(question)

    assert question.options is None
    assert question.explanation is None
    assert question.hint is None
    assert question.difficulty == DifficultyEnum.MEDIUM
    assert question.display_order == 0
    assert question.is_ai_generated is False
    assert question.created_at is not None
    assert question.updated_at is not None


@pytest.mark.asyncio
async def test_question_type_not_nullable(test_session: AsyncSession):
    article = Article(
        title="测试文章", content="测试内容", word_count=100, reading_time=1
    )
    test_session.add(article)
    await test_session.commit()
    await test_session.refresh(article)

    question = Question(article_id=article.id, content="测试问题", answer="A")

    test_session.add(question)

    with pytest.raises(IntegrityError):
        await test_session.commit()


@pytest.mark.asyncio
async def test_question_content_not_nullable(test_session: AsyncSession):
    article = Article(
        title="测试文章", content="测试内容", word_count=100, reading_time=1
    )
    test_session.add(article)
    await test_session.commit()
    await test_session.refresh(article)

    question = Question(article_id=article.id, type=QuestionTypeEnum.CHOICE, answer="A")

    test_session.add(question)

    with pytest.raises(IntegrityError):
        await test_session.commit()


@pytest.mark.asyncio
async def test_question_answer_not_nullable(test_session: AsyncSession):
    article = Article(
        title="测试文章", content="测试内容", word_count=100, reading_time=1
    )
    test_session.add(article)
    await test_session.commit()
    await test_session.refresh(article)

    question = Question(
        article_id=article.id, type=QuestionTypeEnum.CHOICE, content="测试问题"
    )

    test_session.add(question)

    with pytest.raises(IntegrityError):
        await test_session.commit()


@pytest.mark.asyncio
async def test_question_article_id_not_nullable(test_session: AsyncSession):
    question = Question(type=QuestionTypeEnum.CHOICE, content="测试问题", answer="A")

    test_session.add(question)

    with pytest.raises(IntegrityError):
        await test_session.commit()


@pytest.mark.asyncio
async def test_question_options_json_field(test_session: AsyncSession):
    article = Article(
        title="测试文章", content="测试内容", word_count=100, reading_time=1
    )
    test_session.add(article)
    await test_session.commit()
    await test_session.refresh(article)

    options_list = ["选项A", "选项B", "选项C", "选项D"]
    question = Question(
        article_id=article.id,
        type=QuestionTypeEnum.CHOICE,
        content="测试问题",
        options=options_list,
        answer="A",
    )

    test_session.add(question)
    await test_session.commit()
    await test_session.refresh(question)

    assert question.options == options_list
    assert isinstance(question.options, list)
    assert len(question.options) == 4


@pytest.mark.asyncio
async def test_question_repr(test_session: AsyncSession):
    article = Article(
        title="测试文章", content="测试内容", word_count=100, reading_time=1
    )
    test_session.add(article)
    await test_session.commit()
    await test_session.refresh(article)

    question = Question(
        article_id=article.id,
        type=QuestionTypeEnum.CHOICE,
        content="测试问题",
        answer="A",
    )

    repr_str = repr(question)
    assert "Question" in repr_str
    assert "CHOICE" in repr_str


@pytest.mark.asyncio
async def test_multiple_questions_for_one_article(test_session: AsyncSession):
    article = Article(
        title="测试文章", content="测试内容", word_count=100, reading_time=1
    )
    test_session.add(article)
    await test_session.commit()
    await test_session.refresh(article)

    question1 = Question(
        article_id=article.id,
        type=QuestionTypeEnum.CHOICE,
        content="问题1",
        answer="A",
        display_order=1,
    )
    question2 = Question(
        article_id=article.id,
        type=QuestionTypeEnum.JUDGE,
        content="问题2",
        answer="true",
        display_order=2,
    )
    question3 = Question(
        article_id=article.id,
        type=QuestionTypeEnum.FILL,
        content="问题3",
        answer="答案3",
        display_order=3,
    )

    test_session.add(question1)
    test_session.add(question2)
    test_session.add(question3)
    await test_session.commit()

    result = await test_session.execute(
        select(Question)
        .where(Question.article_id == article.id)
        .order_by(Question.display_order)
    )
    questions = result.scalars().all()

    assert len(questions) == 3
    assert questions[0].content == "问题1"
    assert questions[1].content == "问题2"
    assert questions[2].content == "问题3"


@pytest.mark.asyncio
async def test_question_article_id_indexed(test_session: AsyncSession):
    article1 = Article(title="文章1", content="内容1", word_count=100, reading_time=1)
    article2 = Article(title="文章2", content="内容2", word_count=100, reading_time=1)
    test_session.add(article1)
    test_session.add(article2)
    await test_session.commit()
    await test_session.refresh(article1)
    await test_session.refresh(article2)

    question1 = Question(
        article_id=article1.id,
        type=QuestionTypeEnum.CHOICE,
        content="问题1",
        answer="A",
    )
    question2 = Question(
        article_id=article1.id,
        type=QuestionTypeEnum.JUDGE,
        content="问题2",
        answer="true",
    )
    question3 = Question(
        article_id=article2.id,
        type=QuestionTypeEnum.FILL,
        content="问题3",
        answer="答案3",
    )

    test_session.add(question1)
    test_session.add(question2)
    test_session.add(question3)
    await test_session.commit()

    result = await test_session.execute(
        select(Question).where(Question.article_id == article1.id)
    )
    questions = result.scalars().all()

    assert len(questions) == 2


@pytest.mark.asyncio
async def test_question_hint_max_length(test_session: AsyncSession):
    article = Article(
        title="测试文章", content="测试内容", word_count=100, reading_time=1
    )
    test_session.add(article)
    await test_session.commit()
    await test_session.refresh(article)

    long_hint = "a" * 500
    question = Question(
        article_id=article.id,
        type=QuestionTypeEnum.CHOICE,
        content="测试问题",
        answer="A",
        hint=long_hint,
    )

    test_session.add(question)
    await test_session.commit()
    await test_session.refresh(question)

    assert len(question.hint) == 500


@pytest.mark.asyncio
async def test_create_question_ability(test_session: AsyncSession):
    article = Article(
        title="测试文章", content="测试内容", word_count=100, reading_time=1
    )
    ability = AbilityDimension(name="阅读理解", description="理解文章内容的能力")

    test_session.add(article)
    test_session.add(ability)
    await test_session.commit()
    await test_session.refresh(article)
    await test_session.refresh(ability)

    question = Question(
        article_id=article.id,
        type=QuestionTypeEnum.CHOICE,
        content="测试问题",
        answer="A",
    )
    test_session.add(question)
    await test_session.commit()
    await test_session.refresh(question)

    question_ability = QuestionAbility(
        question_id=question.id, ability_id=ability.id, weight=5
    )

    test_session.add(question_ability)
    await test_session.commit()
    await test_session.refresh(question_ability)

    assert question_ability.id is not None
    assert question_ability.question_id == question.id
    assert question_ability.ability_id == ability.id
    assert question_ability.weight == 5


@pytest.mark.asyncio
async def test_question_ability_default_values(test_session: AsyncSession):
    article = Article(
        title="测试文章", content="测试内容", word_count=100, reading_time=1
    )
    ability = AbilityDimension(name="阅读理解", description="理解文章内容的能力")

    test_session.add(article)
    test_session.add(ability)
    await test_session.commit()
    await test_session.refresh(article)
    await test_session.refresh(ability)

    question = Question(
        article_id=article.id,
        type=QuestionTypeEnum.CHOICE,
        content="测试问题",
        answer="A",
    )
    test_session.add(question)
    await test_session.commit()
    await test_session.refresh(question)

    question_ability = QuestionAbility(question_id=question.id, ability_id=ability.id)

    test_session.add(question_ability)
    await test_session.commit()
    await test_session.refresh(question_ability)

    assert question_ability.weight == 1


@pytest.mark.asyncio
async def test_question_ability_unique_constraint(test_session: AsyncSession):
    article = Article(
        title="测试文章", content="测试内容", word_count=100, reading_time=1
    )
    ability = AbilityDimension(name="阅读理解", description="理解文章内容的能力")

    test_session.add(article)
    test_session.add(ability)
    await test_session.commit()
    await test_session.refresh(article)
    await test_session.refresh(ability)

    question = Question(
        article_id=article.id,
        type=QuestionTypeEnum.CHOICE,
        content="测试问题",
        answer="A",
    )
    test_session.add(question)
    await test_session.commit()
    await test_session.refresh(question)

    question_ability1 = QuestionAbility(
        question_id=question.id, ability_id=ability.id, weight=5
    )
    test_session.add(question_ability1)
    await test_session.commit()

    question_ability2 = QuestionAbility(
        question_id=question.id, ability_id=ability.id, weight=3
    )
    test_session.add(question_ability2)

    with pytest.raises(IntegrityError):
        await test_session.commit()


@pytest.mark.asyncio
async def test_question_ability_question_id_not_nullable(test_session: AsyncSession):
    ability = AbilityDimension(name="阅读理解", description="理解文章内容的能力")

    test_session.add(ability)
    await test_session.commit()
    await test_session.refresh(ability)

    question_ability = QuestionAbility(ability_id=ability.id)

    test_session.add(question_ability)

    with pytest.raises(IntegrityError):
        await test_session.commit()


@pytest.mark.asyncio
async def test_question_ability_ability_id_not_nullable(test_session: AsyncSession):
    article = Article(
        title="测试文章", content="测试内容", word_count=100, reading_time=1
    )

    test_session.add(article)
    await test_session.commit()
    await test_session.refresh(article)

    question = Question(
        article_id=article.id,
        type=QuestionTypeEnum.CHOICE,
        content="测试问题",
        answer="A",
    )
    test_session.add(question)
    await test_session.commit()
    await test_session.refresh(question)

    question_ability = QuestionAbility(question_id=question.id)

    test_session.add(question_ability)

    with pytest.raises(IntegrityError):
        await test_session.commit()


@pytest.mark.asyncio
async def test_question_ability_question_id_indexed(test_session: AsyncSession):
    article = Article(
        title="测试文章", content="测试内容", word_count=100, reading_time=1
    )
    ability1 = AbilityDimension(name="能力1", description="能力描述1")
    ability2 = AbilityDimension(name="能力2", description="能力描述2")

    test_session.add(article)
    test_session.add(ability1)
    test_session.add(ability2)
    await test_session.commit()
    await test_session.refresh(article)
    await test_session.refresh(ability1)
    await test_session.refresh(ability2)

    question = Question(
        article_id=article.id,
        type=QuestionTypeEnum.CHOICE,
        content="测试问题",
        answer="A",
    )
    test_session.add(question)
    await test_session.commit()
    await test_session.refresh(question)

    question_ability1 = QuestionAbility(question_id=question.id, ability_id=ability1.id)
    question_ability2 = QuestionAbility(question_id=question.id, ability_id=ability2.id)

    test_session.add(question_ability1)
    test_session.add(question_ability2)
    await test_session.commit()

    result = await test_session.execute(
        select(QuestionAbility).where(QuestionAbility.question_id == question.id)
    )
    question_abilities = result.scalars().all()

    assert len(question_abilities) == 2


@pytest.mark.asyncio
async def test_question_ability_ability_id_indexed(test_session: AsyncSession):
    article1 = Article(title="文章1", content="内容1", word_count=100, reading_time=1)
    article2 = Article(title="文章2", content="内容2", word_count=100, reading_time=1)
    ability = AbilityDimension(name="阅读理解", description="理解文章内容的能力")

    test_session.add(article1)
    test_session.add(article2)
    test_session.add(ability)
    await test_session.commit()
    await test_session.refresh(article1)
    await test_session.refresh(article2)
    await test_session.refresh(ability)

    question1 = Question(
        article_id=article1.id,
        type=QuestionTypeEnum.CHOICE,
        content="问题1",
        answer="A",
    )
    question2 = Question(
        article_id=article2.id,
        type=QuestionTypeEnum.JUDGE,
        content="问题2",
        answer="true",
    )

    test_session.add(question1)
    test_session.add(question2)
    await test_session.commit()
    await test_session.refresh(question1)
    await test_session.refresh(question2)

    question_ability1 = QuestionAbility(question_id=question1.id, ability_id=ability.id)
    question_ability2 = QuestionAbility(question_id=question2.id, ability_id=ability.id)

    test_session.add(question_ability1)
    test_session.add(question_ability2)
    await test_session.commit()

    result = await test_session.execute(
        select(QuestionAbility).where(QuestionAbility.ability_id == ability.id)
    )
    question_abilities = result.scalars().all()

    assert len(question_abilities) == 2


@pytest.mark.asyncio
async def test_multiple_abilities_for_one_question(test_session: AsyncSession):
    article = Article(
        title="测试文章", content="测试内容", word_count=100, reading_time=1
    )
    ability1 = AbilityDimension(name="阅读理解", description="理解文章内容的能力")
    ability2 = AbilityDimension(name="逻辑推理", description="逻辑推理能力")
    ability3 = AbilityDimension(name="词汇理解", description="理解词汇的能力")

    test_session.add(article)
    test_session.add(ability1)
    test_session.add(ability2)
    test_session.add(ability3)
    await test_session.commit()
    await test_session.refresh(article)
    await test_session.refresh(ability1)
    await test_session.refresh(ability2)
    await test_session.refresh(ability3)

    question = Question(
        article_id=article.id,
        type=QuestionTypeEnum.CHOICE,
        content="测试问题",
        answer="A",
    )
    test_session.add(question)
    await test_session.commit()
    await test_session.refresh(question)

    question_ability1 = QuestionAbility(
        question_id=question.id, ability_id=ability1.id, weight=5
    )
    question_ability2 = QuestionAbility(
        question_id=question.id, ability_id=ability2.id, weight=3
    )
    question_ability3 = QuestionAbility(
        question_id=question.id, ability_id=ability3.id, weight=2
    )

    test_session.add(question_ability1)
    test_session.add(question_ability2)
    test_session.add(question_ability3)
    await test_session.commit()

    result = await test_session.execute(
        select(QuestionAbility).where(QuestionAbility.question_id == question.id)
    )
    question_abilities = result.scalars().all()

    assert len(question_abilities) == 3


@pytest.mark.asyncio
async def test_one_ability_for_multiple_questions(test_session: AsyncSession):
    article = Article(
        title="测试文章", content="测试内容", word_count=100, reading_time=1
    )
    ability = AbilityDimension(name="阅读理解", description="理解文章内容的能力")

    test_session.add(article)
    test_session.add(ability)
    await test_session.commit()
    await test_session.refresh(article)
    await test_session.refresh(ability)

    question1 = Question(
        article_id=article.id, type=QuestionTypeEnum.CHOICE, content="问题1", answer="A"
    )
    question2 = Question(
        article_id=article.id,
        type=QuestionTypeEnum.JUDGE,
        content="问题2",
        answer="true",
    )
    question3 = Question(
        article_id=article.id,
        type=QuestionTypeEnum.FILL,
        content="问题3",
        answer="答案3",
    )

    test_session.add(question1)
    test_session.add(question2)
    test_session.add(question3)
    await test_session.commit()
    await test_session.refresh(question1)
    await test_session.refresh(question2)
    await test_session.refresh(question3)

    question_ability1 = QuestionAbility(question_id=question1.id, ability_id=ability.id)
    question_ability2 = QuestionAbility(question_id=question2.id, ability_id=ability.id)
    question_ability3 = QuestionAbility(question_id=question3.id, ability_id=ability.id)

    test_session.add(question_ability1)
    test_session.add(question_ability2)
    test_session.add(question_ability3)
    await test_session.commit()

    result = await test_session.execute(
        select(QuestionAbility).where(QuestionAbility.ability_id == ability.id)
    )
    question_abilities = result.scalars().all()

    assert len(question_abilities) == 3


@pytest.mark.asyncio
async def test_question_foreign_key_cascade_configured(test_engine):
    from sqlalchemy.engine import reflection

    async with test_engine.connect() as conn:
        inspector = await conn.run_sync(
            lambda sync_conn: reflection.Inspector.from_engine(sync_conn)
        )

        foreign_keys = await conn.run_sync(
            lambda sync_conn: inspector.get_foreign_keys("questions")
        )

        article_fk = [
            fk for fk in foreign_keys if "article_id" in fk["constrained_columns"]
        ][0]
        assert "options" in article_fk
        assert article_fk["options"].get("ondelete") == "CASCADE"


@pytest.mark.asyncio
async def test_question_ability_foreign_key_cascade_configured(test_engine):
    from sqlalchemy.engine import reflection

    async with test_engine.connect() as conn:
        inspector = await conn.run_sync(
            lambda sync_conn: reflection.Inspector.from_engine(sync_conn)
        )

        foreign_keys = await conn.run_sync(
            lambda sync_conn: inspector.get_foreign_keys("question_abilities")
        )

        question_fk = [
            fk for fk in foreign_keys if "question_id" in fk["constrained_columns"]
        ][0]
        assert "options" in question_fk
        assert question_fk["options"].get("ondelete") == "CASCADE"

        ability_fk = [
            fk for fk in foreign_keys if "ability_id" in fk["constrained_columns"]
        ][0]
        assert "options" in ability_fk
        assert ability_fk["options"].get("ondelete") == "CASCADE"


@pytest.mark.asyncio
async def test_question_display_order_ordering(test_session: AsyncSession):
    article = Article(
        title="测试文章", content="测试内容", word_count=100, reading_time=1
    )
    test_session.add(article)
    await test_session.commit()
    await test_session.refresh(article)

    question1 = Question(
        article_id=article.id,
        type=QuestionTypeEnum.CHOICE,
        content="问题3",
        answer="A",
        display_order=3,
    )
    question2 = Question(
        article_id=article.id,
        type=QuestionTypeEnum.JUDGE,
        content="问题1",
        answer="true",
        display_order=1,
    )
    question3 = Question(
        article_id=article.id,
        type=QuestionTypeEnum.FILL,
        content="问题2",
        answer="答案3",
        display_order=2,
    )

    test_session.add(question1)
    test_session.add(question2)
    test_session.add(question3)
    await test_session.commit()

    result = await test_session.execute(
        select(Question)
        .where(Question.article_id == article.id)
        .order_by(Question.display_order)
    )
    questions = result.scalars().all()

    assert questions[0].display_order == 1
    assert questions[1].display_order == 2
    assert questions[2].display_order == 3


@pytest.mark.asyncio
async def test_question_is_ai_generated_flag(test_session: AsyncSession):
    article = Article(
        title="测试文章", content="测试内容", word_count=100, reading_time=1
    )
    test_session.add(article)
    await test_session.commit()
    await test_session.refresh(article)

    question1 = Question(
        article_id=article.id,
        type=QuestionTypeEnum.CHOICE,
        content="AI生成的问题",
        answer="A",
        is_ai_generated=True,
    )
    question2 = Question(
        article_id=article.id,
        type=QuestionTypeEnum.JUDGE,
        content="人工编写的问题",
        answer="true",
        is_ai_generated=False,
    )

    test_session.add(question1)
    test_session.add(question2)
    await test_session.commit()

    result = await test_session.execute(
        select(Question).where(Question.is_ai_generated == True)
    )
    ai_questions = result.scalars().all()

    assert len(ai_questions) == 1
    assert ai_questions[0].is_ai_generated is True


@pytest.mark.asyncio
async def test_question_relationships_defined(test_session: AsyncSession):
    article = Article(
        title="测试文章", content="测试内容", word_count=100, reading_time=1
    )
    test_session.add(article)
    await test_session.commit()
    await test_session.refresh(article)

    question = Question(
        article_id=article.id,
        type=QuestionTypeEnum.CHOICE,
        content="测试问题",
        answer="A",
    )

    test_session.add(question)
    await test_session.commit()
    await test_session.refresh(question)

    assert hasattr(question, "article")
    assert hasattr(question, "abilities")
    assert hasattr(question, "answers")
