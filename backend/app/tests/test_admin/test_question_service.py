import pytest
from app.services.admin.question_service import admin_question_service
from app.schemas.admin.question import (
    QuestionCreateRequest,
    QuestionUpdateRequest,
    AbilityWeight,
    QuestionTypeEnum,
    DifficultyEnum
)
from app.models.question import Question, QuestionTypeEnum as DBQuestionTypeEnum, DifficultyEnum as DBDifficultyEnum
from app.models.ability import AbilityDimension, AbilityCategoryEnum


@pytest.mark.asyncio
async def test_create_question_choice(db_session, test_article):
    ability = AbilityDimension(
        name="理解能力",
        code="comprehension",
        category=AbilityCategoryEnum.COMPREHENSION
    )
    db_session.add(ability)
    await db_session.commit()
    await db_session.refresh(ability)

    data = QuestionCreateRequest(
        article_id=test_article.id,
        type=QuestionTypeEnum.CHOICE,
        content="这是什么颜色？",
        options=["红色", "蓝色", "绿色", "黄色"],
        answer="红色",
        explanation="这是解析",
        hint="这是一个提示",
        difficulty=DifficultyEnum.EASY,
        display_order=1,
        abilities=[AbilityWeight(ability_id=ability.id, weight=5)]
    )

    result = await admin_question_service.create_question(db_session, data)

    assert result.id is not None
    assert result.type == QuestionTypeEnum.CHOICE
    assert result.content == "这是什么颜色？"
    assert result.options == ["红色", "蓝色", "绿色", "黄色"]
    assert result.answer == "红色"
    assert result.difficulty == DifficultyEnum.EASY
    assert result.display_order == 1
    assert len(result.abilities) == 1
    assert result.abilities[0]["name"] == "理解能力"
    assert result.abilities[0]["weight"] == 5


@pytest.mark.asyncio
async def test_create_question_judge(db_session, test_article):
    data = QuestionCreateRequest(
        article_id=test_article.id,
        type=QuestionTypeEnum.JUDGE,
        content="这是对的吗？",
        answer="对",
        difficulty=DifficultyEnum.MEDIUM
    )

    result = await admin_question_service.create_question(db_session, data)

    assert result.type == QuestionTypeEnum.JUDGE
    assert result.options is None


@pytest.mark.asyncio
async def test_create_question_choice_without_options(db_session, test_article):
    data = QuestionCreateRequest(
        article_id=test_article.id,
        type=QuestionTypeEnum.CHOICE,
        content="测试问题",
        answer="A"
    )

    with pytest.raises(ValueError, match="选择题必须提供选项"):
        await admin_question_service.create_question(db_session, data)


@pytest.mark.asyncio
async def test_create_question_article_not_found(db_session):
    data = QuestionCreateRequest(
        article_id=99999,
        type=QuestionTypeEnum.JUDGE,
        content="测试问题",
        answer="对"
    )

    with pytest.raises(ValueError, match="文章不存在"):
        await admin_question_service.create_question(db_session, data)


@pytest.mark.asyncio
async def test_get_question_list(db_session, test_article):
    for i in range(3):
        question = Question(
            article_id=test_article.id,
            type=QuestionTypeEnum.JUDGE,
            difficulty=DifficultyEnum.EASY,
            content=f"问题{i}",
            answer="对"
        )
        db_session.add(question)
    await db_session.commit()

    items, total = await admin_question_service.get_question_list(db_session, page=1, page_size=10)

    assert total == 3
    assert len(items) == 3


@pytest.mark.asyncio
async def test_get_question_list_with_filters(db_session, test_article):
    for q_type in [QuestionTypeEnum.CHOICE, QuestionTypeEnum.JUDGE]:
        question = Question(
            article_id=test_article.id,
            type=q_type,
            difficulty=DifficultyEnum.EASY,
            content=f"{q_type.value}问题",
            answer="对",
            options=["A", "B", "C", "D"] if q_type == QuestionTypeEnum.CHOICE else None
        )
        db_session.add(question)
    await db_session.commit()

    items, total = await admin_question_service.get_question_list(
        db_session,
        question_type="choice"
    )

    assert total == 1
    assert len(items) == 1
    assert items[0].type == QuestionTypeEnum.CHOICE

    items, total = await admin_question_service.get_question_list(
        db_session,
        article_id=test_article.id
    )

    assert total == 2


