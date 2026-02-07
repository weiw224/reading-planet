from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class QuestionTypeEnum(str, Enum):
    CHOICE = "choice"
    JUDGE = "judge"
    FILL = "fill"
    SHORT_ANSWER = "short_answer"


class DifficultyEnum(int, Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3


class AbilityWeight(BaseModel):
    ability_id: int
    weight: int = Field(1, ge=1, le=10)


class QuestionCreateRequest(BaseModel):
    article_id: int
    type: QuestionTypeEnum
    content: str = Field(..., min_length=1)
    options: Optional[List[str]] = None
    answer: str = Field(..., min_length=1)
    explanation: Optional[str] = None
    hint: Optional[str] = None
    difficulty: DifficultyEnum = DifficultyEnum.MEDIUM
    display_order: int = 0
    abilities: List[AbilityWeight] = []


class QuestionUpdateRequest(BaseModel):
    type: Optional[QuestionTypeEnum] = None
    content: Optional[str] = None
    options: Optional[List[str]] = None
    answer: Optional[str] = None
    explanation: Optional[str] = None
    hint: Optional[str] = None
    difficulty: Optional[DifficultyEnum] = None
    display_order: Optional[int] = None
    abilities: Optional[List[AbilityWeight]] = None


class QuestionAdminResponse(BaseModel):
    id: int
    article_id: int
    article_title: str
    type: QuestionTypeEnum
    content: str
    options: Optional[List[str]]
    answer: str
    explanation: Optional[str]
    hint: Optional[str]
    difficulty: DifficultyEnum
    display_order: int
    is_ai_generated: bool
    created_at: datetime
    updated_at: datetime
    abilities: List[dict] = []

    class Config:
        from_attributes = True


class QuestionListItemAdmin(BaseModel):
    id: int
    article_id: int
    article_title: str
    type: QuestionTypeEnum
    content: str
    difficulty: DifficultyEnum
    display_order: int
    is_ai_generated: bool

    class Config:
        from_attributes = True
