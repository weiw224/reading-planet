from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.question import Question, QuestionAbility
from app.schemas.question import QuestionItem


class QuestionService:
    
    @staticmethod
    async def get_questions_by_article(
        db: AsyncSession,
        article_id: int,
        user_id: int,
        for_weak_point: bool = False
    ) -> List[QuestionItem]:
        query = (
            select(Question)
            .where(Question.article_id == article_id)
            .order_by(Question.display_order, Question.id)
            .options(selectinload(Question.abilities).selectinload(QuestionAbility.ability))
        )
        result = await db.execute(query)
        questions = result.scalars().all()
        
        return [
            QuestionItem(
                id=q.id,
                type=q.type.value,
                content=q.content,
                options=q.options,
                answer=q.answer,
                explanation=q.explanation,
                hint=q.hint,
                difficulty=q.difficulty.value,
                display_order=q.display_order
            )
            for q in questions
        ]


question_service = QuestionService()
