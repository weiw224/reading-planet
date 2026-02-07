from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.user import User
from app.models.article import Article, ArticleStatusEnum
from app.models.question import Question
from app.models.progress import UserProgress
from app.models.checkin import CheckIn
from app.schemas.admin.user import DashboardStats


class DashboardService:
    @staticmethod
    async def get_stats(db: AsyncSession) -> DashboardStats:
        today = date.today()
        week_ago = today - timedelta(days=7)

        total_users = (await db.execute(
            select(func.count(User.id))
        )).scalar() or 0

        active_today = (await db.execute(
            select(func.count(func.distinct(UserProgress.user_id)))
            .where(func.date(UserProgress.created_at) == today)
        )).scalar() or 0

        active_week = (await db.execute(
            select(func.count(func.distinct(UserProgress.user_id)))
            .where(func.date(UserProgress.created_at) >= week_ago)
        )).scalar() or 0

        total_articles = (await db.execute(
            select(func.count(Article.id))
        )).scalar() or 0

        published_articles = (await db.execute(
            select(func.count(Article.id))
            .where(Article.status == ArticleStatusEnum.PUBLISHED)
        )).scalar() or 0

        total_questions = (await db.execute(
            select(func.count(Question.id))
        )).scalar() or 0

        total_readings = (await db.execute(
            select(func.count(UserProgress.id))
            .where(UserProgress.completed_at.isnot(None))
        )).scalar() or 0

        checkins_today = (await db.execute(
            select(func.count(CheckIn.id))
            .where(CheckIn.check_date == today)
        )).scalar() or 0

        return DashboardStats(
            total_users=total_users,
            active_users_today=active_today,
            active_users_week=active_week,
            total_articles=total_articles,
            published_articles=published_articles,
            total_questions=total_questions,
            total_readings=total_readings,
            checkins_today=checkins_today
        )


dashboard_service = DashboardService()
