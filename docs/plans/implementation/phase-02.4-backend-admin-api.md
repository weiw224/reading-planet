# Phase 2.4: 后端 API 开发 - 管理后台 API

> **预估工时**: 3-4 人天  
> **前置依赖**: Phase 2.3 (学习进度模块)  
> **本文件范围**: 文章管理、题目管理、用户管理、系统配置

---

## 2.4.1 目标概述

本阶段完成管理后台 API，包括：
- 文章 CRUD（创建、编辑、删除、发布）
- 题目 CRUD（创建、编辑、关联能力维度）
- 用户列表与统计
- 标签/勋章/能力维度配置

---

## 2.4.2 API 接口清单

```
/api/v1/admin
├── /articles                    # 文章管理
│   ├── GET /                    # 文章列表（含草稿）
│   ├── POST /                   # 创建文章
│   ├── GET /{id}                # 获取文章详情
│   ├── PUT /{id}                # 更新文章
│   ├── DELETE /{id}             # 删除文章
│   ├── POST /{id}/publish       # 发布文章
│   └── POST /{id}/archive       # 归档文章
│
├── /questions                   # 题目管理
│   ├── GET /                    # 题目列表
│   ├── POST /                   # 创建题目
│   ├── GET /{id}                # 获取题目详情
│   ├── PUT /{id}                # 更新题目
│   └── DELETE /{id}             # 删除题目
│
├── /users                       # 用户管理
│   ├── GET /                    # 用户列表
│   ├── GET /{id}                # 用户详情
│   └── GET /stats               # 整体统计
│
├── /tags                        # 标签管理
│   ├── GET /                    # 标签列表
│   ├── POST /                   # 创建标签
│   ├── PUT /{id}                # 更新标签
│   └── DELETE /{id}             # 删除标签
│
├── /badges                      # 勋章管理
│   ├── GET /                    # 勋章列表
│   ├── POST /                   # 创建勋章
│   ├── PUT /{id}                # 更新勋章
│   └── DELETE /{id}             # 删除勋章
│
└── /dashboard                   # 仪表盘
    └── GET /                    # 获取统计数据
```

---

