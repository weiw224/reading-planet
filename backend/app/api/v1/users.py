from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.common import ResponseModel
from app.schemas.user import (
    UserResponse,
    UserUpdate,
    UserStatsResponse,
    AbilityRadarResponse,
    CheckInResponse,
    BadgeListResponse
)
from app.services.user_service import user_service

router = APIRouter()


@router.get("/me", response_model=ResponseModel[UserResponse])
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    return ResponseModel(data=UserResponse.model_validate(current_user))


@router.put("/me", response_model=ResponseModel[UserResponse])
async def update_current_user(
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    updated_user = await user_service.update_user(db, current_user, data)
    return ResponseModel(data=UserResponse.model_validate(updated_user))


@router.get("/me/stats", response_model=ResponseModel[UserStatsResponse])
async def get_user_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stats = await user_service.get_user_stats(db, current_user.id)
    return ResponseModel(data=stats)


@router.get("/me/abilities", response_model=ResponseModel[AbilityRadarResponse])
async def get_ability_radar(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    abilities = await user_service.get_ability_radar(db, current_user.id)
    return ResponseModel(data=AbilityRadarResponse(abilities=abilities))


@router.get("/me/checkins", response_model=ResponseModel[CheckInResponse])
async def get_checkins(
    year: int = Query(default=None, description="年份，默认当前年"),
    month: int = Query(default=None, ge=1, le=12, description="月份，默认当前月"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    today = date.today()
    if year is None:
        year = today.year
    if month is None:
        month = today.month
    
    current_streak, records = await user_service.get_checkins(db, current_user.id, year, month)
    
    return ResponseModel(data=CheckInResponse(
        current_streak=current_streak,
        records=records
    ))


@router.get("/me/badges", response_model=ResponseModel[BadgeListResponse])
async def get_badges(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    earned_count, total_count, badges = await user_service.get_badges(db, current_user.id)
    
    return ResponseModel(data=BadgeListResponse(
        earned_count=earned_count,
        total_count=total_count,
        badges=badges
    ))
