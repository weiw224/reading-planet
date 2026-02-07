from datetime import timedelta
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.services.wechat_service import wechat_service
from app.utils.security import create_access_token
from app.config import settings


class AuthService:
    @staticmethod
    async def wechat_login(db: AsyncSession, code: str) -> Tuple[str, bool]:
        wechat_data = await wechat_service.code2session(code)
        if not wechat_data:
            raise ValueError("微信登录失败，请重试")
        
        openid = wechat_data["openid"]
        
        result = await db.execute(select(User).where(User.openid == openid))
        user = result.scalar_one_or_none()
        
        is_new_user = False
        if not user:
            user = User(openid=openid)
            db.add(user)
            await db.commit()
            await db.refresh(user)
            is_new_user = True
        
        access_token = create_access_token(
            data={"sub": str(user.id), "openid": openid},
            expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return access_token, is_new_user
    
    @staticmethod
    async def admin_login(db: AsyncSession, username: str, password: str) -> str:
        if username == "admin" and password == "admin123":
            access_token = create_access_token(
                data={"sub": "admin", "role": "admin", "username": username},
                expires_delta=timedelta(hours=24)
            )
            return access_token
        
        raise ValueError("用户名或密码错误")


auth_service = AuthService()
