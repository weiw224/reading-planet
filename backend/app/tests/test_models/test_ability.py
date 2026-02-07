import enum

import pytest
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import Enum as SQLEnum, text
from sqlalchemy import UniqueConstraint, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


TestBase = declarative_base()


class AbilityCategoryEnum(enum.Enum):
    INFORMATION = "information"
    COMPREHENSION = "comprehension"
    ANALYSIS = "analysis"
    EXPRESSION = "expression"


class AbilityDimension(TestBase):
    __tablename__ = "ability_dimensions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    code = Column(String(30), unique=True, nullable=False)
    category = Column(SQLEnum(AbilityCategoryEnum), nullable=False)
    description = Column(String(200), nullable=True)
    display_order = Column(Integer, default=0)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    question_abilities = None
    user_abilities = None

    def __repr__(self):
        return f"<AbilityDimension(id={self.id}, name={self.name})>"


@pytest.fixture
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(TestBase.metadata.create_all)
        await conn.execute(text("PRAGMA foreign_keys=ON"))
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
async def test_ability_category_enum_values():
    assert AbilityCategoryEnum.INFORMATION.value == "information"
    assert AbilityCategoryEnum.COMPREHENSION.value == "comprehension"
    assert AbilityCategoryEnum.ANALYSIS.value == "analysis"
    assert AbilityCategoryEnum.EXPRESSION.value == "expression"


@pytest.mark.asyncio
async def test_create_ability_with_information_category(test_session: AsyncSession):
    ability = AbilityDimension(
        name="细节提取",
        code="detail_extraction",
        category=AbilityCategoryEnum.INFORMATION,
        description="从文章中提取关键细节信息",
        display_order=1,
    )

    test_session.add(ability)
    await test_session.commit()
    await test_session.refresh(ability)

    assert ability.id is not None
    assert ability.name == "细节提取"
    assert ability.code == "detail_extraction"
    assert ability.category == AbilityCategoryEnum.INFORMATION
    assert ability.description == "从文章中提取关键细节信息"
    assert ability.display_order == 1
    assert ability.created_at is not None


@pytest.mark.asyncio
async def test_create_ability_with_comprehension_category(test_session: AsyncSession):
    ability = AbilityDimension(
        name="主旨概括",
        code="main_idea",
        category=AbilityCategoryEnum.COMPREHENSION,
        description="概括文章主要内容和中心思想",
        display_order=2,
    )

    test_session.add(ability)
    await test_session.commit()
    await test_session.refresh(ability)

    assert ability.id is not None
    assert ability.name == "主旨概括"
    assert ability.code == "main_idea"
    assert ability.category == AbilityCategoryEnum.COMPREHENSION
    assert ability.description == "概括文章主要内容和中心思想"
    assert ability.display_order == 2


@pytest.mark.asyncio
async def test_create_ability_with_analysis_category(test_session: AsyncSession):
    ability = AbilityDimension(
        name="逻辑推理",
        code="logical_inference",
        category=AbilityCategoryEnum.ANALYSIS,
        description="根据文章内容进行逻辑推理",
        display_order=3,
    )

    test_session.add(ability)
    await test_session.commit()
    await test_session.refresh(ability)

    assert ability.id is not None
    assert ability.name == "逻辑推理"
    assert ability.code == "logical_inference"
    assert ability.category == AbilityCategoryEnum.ANALYSIS
    assert ability.description == "根据文章内容进行逻辑推理"
    assert ability.display_order == 3


@pytest.mark.asyncio
async def test_create_ability_with_expression_category(test_session: AsyncSession):
    ability = AbilityDimension(
        name="观点评价",
        code="viewpoint_evaluation",
        category=AbilityCategoryEnum.EXPRESSION,
        description="评价作者的观点和态度",
        display_order=4,
    )

    test_session.add(ability)
    await test_session.commit()
    await test_session.refresh(ability)

    assert ability.id is not None
    assert ability.name == "观点评价"
    assert ability.code == "viewpoint_evaluation"
    assert ability.category == AbilityCategoryEnum.EXPRESSION
    assert ability.description == "评价作者的观点和态度"
    assert ability.display_order == 4


@pytest.mark.asyncio
async def test_ability_default_values(test_session: AsyncSession):
    ability = AbilityDimension(
        name="测试能力", code="test_code", category=AbilityCategoryEnum.INFORMATION
    )

    test_session.add(ability)
    await test_session.commit()
    await test_session.refresh(ability)

    assert ability.description is None
    assert ability.display_order == 0
    assert ability.created_at is not None


@pytest.mark.asyncio
async def test_ability_name_unique_constraint(test_session: AsyncSession):
    ability1 = AbilityDimension(
        name="细节提取", code="code1", category=AbilityCategoryEnum.INFORMATION
    )

    test_session.add(ability1)
    await test_session.commit()

    ability2 = AbilityDimension(
        name="细节提取", code="code2", category=AbilityCategoryEnum.INFORMATION
    )

    test_session.add(ability2)

    with pytest.raises(IntegrityError):
        await test_session.commit()


@pytest.mark.asyncio
async def test_ability_code_unique_constraint(test_session: AsyncSession):
    ability1 = AbilityDimension(
        name="能力1", code="detail_extraction", category=AbilityCategoryEnum.INFORMATION
    )

    test_session.add(ability1)
    await test_session.commit()

    ability2 = AbilityDimension(
        name="能力2",
        code="detail_extraction",
        category=AbilityCategoryEnum.COMPREHENSION,
    )

    test_session.add(ability2)

    with pytest.raises(IntegrityError):
        await test_session.commit()