## 2.4.3 管理员文章模型 (schemas/admin/article.py)

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ArticleStatusEnum(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class DifficultyEnum(int, Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3


class ArticleCreateRequest(BaseModel):
    """创建文章请求"""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=10)
    source_book: Optional[str] = None
    source_chapter: Optional[str] = None
    is_excerpt: bool = False
    article_difficulty: DifficultyEnum = DifficultyEnum.MEDIUM
    tag_ids: List[int] = []  # 关联的标签ID


class ArticleUpdateRequest(BaseModel):
    """更新文章请求"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=10)
    source_book: Optional[str] = None
    source_chapter: Optional[str] = None
    is_excerpt: Optional[bool] = None
    article_difficulty: Optional[DifficultyEnum] = None
    tag_ids: Optional[List[int]] = None
    status: Optional[ArticleStatusEnum] = None


class ArticleAdminResponse(BaseModel):
    """文章详情响应（管理端）"""
    id: int
    title: str
    content: str
    source_book: Optional[str]
    source_chapter: Optional[str]
    is_excerpt: bool
    word_count: int
    reading_time: int
    article_difficulty: DifficultyEnum
    status: ArticleStatusEnum
    is_ai_generated: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int]
    tags: List[dict] = []
    question_count: int = 0
    
    class Config:
        from_attributes = True


class ArticleListItemAdmin(BaseModel):
    """文章列表项（管理端）"""
    id: int
    title: str
    source_book: Optional[str]
    word_count: int
    article_difficulty: DifficultyEnum
    status: ArticleStatusEnum
    is_ai_generated: bool
    question_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ArticleListResponseAdmin(BaseModel):
    """文章列表响应（管理端）"""
    items: List[ArticleListItemAdmin]
    total: int
    page: int
    page_size: int
```

---

## 2.4.4 管理员题目模型 (schemas/admin/question.py)

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class QuestionTypeEnum(str, Enum):
    CHOICE = "choice"
    JUDGE = "judge"
    FILL = "fill"
    SHORT_ANSWER = "short_answer"


class DifficultyEnum(int, Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3


class AbilityWeight(BaseModel):
    """能力权重"""
    ability_id: int
    weight: int = Field(1, ge=1, le=10)


class QuestionCreateRequest(BaseModel):
    """创建题目请求"""
    article_id: int
    type: QuestionTypeEnum
    content: str = Field(..., min_length=1)
    options: Optional[List[str]] = None  # 选择题必填
    answer: str = Field(..., min_length=1)
    explanation: Optional[str] = None
    hint: Optional[str] = None
    difficulty: DifficultyEnum = DifficultyEnum.MEDIUM
    display_order: int = 0
    abilities: List[AbilityWeight] = []  # 关联的能力维度


class QuestionUpdateRequest(BaseModel):
    """更新题目请求"""
    type: Optional[QuestionTypeEnum] = None
    content: Optional[str] = None
    options: Optional[List[str]] = None
    answer: Optional[str] = None
    explanation: Optional[str] = None
    hint: Optional[str] = None
    difficulty: Optional[DifficultyEnum] = None
    display_order: Optional[int] = None
    abilities: Optional[List[AbilityWeight]] = None


class QuestionAdminResponse(BaseModel):
    """题目详情响应（管理端）"""
    id: int
    article_id: int
    article_title: str
    type: QuestionTypeEnum
    content: str
    options: Optional[List[str]]
    answer: str
    explanation: Optional[str]
    hint: Optional[str]
    difficulty: DifficultyEnum
    display_order: int
    is_ai_generated: bool
    created_at: datetime
    updated_at: datetime
    abilities: List[dict] = []
    
    class Config:
        from_attributes = True


class QuestionListItemAdmin(BaseModel):
    """题目列表项（管理端）"""
    id: int
    article_id: int
    article_title: str
    type: QuestionTypeEnum
    content: str  # 截取前50字符
    difficulty: DifficultyEnum
    display_order: int
    is_ai_generated: bool
    
    class Config:
        from_attributes = True
```

---

## 2.4.5 管理员用户模型 (schemas/admin/user.py)

```python
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class UserAdminResponse(BaseModel):
    """用户详情响应（管理端）"""
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
    """用户列表项（管理端）"""
    id: int
    nickname: Optional[str]
    grade: Optional[str]
    total_readings: int
    streak_days: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserListResponseAdmin(BaseModel):
    """用户列表响应"""
    items: List[UserListItemAdmin]
    total: int
    page: int
    page_size: int


class DashboardStats(BaseModel):
    """仪表盘统计数据"""
    total_users: int
    active_users_today: int
    active_users_week: int
    total_articles: int
    published_articles: int
    total_questions: int
    total_readings: int
    checkins_today: int
```

---

## 2.4.6 管理员文章服务 (services/admin/article_service.py)

```python
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
    """管理员文章服务"""
    
    @staticmethod
    def _calculate_reading_time(word_count: int) -> int:
        """计算预计阅读时间（分钟）"""
        # 假设阅读速度 300字/分钟
        return max(1, word_count // 300)
    
    @staticmethod
    async def get_article_list(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> Tuple[List[ArticleListItemAdmin], int]:
        """获取文章列表（管理端）"""
        query = select(Article)
        
        if status:
            query = query.where(Article.status == ArticleStatusEnum(status))
        
        if keyword:
            query = query.where(Article.title.ilike(f"%{keyword}%"))
        
        # 统计总数
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar() or 0
        
        # 分页查询
        query = query.order_by(Article.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await db.execute(query)
        articles = result.scalars().all()
        
        # 获取题目数量
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
        """创建文章"""
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
            article_difficulty=data.article_difficulty,
            status=ArticleStatusEnum.DRAFT,
            created_by=admin_id
        )
        db.add(article)
        await db.flush()
        
        # 添加标签关联
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
        """获取文章详情"""
        query = (
            select(Article)
            .where(Article.id == article_id)
            .options(selectinload(Article.tags).selectinload(ArticleTag.tag))
        )
        result = await db.execute(query)
        article = result.scalar_one_or_none()
        
        if not article:
            return None
        
        # 获取题目数量
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
        """更新文章"""
        article = await db.get(Article, article_id)
        if not article:
            return None
        
        update_data = data.model_dump(exclude_unset=True, exclude={"tag_ids"})
        
        for field, value in update_data.items():
            setattr(article, field, value)
        
        # 如果更新了内容，重新计算字数和阅读时间
        if data.content:
            article.word_count = len(data.content)
            article.reading_time = AdminArticleService._calculate_reading_time(article.word_count)
        
        # 更新标签
        if data.tag_ids is not None:
            # 删除旧的关联
            await db.execute(
                delete(ArticleTag).where(ArticleTag.article_id == article_id)
            )
            # 添加新的关联
            for tag_id in data.tag_ids:
                article_tag = ArticleTag(article_id=article_id, tag_id=tag_id)
                db.add(article_tag)
        
        await db.commit()
        
        return await AdminArticleService.get_article_detail(db, article_id)
    
    @staticmethod
    async def delete_article(db: AsyncSession, article_id: int) -> bool:
        """删除文章"""
        article = await db.get(Article, article_id)
        if not article:
            return False
        
        await db.delete(article)
        await db.commit()
        return True
    
    @staticmethod
    async def publish_article(db: AsyncSession, article_id: int) -> bool:
        """发布文章"""
        article = await db.get(Article, article_id)
        if not article:
            return False
        
        article.status = ArticleStatusEnum.PUBLISHED
        await db.commit()
        return True
    
    @staticmethod
    async def archive_article(db: AsyncSession, article_id: int) -> bool:
        """归档文章"""
        article = await db.get(Article, article_id)
        if not article:
            return False
        
        article.status = ArticleStatusEnum.ARCHIVED
        await db.commit()
        return True


admin_article_service = AdminArticleService()
```

---

## 2.4.7 管理员题目服务 (services/admin/question_service.py)

```python
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
    """管理员题目服务"""
    
    @staticmethod
    async def get_question_list(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        article_id: Optional[int] = None,
        question_type: Optional[str] = None
    ) -> Tuple[List[QuestionListItemAdmin], int]:
        """获取题目列表"""
        query = select(Question).options(selectinload(Question.article))
        
        if article_id:
            query = query.where(Question.article_id == article_id)
        
        if question_type:
            query = query.where(Question.type == QuestionTypeEnum(question_type))
        
        # 统计总数
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar() or 0
        
        # 分页
        query = query.order_by(Question.article_id, Question.display_order)
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await db.execute(query)
        questions = result.scalars().all()
        
        items = []
        for q in questions:
            items.append(QuestionListItemAdmin(
                id=q.id,
                article_id=q.article_id,
                article_title=q.article.title if q.article else "",
                type=q.type,
                content=q.content[:50] + "..." if len(q.content) > 50 else q.content,
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
        """创建题目"""
        # 验证文章存在
        article = await db.get(Article, data.article_id)
        if not article:
            raise ValueError("文章不存在")
        
        # 验证选择题有选项
        if data.type == QuestionTypeEnum.CHOICE and not data.options:
            raise ValueError("选择题必须提供选项")
        
        question = Question(
            article_id=data.article_id,
            type=data.type,
            content=data.content,
            options=data.options,
            answer=data.answer,
            explanation=data.explanation,
            hint=data.hint,
            difficulty=data.difficulty,
            display_order=data.display_order
        )
        db.add(question)
        await db.flush()
        
        # 添加能力维度关联
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
        """获取题目详情"""
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
        """更新题目"""
        question = await db.get(Question, question_id)
        if not question:
            return None
        
        update_data = data.model_dump(exclude_unset=True, exclude={"abilities"})
        for field, value in update_data.items():
            setattr(question, field, value)
        
        # 更新能力维度关联
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
        """删除题目"""
        question = await db.get(Question, question_id)
        if not question:
            return False
        
        await db.delete(question)
        await db.commit()
        return True


admin_question_service = AdminQuestionService()
```

---

## 2.4.8 仪表盘服务 (services/admin/dashboard_service.py)

```python
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
    """仪表盘服务"""
    
    @staticmethod
    async def get_stats(db: AsyncSession) -> DashboardStats:
        """获取仪表盘统计数据"""
        today = date.today()
        week_ago = today - timedelta(days=7)
        
        # 总用户数
        total_users = (await db.execute(
            select(func.count(User.id))
        )).scalar() or 0
        
        # 今日活跃用户（今日有打卡或阅读记录）
        active_today = (await db.execute(
            select(func.count(func.distinct(UserProgress.user_id)))
            .where(func.date(UserProgress.created_at) == today)
        )).scalar() or 0
        
        # 本周活跃用户
        active_week = (await db.execute(
            select(func.count(func.distinct(UserProgress.user_id)))
            .where(func.date(UserProgress.created_at) >= week_ago)
        )).scalar() or 0
        
        # 文章统计
        total_articles = (await db.execute(
            select(func.count(Article.id))
        )).scalar() or 0
        
        published_articles = (await db.execute(
            select(func.count(Article.id))
            .where(Article.status == ArticleStatusEnum.PUBLISHED)
        )).scalar() or 0
        
        # 题目总数
        total_questions = (await db.execute(
            select(func.count(Question.id))
        )).scalar() or 0
        
        # 总阅读量
        total_readings = (await db.execute(
            select(func.count(UserProgress.id))
            .where(UserProgress.completed_at.isnot(None))
        )).scalar() or 0
        
        # 今日打卡数
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
```

---

## 2.4.9 管理后台路由 (api/v1/admin/__init__.py)

```python
from fastapi import APIRouter
from app.api.v1.admin import articles, questions, users, tags, badges, dashboard

router = APIRouter()

router.include_router(articles.router, prefix="/articles", tags=["管理-文章"])
router.include_router(questions.router, prefix="/questions", tags=["管理-题目"])
router.include_router(users.router, prefix="/users", tags=["管理-用户"])
router.include_router(tags.router, prefix="/tags", tags=["管理-标签"])
router.include_router(badges.router, prefix="/badges", tags=["管理-勋章"])
router.include_router(dashboard.router, prefix="/dashboard", tags=["管理-仪表盘"])
```

---

## 2.4.10 文章管理路由 (api/v1/admin/articles.py)

```python
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.api.deps import get_admin_user
from app.schemas.common import ResponseModel
from app.schemas.admin.article import (
    ArticleCreateRequest,
    ArticleUpdateRequest,
    ArticleAdminResponse,
    ArticleListResponseAdmin
)
from app.services.admin.article_service import admin_article_service

router = APIRouter()


@router.get("/", response_model=ResponseModel[ArticleListResponseAdmin])
async def get_article_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    """获取文章列表（管理端）"""
    items, total = await admin_article_service.get_article_list(
        db, page, page_size, status, keyword
    )
    
    return ResponseModel(data=ArticleListResponseAdmin(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    ))


@router.post("/", response_model=ResponseModel[ArticleAdminResponse])
async def create_article(
    data: ArticleCreateRequest,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    """创建文章"""
    result = await admin_article_service.create_article(db, data)
    return ResponseModel(data=result)


@router.get("/{article_id}", response_model=ResponseModel[ArticleAdminResponse])
async def get_article_detail(
    article_id: int,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    """获取文章详情"""
    result = await admin_article_service.get_article_detail(db, article_id)
    if not result:
        raise HTTPException(status_code=404, detail="文章不存在")
    return ResponseModel(data=result)


@router.put("/{article_id}", response_model=ResponseModel[ArticleAdminResponse])
async def update_article(
    article_id: int,
    data: ArticleUpdateRequest,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    """更新文章"""
    result = await admin_article_service.update_article(db, article_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="文章不存在")
    return ResponseModel(data=result)


@router.delete("/{article_id}", response_model=ResponseModel)
async def delete_article(
    article_id: int,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    """删除文章"""
    success = await admin_article_service.delete_article(db, article_id)
    if not success:
        raise HTTPException(status_code=404, detail="文章不存在")
    return ResponseModel(message="删除成功")


@router.post("/{article_id}/publish", response_model=ResponseModel)
async def publish_article(
    article_id: int,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    """发布文章"""
    success = await admin_article_service.publish_article(db, article_id)
    if not success:
        raise HTTPException(status_code=404, detail="文章不存在")
    return ResponseModel(message="发布成功")


@router.post("/{article_id}/archive", response_model=ResponseModel)
async def archive_article(
    article_id: int,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    """归档文章"""
    success = await admin_article_service.archive_article(db, article_id)
    if not success:
        raise HTTPException(status_code=404, detail="文章不存在")
    return ResponseModel(message="归档成功")
```

---

## 2.4.11 仪表盘路由 (api/v1/admin/dashboard.py)

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_admin_user
from app.schemas.common import ResponseModel
from app.schemas.admin.user import DashboardStats
from app.services.admin.dashboard_service import dashboard_service

router = APIRouter()


@router.get("/", response_model=ResponseModel[DashboardStats])
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    """获取仪表盘统计数据"""
    stats = await dashboard_service.get_stats(db)
    return ResponseModel(data=stats)
```

---

## 2.4.12 验收标准

### 文章管理验收

- [ ] `GET /api/v1/admin/articles/` 返回文章列表含草稿
- [ ] `POST /api/v1/admin/articles/` 创建文章成功
- [ ] `PUT /api/v1/admin/articles/{id}` 更新文章成功
- [ ] `DELETE /api/v1/admin/articles/{id}` 删除文章成功
- [ ] `POST /api/v1/admin/articles/{id}/publish` 发布文章成功
- [ ] 所有接口需要管理员权限

### 题目管理验收

- [ ] 题目 CRUD 接口正常工作
- [ ] 能力维度关联正确保存
- [ ] 选择题必须有选项

### 仪表盘验收

- [ ] 返回正确的统计数据
- [ ] 今日/本周活跃用户统计正确

---

## 2.4.13 单元测试

```python
import pytest
from httpx import AsyncClient
from app.main import app
from app.utils.security import create_access_token


def get_admin_token() -> str:
    return create_access_token({"sub": "admin", "role": "admin"})


@pytest.mark.asyncio
async def test_admin_require_auth():
    """测试管理接口需要认证"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/admin/articles/")
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_article():
    """测试创建文章"""
    token = get_admin_token()
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/admin/articles/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "测试文章",
                "content": "这是测试内容" * 10,
                "article_difficulty": 1,
                "tag_ids": []
            }
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["title"] == "测试文章"
    assert data["data"]["status"] == "draft"


