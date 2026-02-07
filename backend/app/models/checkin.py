from datetime import datetime, date
from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class CheckIn(Base):
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

    user = relationship("User", back_populates="check_ins")

    __table_args__ = (
        UniqueConstraint("user_id", "check_date", name="uq_user_check_date"),
    )

    def __repr__(self):
        return (
            f"<CheckIn(id={self.id}, user_id={self.user_id}, date={self.check_date})>"
        )
