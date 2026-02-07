from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.question import Question, QuestionAbility
from app.models.article import Article
from app.models.ability import AbilityDimension
from app.models.user_ability import UserAbility
from app.schemas.question import QuestionItem, QuestionWithAnswer, AbilityInfo


class QuestionService:
    """题目服务"""
    
    @staticmethod
    async def get_questions_by_article(
        db: AsyncSession,
        article_id: int,
        user_id: Optional[int] = None,
        for_weak_point: bool = False
    ) -> List[QuestionItem]:
        """
        获取文章的题目列表
        
        - for_weak_point=True 时，优先返回针对用户弱项的题目
        """
        query = (
            select(Question)
            .where(Question.article_id == article_id)
            .options(selectinload(Question.abilities).selectinload(QuestionAbility.ability))
            .order_by(Question.display_order)
        )
        
        result = await db.execute(query)
        questions = result.scalars().all()
        
        if for_weak_point and user_id:
            # 获取用户弱项
            weak_result = await db.execute(
                select(UserAbility.ability_id)
                .where(UserAbility.user_id == user_id)
                .order_by(UserAbility.score)
                .limit(3)
            )
            weak_ability_ids = set(weak_result.scalars().all())
            
            # 对题目排序，弱项相关的题目排在前面
            def sort_key(q: Question):
                q_ability_ids = {qa.ability_id for qa in q.abilities}
                overlap = len(q_ability_ids & weak_ability_ids)
                return -overlap  # 重叠越多越靠前
            
            questions = sorted(questions, key=sort_key)
        
        # 转换为响应模型
        items = []
        for q in questions:
            abilities = [
                AbilityInfo(
                    id=qa.ability.id,
                    name=qa.ability.name,
                    code=qa.ability.code
                )
                for qa in q.abilities
            ]
            items.append(QuestionItem(
                id=q.id,
                type=q.type.value,
                content=q.content,
                options=q.options,
                hint=q.hint,
                difficulty=q.difficulty.value,
                abilities=abilities
            ))
        
        return items
    
    @staticmethod
    async def get_question_with_answer(
        db: AsyncSession,
        question_id: int
    ) -> Optional[QuestionWithAnswer]:
        """获取题目详情（含答案）"""
        query = (
            select(Question)
            .where(Question.id == question_id)
            .options(selectinload(Question.abilities).selectinload(QuestionAbility.ability))
        )
        
        result = await db.execute(query)
        question = result.scalar_one_or_none()
        
        if not question:
            return None
        
        abilities = [
            AbilityInfo(
                id=qa.ability.id,
                name=qa.ability.name,
                code=qa.ability.code
            )
            for qa in question.abilities
        ]
        
        return QuestionWithAnswer(
            id=question.id,
            type=question.type.value,
            content=question.content,
            options=question.options,
            hint=question.hint,
            difficulty=question.difficulty.value,
            abilities=abilities,
            answer=question.answer,
            explanation=question.explanation
        )


question_service = QuestionService()
