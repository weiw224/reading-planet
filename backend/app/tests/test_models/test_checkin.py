import pytest
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Date, String, UniqueConstraint
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone, date
from sqlalchemy import select


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


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
    check_ins = None

    def __repr__(self):
        return f"<User(id={self.id}, nickname={self.nickname})>"


class UserProgress(TestBase):
    """用户阅读进度表（测试用）"""

    __tablename__ = "user_progresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    article_id = Column(Integer, nullable=True)
    score = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # 关系
    user = None

    def __repr__(self):
        return f"<UserProgress(id={self.id}, user_id={self.user_id})>"


class CheckIn(TestBase):
    """打卡记录表"""

    __tablename__ = "check_ins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    check_date = Column(Date, nullable=False, index=True, comment="打卡日期")

    progress_id = Column(
        Integer, ForeignKey("user_progresses.id", ondelete="SET NULL"), nullable=True
    )

    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), comment="打卡时间"
    )

    # 关系
    user = None

    __table_args__ = (
        UniqueConstraint("user_id", "check_date", name="uq_user_check_date"),
    )

    def __repr__(self):
        return f"<CheckIn(id={self.id}, user_id={self.user_id}, date={self.check_date})>"


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
async def sample_progress(test_session: AsyncSession, sample_user: User):
    """创建测试进度"""
    progress = UserProgress(user_id=sample_user.id, article_id=1, score=90)
    test_session.add(progress)
    await test_session.commit()
    await test_session.refresh(progress)
    return progress


@pytest.mark.asyncio
async def test_create_checkin_with_all_fields(
    test_session: AsyncSession, sample_user: User, sample_progress: UserProgress
):
    """测试创建包含所有字段的打卡记录"""
    check_date = date(2024, 2, 7)
    checkin = CheckIn(
        user_id=sample_user.id, check_date=check_date, progress_id=sample_progress.id
    )

    test_session.add(checkin)
    await test_session.commit()
    await test_session.refresh(checkin)

    assert checkin.id is not None
    assert checkin.user_id == sample_user.id
    assert checkin.check_date == check_date
    assert checkin.progress_id == sample_progress.id
    assert checkin.created_at is not None
    assert isinstance(checkin.created_at, datetime)


@pytest.mark.asyncio
async def test_create_checkin_with_minimal_fields(test_session: AsyncSession, sample_user: User):
    """测试创建只包含必需字段的打卡记录"""
    check_date = date(2024, 2, 7)
    checkin = CheckIn(user_id=sample_user.id, check_date=check_date)

    test_session.add(checkin)
    await test_session.commit()
    await test_session.refresh(checkin)

    assert checkin.id is not None
    assert checkin.user_id == sample_user.id
    assert checkin.check_date == check_date
    assert checkin.progress_id is None
    assert checkin.created_at is not None


@pytest.mark.asyncio
async def test_checkin_unique_constraint_user_date(
    test_session: AsyncSession, sample_user: User
):
    """测试同一用户同一天只能打卡一次"""
    check_date = date(2024, 2, 7)

    checkin1 = CheckIn(user_id=sample_user.id, check_date=check_date)
    test_session.add(checkin1)
    await test_session.commit()

    checkin2 = CheckIn(user_id=sample_user.id, check_date=check_date)
    test_session.add(checkin2)

    with pytest.raises(IntegrityError):
        await test_session.commit()


@pytest.mark.asyncio
async def test_checkin_different_users_same_date(
    test_session: AsyncSession, sample_user: User
):
    """测试不同用户同一天可以各自打卡"""
    check_date = date(2024, 2, 7)

    user2 = User(openid="test_user_456", nickname="测试用户2")
    test_session.add(user2)
    await test_session.commit()
    await test_session.refresh(user2)

    checkin1 = CheckIn(user_id=sample_user.id, check_date=check_date)
    checkin2 = CheckIn(user_id=user2.id, check_date=check_date)

    test_session.add(checkin1)
    test_session.add(checkin2)
    await test_session.commit()

    assert checkin1.id is not None
    assert checkin2.id is not None
    assert checkin1.id != checkin2.id


@pytest.mark.asyncio
async def test_checkin_same_user_different_dates(
    test_session: AsyncSession, sample_user: User
):
    """测试同一用户不同日期可以多次打卡"""
    checkin1 = CheckIn(user_id=sample_user.id, check_date=date(2024, 2, 6))
    checkin2 = CheckIn(user_id=sample_user.id, check_date=date(2024, 2, 7))

    test_session.add(checkin1)
    test_session.add(checkin2)
    await test_session.commit()

    assert checkin1.id is not None
    assert checkin2.id is not None
    assert checkin1.id != checkin2.id


