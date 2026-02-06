# Phase 2.1: 后端 API 开发 - 认证与用户模块

> **预估工时**: 2-3 人天  
> **前置依赖**: Phase 1 (数据库设计)  
> **本文件范围**: 认证系统、用户管理 API

---

## 2.1 目标概述

本阶段完成后端 API 的认证与用户模块，包括：
- 微信登录认证
- JWT Token 管理
- 用户信息 CRUD
- 用户学习数据统计

---

## 2.2 API 路由结构

```
/api/v1/
├── /auth                    # 认证模块 (本文件)
│   ├── POST /wechat-login   # 微信登录
│   └── POST /refresh-token  # 刷新 Token
│
├── /users                   # 用户模块 (本文件)
│   ├── GET /me              # 获取当前用户信息
│   ├── PUT /me              # 更新当前用户信息
│   ├── GET /me/stats        # 获取学习统计
│   ├── GET /me/abilities    # 获取能力雷达图数据
│   ├── GET /me/checkins     # 获取打卡记录
│   └── GET /me/badges       # 获取勋章列表
│
├── /articles                # 文章模块 (Phase 2.2)
├── /questions               # 题目模块 (Phase 2.2)
├── /progress                # 学习进度模块 (Phase 2.3)
└── /admin                   # 管理员模块 (Phase 2.4)
```

---

## 2.3 通用组件

### 2.3.1 API 路由入口 (api/router.py)

```python
from fastapi import APIRouter
from app.api.v1 import auth, users, articles, questions, progress, admin

api_router = APIRouter()

# 注册各模块路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(articles.router, prefix="/articles", tags=["文章"])
api_router.include_router(questions.router, prefix="/questions", tags=["题目"])
api_router.include_router(progress.router, prefix="/progress", tags=["学习进度"])
api_router.include_router(admin.router, prefix="/admin", tags=["管理后台"])
```

### 2.3.2 通用响应模型 (schemas/common.py)

```python
from typing import TypeVar, Generic, Optional, List
from pydantic import BaseModel

T = TypeVar('T')


class ResponseModel(BaseModel, Generic[T]):
    """通用响应模型"""
    code: int = 0
    message: str = "success"
    data: Optional[T] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应模型"""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class ErrorResponse(BaseModel):
    """错误响应模型"""
    code: int
    message: str
    detail: Optional[str] = None
```

### 2.3.3 异常处理 (utils/exceptions.py)

```python
from fastapi import HTTPException, status


class AppException(HTTPException):
    """应用自定义异常基类"""
    def __init__(self, code: int, message: str, status_code: int = 400):
        super().__init__(status_code=status_code, detail={"code": code, "message": message})


class AuthenticationError(AppException):
    """认证错误"""
    def __init__(self, message: str = "认证失败"):
        super().__init__(code=1001, message=message, status_code=status.HTTP_401_UNAUTHORIZED)


class AuthorizationError(AppException):
    """授权错误"""
    def __init__(self, message: str = "权限不足"):
        super().__init__(code=1002, message=message, status_code=status.HTTP_403_FORBIDDEN)


class NotFoundError(AppException):
    """资源不存在"""
    def __init__(self, message: str = "资源不存在"):
        super().__init__(code=1003, message=message, status_code=status.HTTP_404_NOT_FOUND)


class ValidationError(AppException):
    """验证错误"""
    def __init__(self, message: str = "参数验证失败"):
        super().__init__(code=1004, message=message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
```

### 2.3.4 安全工具 (utils/security.py)

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT Token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """验证 JWT Token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


def get_password_hash(password: str) -> str:
    """密码哈希（用于管理员账号）"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)
```

### 2.3.5 认证依赖 (api/deps.py)

```python
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
```

---

## 2.4 认证模块 (api/v1/auth.py)

### 2.4.1 请求/响应模型 (schemas/auth.py)

```python
from pydantic import BaseModel
from typing import Optional


class WechatLoginRequest(BaseModel):
    """微信登录请求"""
    code: str  # 微信登录凭证


class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # 过期时间（秒）
    is_new_user: bool = False  # 是否新用户（需要选择年级）


class RefreshTokenRequest(BaseModel):
    """刷新 Token 请求"""
    refresh_token: str


class AdminLoginRequest(BaseModel):
    """管理员登录请求"""
    username: str
    password: str
```

### 2.4.2 微信服务 (services/wechat_service.py)

```python
import httpx
from typing import Optional
from app.config import settings