@pytest.mark.asyncio
async def test_dashboard():
    """测试仪表盘"""
    token = get_admin_token()
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/admin/dashboard/",
            headers={"Authorization": f"Bearer {token}"}
        )
    
    assert response.status_code == 200
    data = response.json()["data"]
    assert "total_users" in data
    assert "total_articles" in data
```

---

## 2.4.14 交付物清单

| 交付物 | 文件路径 | 验收标准 |
|--------|----------|----------|
| 文章管理模型 | `app/schemas/admin/article.py` | 请求/响应模型 |
| 题目管理模型 | `app/schemas/admin/question.py` | 请求/响应模型 |
| 用户管理模型 | `app/schemas/admin/user.py` | 请求/响应模型 |
| 文章管理服务 | `app/services/admin/article_service.py` | CRUD逻辑 |
| 题目管理服务 | `app/services/admin/question_service.py` | CRUD逻辑 |
| 仪表盘服务 | `app/services/admin/dashboard_service.py` | 统计逻辑 |
| 管理路由入口 | `app/api/v1/admin/__init__.py` | 路由注册 |
| 文章管理路由 | `app/api/v1/admin/articles.py` | 7个接口 |
| 题目管理路由 | `app/api/v1/admin/questions.py` | 5个接口 |
| 仪表盘路由 | `app/api/v1/admin/dashboard.py` | 1个接口 |
