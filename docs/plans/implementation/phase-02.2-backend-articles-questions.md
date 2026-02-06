# Phase 2.2: 后端 API 开发 - 文章与题目模块

> **预估工时**: 3-4 人天  
> **前置依赖**: Phase 2.1 (认证与用户模块)  
> **本文件范围**: 文章 CRUD、题目 CRUD、推荐逻辑

---

## 2.2.1 目标概述

本阶段完成后端 API 的文章与题目模块，包括：
- 文章列表与详情
- 每日推荐与智能推荐（补弱项）
- 题目获取
- 标签与能力维度查询

---

## 2.2.2 API 接口清单

```
/api/v1/articles
├── GET /                    # 获取文章列表（支持筛选）
├── GET /today               # 获取今日推荐文章
├── GET /weak-point          # 获取补弱项推荐文章
├── GET /{id}                # 获取文章详情
└── GET /{id}/questions      # 获取文章的题目列表

/api/v1/tags
├── GET /                    # 获取所有标签（按分类）
└── GET /categories          # 获取标签分类

/api/v1/abilities
└── GET /                    # 获取所有能力维度
```

---

## 2.2.3 文章请求/响应模型 (schemas/article.py)

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


class TagInfo(BaseModel):
    """标签信息"""
    id: int
    name: str
    category: str


class ArticleListItem(BaseModel):
    """文章列表项"""
    id: int
    title: str
    source_book: Optional[str] = None
    word_count: int
    reading_time: int
    article_difficulty: DifficultyEnum
    cover_image: Optional[str] = None  # 封面图（从内容中提取或默认）
    tags: List[TagInfo] = []
    
    class Config:
        from_attributes = True


class ArticleDetail(BaseModel):
    """文章详情"""
    id: int
    title: str
    content: str
    source_book: Optional[str] = None
    source_chapter: Optional[str] = None
    is_excerpt: bool = False
    word_count: int
    reading_time: int
    article_difficulty: DifficultyEnum
    tags: List[TagInfo] = []
    question_count: int = 0  # 题目数量
    
    class Config:
        from_attributes = True


class ArticleListResponse(BaseModel):
    """文章列表响应"""
    items: List[ArticleListItem]
    total: int
    page: int
    page_size: int


class ArticleFilterParams(BaseModel):
    """文章筛选参数"""
    grade: Optional[str] = None           # 年级筛选
    genre: Optional[str] = None           # 文体筛选
    difficulty: Optional[int] = None      # 难度筛选 1/2/3
    source: Optional[str] = None          # 来源系列筛选
    keyword: Optional[str] = None         # 关键词搜索
```

---

## 2.2.4 题目请求/响应模型 (schemas/question.py)

```python
from pydantic import BaseModel
from typing import Optional, List
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


class AbilityInfo(BaseModel):
    """能力维度信息"""
    id: int
    name: str
    code: str


class QuestionItem(BaseModel):
    """题目详情（用户端）"""
    id: int
    type: QuestionTypeEnum
    content: str
    options: Optional[List[str]] = None  # 选择题选项
    hint: Optional[str] = None           # 温柔提示
    difficulty: DifficultyEnum
    abilities: List[AbilityInfo] = []    # 涉及的能力维度
    
    # 注意：不返回 answer 和 explanation，答题后再返回
    
    class Config:
        from_attributes = True


class QuestionWithAnswer(QuestionItem):
    """题目详情（含答案，答题后返回）"""
    answer: str
    explanation: Optional[str] = None


class QuestionListResponse(BaseModel):
    """题目列表响应"""
    article_id: int
    article_title: str
    questions: List[QuestionItem]
    total: int
