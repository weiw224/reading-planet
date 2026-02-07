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
    result = await admin_article_service.create_article(db, data)
    return ResponseModel(data=result)


@router.get("/{article_id}", response_model=ResponseModel[ArticleAdminResponse])
async def get_article_detail(
    article_id: int,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
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
    success = await admin_article_service.archive_article(db, article_id)
    if not success:
        raise HTTPException(status_code=404, detail="文章不存在")
    return ResponseModel(message="归档成功")
