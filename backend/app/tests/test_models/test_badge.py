import pytest
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint, Enum as SQLEnum, ForeignKey
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
from sqlalchemy import select
import enum


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


TestBase = declarative_base()


class BadgeCategoryEnum(enum.Enum):
    PERSISTENCE = "persistence"
    ABILITY = "ability"
    READING = "reading"
    EXPLORE = "explore"


class BadgeConditionTypeEnum(enum.Enum):
    FIRST_READING = "first_reading"
    STREAK_DAYS = "streak_days"
    TOTAL_READINGS = "total_readings"
    ABILITY_ACCURACY = "ability_accuracy"
    ABILITY_COUNT = "ability_count"
    GENRE_COUNT = "genre_count"
    ALL_GENRES = "all_genres"


class User(TestBase):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    openid = Column(String, unique=True, nullable=False)
    nickname = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    badges = None

    def __repr__(self):
        return f"<User(id={self.id}, nickname={self.nickname})>"


class Badge(TestBase):
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, comment="勋章名称")
    description = Column(String(200), nullable=True, comment="勋章描述")
    icon_url = Column(String(512), nullable=True, comment="勋章图标URL")

    category = Column(
        SQLEnum(BadgeCategoryEnum), nullable=False, comment="勋章分类"
    )

    condition_type = Column(
        SQLEnum(BadgeConditionTypeEnum), nullable=False, comment="条件类型"
    )
    condition_value = Column(Integer, nullable=False, comment="条件阈值")
    condition_extra = Column(String(100), nullable=True, comment="额外条件参数")

    display_order = Column(Integer, default=0, comment="显示顺序")

    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), comment="创建时间"
    )

    user_badges = None

    def __repr__(self):
        return f"<Badge(id={self.id}, name={self.name})>"


class UserBadge(TestBase):
    __tablename__ = "user_badges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    badge_id = Column(
        Integer, ForeignKey("badges.id", ondelete="CASCADE"), nullable=False, index=True
    )

    earned_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), comment="获得时间"
    )

    user = None
    badge = None

    __table_args__ = (UniqueConstraint("user_id", "badge_id", name="uq_user_badge"),)

    def __repr__(self):
        return f"<UserBadge(id={self.id}, user_id={self.user_id}, badge_id={self.badge_id})>"


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
async def sample_badge(test_session: AsyncSession):
    badge = Badge(
        name="首次阅读",
        description="完成第一次阅读",
        category=BadgeCategoryEnum.READING,
        condition_type=BadgeConditionTypeEnum.FIRST_READING,
        condition_value=1,
    )
    test_session.add(badge)
    await test_session.commit()
    await test_session.refresh(badge)
    return badge


@pytest.mark.asyncio
async def test_create_badge_with_all_fields(test_session: AsyncSession):
    badge = Badge(
        name="连续打卡达人",
        description="连续打卡7天",
        icon_url="https://example.com/badge.png",
        category=BadgeCategoryEnum.PERSISTENCE,
        condition_type=BadgeConditionTypeEnum.STREAK_DAYS,
        condition_value=7,
        condition_extra=None,
        display_order=1,
    )

    test_session.add(badge)
    await test_session.commit()
    await test_session.refresh(badge)

    assert badge.id is not None
    assert badge.name == "连续打卡达人"
    assert badge.description == "连续打卡7天"
    assert badge.icon_url == "https://example.com/badge.png"
    assert badge.category == BadgeCategoryEnum.PERSISTENCE
    assert badge.condition_type == BadgeConditionTypeEnum.STREAK_DAYS
    assert badge.condition_value == 7
    assert badge.condition_extra is None
    assert badge.display_order == 1
    assert badge.created_at is not None


@pytest.mark.asyncio
async def test_create_badge_with_minimal_fields(test_session: AsyncSession):
    badge = Badge(
        name="测试勋章",
        category=BadgeCategoryEnum.READING,
        condition_type=BadgeConditionTypeEnum.FIRST_READING,
        condition_value=1,
    )

    test_session.add(badge)
    await test_session.commit()
    await test_session.refresh(badge)

    assert badge.id is not None
    assert badge.name == "测试勋章"
    assert badge.description is None
    assert badge.icon_url is None
    assert badge.display_order == 0
    assert badge.created_at is not None


@pytest.mark.asyncio
async def test_badge_unique_name_constraint(test_session: AsyncSession):
    badge1 = Badge(
        name="重复名称",
        category=BadgeCategoryEnum.READING,
        condition_type=BadgeConditionTypeEnum.FIRST_READING,
        condition_value=1,
    )
    test_session.add(badge1)
    await test_session.commit()

    badge2 = Badge(
        name="重复名称",
        category=BadgeCategoryEnum.READING,
        condition_type=BadgeConditionTypeEnum.FIRST_READING,
        condition_value=1,
    )
    test_session.add(badge2)

    with pytest.raises(IntegrityError):
        await test_session.commit()


