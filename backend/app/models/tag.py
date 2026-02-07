from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class TagCategoryEnum(enum.Enum):
    """标签分类枚举"""
    GRADE = "grade"
    GENRE = "genre"
    SOURCE = "source"
    THEME = "theme"
    CULTURE = "culture"
    ADAPTATION = "adaptation"


class Tag(Base):
    """标签表"""
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, comment="标签名称")
    category = Column(SQLEnum(TagCategoryEnum), nullable=False, index=True, comment="标签分类")
    description = Column(String(200), nullable=True, comment="标签描述")
    display_order = Column(Integer, default=0, comment="显示顺序")
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), comment="创建时间")
    
    article_tags = relationship("ArticleTag", back_populates="tag")
    
    __table_args__ = (
        UniqueConstraint('name', 'category', name='uq_tag_name_category'),
    )
    
    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name}, category={self.category})>"
