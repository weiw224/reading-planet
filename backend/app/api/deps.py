from typing import Optional
from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.utils.security import verify_token
from app.utils.exceptions import AuthenticationError
from app.models.user import User


async def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """获取当前用户（可选，未登录返回 None）"""
    if not authorization:
        return None
    
    if not authorization.startswith("Bearer "):
        return None
    
    token = authorization[7:]  # 去掉 "Bearer " 前缀
    payload = verify_token(token)
    
    if not payload:
        return None
    
    user_id = payload.get("sub")
    if not user_id:
        return None
    
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    
    return user


async def get_current_user(
    user: Optional[User] = Depends(get_current_user_optional)
) -> User:
    """获取当前用户（必须登录）"""
    if not user:
        raise AuthenticationError("请先登录")
    return user


async def get_admin_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """获取管理员用户（用于后台接口）"""
    if not authorization:
        raise AuthenticationError("请先登录")
    
    if not authorization.startswith("Bearer "):
        raise AuthenticationError("Token 格式错误")
    
    token = authorization[7:]
    payload = verify_token(token)
    
    if not payload:
        raise AuthenticationError("Token 无效或已过期")
    
    if payload.get("role") != "admin":
        raise AuthenticationError("需要管理员权限")
    
    return payload
