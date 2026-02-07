from datetime import date, timedelta
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, Integer, cast
from sqlalchemy.orm import selectinload

from app.models.user import User, GradeEnum as DBGradeEnum
from app.models.progress import UserProgress, QuestionAnswer
from app.models.checkin import CheckIn
from app.models.badge import Badge, UserBadge
from app.models.user_ability import UserAbility
from app.models.ability import AbilityDimension
from app.schemas.user import (
    UserUpdate, 
    UserStatsResponse, 
    AbilityScore,
    CheckInRecord,
    BadgeInfo
)


class UserService:
    
    @staticmethod
    async def update_user(db: AsyncSession, user: User, data: UserUpdate) -> User:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "grade" and value is not None:
                grade_map = {
                    "1年级": DBGradeEnum.GRADE_1,
                    "2年级": DBGradeEnum.GRADE_2,
                    "3年级": DBGradeEnum.GRADE_3,
                    "4年级": DBGradeEnum.GRADE_4,
                    "5年级": DBGradeEnum.GRADE_5,
                    "6年级": DBGradeEnum.GRADE_6,
                }
                setattr(user, field, grade_map.get(value))
            else:
                setattr(user, field, value)
        
        await db.commit()
        await db.refresh(user)
        return user

    
    @staticmethod
    async def get_user_stats(db: AsyncSession, user_id: int) -> UserStatsResponse:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        
        answer_stats = await db.execute(
            select(
                func.count(QuestionAnswer.id).label("total"),
                func.sum(cast(QuestionAnswer.is_correct, Integer)).label("correct")
            )
            .join(UserProgress)
            .where(UserProgress.user_id == user_id)
        )
        stats = answer_stats.first()
        total_questions = stats.total or 0
        correct_count = stats.correct or 0
        correct_rate = (correct_count / total_questions * 100) if total_questions > 0 else 0
        
        time_result = await db.execute(
            select(func.sum(UserProgress.time_spent))
            .where(UserProgress.user_id == user_id)
        )
        total_seconds = time_result.scalar() or 0
        total_time = total_seconds // 60
        
        badge_result = await db.execute(
            select(func.count(UserBadge.id))
            .where(UserBadge.user_id == user_id)
        )
        total_badges = badge_result.scalar() or 0
        
        return UserStatsResponse(
            total_readings=user.total_readings,
            total_questions=total_questions,
            correct_rate=round(correct_rate, 1),
            streak_days=user.streak_days,
            max_streak_days=user.max_streak_days,
            total_badges=total_badges,
            total_time=total_time
        )
    
    @staticmethod
    async def get_ability_radar(db: AsyncSession, user_id: int) -> List[AbilityScore]:
        abilities_result = await db.execute(
            select(AbilityDimension).order_by(AbilityDimension.display_order)
        )
        abilities = abilities_result.scalars().all()
        
        user_abilities_result = await db.execute(
            select(UserAbility).where(UserAbility.user_id == user_id)
        )
        user_abilities = {ua.ability_id: ua for ua in user_abilities_result.scalars().all()}
        
        result = []
        for ability in abilities:
            ua = user_abilities.get(ability.id)
            result.append(AbilityScore(
                ability_id=ability.id,
                ability_name=ability.name,
                ability_code=ability.code,
                category=ability.category.value,
                score=ua.score if ua else 0,
                correct_count=ua.correct_count if ua else 0,
                total_count=ua.total_count if ua else 0
            ))
        
        return result
    
    @staticmethod
    async def get_checkins(
        db: AsyncSession, 
        user_id: int, 
        year: int, 
        month: int
    ) -> Tuple[int, List[CheckInRecord]]:
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one()
        
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)
        
        result = await db.execute(
            select(CheckIn)
            .where(
                CheckIn.user_id == user_id,
                CheckIn.check_date >= start_date,
                CheckIn.check_date < end_date
            )
            .order_by(CheckIn.check_date)
        )
        checkins = result.scalars().all()
        
        records = [
            CheckInRecord(
                date=ci.check_date,
                article_title=None
            )
            for ci in checkins
        ]
        
        return user.streak_days, records
    
    @staticmethod
    async def get_badges(db: AsyncSession, user_id: int) -> Tuple[int, int, List[BadgeInfo]]:
        badges_result = await db.execute(
            select(Badge).order_by(Badge.category, Badge.display_order)
        )
        badges = badges_result.scalars().all()
        
        user_badges_result = await db.execute(
            select(UserBadge).where(UserBadge.user_id == user_id)
        )
        user_badges = {ub.badge_id: ub for ub in user_badges_result.scalars().all()}
        
        result = []
        earned_count = 0
        for badge in badges:
            ub = user_badges.get(badge.id)
            earned = ub is not None
            if earned:
                earned_count += 1
            
            result.append(BadgeInfo(
                id=badge.id,
                name=badge.name,
                description=badge.description,
                icon_url=badge.icon_url,
                category=badge.category.value,
                earned=earned,
                earned_at=ub.earned_at if ub else None,
                progress=None
            ))
        
        return earned_count, len(badges), result


user_service = UserService()
