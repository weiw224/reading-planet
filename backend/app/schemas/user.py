from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


class GradeEnum(str, Enum):
    GRADE_1 = "GRADE_1"
    GRADE_2 = "GRADE_2"
    GRADE_3 = "GRADE_3"
    GRADE_4 = "GRADE_4"
    GRADE_5 = "GRADE_5"
    GRADE_6 = "GRADE_6"


class UserBase(BaseModel):
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    grade: Optional[str] = None
    
    @field_validator('grade')
    @classmethod
    def parse_grade(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            if v in ["GRADE_1", "GRADE_2", "GRADE_3", "GRADE_4", "GRADE_5", "GRADE_6"]:
                return v
            if v in ["1年级", "2年级", "3年级", "4年级", "5年级", "6年级"]:
                chinese_map = {
                    "1年级": "GRADE_1",
                    "2年级": "GRADE_2",
                    "3年级": "GRADE_3",
                    "4年级": "GRADE_4",
                    "5年级": "GRADE_5",
                    "6年级": "GRADE_6"
                }
                return chinese_map.get(v)
            if v in ["1", "2", "3", "4", "5", "6"]:
                int_map = {
                    "1": "GRADE_1",
                    "2": "GRADE_2",
                    "3": "GRADE_3",
                    "4": "GRADE_4",
                    "5": "GRADE_5",
                    "6": "GRADE_6"
                }
                return int_map.get(v)
            return v
        if isinstance(v, int):
            int_map = {
                1: "GRADE_1",
                2: "GRADE_2",
                3: "GRADE_3",
                4: "GRADE_4",
                5: "GRADE_5",
                6: "GRADE_6"
            }
            return int_map.get(v)
        return v


class UserUpdate(UserBase):
    pass
    
    @field_validator('grade')
    @classmethod
    def parse_grade(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            if v in ["GRADE_1", "GRADE_2", "GRADE_3", "GRADE_4", "GRADE_5", "GRADE_6"]:
                return v
            if v in ["1年级", "2年级", "3年级", "4年级", "5年级", "6年级"]:
                chinese_map = {
                    "1年级": "GRADE_1",
                    "2年级": "GRADE_2",
                    "3年级": "GRADE_3",
                    "4年级": "GRADE_4",
                    "5年级": "GRADE_5",
                    "6年级": "GRADE_6"
                }
                return chinese_map.get(v)
            if v in ["1", "2", "3", "4", "5", "6"]:
                int_map = {
                    "1": "GRADE_1",
                    "2": "GRADE_2",
                    "3": "GRADE_3",
                    "4": "GRADE_4",
                    "5": "GRADE_5",
                    "6": "GRADE_6"
                }
                return int_map.get(v)
            return v
        if isinstance(v, int):
            int_map = {
                1: "GRADE_1",
                2: "GRADE_2",
                3: "GRADE_3",
                4: "GRADE_4",
                5: "GRADE_5",
                6: "GRADE_6"
            }
            return int_map.get(v)
        return v


class UserResponse(UserBase):
    id: int
    total_readings: int
    streak_days: int
    max_streak_days: int
    created_at: datetime
    grade: Optional[str] = None
    
    @field_validator('grade')
    @classmethod
    def parse_grade(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            if v in ["GRADE_1", "GRADE_2", "GRADE_3", "GRADE_4", "GRADE_5", "GRADE_6"]:
                return v
            if v in ["1年级", "2年级", "3年级", "4年级", "5年级", "6年级"]:
                chinese_map = {
                    "1年级": "GRADE_1",
                    "2年级": "GRADE_2",
                    "3年级": "GRADE_3",
                    "4年级": "GRADE_4",
                    "5年级": "GRADE_5",
                    "6年级": "GRADE_6"
                }
                return chinese_map.get(v)
            if v in ["1", "2", "3", "4", "5", "6"]:
                int_map = {
                    "1": "GRADE_1",
                    "2": "GRADE_2",
                    "3": "GRADE_3",
                    "4": "GRADE_4",
                    "5": "GRADE_5",
                    "6": "GRADE_6"
                }
                return int_map.get(v)
            return v
        if isinstance(v, int):
            int_map = {
                1: "GRADE_1",
                2: "GRADE_2",
                3: "GRADE_3",
                4: "GRADE_4",
                5: "GRADE_5",
                6: "GRADE_6"
            }
            return int_map.get(v)
        return v
    
    class Config:
        from_attributes = True










class UserStatsResponse(BaseModel):
    total_readings: int
    total_questions: int
    correct_rate: float
    streak_days: int
    max_streak_days: int
    total_badges: int
    total_time: int


class AbilityScore(BaseModel):
    ability_id: int
    ability_name: str
    ability_code: str
    category: str
    score: float
    correct_count: int
    total_count: int


class AbilityRadarResponse(BaseModel):
    abilities: List[AbilityScore]


class CheckInRecord(BaseModel):
    date: date
    article_title: Optional[str] = None


class CheckInResponse(BaseModel):
    current_streak: int
    records: List[CheckInRecord]


class BadgeInfo(BaseModel):
    id: int
    name: str
    description: str
    icon_url: Optional[str]
    category: str
    earned: bool
    earned_at: Optional[datetime] = None
    progress: Optional[float] = None


class BadgeListResponse(BaseModel):
    earned_count: int
    total_count: int
    badges: List[BadgeInfo]
