from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.api.deps import get_admin_user
from app.schemas.common import ResponseModel
from app.schemas.admin.question import (
    QuestionCreateRequest,
    QuestionUpdateRequest,
    QuestionAdminResponse,
    QuestionListItemAdmin
)
from app.services.admin.question_service import admin_question_service

router = APIRouter()


@router.get("/", response_model=ResponseModel)
async def get_question_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    article_id: Optional[int] = Query(None),
    question_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    items, total = await admin_question_service.get_question_list(
        db, page, page_size, article_id, question_type
    )
    
    return ResponseModel(data={
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    })


@router.post("/", response_model=ResponseModel[QuestionAdminResponse])
async def create_question(
    data: QuestionCreateRequest,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    try:
        result = await admin_question_service.create_question(db, data)
        return ResponseModel(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{question_id}", response_model=ResponseModel[QuestionAdminResponse])
async def get_question_detail(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    result = await admin_question_service.get_question_detail(db, question_id)
    if not result:
        raise HTTPException(status_code=404, detail="题目不存在")
    return ResponseModel(data=result)


@router.put("/{question_id}", response_model=ResponseModel[QuestionAdminResponse])
async def update_question(
    question_id: int,
    data: QuestionUpdateRequest,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    result = await admin_question_service.update_question(db, question_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="题目不存在")
    return ResponseModel(data=result)


@router.delete("/{question_id}", response_model=ResponseModel)
async def delete_question(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    success = await admin_question_service.delete_question(db, question_id)
    if not success:
        raise HTTPException(status_code=404, detail="题目不存在")
    return ResponseModel(message="删除成功")
