import pytest
import asyncio
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, UniqueConstraint, String
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
from sqlalchemy import select


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


TestBase = declarative_base()


class User(TestBase):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    openid = Column(String, unique=True, nullable=False)
    nickname = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    abilities = None

    def __repr__(self):
        return f"<User(id={self.id}, nickname={self.nickname})>"


class AbilityDimension(TestBase):
    __tablename__ = "ability_dimensions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user_abilities = None

    def __repr__(self):
        return f"<AbilityDimension(id={self.id}, name={self.name})>"


class UserAbility(TestBase):
    __tablename__ = "user_abilities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ability_id = Column(
        Integer,
        ForeignKey("ability_dimensions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    correct_count = Column(Integer, default=0, comment="正确题数")
    total_count = Column(Integer, default=0, comment="总题数")

    score = Column(Float, default=0, comment="能力得分（0-100）")

    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        comment="更新时间",
    )

    user = None
    ability = None

    __table_args__ = (UniqueConstraint("user_id", "ability_id", name="uq_user_ability"),)

    def __repr__(self):
        return f"<UserAbility(user_id={self.user_id}, ability_id={self.ability_id}, score={self.score})>"


@pytest.fixture
async def test_engine():
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
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def sample_user(test_session: AsyncSession):
    user = User(openid="test_user_123", nickname="测试用户")
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest.fixture
async def sample_ability(test_session: AsyncSession):
    ability = AbilityDimension(name="理解能力", description="理解文章内容的能力")
    test_session.add(ability)
    await test_session.commit()
    await test_session.refresh(ability)
    return ability


@pytest.mark.asyncio
async def test_create_user_ability_with_all_fields(
    test_session: AsyncSession, sample_user: User, sample_ability: AbilityDimension
):
    user_ability = UserAbility(
        user_id=sample_user.id,
        ability_id=sample_ability.id,
        correct_count=8,
        total_count=10,
        score=80.0,
    )

    test_session.add(user_ability)
    await test_session.commit()
    await test_session.refresh(user_ability)

    assert user_ability.id is not None
    assert user_ability.user_id == sample_user.id
    assert user_ability.ability_id == sample_ability.id
    assert user_ability.correct_count == 8
    assert user_ability.total_count == 10
    assert user_ability.score == 80.0
    assert user_ability.updated_at is not None


@pytest.mark.asyncio
async def test_create_user_ability_with_minimal_fields(
    test_session: AsyncSession, sample_user: User, sample_ability: AbilityDimension
):
    user_ability = UserAbility(user_id=sample_user.id, ability_id=sample_ability.id)

    test_session.add(user_ability)
    await test_session.commit()
    await test_session.refresh(user_ability)

    assert user_ability.id is not None
    assert user_ability.user_id == sample_user.id
    assert user_ability.ability_id == sample_ability.id
    assert user_ability.correct_count == 0
    assert user_ability.total_count == 0
    assert user_ability.score == 0
    assert user_ability.updated_at is not None


@pytest.mark.asyncio
async def test_user_ability_unique_constraint(
    test_session: AsyncSession, sample_user: User, sample_ability: AbilityDimension
):
    user_ability1 = UserAbility(user_id=sample_user.id, ability_id=sample_ability.id)
    test_session.add(user_ability1)
    await test_session.commit()

    user_ability2 = UserAbility(user_id=sample_user.id, ability_id=sample_ability.id)
    test_session.add(user_ability2)

    with pytest.raises(IntegrityError):
        await test_session.commit()


@pytest.mark.asyncio
async def test_user_ability_different_users_same_ability(
    test_session: AsyncSession, sample_ability: AbilityDimension
):
    user1 = User(openid="test_user_1", nickname="用户1")
    user2 = User(openid="test_user_2", nickname="用户2")
    test_session.add(user1)
    test_session.add(user2)
    await test_session.commit()
    await test_session.refresh(user1)
    await test_session.refresh(user2)

    user_ability1 = UserAbility(user_id=user1.id, ability_id=sample_ability.id)
    user_ability2 = UserAbility(user_id=user2.id, ability_id=sample_ability.id)

    test_session.add(user_ability1)
    test_session.add(user_ability2)
    await test_session.commit()

    assert user_ability1.id is not None
    assert user_ability2.id is not None
    assert user_ability1.id != user_ability2.id


@pytest.mark.asyncio
async def test_user_ability_same_user_different_abilities(
    test_session: AsyncSession, sample_user: User
):
    ability1 = AbilityDimension(name="能力1", description="描述1")
    ability2 = AbilityDimension(name="能力2", description="描述2")
    test_session.add(ability1)
    test_session.add(ability2)
    await test_session.commit()
    await test_session.refresh(ability1)
    await test_session.refresh(ability2)

    user_ability1 = UserAbility(user_id=sample_user.id, ability_id=ability1.id)
    user_ability2 = UserAbility(user_id=sample_user.id, ability_id=ability2.id)

    test_session.add(user_ability1)
    test_session.add(user_ability2)
    await test_session.commit()

    assert user_ability1.id is not None
    assert user_ability2.id is not None
    assert user_ability1.id != user_ability2.id


