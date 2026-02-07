from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ArticleStatusEnum(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class DifficultyEnum(int, Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3


class TagInfo(BaseModel):
    id: int
    name: str
    category: str


class ArticleListItem(BaseModel):
    id: int
    title: str
    source_book: Optional[str] = None
    word_count: int
    reading_time: int
    article_difficulty: DifficultyEnum
    cover_image: Optional[str] = None
    tags: List[TagInfo] = []
    
    class Config:
        from_attributes = True


class ArticleDetail(BaseModel):
    id: int
    title: str
    content: str
    source_book: Optional[str] = None
    source_chapter: Optional[str] = None
    is_excerpt: bool = False
    word_count: int
    reading_time: int
    article_difficulty: DifficultyEnum
    tags: List[TagInfo] = []
    question_count: int = 0
    
    class Config:
        from_attributes = True


class ArticleListResponse(BaseModel):
    items: List[ArticleListItem]
    total: int
    page: int
    page_size: int


class ArticleFilterParams(BaseModel):
    grade: Optional[str] = None
    genre: Optional[str] = None
    difficulty: Optional[int] = None
    source: Optional[str] = None
    keyword: Optional[str] = None