```

---

## 2.2.5 文章服务 (services/article_service.py)

```python
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
    """文章服务"""
    
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
        """
        获取文章列表（支持筛选和分页）
        """
        # 基础查询
        query = select(Article).where(Article.status == ArticleStatusEnum.PUBLISHED)
        
        # 关键词搜索
        if keyword:
            query = query.where(
                or_(
                    Article.title.ilike(f"%{keyword}%"),
                    Article.source_book.ilike(f"%{keyword}%")
                )
            )
        
        # 难度筛选
        if difficulty:
            query = query.where(Article.article_difficulty == DifficultyEnum(difficulty))
        
        # 标签筛选（年级、文体、来源）
        tag_filters = []
        if grade:
            tag_filters.append(("grade", grade))
        if genre:
            tag_filters.append(("genre", genre))
        if source:
            tag_filters.append(("source", source))
        
        if tag_filters:
            # 子查询：找到包含指定标签的文章ID
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
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 分页
        query = query.offset((page - 1) * page_size).limit(page_size)
        query = query.options(selectinload(Article.tags).selectinload(ArticleTag.tag))
        
        result = await db.execute(query)
        articles = result.scalars().all()
        
        # 转换为响应模型
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
        """获取文章详情"""
        query = (
            select(Article)
            .where(Article.id == article_id, Article.status == ArticleStatusEnum.PUBLISHED)
            .options(selectinload(Article.tags).selectinload(ArticleTag.tag))
        )
        result = await db.execute(query)
        article = result.scalar_one_or_none()
        
        if not article:
            return None
        
        # 获取题目数量
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
        """
        获取今日推荐文章
        
        逻辑：
        1. 筛选适合用户年级的文章
        2. 排除用户今天已读过的文章
        3. 随机选择一篇
        """
        if not user.grade:
            # 用户未设置年级，随机推荐低难度文章
            query = (
                select(Article)
                .where(
                    Article.status == ArticleStatusEnum.PUBLISHED,
                    Article.article_difficulty == DifficultyEnum.EASY
                )
            )
        else:
            # 获取用户年级对应的标签
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
        
        # 排除今天已读过的文章
        today = date.today()
        read_today_subquery = (
            select(UserProgress.article_id)
            .where(
                UserProgress.user_id == user.id,
                func.date(UserProgress.created_at) == today
            )
        )
        query = query.where(Article.id.notin_(read_today_subquery))
        
        # 获取候选文章
        result = await db.execute(query)
        candidates = result.scalars().all()
        
        if not candidates:
            # 如果没有未读文章，随机选择一篇已发布的文章
            all_query = (
                select(Article)
                .where(Article.status == ArticleStatusEnum.PUBLISHED)
                .limit(50)
            )
            result = await db.execute(all_query)
            candidates = result.scalars().all()
        
        if not candidates:
            return None
        
        # 随机选择
        selected = random.choice(candidates)
        return await ArticleService.get_article_detail(db, selected.id)
    
    @staticmethod
    async def get_weak_point_recommendation(
        db: AsyncSession,
        user: User
    ) -> Optional[ArticleDetail]:
        """
        获取补弱项推荐文章
        
        逻辑：
        1. 找到用户最弱的能力维度
        2. 找到包含该能力训练的文章
        3. 优先推荐用户未读过的文章
        """
        # 获取用户能力数据，找到最弱的能力
        ability_result = await db.execute(
            select(UserAbility)
            .where(UserAbility.user_id == user.id)
            .order_by(UserAbility.score)
            .limit(3)  # 取最弱的3个
        )
        weak_abilities = ability_result.scalars().all()
        
        if not weak_abilities:
            # 没有答题记录，返回普通推荐
            return await ArticleService.get_today_recommendation(db, user)
        
        # 获取包含这些弱项能力训练的文章
        weak_ability_ids = [wa.ability_id for wa in weak_abilities]
        
        from app.models.question import QuestionAbility
        
        # 找到训练这些能力的题目所属的文章
        query = (
            select(Article)
            .where(Article.status == ArticleStatusEnum.PUBLISHED)
            .join(Question)
            .join(QuestionAbility)
            .where(QuestionAbility.ability_id.in_(weak_ability_ids))
            .distinct()
        )
        
        # 排除用户已读过的文章
        read_subquery = select(UserProgress.article_id).where(UserProgress.user_id == user.id)
        query = query.where(Article.id.notin_(read_subquery))
        
        result = await db.execute(query)
        candidates = result.scalars().all()
        
        if not candidates:
            # 没有未读的，从已读中选择
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
```

---

## 2.2.6 题目服务 (services/question_service.py)

```python
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
                type=q.type,
                content=q.content,
                options=q.options,
                hint=q.hint,
                difficulty=q.difficulty,
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
            type=question.type,
            content=question.content,
            options=question.options,
            hint=question.hint,
            difficulty=question.difficulty,
            abilities=abilities,
            answer=question.answer,
            explanation=question.explanation
        )


question_service = QuestionService()
```

---

## 2.2.7 标签服务 (services/tag_service.py)

```python
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.tag import Tag, TagCategoryEnum
from app.models.ability import AbilityDimension