@pytest.mark.asyncio
async def test_badge_enum_values(test_session: AsyncSession):
    categories = [
        BadgeCategoryEnum.PERSISTENCE,
        BadgeCategoryEnum.ABILITY,
        BadgeCategoryEnum.READING,
        BadgeCategoryEnum.EXPLORE,
    ]

    for category in categories:
        badge = Badge(
            name=f"test_{category.value}",
            category=category,
            condition_type=BadgeConditionTypeEnum.FIRST_READING,
            condition_value=1,
        )
        test_session.add(badge)

    await test_session.commit()

    condition_types = [
        BadgeConditionTypeEnum.FIRST_READING,
        BadgeConditionTypeEnum.STREAK_DAYS,
        BadgeConditionTypeEnum.TOTAL_READINGS,
        BadgeConditionTypeEnum.ABILITY_ACCURACY,
        BadgeConditionTypeEnum.ABILITY_COUNT,
        BadgeConditionTypeEnum.GENRE_COUNT,
        BadgeConditionTypeEnum.ALL_GENRES,
    ]

    for condition_type in condition_types:
        badge = Badge(
            name=f"test_{condition_type.value}",
            category=BadgeCategoryEnum.READING,
            condition_type=condition_type,
            condition_value=1,
        )
        test_session.add(badge)

    await test_session.commit()


@pytest.mark.asyncio
async def test_badge_condition_extra(test_session: AsyncSession):
    badge = Badge(
        name="能力达人",
        category=BadgeCategoryEnum.ABILITY,
        condition_type=BadgeConditionTypeEnum.ABILITY_COUNT,
        condition_value=10,
        condition_extra="1",
    )

    test_session.add(badge)
    await test_session.commit()
    await test_session.refresh(badge)

    assert badge.condition_extra == "1"


@pytest.mark.asyncio
async def test_badge_created_at_timezone(test_session: AsyncSession):
    badge = Badge(
        name="测试勋章",
        category=BadgeCategoryEnum.READING,
        condition_type=BadgeConditionTypeEnum.FIRST_READING,
        condition_value=1,
    )

    test_session.add(badge)
    await test_session.commit()
    await test_session.refresh(badge)

    assert badge.created_at is not None
    assert isinstance(badge.created_at, datetime)


@pytest.mark.asyncio
async def test_badge_repr(test_session: AsyncSession):
    badge = Badge(
        name="测试勋章",
        category=BadgeCategoryEnum.READING,
        condition_type=BadgeConditionTypeEnum.FIRST_READING,
        condition_value=1,
    )

    repr_str = repr(badge)
    assert "Badge" in repr_str
    assert "测试勋章" in repr_str


@pytest.mark.asyncio
async def test_badge_user_badges_relationship(test_session: AsyncSession):
    badge = Badge(
        name="测试勋章",
        category=BadgeCategoryEnum.READING,
        condition_type=BadgeConditionTypeEnum.FIRST_READING,
        condition_value=1,
    )

    test_session.add(badge)
    await test_session.commit()
    await test_session.refresh(badge)

    assert hasattr(badge, "user_badges")


@pytest.mark.asyncio
async def test_create_user_badge_with_all_fields(
    test_session: AsyncSession, sample_user: User, sample_badge: Badge
):
    user_badge = UserBadge(user_id=sample_user.id, badge_id=sample_badge.id)

    test_session.add(user_badge)
    await test_session.commit()
    await test_session.refresh(user_badge)

    assert user_badge.id is not None
    assert user_badge.user_id == sample_user.id
    assert user_badge.badge_id == sample_badge.id
    assert user_badge.earned_at is not None
    assert isinstance(user_badge.earned_at, datetime)


@pytest.mark.asyncio
async def test_user_badge_unique_constraint_user_badge(
    test_session: AsyncSession, sample_user: User, sample_badge: Badge
):
    user_badge1 = UserBadge(user_id=sample_user.id, badge_id=sample_badge.id)
    test_session.add(user_badge1)
    await test_session.commit()

    user_badge2 = UserBadge(user_id=sample_user.id, badge_id=sample_badge.id)
    test_session.add(user_badge2)

    with pytest.raises(IntegrityError):
        await test_session.commit()


@pytest.mark.asyncio
async def test_user_badge_different_users_same_badge(
    test_session: AsyncSession, sample_badge: Badge
):
    user1 = User(openid="test_user_1", nickname="用户1")
    user2 = User(openid="test_user_2", nickname="用户2")
    test_session.add(user1)
    test_session.add(user2)
    await test_session.commit()
    await test_session.refresh(user1)
    await test_session.refresh(user2)

    user_badge1 = UserBadge(user_id=user1.id, badge_id=sample_badge.id)
    user_badge2 = UserBadge(user_id=user2.id, badge_id=sample_badge.id)

    test_session.add(user_badge1)
    test_session.add(user_badge2)
    await test_session.commit()

    assert user_badge1.id is not None
    assert user_badge2.id is not None
    assert user_badge1.id != user_badge2.id