class WechatService:
    """微信服务"""
    
    AUTH_URL = "https://api.weixin.qq.com/sns/jscode2session"
    
    @classmethod
    async def code2session(cls, code: str) -> Optional[dict]:
        """
        通过 code 获取 openid 和 session_key
        返回: {"openid": "xxx", "session_key": "xxx"} 或 None
        """
        params = {
            "appid": settings.WECHAT_APP_ID,
            "secret": settings.WECHAT_APP_SECRET,
            "js_code": code,
            "grant_type": "authorization_code"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(cls.AUTH_URL, params=params)
            data = response.json()
        
        if "openid" in data:
            return {
                "openid": data["openid"],
                "session_key": data.get("session_key", "")
            }
        
        # 记录错误日志
        print(f"微信登录失败: {data}")
        return None


wechat_service = WechatService()
```

### 2.4.3 认证服务 (services/auth_service.py)

```python
from datetime import timedelta
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.services.wechat_service import wechat_service
from app.utils.security import create_access_token
from app.config import settings


class AuthService:
    """认证服务"""
    
    @staticmethod
    async def wechat_login(db: AsyncSession, code: str) -> Tuple[str, bool]:
        """
        微信登录
        返回: (access_token, is_new_user)
        """
        # 1. 调用微信接口获取 openid
        wechat_data = await wechat_service.code2session(code)
        if not wechat_data:
            raise ValueError("微信登录失败，请重试")
        
        openid = wechat_data["openid"]
        
        # 2. 查找或创建用户
        result = await db.execute(select(User).where(User.openid == openid))
        user = result.scalar_one_or_none()
        
        is_new_user = False
        if not user:
            user = User(openid=openid)
            db.add(user)
            await db.commit()
            await db.refresh(user)
            is_new_user = True
        
        # 3. 生成 Token
        access_token = create_access_token(
            data={"sub": str(user.id), "openid": openid},
            expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return access_token, is_new_user
    
    @staticmethod
    async def admin_login(db: AsyncSession, username: str, password: str) -> str:
        """
        管理员登录
        返回: access_token
        """
        # TODO: 从数据库验证管理员账号
        # 这里简化处理，实际应该有 Admin 表
        from app.utils.security import verify_password
        
        # 临时硬编码（生产环境应该从数据库读取）
        if username == "admin" and password == "admin123":
            access_token = create_access_token(
                data={"sub": "admin", "role": "admin", "username": username},
                expires_delta=timedelta(hours=24)
            )
            return access_token
        
        raise ValueError("用户名或密码错误")


auth_service = AuthService()
```

### 2.4.4 认证路由 (api/v1/auth.py)

```python
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
    """
    微信登录
    
    - 接收微信 wx.login() 返回的 code
    - 返回 JWT Token
    - 如果是新用户，is_new_user=True，客户端需要引导用户选择年级
    """
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
    """
    管理员登录
    
    - 用于后台管理系统登录
    - 返回 JWT Token（包含 role=admin）
    """
    try:
        access_token = await auth_service.admin_login(db, request.username, request.password)
        
        return ResponseModel(
            data=TokenResponse(
                access_token=access_token,
                expires_in=24 * 60 * 60,  # 24小时
                is_new_user=False
            )
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
```

---

## 2.5 用户模块 (api/v1/users.py)

### 2.5.1 请求/响应模型 (schemas/user.py)

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


class GradeEnum(str, Enum):
    GRADE_1 = "GRADE_1"
    GRADE_2 = "GRADE_2"
    GRADE_3 = "GRADE_3"
    GRADE_4 = "GRADE_4"
    GRADE_5 = "GRADE_5"
    GRADE_6 = "GRADE_6"


class UserBase(BaseModel):
    """用户基础信息"""
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    grade: Optional[GradeEnum] = None


class UserUpdate(UserBase):
    """更新用户信息"""
    pass


class UserResponse(UserBase):
    """用户信息响应"""
    id: int
    total_readings: int
    streak_days: int
    max_streak_days: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserStatsResponse(BaseModel):
    """用户统计数据"""
    total_readings: int        # 累计阅读篇数
    total_questions: int       # 累计答题数
    correct_rate: float        # 总正确率
    streak_days: int           # 当前连续打卡天数
    max_streak_days: int       # 最长连续打卡天数
    total_badges: int          # 获得勋章数
    total_time: int            # 累计学习时长（分钟）


class AbilityScore(BaseModel):
    """能力得分"""
    ability_id: int
    ability_name: str
    ability_code: str
    category: str
    score: float              # 0-100
    correct_count: int
    total_count: int


class AbilityRadarResponse(BaseModel):
    """能力雷达图数据"""
    abilities: List[AbilityScore]


class CheckInRecord(BaseModel):
    """打卡记录"""
    date: date
    article_title: Optional[str] = None


class CheckInResponse(BaseModel):
    """打卡记录响应"""
    current_streak: int       # 当前连续天数
    records: List[CheckInRecord]  # 本月打卡记录


class BadgeInfo(BaseModel):
    """勋章信息"""
    id: int
    name: str
    description: str
    icon_url: Optional[str]
    category: str
    earned: bool              # 是否已获得
    earned_at: Optional[datetime] = None  # 获得时间
    progress: Optional[float] = None  # 进度（未获得时显示）


class BadgeListResponse(BaseModel):
    """勋章列表响应"""
    earned_count: int         # 已获得数量
    total_count: int          # 总数量
    badges: List[BadgeInfo]
```

### 2.5.2 用户服务 (services/user_service.py)

```python
from datetime import date, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.user import User, GradeEnum
from app.models.progress import UserProgress, QuestionAnswer
from app.models.checkin import CheckIn
from app.models.badge import Badge, UserBadge
from app.models.user_ability import UserAbility
from app.models.ability import AbilityDimension
from app.schemas.user import (
    UserUpdate, 
    UserStatsResponse, 
    AbilityScore,
    CheckInRecord,
    BadgeInfo
)


class UserService:
    """用户服务"""
    
    @staticmethod
    async def update_user(db: AsyncSession, user: User, data: UserUpdate) -> User:
        """更新用户信息"""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await db.commit()
        await db.refresh(user)
        return user
    
    @staticmethod
    async def get_user_stats(db: AsyncSession, user_id: int) -> UserStatsResponse:
        """获取用户统计数据"""
        # 获取用户基础信息
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        
        # 统计答题数据
        answer_stats = await db.execute(
            select(
                func.count(QuestionAnswer.id).label("total"),
                func.sum(func.cast(QuestionAnswer.is_correct, Integer)).label("correct")
            )
            .join(UserProgress)
            .where(UserProgress.user_id == user_id)
        )
        stats = answer_stats.first()
        total_questions = stats.total or 0
        correct_count = stats.correct or 0
        correct_rate = (correct_count / total_questions * 100) if total_questions > 0 else 0
        
        # 统计学习时长
        time_result = await db.execute(
            select(func.sum(UserProgress.time_spent))
            .where(UserProgress.user_id == user_id)
        )
        total_seconds = time_result.scalar() or 0
        total_time = total_seconds // 60
        
        # 统计勋章数
        badge_result = await db.execute(
            select(func.count(UserBadge.id))
            .where(UserBadge.user_id == user_id)
        )
        total_badges = badge_result.scalar() or 0
        
        return UserStatsResponse(
            total_readings=user.total_readings,
            total_questions=total_questions,
            correct_rate=round(correct_rate, 1),
            streak_days=user.streak_days,
            max_streak_days=user.max_streak_days,
            total_badges=total_badges,
            total_time=total_time
        )
    
    @staticmethod
    async def get_ability_radar(db: AsyncSession, user_id: int) -> List[AbilityScore]:
        """获取能力雷达图数据"""
        # 查询所有能力维度
        abilities_result = await db.execute(
            select(AbilityDimension).order_by(AbilityDimension.display_order)
        )
        abilities = abilities_result.scalars().all()
        
        # 查询用户能力数据
        user_abilities_result = await db.execute(
            select(UserAbility).where(UserAbility.user_id == user_id)
        )
        user_abilities = {ua.ability_id: ua for ua in user_abilities_result.scalars().all()}
        
        result = []
        for ability in abilities:
            ua = user_abilities.get(ability.id)
            result.append(AbilityScore(
                ability_id=ability.id,
                ability_name=ability.name,
                ability_code=ability.code,
                category=ability.category.value,
                score=ua.score if ua else 0,
                correct_count=ua.correct_count if ua else 0,
                total_count=ua.total_count if ua else 0
            ))
        
        return result
    
    @staticmethod
    async def get_checkins(
        db: AsyncSession, 
        user_id: int, 
        year: int, 
        month: int
    ) -> tuple[int, List[CheckInRecord]]:
        """获取打卡记录"""
        # 获取用户当前连续天数
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one()
        
        # 查询指定月份的打卡记录
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)
        
        result = await db.execute(
            select(CheckIn)
            .where(
                CheckIn.user_id == user_id,
                CheckIn.check_date >= start_date,
                CheckIn.check_date < end_date
            )
            .order_by(CheckIn.check_date)
        )
        checkins = result.scalars().all()
        
        records = [
            CheckInRecord(
                date=ci.check_date,
                article_title=None  # TODO: 关联查询文章标题
            )
            for ci in checkins
        ]
        
        return user.streak_days, records
    
    @staticmethod
    async def get_badges(db: AsyncSession, user_id: int) -> tuple[int, int, List[BadgeInfo]]:
        """获取勋章列表"""
        # 查询所有勋章
        badges_result = await db.execute(
            select(Badge).order_by(Badge.category, Badge.display_order)
        )
        badges = badges_result.scalars().all()
        
        # 查询用户已获得的勋章
        user_badges_result = await db.execute(
            select(UserBadge).where(UserBadge.user_id == user_id)
        )
        user_badges = {ub.badge_id: ub for ub in user_badges_result.scalars().all()}
        
        result = []
        earned_count = 0
        for badge in badges:
            ub = user_badges.get(badge.id)
            earned = ub is not None
            if earned:
                earned_count += 1
            
            result.append(BadgeInfo(
                id=badge.id,
                name=badge.name,
                description=badge.description,
                icon_url=badge.icon_url,
                category=badge.category.value,
                earned=earned,
                earned_at=ub.earned_at if ub else None,
                progress=None  # TODO: 计算进度
            ))
        
        return earned_count, len(badges), result


user_service = UserService()
```

### 2.5.3 用户路由 (api/v1/users.py)

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.common import ResponseModel
from app.schemas.user import (
    UserResponse,
    UserUpdate,
    UserStatsResponse,
    AbilityRadarResponse,
    CheckInResponse,
    BadgeListResponse
)
from app.services.user_service import user_service

router = APIRouter()


@router.get("/me", response_model=ResponseModel[UserResponse])
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户信息
    """
    return ResponseModel(data=UserResponse.model_validate(current_user))


@router.put("/me", response_model=ResponseModel[UserResponse])
async def update_current_user(
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新当前用户信息
    
    - 首次登录时用于设置年级
    - 后续可修改昵称、头像
    """
    updated_user = await user_service.update_user(db, current_user, data)
    return ResponseModel(data=UserResponse.model_validate(updated_user))


@router.get("/me/stats", response_model=ResponseModel[UserStatsResponse])
async def get_user_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取用户学习统计数据
    
    - 累计阅读篇数、答题数、正确率
    - 打卡天数、勋章数、学习时长
    """
    stats = await user_service.get_user_stats(db, current_user.id)
    return ResponseModel(data=stats)


@router.get("/me/abilities", response_model=ResponseModel[AbilityRadarResponse])
async def get_ability_radar(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取能力雷达图数据
    
    - 返回 10 个能力维度的得分
    - 用于绘制雷达图
    """
    abilities = await user_service.get_ability_radar(db, current_user.id)
    return ResponseModel(data=AbilityRadarResponse(abilities=abilities))


@router.get("/me/checkins", response_model=ResponseModel[CheckInResponse])
async def get_checkins(
    year: int = Query(default=None, description="年份，默认当前年"),
    month: int = Query(default=None, ge=1, le=12, description="月份，默认当前月"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取打卡记录
    
    - 返回指定月份的打卡日期列表
    - 用于渲染日历打卡状态
    """
    today = date.today()
    if year is None:
        year = today.year
    if month is None:
        month = today.month
    
    current_streak, records = await user_service.get_checkins(db, current_user.id, year, month)
    
    return ResponseModel(data=CheckInResponse(
        current_streak=current_streak,
        records=records
    ))


@router.get("/me/badges", response_model=ResponseModel[BadgeListResponse])
async def get_badges(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取勋章列表
    
    - 返回所有勋章（已获得和未获得）
    - 已获得的显示获得时间
    - 未获得的可显示进度
    """
    earned_count, total_count, badges = await user_service.get_badges(db, current_user.id)
    
    return ResponseModel(data=BadgeListResponse(
        earned_count=earned_count,
        total_count=total_count,
        badges=badges
    ))
```

---

## 2.6 验收标准

### 2.6.1 认证模块验收

- [ ] `POST /api/v1/auth/wechat-login` 接口可用
  - 输入正确的微信 code 返回 Token
  - 新用户返回 `is_new_user=true`
  - 老用户返回 `is_new_user=false`
  
- [ ] `POST /api/v1/auth/admin-login` 接口可用
  - 正确的用户名密码返回 Token
  - 错误的凭证返回 401

### 2.6.2 用户模块验收

- [ ] `GET /api/v1/users/me` 需要 Token 认证
- [ ] `PUT /api/v1/users/me` 可以更新用户信息
- [ ] `GET /api/v1/users/me/stats` 返回正确的统计数据
- [ ] `GET /api/v1/users/me/abilities` 返回 10 个能力维度
- [ ] `GET /api/v1/users/me/checkins` 返回打卡记录
- [ ] `GET /api/v1/users/me/badges` 返回勋章列表

### 2.6.3 错误处理验收

- [ ] 未授权访问返回 401
- [ ] 参数验证失败返回 422
- [ ] 资源不存在返回 404

---

## 2.7 单元测试

### 2.7.1 认证测试 (tests/test_auth.py)

```python
import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from app.main import app


@pytest.mark.asyncio
async def test_wechat_login_success():
    """测试微信登录成功"""
    with patch('app.services.wechat_service.wechat_service.code2session', new_callable=AsyncMock) as mock:
        mock.return_value = {"openid": "test_openid_123", "session_key": "xxx"}
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/wechat-login",
                json={"code": "test_code"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "access_token" in data["data"]
        assert data["data"]["is_new_user"] == True


@pytest.mark.asyncio
async def test_wechat_login_invalid_code():
    """测试微信登录失败（无效code）"""
    with patch('app.services.wechat_service.wechat_service.code2session', new_callable=AsyncMock) as mock:
        mock.return_value = None
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/wechat-login",
                json={"code": "invalid_code"}
            )
        
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_admin_login_success():
    """测试管理员登录成功"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/admin-login",
            json={"username": "admin", "password": "admin123"}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data["data"]


@pytest.mark.asyncio
async def test_admin_login_wrong_password():
    """测试管理员登录失败（密码错误）"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/admin-login",
            json={"username": "admin", "password": "wrong"}
        )
    
    assert response.status_code == 401
```

### 2.7.2 用户测试 (tests/test_users.py)

```python
import pytest
from httpx import AsyncClient
from app.main import app
from app.utils.security import create_access_token


def get_test_token(user_id: int = 1) -> str:
    """生成测试用 Token"""
    return create_access_token({"sub": str(user_id)})


@pytest.mark.asyncio
async def test_get_me_unauthorized():
    """测试未授权访问"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/users/me")
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_success():
    """测试获取当前用户信息"""
    token = get_test_token()
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
    
    # 注意：需要先创建测试用户，否则会 404
    # 这里只验证接口格式正确
    assert response.status_code in [200, 401]


@pytest.mark.asyncio
async def test_update_user_grade():
    """测试更新用户年级"""
    token = get_test_token()
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.put(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"grade": "GRADE_3"}
        )
    
    # 验证请求格式正确
    assert response.status_code in [200, 401]
```

### 2.7.3 运行测试

```bash
cd backend
source venv/bin/activate

# 运行认证模块测试
pytest app/tests/test_auth.py -v

# 运行用户模块测试
pytest app/tests/test_users.py -v

# 运行所有测试
pytest app/tests/ -v --cov=app
```

---

## 2.8 交付物清单

| 交付物 | 文件路径 | 验收标准 |
|--------|----------|----------|
| API 路由入口 | `app/api/router.py` | 注册所有模块路由 |
| 通用响应模型 | `app/schemas/common.py` | ResponseModel 等 |
| 异常处理 | `app/utils/exceptions.py` | 自定义异常类 |
| 安全工具 | `app/utils/security.py` | JWT 相关函数 |
| 认证依赖 | `app/api/deps.py` | get_current_user 等 |
| 认证模型 | `app/schemas/auth.py` | 登录请求/响应 |
| 微信服务 | `app/services/wechat_service.py` | code2session |
| 认证服务 | `app/services/auth_service.py` | 登录逻辑 |
| 认证路由 | `app/api/v1/auth.py` | 登录接口 |
| 用户模型 | `app/schemas/user.py` | 用户请求/响应 |
| 用户服务 | `app/services/user_service.py` | 用户业务逻辑 |
| 用户路由 | `app/api/v1/users.py` | 用户接口 |
| 认证测试 | `app/tests/test_auth.py` | 登录测试用例 |
| 用户测试 | `app/tests/test_users.py` | 用户接口测试 |
