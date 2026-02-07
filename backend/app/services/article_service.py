from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
import random
from datetime import date

from app.models.article import Article, ArticleTag, ArticleStatusEnum, DifficultyEnum
from app.models.tag import Tag, TagCategoryEnum
from app.models.question import Question
from app.models.user import User
from app.models.progress import UserProgress
from app.models.user_ability import UserAbility
from app.models.ability import AbilityDimension
from app.schemas.article import ArticleListItem, ArticleDetail, TagInfo


class ArticleService:
    
    @staticmethod
    async def get_article_list(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        grade: Optional[str] = None,
        genre: Optional[str] = None,
        difficulty: Optional[int] = None,
        source: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> Tuple[List[ArticleListItem], int]:
        query = select(Article).where(Article.status == ArticleStatusEnum.PUBLISHED)
        
        if keyword:
            query = query.where(
                or_(
                    Article.title.ilike(f"%{keyword}%"),
                    Article.source_book.ilike(f"%{keyword}%")
                )
            )
        
        if difficulty:
            query = query.where(Article.article_difficulty == DifficultyEnum(difficulty))
        
        tag_filters = []
        if grade:
            tag_filters.append(("grade", grade))
        if genre:
            tag_filters.append(("genre", genre))
        if source:
            tag_filters.append(("source", source))
        
        if tag_filters:
            for category, tag_name in tag_filters:
                subquery = (
                    select(ArticleTag.article_id)
                    .join(Tag)
                    .where(
                        Tag.category == TagCategoryEnum(category),
                        Tag.name == tag_name
                    )
                )
                query = query.where(Article.id.in_(subquery))
        
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        query = query.offset((page - 1) * page_size).limit(page_size)
        query = query.options(selectinload(Article.tags).selectinload(ArticleTag.tag))
        
        result = await db.execute(query)
        articles = result.scalars().all()
        
        items = []
        for article in articles:
            tags = [
                TagInfo(id=at.tag.id, name=at.tag.name, category=at.tag.category.value)
                for at in article.tags
            ]
            items.append(ArticleListItem(
                id=article.id,
                title=article.title,
                source_book=article.source_book,
                word_count=article.word_count,
                reading_time=article.reading_time,
                article_difficulty=article.article_difficulty,
                tags=tags
            ))
        
        return items, total
    
    @staticmethod
    async def get_article_detail(db: AsyncSession, article_id: int) -> Optional[ArticleDetail]:
        query = (
            select(Article)
            .where(Article.id == article_id, Article.status == ArticleStatusEnum.PUBLISHED)
            .options(selectinload(Article.tags).selectinload(ArticleTag.tag))
        )
        result = await db.execute(query)
        article = result.scalar_one_or_none()
        
        if not article:
            return None
        
        question_count_result = await db.execute(
            select(func.count(Question.id)).where(Question.article_id == article_id)
        )
        question_count = question_count_result.scalar() or 0
        
        tags = [
            TagInfo(id=at.tag.id, name=at.tag.name, category=at.tag.category.value)
            for at in article.tags
        ]
        
        return ArticleDetail(
            id=article.id,
            title=article.title,
            content=article.content,
            source_book=article.source_book,
            source_chapter=article.source_chapter,
            is_excerpt=article.is_excerpt,
            word_count=article.word_count,
            reading_time=article.reading_time,
            article_difficulty=article.article_difficulty,
            tags=tags,
            question_count=question_count
        )
    
    @staticmethod
    async def get_today_recommendation(
        db: AsyncSession, 
        user: User
    ) -> Optional[ArticleDetail]:
        if not user.grade:
            query = (
                select(Article)
                .where(
                    Article.status == ArticleStatusEnum.PUBLISHED,
                    Article.article_difficulty == DifficultyEnum.EASY
                )
            )
        else:
            grade_name = f"{user.grade.value}年级"
            
            query = (
                select(Article)
                .where(Article.status == ArticleStatusEnum.PUBLISHED)
                .join(ArticleTag)
                .join(Tag)
                .where(
                    Tag.category == TagCategoryEnum.GRADE,
                    Tag.name == grade_name
                )
            )
        
        today = date.today()
        read_today_subquery = (
            select(UserProgress.article_id)
            .where(
                UserProgress.user_id == user.id,
                func.date(UserProgress.created_at) == today
            )
        )
        query = query.where(Article.id.notin_(read_today_subquery))
        
        result = await db.execute(query)
        candidates = result.scalars().all()
        
        if not candidates:
            all_query = (
                select(Article)
                .where(Article.status == ArticleStatusEnum.PUBLISHED)
                .limit(50)
            )
            result = await db.execute(all_query)
            candidates = result.scalars().all()
        
        if not candidates:
            return None
        
        selected = random.choice(candidates)
        return await ArticleService.get_article_detail(db, selected.id)
    
    @staticmethod
    async def get_weak_point_recommendation(
        db: AsyncSession,
        user: User
    ) -> Optional[ArticleDetail]:
        ability_result = await db.execute(
            select(UserAbility)
            .where(UserAbility.user_id == user.id)
            .order_by(UserAbility.score)
            .limit(3)
        )
        weak_abilities = ability_result.scalars().all()
        
        if not weak_abilities:
            return await ArticleService.get_today_recommendation(db, user)
        
        weak_ability_ids = [wa.ability_id for wa in weak_abilities]
        
        from app.models.question import QuestionAbility
        
        query = (
            select(Article)
            .where(Article.status == ArticleStatusEnum.PUBLISHED)
            .join(Question)
            .join(QuestionAbility)
            .where(QuestionAbility.ability_id.in_(weak_ability_ids))
            .distinct()
        )
        
        read_subquery = select(UserProgress.article_id).where(UserProgress.user_id == user.id)
        query = query.where(Article.id.notin_(read_subquery))
        
        result = await db.execute(query)
        candidates = result.scalars().all()
        
        if not candidates:
            query_with_read = (
                select(Article)
                .where(Article.status == ArticleStatusEnum.PUBLISHED)
                .join(Question)
                .join(QuestionAbility)
                .where(QuestionAbility.ability_id.in_(weak_ability_ids))
                .distinct()
                .limit(20)
            )
            result = await db.execute(query_with_read)
            candidates = result.scalars().all()
        
        if not candidates:
            return await ArticleService.get_today_recommendation(db, user)
        
        selected = random.choice(candidates)
        return await ArticleService.get_article_detail(db, selected.id)


article_service = ArticleService()
