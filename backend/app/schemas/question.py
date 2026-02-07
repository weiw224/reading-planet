from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class QuestionTypeEnum(str, Enum):
    """题目类型枚举"""
    CHOICE = "choice"
    JUDGE = "judge"
    FILL = "fill"
    SHORT_ANSWER = "short_answer"


class DifficultyEnum(int, Enum):
    """难度枚举"""
    EASY = 1
    MEDIUM = 2
    HARD = 3


class AbilityInfo(BaseModel):
    """能力维度信息"""
    id: int
    name: str
    code: str


class QuestionItem(BaseModel):
    """题目详情（用户端）"""
    id: int
    type: QuestionTypeEnum
    content: str
    options: Optional[List[str]] = None
    hint: Optional[str] = None
    difficulty: DifficultyEnum
    abilities: List[AbilityInfo] = []
    
    class Config:
        from_attributes = True


class QuestionWithAnswer(QuestionItem):
    """题目详情（含答案，答题后返回）"""
    answer: str
    explanation: Optional[str] = None


class QuestionListResponse(BaseModel):
    """题目列表响应"""
    article_id: int
    article_title: str
    questions: List[QuestionItem]
    total: int
