from pydantic import BaseModel
from typing import List, Optional


class QuestionItem(BaseModel):
    id: int
    type: str
    content: str
    options: Optional[dict] = None
    answer: Optional[str] = None
    explanation: Optional[str] = None
    hint: Optional[str] = None
    difficulty: int
    display_order: int
    
    class Config:
        from_attributes = True


class QuestionListResponse(BaseModel):
    article_id: int
    article_title: str
    questions: List[QuestionItem]
    total: int
