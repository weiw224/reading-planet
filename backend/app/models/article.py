from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import UniqueConstraint
from app.database import Base
import enum


class ArticleStatusEnum(enum.Enum):
    """文章状态枚举"""
    DRAFT = "draft"           # 草稿
    PENDING = "pending"       # 待审核
    PUBLISHED = "published"   # 已发布
    ARCHIVED = "archived"     # 已归档


class DifficultyEnum(enum.Enum):
    """难度枚举"""
    EASY = 1      # ⭐
    MEDIUM = 2    # ⭐⭐
    HARD = 3      # ⭐⭐⭐


class Article(Base):
    """文章表"""
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True, comment="标题")
    content = Column(Text, nullable=False, comment="文章内容")
    
    # 来源信息
    source_book = Column(String(200), nullable=True, comment="来源书籍，如《伊索寓言》")
    source_chapter = Column(String(200), nullable=True, comment="来源章节")
    is_excerpt = Column(Boolean, default=False, comment="是否为节选")
    
    # 文章属性
    word_count = Column(Integer, nullable=False, comment="字数")
    reading_time = Column(Integer, nullable=False, comment="预计阅读时间(分钟)")
    article_difficulty = Column(SQLEnum(DifficultyEnum), default=DifficultyEnum.MEDIUM, comment="文章难度")
    
    # 状态
    status = Column(SQLEnum(ArticleStatusEnum), default=ArticleStatusEnum.DRAFT, index=True, comment="状态")
    
    # AI 导入标记
    is_ai_generated = Column(Boolean, default=False, comment="是否AI导入")
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), comment="创建时间")
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), comment="更新时间")
    created_by = Column(Integer, nullable=True, comment="创建者ID（管理员）")
    
    # 关系
    questions = relationship("Question", back_populates="article", cascade="all, delete-orphan")
    tags = relationship("ArticleTag", back_populates="article", cascade="all, delete-orphan")
    progresses = relationship("UserProgress", back_populates="article")
    
    def __repr__(self):
        return f"<Article(id={self.id}, title={self.title})>"


class ArticleTag(Base):
    """文章-标签关联表"""
    __tablename__ = "article_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 关系
    article = relationship("Article", back_populates="tags")
    tag = relationship("Tag", back_populates="article_tags")
    
    # 唯一约束
    __table_args__ = (
        UniqueConstraint('article_id', 'tag_id', name='uq_article_tag'),
    )