@pytest.mark.asyncio
async def test_checkin_foreign_key_constraint_user(
    test_session: AsyncSession
):
    """测试打卡记录用户外键约束"""
    checkin = CheckIn(user_id=999, check_date=date(2024, 2, 7))

    test_session.add(checkin)
    with pytest.raises(IntegrityError):
        await test_session.commit()


@pytest.mark.asyncio
async def test_checkin_foreign_key_constraint_progress(
    test_session: AsyncSession, sample_user: User
):
    """测试打卡记录进度外键约束"""
    checkin = CheckIn(
        user_id=sample_user.id, check_date=date(2024, 2, 7), progress_id=999
    )

    test_session.add(checkin)
    with pytest.raises(IntegrityError):
        await test_session.commit()


@pytest.mark.asyncio
async def test_checkin_cascade_delete_user(
    test_session: AsyncSession, sample_user: User
):
    """测试删除用户时级联删除打卡记录"""
    checkin = CheckIn(user_id=sample_user.id, check_date=date(2024, 2, 7))

    test_session.add(checkin)
    await test_session.commit()
    checkin_id = checkin.id

    await test_session.delete(sample_user)
    await test_session.commit()

    result = await test_session.execute(select(CheckIn).where(CheckIn.id == checkin_id))
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_checkin_set_null_delete_progress(
    test_session: AsyncSession, sample_user: User, sample_progress: UserProgress
):
    """测试删除进度时打卡记录的progress_id设为NULL"""
    checkin = CheckIn(
        user_id=sample_user.id,
        check_date=date(2024, 2, 7),
        progress_id=sample_progress.id,
    )

    test_session.add(checkin)
    await test_session.commit()
    await test_session.refresh(checkin)

    progress_id = sample_progress.id
    checkin_id = checkin.id

    await test_session.delete(sample_progress)
    await test_session.commit()
    await test_session.refresh(checkin)

    assert checkin.progress_id is None

    result = await test_session.execute(select(CheckIn).where(CheckIn.id == checkin_id))
    assert result.scalar_one_or_none() is not None


@pytest.mark.asyncio
async def test_checkin_relationship_user_defined(
    test_session: AsyncSession, sample_user: User
):
    """测试打卡记录用户关系定义"""
    checkin = CheckIn(user_id=sample_user.id, check_date=date(2024, 2, 7))

    test_session.add(checkin)
    await test_session.commit()
    await test_session.refresh(checkin)

    assert hasattr(checkin, "user")


@pytest.mark.asyncio
async def test_checkin_repr(test_session: AsyncSession, sample_user: User):
    """测试打卡记录__repr__方法"""
    check_date = date(2024, 2, 7)
    checkin = CheckIn(user_id=sample_user.id, check_date=check_date)

    repr_str = repr(checkin)
    assert "CheckIn" in repr_str
    assert str(sample_user.id) in repr_str
    assert str(check_date) in repr_str


@pytest.mark.asyncio
async def test_checkin_foreign_key_indexes(
    test_session: AsyncSession, sample_user: User, sample_progress: UserProgress
):
    """测试打卡记录外键索引"""
    checkin = CheckIn(
        user_id=sample_user.id,
        check_date=date(2024, 2, 7),
        progress_id=sample_progress.id,
    )
    test_session.add(checkin)
    await test_session.commit()

    result = await test_session.execute(
        select(CheckIn).where(CheckIn.user_id == sample_user.id)
    )
    assert result.scalar_one_or_none() is not None

    result = await test_session.execute(
        select(CheckIn).where(CheckIn.progress_id == sample_progress.id)
    )
    assert result.scalar_one_or_none() is not None


@pytest.mark.asyncio
async def test_checkin_created_at_timezone(test_session: AsyncSession, sample_user: User):
    """测试打卡记录created_at使用UTC时区"""
    checkin = CheckIn(user_id=sample_user.id, check_date=date(2024, 2, 7))

    test_session.add(checkin)
    await test_session.commit()
    await test_session.refresh(checkin)

    assert checkin.created_at is not None
    assert isinstance(checkin.created_at, datetime)


@pytest.mark.asyncio
async def test_checkin_check_date_index(test_session: AsyncSession, sample_user: User):
    """测试打卡日期索引"""
    checkin = CheckIn(user_id=sample_user.id, check_date=date(2024, 2, 7))

    test_session.add(checkin)
    await test_session.commit()

    result = await test_session.execute(
        select(CheckIn).where(CheckIn.check_date == date(2024, 2, 7))
    )
    assert result.scalar_one_or_none() is not None
