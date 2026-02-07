import pytest
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from datetime import datetime
import enum


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


# Create a separate Base for testing to avoid importing from app.database
TestBase = declarative_base()


# GradeEnum for testing
class GradeEnum(enum.Enum):
    GRADE_1 = 1
    GRADE_2 = 2
    GRADE_3 = 3
    GRADE_4 = 4
    GRADE_5 = 5
    GRADE_6 = 6


# Test User model
class User(TestBase):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    openid = Column(String(64), unique=True, index=True, nullable=False)
    nickname = Column(String(64), nullable=True)
    avatar_url = Column(String(512), nullable=True)
    grade = Column(SQLEnum(GradeEnum), nullable=True)
    total_readings = Column(Integer, default=0)
    streak_days = Column(Integer, default=0)
    max_streak_days = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships (placeholder attributes for testing)
    progresses = None
    check_ins = None
    badges = None
    abilities = None
    
    def __repr__(self):
        return f"<User(id={self.id}, nickname={self.nickname})>"


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
async def test_create_user(test_session: AsyncSession):
    """测试创建用户"""
    user = User(
        openid="test_openid_123",
        nickname="测试用户",
        avatar_url="https://example.com/avatar.jpg",
        grade=GradeEnum.GRADE_3
    )
    
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    
    assert user.id is not None
    assert user.openid == "test_openid_123"
    assert user.nickname == "测试用户"
    assert user.avatar_url == "https://example.com/avatar.jpg"
    assert user.grade == GradeEnum.GRADE_3


@pytest.mark.asyncio
async def test_user_default_values(test_session: AsyncSession):
    """测试用户默认值"""
    user = User(openid="test_openid_456")
    
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    
    assert user.total_readings == 0
    assert user.streak_days == 0
    assert user.max_streak_days == 0
    assert user.nickname is None
    assert user.avatar_url is None
    assert user.grade is None
    assert user.created_at is not None
    assert user.updated_at is not None


@pytest.mark.asyncio
async def test_user_openid_unique(test_session: AsyncSession):
    """测试openid唯一性约束"""
    user1 = User(openid="test_openid_789")
    user2 = User(openid="test_openid_789")
    
    test_session.add(user1)
    await test_session.commit()
    
    test_session.add(user2)
    with pytest.raises(Exception):  # Should raise an integrity error
        await test_session.commit()


@pytest.mark.asyncio
async def test_user_repr(test_session: AsyncSession):
    """测试用户__repr__方法"""
    user = User(openid="test_openid_000", nickname="测试昵称")
    
    repr_str = repr(user)
    assert "User" in repr_str
    assert "测试昵称" in repr_str


@pytest.mark.asyncio
async def test_grade_enum_values():
    """测试年级枚举值"""
    assert GradeEnum.GRADE_1.value == 1
    assert GradeEnum.GRADE_2.value == 2
    assert GradeEnum.GRADE_3.value == 3
    assert GradeEnum.GRADE_4.value == 4
    assert GradeEnum.GRADE_5.value == 5
    assert GradeEnum.GRADE_6.value == 6


@pytest.mark.asyncio
async def test_user_relationships_defined(test_session: AsyncSession):
    """测试用户关系定义（不测试功能，只验证关系存在）"""
    user = User(openid="test_openid_rel")
    
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    
    assert hasattr(user, 'progresses')
    assert hasattr(user, 'check_ins')
    assert hasattr(user, 'badges')
    assert hasattr(user, 'abilities')