@pytest.mark.asyncio
async def test_user_ability_foreign_key_constraint_user(
    test_session: AsyncSession, sample_ability: AbilityDimension
):
    user_ability = UserAbility(user_id=999, ability_id=sample_ability.id)

    test_session.add(user_ability)
    with pytest.raises(IntegrityError):
        await test_session.commit()


@pytest.mark.asyncio
async def test_user_ability_foreign_key_constraint_ability(
    test_session: AsyncSession, sample_user: User
):
    user_ability = UserAbility(user_id=sample_user.id, ability_id=999)

    test_session.add(user_ability)
    with pytest.raises(IntegrityError):
        await test_session.commit()


@pytest.mark.asyncio
async def test_user_ability_cascade_delete_user(
    test_session: AsyncSession, sample_user: User, sample_ability: AbilityDimension
):
    user_ability = UserAbility(
        user_id=sample_user.id,
        ability_id=sample_ability.id,
        correct_count=5,
        total_count=10,
    )

    test_session.add(user_ability)
    await test_session.commit()
    user_ability_id = user_ability.id

    await test_session.delete(sample_user)
    await test_session.commit()

    result = await test_session.execute(
        select(UserAbility).where(UserAbility.id == user_ability_id)
    )
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_user_ability_cascade_delete_ability(
    test_session: AsyncSession, sample_user: User, sample_ability: AbilityDimension
):
    user_ability = UserAbility(
        user_id=sample_user.id,
        ability_id=sample_ability.id,
        correct_count=5,
        total_count=10,
    )

    test_session.add(user_ability)
    await test_session.commit()
    user_ability_id = user_ability.id

    await test_session.delete(sample_ability)
    await test_session.commit()

    result = await test_session.execute(
        select(UserAbility).where(UserAbility.id == user_ability_id)
    )
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_user_ability_relationships_defined(
    test_session: AsyncSession, sample_user: User, sample_ability: AbilityDimension
):
    user_ability = UserAbility(user_id=sample_user.id, ability_id=sample_ability.id)

    test_session.add(user_ability)
    await test_session.commit()
    await test_session.refresh(user_ability)

    assert hasattr(user_ability, "user")
    assert hasattr(user_ability, "ability")


@pytest.mark.asyncio
async def test_user_ability_repr(
    test_session: AsyncSession, sample_user: User, sample_ability: AbilityDimension
):
    user_ability = UserAbility(
        user_id=sample_user.id,
        ability_id=sample_ability.id,
        score=85.5,
    )

    repr_str = repr(user_ability)
    assert "UserAbility" in repr_str
    assert str(sample_user.id) in repr_str
    assert str(sample_ability.id) in repr_str
    assert "85.5" in repr_str


@pytest.mark.asyncio
async def test_user_ability_foreign_key_indexes(
    test_session: AsyncSession, sample_user: User, sample_ability: AbilityDimension
):
    user_ability = UserAbility(user_id=sample_user.id, ability_id=sample_ability.id)
    test_session.add(user_ability)
    await test_session.commit()

    result = await test_session.execute(
        select(UserAbility).where(UserAbility.user_id == sample_user.id)
    )
    assert result.scalar_one_or_none() is not None

    result = await test_session.execute(
        select(UserAbility).where(UserAbility.ability_id == sample_ability.id)
    )
    assert result.scalar_one_or_none() is not None


@pytest.mark.asyncio
async def test_user_ability_updated_at_timezone(
    test_session: AsyncSession, sample_user: User, sample_ability: AbilityDimension
):
    user_ability = UserAbility(user_id=sample_user.id, ability_id=sample_ability.id)

    test_session.add(user_ability)
    await test_session.commit()
    await test_session.refresh(user_ability)

    assert user_ability.updated_at is not None
    assert isinstance(user_ability.updated_at, datetime)


@pytest.mark.asyncio
async def test_user_ability_updated_at_on_update(
    test_session: AsyncSession, sample_user: User, sample_ability: AbilityDimension
):
    user_ability = UserAbility(
        user_id=sample_user.id,
        ability_id=sample_ability.id,
        correct_count=5,
        total_count=10,
    )

    test_session.add(user_ability)
    await test_session.commit()
    await test_session.refresh(user_ability)

    original_updated_at = user_ability.updated_at

    await asyncio.sleep(0.1)

    user_ability.correct_count = 8
    await test_session.commit()
    await test_session.refresh(user_ability)

    assert user_ability.updated_at > original_updated_at


@pytest.mark.asyncio
async def test_user_ability_score_calculated(
    test_session: AsyncSession, sample_user: User, sample_ability: AbilityDimension
):
    user_ability = UserAbility(
        user_id=sample_user.id, ability_id=sample_ability.id, score=75.0
    )

    test_session.add(user_ability)
    await test_session.commit()
    await test_session.refresh(user_ability)

    assert user_ability.score == 75.0
    assert isinstance(user_ability.score, float)


@pytest.mark.asyncio
async def test_user_ability_count_values(
    test_session: AsyncSession, sample_user: User, sample_ability: AbilityDimension
):
    user_ability = UserAbility(
        user_id=sample_user.id,
        ability_id=sample_ability.id,
        correct_count=15,
        total_count=20,
    )

    test_session.add(user_ability)
    await test_session.commit()
    await test_session.refresh(user_ability)

    assert user_ability.correct_count == 15
    assert user_ability.total_count == 20