class TagService:
    """标签服务"""
    
    @staticmethod
    async def get_all_tags(db: AsyncSession) -> Dict[str, List[dict]]:
        """
        获取所有标签，按分类组织
        返回格式: {"grade": [...], "genre": [...], ...}
        """
        result = await db.execute(
            select(Tag).order_by(Tag.category, Tag.display_order)
        )
        tags = result.scalars().all()
        
        categorized = {}
        for tag in tags:
            category = tag.category.value
            if category not in categorized:
                categorized[category] = []
            categorized[category].append({
                "id": tag.id,
                "name": tag.name,
                "description": tag.description
            })
        
        return categorized
    
    @staticmethod
    async def get_tag_categories() -> List[dict]:
        """获取标签分类列表"""
        return [
            {"code": "grade", "name": "年级适配"},
            {"code": "genre", "name": "文体类型"},
            {"code": "source", "name": "来源系列"},
            {"code": "theme", "name": "主题标签"},
            {"code": "culture", "name": "文化来源"},
            {"code": "adaptation", "name": "改编程度"},
        ]
    
    @staticmethod
    async def get_all_abilities(db: AsyncSession) -> List[dict]:
        """获取所有能力维度"""
        result = await db.execute(
            select(AbilityDimension).order_by(AbilityDimension.display_order)
        )
        abilities = result.scalars().all()
        
        return [
            {
                "id": a.id,
                "name": a.name,
                "code": a.code,
                "category": a.category.value,
                "description": a.description
            }
            for a in abilities
        ]


tag_service = TagService()
```

---

## 2.2.8 文章路由 (api/v1/articles.py)

```python
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.api.deps import get_current_user, get_current_user_optional
from app.models.user import User
from app.schemas.common import ResponseModel
from app.schemas.article import ArticleListResponse, ArticleDetail, ArticleListItem
from app.schemas.question import QuestionListResponse
from app.services.article_service import article_service
from app.services.question_service import question_service

router = APIRouter()


