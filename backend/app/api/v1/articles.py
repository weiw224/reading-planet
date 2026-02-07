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
    article = await article_service.get_today_recommendation(db, current_user)
    
    if not article:
        raise HTTPException(status_code=404, detail="暂无推荐文章")
    
    return ResponseModel(data=article)


@router.get("/weak-point", response_model=ResponseModel[ArticleDetail])
async def get_weak_point_recommendation(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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
