from typing import List, Optional, Tuple
from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.article import Article
from app.models.question import Question, QuestionAbility
from app.models.progress import UserProgress, QuestionAnswer
from app.models.checkin import CheckIn
from app.models.user_ability import UserAbility
from app.models.badge import Badge, UserBadge, BadgeConditionTypeEnum
from app.models.ability import AbilityDimension
from app.schemas.progress import (
    StartReadingResponse,
    SubmitAnswerResponse,
    CompleteReadingResponse,
    AbilityScoreItem,
    BadgeUnlock,
    ProgressWithAnswers,
    AnswerDetail,
    HistoryItem
)
from app.utils.exceptions import NotFoundError, ValidationError


class ProgressService:
    
    @staticmethod
    async def start_reading(
        db: AsyncSession,
        user_id: int,
        article_id: int
    ) -> StartReadingResponse:
        try:
            article = await db.get(Article, article_id)
            if not article:
                raise NotFoundError("文章不存在")

            question_count_result = await db.execute(
                select(func.count(Question.id)).where(Question.article_id == article_id)
            )
            question_count = question_count_result.scalar() or 0

            progress = UserProgress(
                user_id=user_id,
                article_id=article_id,
                total_count=question_count
            )
            db.add(progress)
            await db.commit()
            await db.refresh(progress)

            return StartReadingResponse(
                progress_id=progress.id,
                article_id=article_id,
                article_title=article.title,
                question_count=question_count
            )
        except Exception as e:
            await db.rollback()
            raise

    @staticmethod
    async def submit_answer(
        db: AsyncSession,
        progress_id: int,
        user_id: int,
        question_id: int,
        user_answer: str
    ) -> SubmitAnswerResponse:
        try:
            progress = await db.get(UserProgress, progress_id)
            if not progress or progress.user_id != user_id:
                raise ValidationError("进度记录不存在")

            if progress.completed_at:
                raise ValidationError("该阅读已完成，无法继续答题")

            question = await db.get(Question, question_id)
            if not question or question.article_id != progress.article_id:
                raise ValidationError("题目不存在或不属于该文章")

            existing = await db.execute(
                select(QuestionAnswer).where(
                    QuestionAnswer.progress_id == progress_id,
                    QuestionAnswer.question_id == question_id
                ).with_for_update()
            )
            if existing.scalar_one_or_none():
                raise ValidationError("该题目已提交答案")

            is_correct = ProgressService._check_answer(
                question.type.value,
                user_answer,
                question.answer
            )

            answer_record = QuestionAnswer(
                progress_id=progress_id,
                question_id=question_id,
                user_answer=user_answer,
                is_correct=is_correct
            )
            db.add(answer_record)

            if is_correct:
                progress.correct_count += 1

            await db.commit()

            ability_result = await db.execute(
                select(QuestionAbility)
                .where(QuestionAbility.question_id == question_id)
                .options(selectinload(QuestionAbility.ability))
            )
            ability_names = [qa.ability.name for qa in ability_result.scalars().all()]

            return SubmitAnswerResponse(
                question_id=question_id,
                is_correct=is_correct,
                correct_answer=question.answer,
                explanation=question.explanation,
                ability_names=ability_names
            )
        except (ValidationError, NotFoundError):
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            raise

    @staticmethod
    def _check_answer(question_type: str, user_answer: str, correct_answer: str) -> bool:
        user_answer = user_answer.strip().upper()
        correct_answer = correct_answer.strip().upper()

        if question_type == "choice":
            return user_answer == correct_answer

        elif question_type == "judge":
            return user_answer == correct_answer

        elif question_type == "fill":
            return user_answer.lower() == correct_answer.lower()

        elif question_type == "short_answer":
            return True

        return False

    @staticmethod
    async def complete_reading(
        db: AsyncSession,
        progress_id: int,
        user_id: int,
        time_spent: int
    ) -> CompleteReadingResponse:
        try:
            progress = await db.get(UserProgress, progress_id)
            if not progress or progress.user_id != user_id:
                raise ValidationError("进度记录不存在")

            if progress.completed_at:
                raise ValidationError("该阅读已完成")

            score = 0
            if progress.total_count > 0:
                score = int(progress.correct_count / progress.total_count * 100)

            progress.score = score
            progress.time_spent = time_spent
            progress.completed_at = datetime.utcnow()

            user = await db.get(User, user_id)
            user.total_readings += 1

            ability_scores = await ProgressService._update_user_abilities(db, progress)

            is_checked_in, streak_days = await ProgressService._handle_checkin(db, user, progress)

            new_badges = await ProgressService._check_badges(db, user)

            await db.commit()

            return CompleteReadingResponse(
                progress_id=progress_id,
                score=score,
                correct_count=progress.correct_count,
                total_count=progress.total_count,
                time_spent=time_spent,
                ability_scores=ability_scores,
                is_checked_in=is_checked_in,
                streak_days=streak_days,
                new_badges=new_badges
            )
        except (ValidationError, NotFoundError):
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            raise

    @staticmethod
    async def _update_user_abilities(
        db: AsyncSession,
        progress: UserProgress
    ) -> List[AbilityScoreItem]:
        try:
            answers_result = await db.execute(
                select(QuestionAnswer)
                .where(QuestionAnswer.progress_id == progress.id)
                .options(
                    selectinload(QuestionAnswer.question)
                    .selectinload(Question.abilities)
                    .selectinload(QuestionAbility.ability)
                )
            )
            answers = answers_result.scalars().all()

            ability_stats = {}

            for answer in answers:
                for qa in answer.question.abilities:
                    ability_id = qa.ability_id
                    if ability_id not in ability_stats:
                        ability_stats[ability_id] = {
                            "correct": 0,
                            "total": 0,
                            "name": qa.ability.name
                        }
                    ability_stats[ability_id]["total"] += 1
                    if answer.is_correct:
                        ability_stats[ability_id]["correct"] += 1

            result_scores = []
            for ability_id, stats in ability_stats.items():
                user_ability_result = await db.execute(
                    select(UserAbility).where(
                        UserAbility.user_id == progress.user_id,
                        UserAbility.ability_id == ability_id
                    )
                )
                user_ability = user_ability_result.scalar_one_or_none()

                if not user_ability:
                    user_ability = UserAbility(
                        user_id=progress.user_id,
                        ability_id=ability_id
                    )
                    db.add(user_ability)

                if user_ability.correct_count is None:
                    user_ability.correct_count = 0
                if user_ability.total_count is None:
                    user_ability.total_count = 0
                user_ability.correct_count += stats["correct"]
                user_ability.total_count += stats["total"]

                if user_ability.total_count > 0:
                    user_ability.score = user_ability.correct_count / user_ability.total_count * 100

                this_score = 0
                if stats["total"] > 0:
                    this_score = stats["correct"] / stats["total"] * 100

                result_scores.append(AbilityScoreItem(
                    ability_id=ability_id,
                    ability_name=stats["name"],
                    correct_count=stats["correct"],
                    total_count=stats["total"],
                    score=round(this_score, 1)
                ))

            return result_scores
        except Exception as e:
            await db.rollback()
            raise

    @staticmethod
    async def _handle_checkin(
        db: AsyncSession,
        user: User,
        progress: UserProgress
    ) -> Tuple[bool, int]:
        try:
            today = date.today()

            existing = await db.execute(
                select(CheckIn).where(
                    CheckIn.user_id == user.id,
                    CheckIn.check_date == today
                )
            )
            if existing.scalar_one_or_none():
                return False, user.streak_days

            checkin = CheckIn(
                user_id=user.id,
                check_date=today,
                progress_id=progress.id
            )
            db.add(checkin)

            yesterday = today - timedelta(days=1)

            yesterday_result = await db.execute(
                select(CheckIn).where(
                    CheckIn.user_id == user.id,
                    CheckIn.check_date == yesterday
                )
            )

            if yesterday_result.scalar_one_or_none():
                user.streak_days += 1
            else:
                user.streak_days = 1

            if user.streak_days > user.max_streak_days:
                user.max_streak_days = user.streak_days

            return True, user.streak_days
        except Exception as e:
            await db.rollback()
            raise

    @staticmethod
    async def _check_badges(
        db: AsyncSession,
        user: User
    ) -> List[BadgeUnlock]:
        try:
            new_badges = []

            badges_result = await db.execute(select(Badge))
            all_badges = badges_result.scalars().all()

            user_badges_result = await db.execute(
                select(UserBadge.badge_id).where(UserBadge.user_id == user.id)
            )
            owned_badge_ids = set(user_badges_result.scalars().all())

            for badge in all_badges:
                if badge.id in owned_badge_ids:
                    continue

                earned = False

                if badge.condition_type == BadgeConditionTypeEnum.FIRST_READING:
                    earned = user.total_readings >= 1

                elif badge.condition_type == BadgeConditionTypeEnum.STREAK_DAYS:
                    earned = user.streak_days >= badge.condition_value

                elif badge.condition_type == BadgeConditionTypeEnum.TOTAL_READINGS:
                    earned = user.total_readings >= badge.condition_value

                elif badge.condition_type == BadgeConditionTypeEnum.ABILITY_ACCURACY:
                    ability_code = badge.condition_extra

                    ability_result = await db.execute(
                        select(AbilityDimension).where(AbilityDimension.code == ability_code)
                    )
                    ability = ability_result.scalar_one_or_none()

                    if ability:
                        user_ability_result = await db.execute(
                            select(UserAbility).where(
                                UserAbility.user_id == user.id,
                                UserAbility.ability_id == ability.id
                            )
                        )
                        user_ability = user_ability_result.scalar_one_or_none()

                        if user_ability and user_ability.total_count >= 10:
                            earned = user_ability.score >= badge.condition_value

                elif badge.condition_type == BadgeConditionTypeEnum.ABILITY_COUNT:
                    ability_code = badge.condition_extra

                    ability_result = await db.execute(
                        select(AbilityDimension).where(AbilityDimension.code == ability_code)
                    )
                    ability = ability_result.scalar_one_or_none()

                    if ability:
                        user_ability_result = await db.execute(
                            select(UserAbility).where(
                                UserAbility.user_id == user.id,
                                UserAbility.ability_id == ability.id
                            )
                        )
                        user_ability = user_ability_result.scalar_one_or_none()

                        if user_ability:
                            earned = user_ability.correct_count >= badge.condition_value

                if earned:
                    user_badge = UserBadge(
                        user_id=user.id,
                        badge_id=badge.id
                    )
                    db.add(user_badge)

                    new_badges.append(BadgeUnlock(
                        id=badge.id,
                        name=badge.name,
                        description=badge.description,
                        icon_url=badge.icon_url
                    ))

            return new_badges
        except Exception as e:
            await db.rollback()
            raise

    @staticmethod
    async def get_progress_detail(
        db: AsyncSession,
        progress_id: int,
        user_id: int
    ) -> Optional[ProgressWithAnswers]:
        try:
            progress = await db.get(UserProgress, progress_id)
            if not progress or progress.user_id != user_id:
                return None

            article = await db.get(Article, progress.article_id)

            answers_result = await db.execute(
                select(QuestionAnswer)
                .where(QuestionAnswer.progress_id == progress_id)
                .options(selectinload(QuestionAnswer.question))
            )
            answers = answers_result.scalars().all()

            answer_details = [
                AnswerDetail(
                    question_id=ans.question_id,
                    question_content=ans.question.content,
                    question_type=ans.question.type.value,
                    user_answer=ans.user_answer,
                    correct_answer=ans.question.answer,
                    is_correct=ans.is_correct,
                    explanation=ans.question.explanation
                )
                for ans in answers
            ]

            return ProgressWithAnswers(
                id=progress.id,
                article_id=progress.article_id,
                article_title=article.title if article else "",
                score=progress.score,
                correct_count=progress.correct_count,
                total_count=progress.total_count,
                time_spent=progress.time_spent,
                completed_at=progress.completed_at,
                created_at=progress.created_at,
                answers=answer_details
            )
        except Exception as e:
            await db.rollback()
            raise

    @staticmethod
    async def get_history(
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[HistoryItem], int]:
        try:
            count_result = await db.execute(
                select(func.count(UserProgress.id))
                .where(
                    UserProgress.user_id == user_id,
                    UserProgress.completed_at.isnot(None)
                )
            )
            total = count_result.scalar() or 0

            result = await db.execute(
                select(UserProgress)
                .where(
                    UserProgress.user_id == user_id,
                    UserProgress.completed_at.isnot(None)
                )
                .options(selectinload(UserProgress.article))
                .order_by(UserProgress.completed_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            progresses = result.scalars().all()

            items = [
                HistoryItem(
                    id=p.id,
                    article_id=p.article_id,
                    article_title=p.article.title if p.article else "",
                    score=p.score,
                    completed_at=p.completed_at
                )
                for p in progresses
            ]

            return items, total
        except Exception as e:
            await db.rollback()
            raise


progress_service = ProgressService()
