from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.auth import (
    WechatLoginRequest, 
    TokenResponse, 
    AdminLoginRequest
)
from app.schemas.common import ResponseModel
from app.services.auth_service import auth_service
from app.config import settings

router = APIRouter()


@router.post("/wechat-login", response_model=ResponseModel[TokenResponse])
async def wechat_login(
    request: WechatLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        access_token, is_new_user = await auth_service.wechat_login(db, request.code)
        
        return ResponseModel(
            data=TokenResponse(
                access_token=access_token,
                expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                is_new_user=is_new_user
            )
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/admin-login", response_model=ResponseModel[TokenResponse])
async def admin_login(
    request: AdminLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        access_token = await auth_service.admin_login(db, request.username, request.password)
        
        return ResponseModel(
            data=TokenResponse(
                access_token=access_token,
                expires_in=24 * 60 * 60,
                is_new_user=False
            )
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
