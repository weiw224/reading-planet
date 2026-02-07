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


class ArticleCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=10)
    source_book: Optional[str] = None
    source_chapter: Optional[str] = None
    is_excerpt: bool = False
    article_difficulty: DifficultyEnum = DifficultyEnum.MEDIUM
    tag_ids: List[int] = []


class ArticleUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=10)
    source_book: Optional[str] = None
    source_chapter: Optional[str] = None
    is_excerpt: Optional[bool] = None
    article_difficulty: Optional[DifficultyEnum] = None
    tag_ids: Optional[List[int]] = None
    status: Optional[ArticleStatusEnum] = None


class ArticleAdminResponse(BaseModel):
    id: int
    title: str
    content: str
    source_book: Optional[str]
    source_chapter: Optional[str]
    is_excerpt: bool
    word_count: int
    reading_time: int
    article_difficulty: DifficultyEnum
    status: ArticleStatusEnum
    is_ai_generated: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int]
    tags: List[dict] = []
    question_count: int = 0

    class Config:
        from_attributes = True


class ArticleListItemAdmin(BaseModel):
    id: int
    title: str
    source_book: Optional[str]
    word_count: int
    article_difficulty: DifficultyEnum
    status: ArticleStatusEnum
    is_ai_generated: bool
    question_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class ArticleListResponseAdmin(BaseModel):
    items: List[ArticleListItemAdmin]
    total: int
    page: int
    page_size: int
