from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base
import enum


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


class Badge(Base):
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, comment="勋章名称")
    description = Column(String(200), nullable=True, comment="勋章描述")
    icon_url = Column(String(512), nullable=True, comment="勋章图标URL")

    category = Column(SQLEnum(BadgeCategoryEnum), nullable=False, comment="勋章分类")

    condition_type = Column(
        SQLEnum(BadgeConditionTypeEnum), nullable=False, comment="条件类型"
    )
    condition_value = Column(Integer, nullable=False, comment="条件阈值")
    condition_extra = Column(String(100), nullable=True, comment="额外条件参数")

    display_order = Column(Integer, default=0, comment="显示顺序")

    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), comment="创建时间"
    )

    user_badges = relationship("UserBadge", back_populates="badge")

    def __repr__(self):
        return f"<Badge(id={self.id}, name={self.name})>"


class UserBadge(Base):
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

    user = relationship("User", back_populates="badges")
    badge = relationship("Badge", back_populates="user_badges")

    __table_args__ = (UniqueConstraint("user_id", "badge_id", name="uq_user_badge"),)

    def __repr__(self):
        return f"<UserBadge(id={self.id}, user_id={self.user_id}, badge_id={self.badge_id})>"
