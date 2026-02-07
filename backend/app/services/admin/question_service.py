from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from sqlalchemy.orm import selectinload

from app.models.question import Question, QuestionAbility, QuestionTypeEnum, DifficultyEnum
from app.models.article import Article
from app.models.ability import AbilityDimension
from app.schemas.admin.question import (
    QuestionCreateRequest,
    QuestionUpdateRequest,
    QuestionAdminResponse,
    QuestionListItemAdmin
)


class AdminQuestionService:
    @staticmethod
    async def get_question_list(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        article_id: Optional[int] = None,
        question_type: Optional[str] = None
    ) -> Tuple[List[QuestionListItemAdmin], int]:
        query = select(Question).options(selectinload(Question.article))

        if article_id:
            query = query.where(Question.article_id == article_id)

        if question_type:
            query = query.where(Question.type == QuestionTypeEnum(question_type))

        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar() or 0

        query = query.order_by(Question.article_id, Question.display_order)
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        questions = result.scalars().all()

        items = []
        for q in questions:
            content = q.content[:50] + "..." if len(q.content) > 50 else q.content
            items.append(QuestionListItemAdmin(
                id=q.id,
                article_id=q.article_id,
                article_title=q.article.title if q.article else "",
                type=q.type,
                content=content,
                difficulty=q.difficulty,
                display_order=q.display_order,
                is_ai_generated=q.is_ai_generated
            ))

        return items, total

    @staticmethod
    async def create_question(
        db: AsyncSession,
        data: QuestionCreateRequest
    ) -> QuestionAdminResponse:
        article = await db.get(Article, data.article_id)
        if not article:
            raise ValueError("文章不存在")

        if data.type == QuestionTypeEnum.CHOICE and not data.options:
            raise ValueError("选择题必须提供选项")

        question = Question(
            article_id=data.article_id,
            type=QuestionTypeEnum(data.type.value) if isinstance(data.type, QuestionTypeEnum) else QuestionTypeEnum(data.type),
            content=data.content,
            options=data.options,
            answer=data.answer,
            explanation=data.explanation,
            hint=data.hint,
            difficulty=DifficultyEnum(data.difficulty.value) if isinstance(data.difficulty, DifficultyEnum) else DifficultyEnum(data.difficulty),
            display_order=data.display_order
        )
        db.add(question)
        await db.flush()

        for ability_weight in data.abilities:
            qa = QuestionAbility(
                question_id=question.id,
                ability_id=ability_weight.ability_id,
                weight=ability_weight.weight
            )
            db.add(qa)

        await db.commit()
        await db.refresh(question)

        return await AdminQuestionService.get_question_detail(db, question.id)

    @staticmethod
    async def get_question_detail(
        db: AsyncSession,
        question_id: int
    ) -> Optional[QuestionAdminResponse]:
        query = (
            select(Question)
            .where(Question.id == question_id)
            .options(
                selectinload(Question.article),
                selectinload(Question.abilities).selectinload(QuestionAbility.ability)
            )
        )
        result = await db.execute(query)
        question = result.scalar_one_or_none()

        if not question:
            return None

        abilities = [
            {
                "id": qa.ability.id,
                "name": qa.ability.name,
                "code": qa.ability.code,
                "weight": qa.weight
            }
            for qa in question.abilities
        ]

        return QuestionAdminResponse(
            id=question.id,
            article_id=question.article_id,
            article_title=question.article.title if question.article else "",
            type=question.type,
            content=question.content,
            options=question.options,
            answer=question.answer,
            explanation=question.explanation,
            hint=question.hint,
            difficulty=question.difficulty,
            display_order=question.display_order,
            is_ai_generated=question.is_ai_generated,
            created_at=question.created_at,
            updated_at=question.updated_at,
            abilities=abilities
        )

    @staticmethod
    async def update_question(
        db: AsyncSession,
        question_id: int,
        data: QuestionUpdateRequest
    ) -> Optional[QuestionAdminResponse]:
        question = await db.get(Question, question_id)
        if not question:
            return None

        update_data = data.model_dump(exclude_unset=True, exclude={"abilities"})
        for field, value in update_data.items():
            setattr(question, field, value)

        if data.abilities is not None:
            await db.execute(
                delete(QuestionAbility).where(QuestionAbility.question_id == question_id)
            )
            for ability_weight in data.abilities:
                qa = QuestionAbility(
                    question_id=question_id,
                    ability_id=ability_weight.ability_id,
                    weight=ability_weight.weight
                )
                db.add(qa)

        await db.commit()

        return await AdminQuestionService.get_question_detail(db, question_id)

    @staticmethod
    async def delete_question(db: AsyncSession, question_id: int) -> bool:
        question = await db.get(Question, question_id)
        if not question:
            return False

        await db.delete(question)
        await db.commit()
        return True


admin_question_service = AdminQuestionService()
