from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class AbilityCategoryEnum(enum.Enum):
    """能力分类枚举"""
    INFORMATION = "information"
    COMPREHENSION = "comprehension"
    ANALYSIS = "analysis"
    EXPRESSION = "expression"


class AbilityDimension(Base):
    """能力维度表"""
    __tablename__ = "ability_dimensions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, comment="能力名称")
    code = Column(String(30), unique=True, nullable=False, comment="能力编码，如 detail_extraction")
    category = Column(SQLEnum(AbilityCategoryEnum), nullable=False, comment="能力分类")
    description = Column(String(200), nullable=True, comment="能力描述")
    display_order = Column(Integer, default=0, comment="显示顺序")

    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), comment="创建时间"
    )

    question_abilities = relationship("QuestionAbility", back_populates="ability")
    # TODO: UserAbility model will be implemented in Task 10
    user_abilities = relationship("UserAbility", back_populates="ability")

    def __repr__(self):
        return f"<AbilityDimension(id={self.id}, name={self.name})>"
