from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from sqlalchemy.orm import selectinload

from app.models.article import Article, ArticleTag, ArticleStatusEnum, DifficultyEnum
from app.models.tag import Tag
from app.models.question import Question
from app.schemas.admin.article import (
    ArticleCreateRequest,
    ArticleUpdateRequest,
    ArticleAdminResponse,
    ArticleListItemAdmin
)


class AdminArticleService:
    @staticmethod
    def _calculate_reading_time(word_count: int) -> int:
        return max(1, word_count // 300)

    @staticmethod
    async def get_article_list(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> Tuple[List[ArticleListItemAdmin], int]:
        query = select(Article)

        if status:
            query = query.where(Article.status == ArticleStatusEnum(status))

        if keyword:
            query = query.where(Article.title.ilike(f"%{keyword}%"))

        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar() or 0

        query = query.order_by(Article.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        articles = result.scalars().all()

        items = []
        for article in articles:
            q_count = (await db.execute(
                select(func.count(Question.id)).where(Question.article_id == article.id)
            )).scalar() or 0

            items.append(ArticleListItemAdmin(
                id=article.id,
                title=article.title,
                source_book=article.source_book,
                word_count=article.word_count,
                article_difficulty=article.article_difficulty,
                status=article.status,
                is_ai_generated=article.is_ai_generated,
                question_count=q_count,
                created_at=article.created_at
            ))

        return items, total

    @staticmethod
    async def create_article(
        db: AsyncSession,
        data: ArticleCreateRequest,
        admin_id: Optional[int] = None
    ) -> ArticleAdminResponse:
        word_count = len(data.content)
        reading_time = AdminArticleService._calculate_reading_time(word_count)

        article = Article(
            title=data.title,
            content=data.content,
            source_book=data.source_book,
            source_chapter=data.source_chapter,
            is_excerpt=data.is_excerpt,
            word_count=word_count,
            reading_time=reading_time,
            article_difficulty=DifficultyEnum(data.article_difficulty.value) if isinstance(data.article_difficulty, DifficultyEnum) else DifficultyEnum(data.article_difficulty),
            status=ArticleStatusEnum.DRAFT,
            created_by=admin_id
        )
        db.add(article)
        await db.flush()

        for tag_id in data.tag_ids:
            article_tag = ArticleTag(article_id=article.id, tag_id=tag_id)
            db.add(article_tag)

        await db.commit()
        await db.refresh(article)

        return await AdminArticleService.get_article_detail(db, article.id)

    @staticmethod
    async def get_article_detail(
        db: AsyncSession,
        article_id: int
    ) -> Optional[ArticleAdminResponse]:
        query = (
            select(Article)
            .where(Article.id == article_id)
            .options(selectinload(Article.tags).selectinload(ArticleTag.tag))
        )
        result = await db.execute(query)
        article = result.scalar_one_or_none()

        if not article:
            return None

        q_count = (await db.execute(
            select(func.count(Question.id)).where(Question.article_id == article_id)
        )).scalar() or 0

        tags = [
            {"id": at.tag.id, "name": at.tag.name, "category": at.tag.category.value}
            for at in article.tags
        ]

        return ArticleAdminResponse(
            id=article.id,
            title=article.title,
            content=article.content,
            source_book=article.source_book,
            source_chapter=article.source_chapter,
            is_excerpt=article.is_excerpt,
            word_count=article.word_count,
            reading_time=article.reading_time,
            article_difficulty=article.article_difficulty,
            status=article.status,
            is_ai_generated=article.is_ai_generated,
            created_at=article.created_at,
            updated_at=article.updated_at,
            created_by=article.created_by,
            tags=tags,
            question_count=q_count
        )

    @staticmethod
    async def update_article(
        db: AsyncSession,
        article_id: int,
        data: ArticleUpdateRequest
    ) -> Optional[ArticleAdminResponse]:
        article = await db.get(Article, article_id)
        if not article:
            return None

        update_data = data.model_dump(exclude_unset=True, exclude={"tag_ids"})

        for field, value in update_data.items():
            setattr(article, field, value)

        if data.content:
            article.word_count = len(data.content)
            article.reading_time = AdminArticleService._calculate_reading_time(article.word_count)

        if data.tag_ids is not None:
            await db.execute(
                delete(ArticleTag).where(ArticleTag.article_id == article_id)
            )
            for tag_id in data.tag_ids:
                article_tag = ArticleTag(article_id=article_id, tag_id=tag_id)
                db.add(article_tag)

        await db.commit()

        return await AdminArticleService.get_article_detail(db, article_id)

    @staticmethod
    async def delete_article(db: AsyncSession, article_id: int) -> bool:
        article = await db.get(Article, article_id)
        if not article:
            return False

        await db.delete(article)
        await db.commit()
        return True

    @staticmethod
    async def publish_article(db: AsyncSession, article_id: int) -> bool:
        article = await db.get(Article, article_id)
        if not article:
            return False

        article.status = ArticleStatusEnum.PUBLISHED
        await db.commit()
        return True

    @staticmethod
    async def archive_article(db: AsyncSession, article_id: int) -> bool:
        article = await db.get(Article, article_id)
        if not article:
            return False

        article.status = ArticleStatusEnum.ARCHIVED
        await db.commit()
        return True


admin_article_service = AdminArticleService()