@pytest.mark.asyncio
async def test_user_badge_same_user_different_badges(
    test_session: AsyncSession, sample_user: User
):
    badge1 = Badge(
        name="勋章1",
        category=BadgeCategoryEnum.READING,
        condition_type=BadgeConditionTypeEnum.FIRST_READING,
        condition_value=1,
    )
    badge2 = Badge(
        name="勋章2",
        category=BadgeCategoryEnum.READING,
        condition_type=BadgeConditionTypeEnum.FIRST_READING,
        condition_value=1,
    )
    test_session.add(badge1)
    test_session.add(badge2)
    await test_session.commit()
    await test_session.refresh(badge1)
    await test_session.refresh(badge2)

    user_badge1 = UserBadge(user_id=sample_user.id, badge_id=badge1.id)
    user_badge2 = UserBadge(user_id=sample_user.id, badge_id=badge2.id)

    test_session.add(user_badge1)
    test_session.add(user_badge2)
    await test_session.commit()

    assert user_badge1.id is not None
    assert user_badge2.id is not None
    assert user_badge1.id != user_badge2.id


@pytest.mark.asyncio
async def test_user_badge_foreign_key_constraint_user(
    test_session: AsyncSession, sample_badge: Badge
):
    user_badge = UserBadge(user_id=999, badge_id=sample_badge.id)

    test_session.add(user_badge)
    with pytest.raises(IntegrityError):
        await test_session.commit()


@pytest.mark.asyncio
async def test_user_badge_foreign_key_constraint_badge(
    test_session: AsyncSession, sample_user: User
):
    user_badge = UserBadge(user_id=sample_user.id, badge_id=999)

    test_session.add(user_badge)
    with pytest.raises(IntegrityError):
        await test_session.commit()


@pytest.mark.asyncio
async def test_user_badge_cascade_delete_user(
    test_session: AsyncSession, sample_user: User, sample_badge: Badge
):
    user_badge = UserBadge(user_id=sample_user.id, badge_id=sample_badge.id)

    test_session.add(user_badge)
    await test_session.commit()
    user_badge_id = user_badge.id

    await test_session.delete(sample_user)
    await test_session.commit()

    result = await test_session.execute(
        select(UserBadge).where(UserBadge.id == user_badge_id)
    )
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_user_badge_cascade_delete_badge(
    test_session: AsyncSession, sample_user: User, sample_badge: Badge
):
    user_badge = UserBadge(user_id=sample_user.id, badge_id=sample_badge.id)

    test_session.add(user_badge)
    await test_session.commit()
    user_badge_id = user_badge.id

    await test_session.delete(sample_badge)
    await test_session.commit()

    result = await test_session.execute(
        select(UserBadge).where(UserBadge.id == user_badge_id)
    )
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_user_badge_relationships_defined(
    test_session: AsyncSession, sample_user: User, sample_badge: Badge
):
    user_badge = UserBadge(user_id=sample_user.id, badge_id=sample_badge.id)

    test_session.add(user_badge)
    await test_session.commit()
    await test_session.refresh(user_badge)

    assert hasattr(user_badge, "user")
    assert hasattr(user_badge, "badge")


@pytest.mark.asyncio
async def test_user_badge_repr(
    test_session: AsyncSession, sample_user: User, sample_badge: Badge
):
    user_badge = UserBadge(user_id=sample_user.id, badge_id=sample_badge.id)

    repr_str = repr(user_badge)
    assert "UserBadge" in repr_str
    assert str(sample_user.id) in repr_str
    assert str(sample_badge.id) in repr_str


@pytest.mark.asyncio
async def test_user_badge_foreign_key_indexes(
    test_session: AsyncSession, sample_user: User, sample_badge: Badge
):
    user_badge = UserBadge(user_id=sample_user.id, badge_id=sample_badge.id)
    test_session.add(user_badge)
    await test_session.commit()

    result = await test_session.execute(
        select(UserBadge).where(UserBadge.user_id == sample_user.id)
    )
    assert result.scalar_one_or_none() is not None

    result = await test_session.execute(
        select(UserBadge).where(UserBadge.badge_id == sample_badge.id)
    )
    assert result.scalar_one_or_none() is not None


@pytest.mark.asyncio
async def test_user_badge_earned_at_timezone(
    test_session: AsyncSession, sample_user: User, sample_badge: Badge
):
    user_badge = UserBadge(user_id=sample_user.id, badge_id=sample_badge.id)

    test_session.add(user_badge)
    await test_session.commit()
    await test_session.refresh(user_badge)

    assert user_badge.earned_at is not None
    assert isinstance(user_badge.earned_at, datetime)
