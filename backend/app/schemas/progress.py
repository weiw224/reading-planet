from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class StartReadingRequest(BaseModel):
    article_id: int


class StartReadingResponse(BaseModel):
    progress_id: int
    article_id: int
    article_title: str
    question_count: int


class SubmitAnswerRequest(BaseModel):
    question_id: int
    user_answer: str


class SubmitAnswerResponse(BaseModel):
    question_id: int
    is_correct: bool
    correct_answer: str
    explanation: Optional[str] = None
    ability_names: List[str] = []


class CompleteReadingRequest(BaseModel):
    time_spent: int = Field(..., ge=0, description="阅读用时（秒）")


class AbilityScoreItem(BaseModel):
    ability_id: int
    ability_name: str
    correct_count: int
    total_count: int
    score: float


class BadgeUnlock(BaseModel):
    id: int
    name: str
    description: str
    icon_url: Optional[str] = None


class CompleteReadingResponse(BaseModel):
    progress_id: int
    score: int
    correct_count: int
    total_count: int
    time_spent: int
    ability_scores: List[AbilityScoreItem]
    is_checked_in: bool
    streak_days: int
    new_badges: List[BadgeUnlock] = []


class ProgressDetail(BaseModel):
    id: int
    article_id: int
    article_title: str
    score: Optional[int] = None
    correct_count: int
    total_count: int
    time_spent: Optional[int] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AnswerDetail(BaseModel):
    question_id: int
    question_content: str
    question_type: str
    user_answer: Optional[str]
    correct_answer: str
    is_correct: Optional[bool]
    explanation: Optional[str] = None


class ProgressWithAnswers(ProgressDetail):
    answers: List[AnswerDetail] = []


class HistoryItem(BaseModel):
    id: int
    article_id: int
    article_title: str
    score: Optional[int]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class HistoryResponse(BaseModel):
    items: List[HistoryItem]
    total: int
    page: int
    page_size: int