@pytest.mark.asyncio
async def test_ability_name_not_nullable(test_session: AsyncSession):
    ability = AbilityDimension(
        code="test_code", category=AbilityCategoryEnum.INFORMATION
    )

    test_session.add(ability)

    with pytest.raises(IntegrityError):
        await test_session.commit()


@pytest.mark.asyncio
async def test_ability_code_not_nullable(test_session: AsyncSession):
    ability = AbilityDimension(
        name="测试能力", category=AbilityCategoryEnum.INFORMATION
    )

    test_session.add(ability)

    with pytest.raises(IntegrityError):
        await test_session.commit()


@pytest.mark.asyncio
async def test_ability_category_not_nullable(test_session: AsyncSession):
    ability = AbilityDimension(name="测试能力", code="test_code")

    test_session.add(ability)

    with pytest.raises(IntegrityError):
        await test_session.commit()


@pytest.mark.asyncio
async def test_ability_repr(test_session: AsyncSession):
    ability = AbilityDimension(
        name="细节提取", code="detail_extraction", category=AbilityCategoryEnum.INFORMATION
    )

    repr_str = repr(ability)
    assert "AbilityDimension" in repr_str
    assert "细节提取" in repr_str


@pytest.mark.asyncio
async def test_multiple_abilities_same_category(test_session: AsyncSession):
    ability1 = AbilityDimension(
        name="细节提取",
        code="detail_extraction",
        category=AbilityCategoryEnum.INFORMATION,
        display_order=1,
    )
    ability2 = AbilityDimension(
        name="关键信息识别",
        code="key_info",
        category=AbilityCategoryEnum.INFORMATION,
        display_order=2,
    )
    ability3 = AbilityDimension(
        name="主旨概括",
        code="main_idea",
        category=AbilityCategoryEnum.COMPREHENSION,
        display_order=3,
    )

    test_session.add(ability1)
    test_session.add(ability2)
    test_session.add(ability3)
    await test_session.commit()

    result = await test_session.execute(
        select(AbilityDimension)
        .where(AbilityDimension.category == AbilityCategoryEnum.INFORMATION)
        .order_by(AbilityDimension.display_order)
    )
    information_abilities = result.scalars().all()

    assert len(information_abilities) == 2
    assert information_abilities[0].name == "细节提取"
    assert information_abilities[1].name == "关键信息识别"


@pytest.mark.asyncio
async def test_ability_display_order(test_session: AsyncSession):
    ability1 = AbilityDimension(
        name="细节提取",
        code="detail_extraction",
        category=AbilityCategoryEnum.INFORMATION,
        display_order=2,
    )
    ability2 = AbilityDimension(
        name="主旨概括",
        code="main_idea",
        category=AbilityCategoryEnum.COMPREHENSION,
        display_order=1,
    )
    ability3 = AbilityDimension(
        name="逻辑推理",
        code="logical_inference",
        category=AbilityCategoryEnum.ANALYSIS,
        display_order=3,
    )

    test_session.add(ability1)
    test_session.add(ability2)
    test_session.add(ability3)
    await test_session.commit()

    result = await test_session.execute(
        select(AbilityDimension).order_by(AbilityDimension.display_order)
    )
    ordered_abilities = result.scalars().all()

    assert ordered_abilities[0].display_order == 1
    assert ordered_abilities[1].display_order == 2
    assert ordered_abilities[2].display_order == 3


@pytest.mark.asyncio
async def test_ability_name_max_length(test_session: AsyncSession):
    long_name = "a" * 50
    ability = AbilityDimension(
        name=long_name,
        code="test_code",
        category=AbilityCategoryEnum.INFORMATION,
    )

    test_session.add(ability)
    await test_session.commit()
    await test_session.refresh(ability)

    assert len(ability.name) == 50


@pytest.mark.asyncio
async def test_ability_code_max_length(test_session: AsyncSession):
    long_code = "a" * 30
    ability = AbilityDimension(
        name="测试能力",
        code=long_code,
        category=AbilityCategoryEnum.INFORMATION,
    )

    test_session.add(ability)
    await test_session.commit()
    await test_session.refresh(ability)

    assert len(ability.code) == 30


@pytest.mark.asyncio
async def test_ability_description_max_length(test_session: AsyncSession):
    long_description = "a" * 200
    ability = AbilityDimension(
        name="测试能力",
        code="test_code",
        category=AbilityCategoryEnum.INFORMATION,
        description=long_description,
    )

    test_session.add(ability)
    await test_session.commit()
    await test_session.refresh(ability)

    assert len(ability.description) == 200


@pytest.mark.asyncio
async def test_ability_relationships_defined(test_session: AsyncSession):
    ability = AbilityDimension(
        name="测试能力", code="test_code", category=AbilityCategoryEnum.INFORMATION
    )

    test_session.add(ability)
    await test_session.commit()
    await test_session.refresh(ability)

    assert hasattr(ability, "question_abilities")
    assert hasattr(ability, "user_abilities")


@pytest.mark.asyncio
async def test_ability_created_at_timestamp(test_session: AsyncSession):
    ability = AbilityDimension(
        name="测试能力", code="test_code", category=AbilityCategoryEnum.INFORMATION
    )

    test_session.add(ability)
    await test_session.commit()
    await test_session.refresh(ability)

    assert ability.created_at is not None
    assert isinstance(ability.created_at, datetime)