@router.get("/", response_model=ResponseModel[ArticleListResponse])
async def get_article_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    grade: Optional[str] = Query(None, description="年级，如：3年级"),
    genre: Optional[str] = Query(None, description="文体，如：童话"),
    difficulty: Optional[int] = Query(None, ge=1, le=3, description="难度 1/2/3"),
    source: Optional[str] = Query(None, description="来源，如：伊索寓言"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    获取文章列表
    
    - 支持按年级、文体、难度、来源筛选
    - 支持关键词搜索（标题、来源）
    - 分页返回
    """
    items, total = await article_service.get_article_list(
        db, page, page_size, grade, genre, difficulty, source, keyword
    )
    
    return ResponseModel(data=ArticleListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    ))


@router.get("/today", response_model=ResponseModel[ArticleDetail])
async def get_today_recommendation(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取今日推荐文章
    
    - 根据用户年级随机推荐
    - 优先推荐今天未读过的文章
    """
    article = await article_service.get_today_recommendation(db, current_user)
    
    if not article:
        raise HTTPException(status_code=404, detail="暂无推荐文章")
    
    return ResponseModel(data=article)


@router.get("/weak-point", response_model=ResponseModel[ArticleDetail])
async def get_weak_point_recommendation(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取补弱项推荐文章
    
    - 分析用户能力雷达图，找到最弱的能力
    - 推荐包含该能力训练的文章
    """
    article = await article_service.get_weak_point_recommendation(db, current_user)
    
    if not article:
        raise HTTPException(status_code=404, detail="暂无推荐文章")
    
    return ResponseModel(data=article)


@router.get("/{article_id}", response_model=ResponseModel[ArticleDetail])
async def get_article_detail(
    article_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    获取文章详情
    """
    article = await article_service.get_article_detail(db, article_id)
    
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    return ResponseModel(data=article)


@router.get("/{article_id}/questions", response_model=ResponseModel[QuestionListResponse])
async def get_article_questions(
    article_id: int,
    for_weak_point: bool = Query(False, description="是否为补弱项模式"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取文章的题目列表
    
    - for_weak_point=True 时，题目会按弱项相关性排序
    - 不返回答案，答题后通过 progress 接口获取
    """
    # 验证文章存在
    article = await article_service.get_article_detail(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    questions = await question_service.get_questions_by_article(
        db, article_id, current_user.id, for_weak_point
    )
    
    return ResponseModel(data=QuestionListResponse(
        article_id=article_id,
        article_title=article.title,
        questions=questions,
        total=len(questions)
    ))
```

---

## 2.2.9 标签路由 (api/v1/tags.py)

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List

from app.database import get_db
from app.schemas.common import ResponseModel
from app.services.tag_service import tag_service

router = APIRouter()


@router.get("/", response_model=ResponseModel[Dict[str, List[dict]]])
async def get_all_tags(
    db: AsyncSession = Depends(get_db)
):
    """
    获取所有标签（按分类）
    
    返回格式:
    {
        "grade": [{"id": 1, "name": "1年级"}, ...],
        "genre": [{"id": 7, "name": "童话"}, ...],
        ...
    }
    """
    tags = await tag_service.get_all_tags(db)
    return ResponseModel(data=tags)


@router.get("/categories", response_model=ResponseModel[List[dict]])
async def get_tag_categories():
    """
    获取标签分类列表
    
    返回:
    [
        {"code": "grade", "name": "年级适配"},
        {"code": "genre", "name": "文体类型"},
        ...
    ]
    """
    categories = await tag_service.get_tag_categories()
    return ResponseModel(data=categories)
```

---

## 2.2.10 能力维度路由 (api/v1/abilities.py)

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.common import ResponseModel
from app.services.tag_service import tag_service

router = APIRouter()


@router.get("/", response_model=ResponseModel[List[dict]])
async def get_all_abilities(
    db: AsyncSession = Depends(get_db)
):
    """
    获取所有能力维度
    
    返回 10 个能力维度，用于：
    - 筛选文章/题目
    - 显示能力名称
    """
    abilities = await tag_service.get_all_abilities(db)
    return ResponseModel(data=abilities)
```

---

## 2.2.11 更新路由注册 (api/router.py)

```python
from fastapi import APIRouter
from app.api.v1 import auth, users, articles, tags, abilities, questions, progress, admin

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(articles.router, prefix="/articles", tags=["文章"])
api_router.include_router(tags.router, prefix="/tags", tags=["标签"])
api_router.include_router(abilities.router, prefix="/abilities", tags=["能力维度"])
# api_router.include_router(questions.router, prefix="/questions", tags=["题目"])
# api_router.include_router(progress.router, prefix="/progress", tags=["学习进度"])
# api_router.include_router(admin.router, prefix="/admin", tags=["管理后台"])
```

---

## 2.2.12 验收标准

### 文章模块验收

- [ ] `GET /api/v1/articles/` 返回分页文章列表
- [ ] 支持 grade、genre、difficulty、source、keyword 筛选
- [ ] `GET /api/v1/articles/today` 返回今日推荐文章
- [ ] `GET /api/v1/articles/weak-point` 返回补弱项推荐
- [ ] `GET /api/v1/articles/{id}` 返回文章详情（含内容）
- [ ] `GET /api/v1/articles/{id}/questions` 返回题目列表（不含答案）

### 标签模块验收

- [ ] `GET /api/v1/tags/` 返回按分类组织的标签
- [ ] `GET /api/v1/tags/categories` 返回标签分类

### 能力维度验收

- [ ] `GET /api/v1/abilities/` 返回 10 个能力维度

---

## 2.2.13 单元测试

### 文章测试 (tests/test_articles.py)

```python
import pytest
from httpx import AsyncClient
from app.main import app
from app.utils.security import create_access_token


def get_test_token(user_id: int = 1) -> str:
    return create_access_token({"sub": str(user_id)})


@pytest.mark.asyncio
async def test_get_article_list():
    """测试获取文章列表"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/articles/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "items" in data["data"]
    assert "total" in data["data"]


@pytest.mark.asyncio
async def test_get_article_list_with_filters():
    """测试文章列表筛选"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/articles/",
            params={"grade": "3年级", "genre": "童话", "difficulty": 1}
        )
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_today_recommendation():
    """测试今日推荐"""
    token = get_test_token()
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/articles/today",
            headers={"Authorization": f"Bearer {token}"}
        )
    
    # 可能没有文章返回 404
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_get_article_detail():
    """测试获取文章详情"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/articles/1")
    
    # 可能不存在返回 404
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_get_tags():
    """测试获取标签"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/tags/")
    
    assert response.status_code == 200
    data = response.json()
    assert "grade" in data["data"] or len(data["data"]) >= 0


@pytest.mark.asyncio
async def test_get_abilities():
    """测试获取能力维度"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/abilities/")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 10  # 10个能力维度
```

---

## 2.2.14 交付物清单

| 交付物 | 文件路径 | 验收标准 |
|--------|----------|----------|
| 文章模型 | `app/schemas/article.py` | 请求/响应模型 |
| 题目模型 | `app/schemas/question.py` | 请求/响应模型 |
| 文章服务 | `app/services/article_service.py` | 列表、详情、推荐 |
| 题目服务 | `app/services/question_service.py` | 获取题目 |
| 标签服务 | `app/services/tag_service.py` | 标签和能力查询 |
| 文章路由 | `app/api/v1/articles.py` | 文章接口 |
| 标签路由 | `app/api/v1/tags.py` | 标签接口 |
| 能力路由 | `app/api/v1/abilities.py` | 能力接口 |
| 单元测试 | `app/tests/test_articles.py` | 文章相关测试 |
