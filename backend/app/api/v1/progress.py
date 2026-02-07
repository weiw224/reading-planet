from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.common import ResponseModel
from app.schemas.progress import (
    StartReadingRequest,
    StartReadingResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
    CompleteReadingRequest,
    CompleteReadingResponse,
    ProgressWithAnswers,
    HistoryItem,
    HistoryListResponse
)
from app.services.progress_service import progress_service

router = APIRouter()


@router.post("/start", response_model=ResponseModel[StartReadingResponse])
async def start_reading(
    request: StartReadingRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        result = await progress_service.start_reading(
            db=db,
            user_id=current_user.id,
            article_id=request.article_id
        )
        return ResponseModel(data=result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器错误"
        )


@router.post("/{progress_id}/submit", response_model=ResponseModel[SubmitAnswerResponse])
async def submit_answer(
    progress_id: int,
    request: SubmitAnswerRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        result = await progress_service.submit_answer(
            db=db,
            progress_id=progress_id,
            user_id=current_user.id,
            question_id=request.question_id,
            user_answer=request.user_answer
        )
        return ResponseModel(data=result)
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器错误"
        )


@router.post("/{progress_id}/complete", response_model=ResponseModel[CompleteReadingResponse])
async def complete_reading(
    progress_id: int,
    request: CompleteReadingRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        result = await progress_service.complete_reading(
            db=db,
            progress_id=progress_id,
            user_id=current_user.id,
            time_spent=request.time_spent
        )
        return ResponseModel(data=result)
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器错误"
        )


@router.get("/{progress_id}", response_model=ResponseModel[ProgressWithAnswers])
async def get_progress_detail(
    progress_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        result = await progress_service.get_progress_detail(
            db=db,
            progress_id=progress_id,
            user_id=current_user.id
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="进度记录不存在"
            )
        return ResponseModel(data=result)
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器错误"
        )


@router.get("/history", response_model=ResponseModel[HistoryListResponse])
async def get_history(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        items, total = await progress_service.get_history(
            db=db,
            user_id=current_user.id,
            page=page,
            page_size=page_size
        )
        return ResponseModel(data=HistoryListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        ))
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器错误"
        )
