from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    JSON,
    Boolean,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.article import DifficultyEnum
import enum


class QuestionTypeEnum(enum.Enum):
    """题目类型枚举"""

    CHOICE = "choice"
    JUDGE = "judge"
    FILL = "fill"
    SHORT_ANSWER = "short_answer"


class Question(Base):
    """题目表"""

    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(
        Integer,
        ForeignKey("articles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    type = Column(SQLEnum(QuestionTypeEnum), nullable=False, comment="题目类型")
    content = Column(Text, nullable=False, comment="题干内容")

    options = Column(JSON, nullable=True, comment="选项（选择题）")

    answer = Column(Text, nullable=False, comment="正确答案")

    explanation = Column(Text, nullable=True, comment="答案解析")
    hint = Column(String(500), nullable=True, comment="温柔提示")

    difficulty = Column(
        SQLEnum(DifficultyEnum), default=DifficultyEnum.MEDIUM, comment="题目难度"
    )

    display_order = Column(Integer, default=0, comment="题目顺序")

    is_ai_generated = Column(Boolean, default=False, comment="是否AI生成")

    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), comment="创建时间"
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        comment="更新时间",
    )

    article = relationship("Article", back_populates="questions")
    abilities = relationship(
        "QuestionAbility", back_populates="question", cascade="all, delete-orphan"
    )
    answers = relationship("QuestionAnswer", back_populates="question")

    def __repr__(self):
        return f"<Question(id={self.id}, type={self.type})>"


class QuestionAbility(Base):
    """题目-能力维度关联表"""

    __tablename__ = "question_abilities"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(
        Integer,
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ability_id = Column(
        Integer,
        ForeignKey("ability_dimensions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    weight = Column(Integer, default=1, comment="权重 1-10")

    question = relationship("Question", back_populates="abilities")
    ability = relationship("AbilityDimension", back_populates="question_abilities")

    __table_args__ = (
        UniqueConstraint("question_id", "ability_id", name="uq_question_ability"),
    )
