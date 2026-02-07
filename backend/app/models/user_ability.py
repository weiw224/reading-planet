from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class UserAbility(Base):
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

    user = relationship("User", back_populates="abilities")
    ability = relationship("AbilityDimension", back_populates="user_abilities")

    __table_args__ = (
        UniqueConstraint("user_id", "ability_id", name="uq_user_ability"),
    )

    def __repr__(self):
        return f"<UserAbility(user_id={self.user_id}, ability_id={self.ability_id}, score={self.score})>"