@pytest.mark.asyncio
async def test_get_question_detail(db_session, test_article):
    ability = AbilityDimension(
        name="分析能力",
        code="analysis",
        category=AbilityCategoryEnum.ANALYSIS
    )
    db_session.add(ability)
    await db_session.commit()

    question = Question(
        article_id=test_article.id,
        type=QuestionTypeEnum.CHOICE,
        difficulty=DifficultyEnum.EASY,
        content="测试问题",
        answer="A",
        options=["A", "B", "C", "D"]
    )
    db_session.add(question)
    await db_session.commit()
    await db_session.refresh(question)

    from app.models.question import QuestionAbility
    qa = QuestionAbility(
        question_id=question.id,
        ability_id=ability.id,
        weight=3
    )
    db_session.add(qa)
    await db_session.commit()

    result = await admin_question_service.get_question_detail(db_session, question.id)

    assert result is not None
    assert result.id == question.id
    assert result.content == "测试问题"
    assert result.article_title == test_article.title
    assert len(result.abilities) == 1
    assert result.abilities[0]["name"] == "分析能力"
    assert result.abilities[0]["code"] == "analysis"


@pytest.mark.asyncio
async def test_update_question(db_session, test_article):
    question = Question(
        article_id=test_article.id,
        type=QuestionTypeEnum.JUDGE,
        difficulty=DifficultyEnum.EASY,
        content="原问题",
        answer="对"
    )
    db_session.add(question)
    await db_session.commit()
    await db_session.refresh(question)

    data = QuestionUpdateRequest(
        content="新问题",
        difficulty=DifficultyEnum.HARD,
        display_order=5
    )

    result = await admin_question_service.update_question(db_session, question.id, data)

    assert result is not None
    assert result.content == "新问题"
    assert result.difficulty == DifficultyEnum.HARD
    assert result.display_order == 5


@pytest.mark.asyncio
async def test_update_question_abilities(db_session, test_article):
    ability1 = AbilityDimension(
        name="能力1",
        code="ability1",
        category=AbilityCategoryEnum.COMPREHENSION
    )
    ability2 = AbilityDimension(
        name="能力2",
        code="ability2",
        category=AbilityCategoryEnum.ANALYSIS
    )
    db_session.add(ability1)
    db_session.add(ability2)
    await db_session.commit()

    question = Question(
        article_id=test_article.id,
        type=QuestionTypeEnum.JUDGE,
        difficulty=DifficultyEnum.EASY,
        content="测试问题",
        answer="对"
    )
    db_session.add(question)
    await db_session.commit()
    await db_session.refresh(question)

    from app.models.question import QuestionAbility
    qa = QuestionAbility(
        question_id=question.id,
        ability_id=ability1.id,
        weight=5
    )
    db_session.add(qa)
    await db_session.commit()

    data = QuestionUpdateRequest(
        abilities=[AbilityWeight(ability_id=ability2.id, weight=8)]
    )
    result = await admin_question_service.update_question(db_session, question.id, data)

    assert result is not None
    assert len(result.abilities) == 1
    assert result.abilities[0]["name"] == "能力2"
    assert result.abilities[0]["weight"] == 8


@pytest.mark.asyncio
async def test_delete_question(db_session, test_article):
    question = Question(
        article_id=test_article.id,
        type=QuestionTypeEnum.JUDGE,
        difficulty=DifficultyEnum.EASY,
        content="测试问题",
        answer="对"
    )
    db_session.add(question)
    await db_session.commit()
    await db_session.refresh(question)

    question_id = question.id
    success = await admin_question_service.delete_question(db_session, question_id)

    assert success is True

    from sqlalchemy import select
    result = await db_session.execute(select(Question).where(Question.id == question_id))
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_get_question_detail_not_found(db_session):
    result = await admin_question_service.get_question_detail(db_session, 99999)
    assert result is None


@pytest.mark.asyncio
async def test_update_question_not_found(db_session):
    data = QuestionUpdateRequest(content="新问题")
    result = await admin_question_service.update_question(db_session, 99999, data)
    assert result is None


@pytest.mark.asyncio
async def test_delete_question_not_found(db_session):
    success = await admin_question_service.delete_question(db_session, 99999)
    assert success is False
