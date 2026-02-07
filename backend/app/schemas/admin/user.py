from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class UserAdminResponse(BaseModel):
    id: int
    openid: str
    nickname: Optional[str]
    avatar_url: Optional[str]
    grade: Optional[str]
    total_readings: int
    streak_days: int
    max_streak_days: int
    badge_count: int
    created_at: datetime
    last_active_at: Optional[datetime]

    class Config:
        from_attributes = True


class UserListItemAdmin(BaseModel):
    id: int
    nickname: Optional[str]
    grade: Optional[str]
    total_readings: int
    streak_days: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserListResponseAdmin(BaseModel):
    items: List[UserListItemAdmin]
    total: int
    page: int
    page_size: int


class DashboardStats(BaseModel):
    total_users: int
    active_users_today: int
    active_users_week: int
    total_articles: int
    published_articles: int
    total_questions: int
    total_readings: int
    checkins_today: int
