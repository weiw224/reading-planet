from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class UserProgress(Base):
    """用户阅读进度表"""

    __tablename__ = "user_progresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    article_id = Column(
        Integer,
        ForeignKey("articles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # 成绩
    score = Column(Integer, nullable=True, comment="得分（百分制）")
    correct_count = Column(Integer, default=0, comment="正确题数")
    total_count = Column(Integer, default=0, comment="总题数")

    # 用时
    time_spent = Column(Integer, nullable=True, comment="用时（秒）")

    # 状态
    completed_at = Column(DateTime, nullable=True, comment="完成时间")

    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), comment="开始时间"
    )

    # 关系
    user = relationship("User", back_populates="progresses")
    article = relationship("Article", back_populates="progresses")
    answers = relationship(
        "QuestionAnswer", back_populates="progress", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<UserProgress(id={self.id}, user_id={self.user_id}, article_id={self.article_id})>"


class QuestionAnswer(Base):
    """用户答题记录表"""

    __tablename__ = "question_answers"

    id = Column(Integer, primary_key=True, index=True)
    progress_id = Column(
        Integer,
        ForeignKey("user_progresses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id = Column(
        Integer,
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # 用户答案
    user_answer = Column(Text, nullable=True, comment="用户答案")
    is_correct = Column(Boolean, nullable=True, comment="是否正确")

    # 简答题 AI 评分（可选）
    ai_score = Column(Integer, nullable=True, comment="AI评分（0-100）")
    ai_feedback = Column(Text, nullable=True, comment="AI反馈")

    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), comment="答题时间"
    )

    # 关系
    progress = relationship("UserProgress", back_populates="answers")
    question = relationship("Question", back_populates="answers")

    def __repr__(self):
        return f"<QuestionAnswer(id={self.id}, is_correct={self.is_correct})>"
