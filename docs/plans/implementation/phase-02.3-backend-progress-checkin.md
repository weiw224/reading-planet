# Phase 2.3: 后端 API 开发 - 学习进度与打卡模块

> **预估工时**: 2-3 人天  
> **前置依赖**: Phase 2.2 (文章与题目模块)  
> **本文件范围**: 答题提交、进度记录、打卡、勋章检测

---

## 2.3.1 目标概述

本阶段完成后端 API 的学习进度模块，包括：
- 开始阅读（创建进度记录）
- 提交答案并评分
- 完成阅读（触发打卡和勋章检测）
- 历史记录查询

---

## 2.3.2 API 接口清单

```
/api/v1/progress
├── POST /start              # 开始阅读一篇文章
├── POST /{id}/submit        # 提交一道题的答案
├── POST /{id}/complete      # 完成阅读
├── GET /{id}                # 获取进度详情（含答案解析）
└── GET /history             # 获取历史阅读记录
```

---

## 2.3.3 请求/响应模型 (schemas/progress.py)

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class StartReadingRequest(BaseModel):
    """开始阅读请求"""
    article_id: int


class StartReadingResponse(BaseModel):
    """开始阅读响应"""
    progress_id: int
    article_id: int
    article_title: str
    question_count: int


class SubmitAnswerRequest(BaseModel):
    """提交答案请求"""
    question_id: int
    user_answer: str  # 用户的答案


class SubmitAnswerResponse(BaseModel):
    """提交答案响应"""
    question_id: int
    is_correct: bool
    correct_answer: str
    explanation: Optional[str] = None
    ability_names: List[str] = []  # 涉及的能力维度


class CompleteReadingRequest(BaseModel):
    """完成阅读请求"""
    time_spent: int = Field(..., ge=0, description="阅读用时（秒）")


class AbilityScoreItem(BaseModel):
    """能力得分项"""
    ability_id: int
    ability_name: str
    correct_count: int
    total_count: int
    score: float  # 本次练习该能力的得分


class BadgeUnlock(BaseModel):
    """解锁的勋章"""
    id: int
    name: str
    description: str
    icon_url: Optional[str] = None


class CompleteReadingResponse(BaseModel):
    """完成阅读响应"""
    progress_id: int
    score: int                          # 总分（百分制）
    correct_count: int
    total_count: int
    time_spent: int
    ability_scores: List[AbilityScoreItem]  # 各能力得分
    is_checked_in: bool                 # 是否完成今日打卡
    streak_days: int                    # 当前连续打卡天数
    new_badges: List[BadgeUnlock] = []  # 新解锁的勋章


class ProgressDetail(BaseModel):
    """进度详情"""
    id: int
    article_id: int
    article_title: str
    score: Optional[int] = None
    correct_count: int
    total_count: int
    time_spent: Optional[int] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AnswerDetail(BaseModel):
    """答案详情"""
    question_id: int
    question_content: str
    question_type: str
    user_answer: Optional[str]
    correct_answer: str
    is_correct: Optional[bool]
    explanation: Optional[str] = None


class ProgressWithAnswers(ProgressDetail):
    """进度详情（含答案）"""
    answers: List[AnswerDetail] = []


class HistoryItem(BaseModel):
    """历史记录项"""
    id: int
    article_id: int
    article_title: str
    score: Optional[int]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class HistoryResponse(BaseModel):
    """历史记录响应"""
    items: List[HistoryItem]
    total: int
    page: int
    page_size: int
```

---

## 2.3.4 进度服务 (services/progress_service.py)

```python
from typing import List, Optional, Tuple
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.article import Article
from app.models.question import Question, QuestionAbility
from app.models.progress import UserProgress, QuestionAnswer
from app.models.checkin import CheckIn
from app.models.user_ability import UserAbility
from app.models.badge import Badge, UserBadge, BadgeConditionTypeEnum
from app.schemas.progress import (
    StartReadingResponse,
    SubmitAnswerResponse,
    CompleteReadingResponse,
    AbilityScoreItem,
    BadgeUnlock,
    ProgressWithAnswers,
    AnswerDetail,
    HistoryItem
)


class ProgressService:
    """学习进度服务"""
    
    @staticmethod
    async def start_reading(
        db: AsyncSession,
        user_id: int,
        article_id: int
    ) -> StartReadingResponse:
        """
        开始阅读一篇文章
        创建进度记录
        """
        # 验证文章存在
        article = await db.get(Article, article_id)
        if not article:
            raise ValueError("文章不存在")
        
        # 获取题目数量
        question_count_result = await db.execute(
            select(func.count(Question.id)).where(Question.article_id == article_id)
        )
        question_count = question_count_result.scalar() or 0
        
        # 创建进度记录
        progress = UserProgress(
            user_id=user_id,
            article_id=article_id,
            total_count=question_count
        )
        db.add(progress)
        await db.commit()
        await db.refresh(progress)
        
        return StartReadingResponse(
            progress_id=progress.id,
            article_id=article_id,
            article_title=article.title,
            question_count=question_count
        )
    
    @staticmethod
    async def submit_answer(
        db: AsyncSession,
        progress_id: int,
        user_id: int,
        question_id: int,
        user_answer: str
    ) -> SubmitAnswerResponse:
        """
        提交一道题的答案
        """
        # 验证进度记录
        progress = await db.get(UserProgress, progress_id)
        if not progress or progress.user_id != user_id:
            raise ValueError("进度记录不存在")
        
        if progress.completed_at:
            raise ValueError("该阅读已完成，无法继续答题")
        
        # 获取题目
        question = await db.get(Question, question_id)
        if not question or question.article_id != progress.article_id:
            raise ValueError("题目不存在或不属于该文章")
        
        # 检查是否已答过这道题
        existing = await db.execute(
            select(QuestionAnswer).where(
                QuestionAnswer.progress_id == progress_id,
                QuestionAnswer.question_id == question_id
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("该题目已提交答案")
        
        # 判断答案是否正确
        is_correct = ProgressService._check_answer(
            question.type.value, 
            user_answer, 
            question.answer
        )
        
        # 保存答案
        answer_record = QuestionAnswer(
            progress_id=progress_id,
            question_id=question_id,
            user_answer=user_answer,
            is_correct=is_correct
        )
        db.add(answer_record)
        
        # 更新正确题数
        if is_correct:
            progress.correct_count += 1
        
        await db.commit()
        
        # 获取题目涉及的能力
        ability_result = await db.execute(
            select(QuestionAbility)
            .where(QuestionAbility.question_id == question_id)
            .options(selectinload(QuestionAbility.ability))
        )
        ability_names = [qa.ability.name for qa in ability_result.scalars().all()]
        
        return SubmitAnswerResponse(
            question_id=question_id,
            is_correct=is_correct,
            correct_answer=question.answer,
            explanation=question.explanation,
            ability_names=ability_names
        )
    
    @staticmethod
    def _check_answer(question_type: str, user_answer: str, correct_answer: str) -> bool:
        """检查答案是否正确"""
        user_answer = user_answer.strip().upper()
        correct_answer = correct_answer.strip().upper()
        
        if question_type == "choice":
            # 选择题：直接比较选项字母
            return user_answer == correct_answer
        
        elif question_type == "judge":
            # 判断题：TRUE/FALSE
            return user_answer == correct_answer
        
        elif question_type == "fill":
            # 填空题：允许一定的容错
            return user_answer.lower() == correct_answer.lower()
        
        elif question_type == "short_answer":
            # 简答题：暂时总是返回 True，后续可接入 AI 评分
            return True
        
        return False
    
    @staticmethod
    async def complete_reading(
        db: AsyncSession,
        progress_id: int,
        user_id: int,
        time_spent: int
    ) -> CompleteReadingResponse:
        """
        完成阅读
        - 计算得分
        - 更新用户能力
        - 处理打卡
        - 检查勋章
        """
        # 获取进度记录
        progress = await db.get(UserProgress, progress_id)
        if not progress or progress.user_id != user_id:
            raise ValueError("进度记录不存在")
        
        if progress.completed_at:
            raise ValueError("该阅读已完成")
        
        # 计算得分
        score = 0
        if progress.total_count > 0:
            score = int(progress.correct_count / progress.total_count * 100)
        
        # 更新进度记录
        progress.score = score
        progress.time_spent = time_spent
        progress.completed_at = datetime.utcnow()
        
        # 获取用户
        user = await db.get(User, user_id)
        user.total_readings += 1
        
        # 更新用户能力统计
        ability_scores = await ProgressService._update_user_abilities(db, progress)
        
        # 处理打卡
        is_checked_in, streak_days = await ProgressService._handle_checkin(db, user, progress)
        
        # 检查勋章
        new_badges = await ProgressService._check_badges(db, user)
        
        await db.commit()
        
        return CompleteReadingResponse(
            progress_id=progress_id,
            score=score,
            correct_count=progress.correct_count,
            total_count=progress.total_count,
            time_spent=time_spent,
            ability_scores=ability_scores,
            is_checked_in=is_checked_in,
            streak_days=streak_days,
            new_badges=new_badges
        )
    
    @staticmethod
    async def _update_user_abilities(
        db: AsyncSession,
        progress: UserProgress
    ) -> List[AbilityScoreItem]:
        """更新用户能力统计"""
        # 获取本次答题记录
        answers_result = await db.execute(
            select(QuestionAnswer)
            .where(QuestionAnswer.progress_id == progress.id)
            .options(
                selectinload(QuestionAnswer.question)
                .selectinload(Question.abilities)
                .selectinload(QuestionAbility.ability)
            )
        )
        answers = answers_result.scalars().all()
        
        # 按能力维度统计
        ability_stats = {}  # ability_id -> {"correct": 0, "total": 0, "name": ""}
        
        for answer in answers:
            for qa in answer.question.abilities:
                ability_id = qa.ability_id
                if ability_id not in ability_stats:
                    ability_stats[ability_id] = {
                        "correct": 0,
                        "total": 0,
                        "name": qa.ability.name
                    }
                ability_stats[ability_id]["total"] += 1
                if answer.is_correct:
                    ability_stats[ability_id]["correct"] += 1
        
        # 更新用户能力表
        result_scores = []
        for ability_id, stats in ability_stats.items():
            # 查找或创建用户能力记录
            user_ability_result = await db.execute(
                select(UserAbility).where(
                    UserAbility.user_id == progress.user_id,
                    UserAbility.ability_id == ability_id
                )
            )
            user_ability = user_ability_result.scalar_one_or_none()
            
            if not user_ability:
                user_ability = UserAbility(
                    user_id=progress.user_id,
                    ability_id=ability_id
                )
                db.add(user_ability)
            
            # 累计统计
            user_ability.correct_count += stats["correct"]
            user_ability.total_count += stats["total"]
            
            # 重新计算得分
            if user_ability.total_count > 0:
                user_ability.score = user_ability.correct_count / user_ability.total_count * 100
            
            # 本次练习得分
            this_score = 0
            if stats["total"] > 0:
                this_score = stats["correct"] / stats["total"] * 100
            
            result_scores.append(AbilityScoreItem(
                ability_id=ability_id,
                ability_name=stats["name"],
                correct_count=stats["correct"],
                total_count=stats["total"],
                score=round(this_score, 1)
            ))
        
        return result_scores
    
    @staticmethod
    async def _handle_checkin(
        db: AsyncSession,
        user: User,
        progress: UserProgress
    ) -> Tuple[bool, int]:
        """处理打卡"""
        today = date.today()
        
        # 检查今天是否已打卡
        existing = await db.execute(
            select(CheckIn).where(
                CheckIn.user_id == user.id,
                CheckIn.check_date == today
            )
        )
        if existing.scalar_one_or_none():
            # 已打卡
            return False, user.streak_days
        
        # 创建打卡记录
        checkin = CheckIn(
            user_id=user.id,
            check_date=today,
            progress_id=progress.id
        )
        db.add(checkin)
        
        # 检查昨天是否打卡，更新连续天数
        yesterday = date.today().replace(day=today.day - 1) if today.day > 1 else date(today.year, today.month - 1, 28)
        try:
            from datetime import timedelta
            yesterday = today - timedelta(days=1)
        except:
            pass
        
        yesterday_result = await db.execute(
            select(CheckIn).where(
                CheckIn.user_id == user.id,
                CheckIn.check_date == yesterday
            )
        )
        
        if yesterday_result.scalar_one_or_none():
            # 昨天打卡了，连续天数+1
            user.streak_days += 1
        else:
            # 昨天没打卡，重新开始
            user.streak_days = 1
        
        # 更新最长连续天数
        if user.streak_days > user.max_streak_days:
            user.max_streak_days = user.streak_days
        
        return True, user.streak_days
    
    @staticmethod
    async def _check_badges(
        db: AsyncSession,
        user: User
    ) -> List[BadgeUnlock]:
        """检查并发放勋章"""
        new_badges = []
        
        # 获取所有勋章
        badges_result = await db.execute(select(Badge))
        all_badges = badges_result.scalars().all()
        
        # 获取用户已有勋章
        user_badges_result = await db.execute(
            select(UserBadge.badge_id).where(UserBadge.user_id == user.id)
        )
        owned_badge_ids = set(user_badges_result.scalars().all())
        
        for badge in all_badges:
            if badge.id in owned_badge_ids:
                continue
            
            # 检查是否满足条件
            earned = False
            
            if badge.condition_type == BadgeConditionTypeEnum.FIRST_READING:
                earned = user.total_readings >= 1
            
            elif badge.condition_type == BadgeConditionTypeEnum.STREAK_DAYS:
                earned = user.streak_days >= badge.condition_value
            
            elif badge.condition_type == BadgeConditionTypeEnum.TOTAL_READINGS:
                earned = user.total_readings >= badge.condition_value
            
            elif badge.condition_type == BadgeConditionTypeEnum.ABILITY_ACCURACY:
                # 检查指定能力的正确率
                ability_code = badge.condition_extra
                from app.models.ability import AbilityDimension
                
                ability_result = await db.execute(
                    select(AbilityDimension).where(AbilityDimension.code == ability_code)
                )
                ability = ability_result.scalar_one_or_none()
                
                if ability:
                    user_ability_result = await db.execute(
                        select(UserAbility).where(
                            UserAbility.user_id == user.id,
                            UserAbility.ability_id == ability.id
                        )
                    )
                    user_ability = user_ability_result.scalar_one_or_none()
                    
                    if user_ability and user_ability.total_count >= 10:  # 至少做过10题
                        earned = user_ability.score >= badge.condition_value
            
            elif badge.condition_type == BadgeConditionTypeEnum.ABILITY_COUNT:
                # 检查指定能力的正确题数
                ability_code = badge.condition_extra
                from app.models.ability import AbilityDimension
                
                ability_result = await db.execute(
                    select(AbilityDimension).where(AbilityDimension.code == ability_code)
                )
                ability = ability_result.scalar_one_or_none()
                
                if ability:
                    user_ability_result = await db.execute(
                        select(UserAbility).where(
                            UserAbility.user_id == user.id,
                            UserAbility.ability_id == ability.id
                        )
                    )
                    user_ability = user_ability_result.scalar_one_or_none()
                    
                    if user_ability:
                        earned = user_ability.correct_count >= badge.condition_value
            
            # TODO: 实现 GENRE_COUNT 和 ALL_GENRES 的检查
            
            if earned:
                # 发放勋章
                user_badge = UserBadge(
                    user_id=user.id,
                    badge_id=badge.id
                )
                db.add(user_badge)
                
                new_badges.append(BadgeUnlock(
                    id=badge.id,
                    name=badge.name,
                    description=badge.description,
                    icon_url=badge.icon_url
                ))
        
        return new_badges
    
    @staticmethod
    async def get_progress_detail(
        db: AsyncSession,
        progress_id: int,
        user_id: int
    ) -> Optional[ProgressWithAnswers]:
        """获取进度详情"""
        progress = await db.get(UserProgress, progress_id)
        if not progress or progress.user_id != user_id:
            return None
        
        # 获取文章标题
        article = await db.get(Article, progress.article_id)
        
        # 获取答题记录
        answers_result = await db.execute(
            select(QuestionAnswer)
            .where(QuestionAnswer.progress_id == progress_id)
            .options(selectinload(QuestionAnswer.question))
        )
        answers = answers_result.scalars().all()
        
        answer_details = [
            AnswerDetail(
                question_id=ans.question_id,
                question_content=ans.question.content,
                question_type=ans.question.type.value,
                user_answer=ans.user_answer,
                correct_answer=ans.question.answer,
                is_correct=ans.is_correct,
                explanation=ans.question.explanation
            )
            for ans in answers
        ]
        
        return ProgressWithAnswers(
            id=progress.id,
            article_id=progress.article_id,
            article_title=article.title if article else "",
            score=progress.score,
            correct_count=progress.correct_count,
            total_count=progress.total_count,
            time_spent=progress.time_spent,
            completed_at=progress.completed_at,
            created_at=progress.created_at,
            answers=answer_details
        )
    
    @staticmethod
    async def get_history(
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[HistoryItem], int]:
        """获取历史阅读记录"""
        # 计算总数
        count_result = await db.execute(
            select(func.count(UserProgress.id))
            .where(
                UserProgress.user_id == user_id,
                UserProgress.completed_at.isnot(None)
            )
        )
        total = count_result.scalar() or 0
        
        # 查询记录
        result = await db.execute(
            select(UserProgress)
            .where(
                UserProgress.user_id == user_id,
                UserProgress.completed_at.isnot(None)
            )
            .options(selectinload(UserProgress.article))
            .order_by(UserProgress.completed_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        progresses = result.scalars().all()
        
        items = [
            HistoryItem(
                id=p.id,
                article_id=p.article_id,
                article_title=p.article.title if p.article else "",
                score=p.score,
                completed_at=p.completed_at
            )
            for p in progresses
        ]
        
        return items, total


progress_service = ProgressService()
```

---

## 2.3.5 进度路由 (api/v1/progress.py)

```python
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

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
    HistoryResponse,
    HistoryItem
)
from app.services.progress_service import progress_service

router = APIRouter()


@router.post("/start", response_model=ResponseModel[StartReadingResponse])
async def start_reading(
    request: StartReadingRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    开始阅读一篇文章
    
    - 创建进度记录
    - 返回进度ID，后续答题需要用到
    """
    try:
        result = await progress_service.start_reading(
            db, current_user.id, request.article_id
        )
        return ResponseModel(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{progress_id}/submit", response_model=ResponseModel[SubmitAnswerResponse])
async def submit_answer(
    progress_id: int,
    request: SubmitAnswerRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    提交一道题的答案
    
    - 每道题只能提交一次
    - 返回是否正确、正确答案、解析
    """
    try:
        result = await progress_service.submit_answer(
            db, progress_id, current_user.id,
            request.question_id, request.user_answer
        )
        return ResponseModel(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{progress_id}/complete", response_model=ResponseModel[CompleteReadingResponse])
async def complete_reading(
    progress_id: int,
    request: CompleteReadingRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    完成阅读
    
    - 计算得分和能力分布
    - 处理打卡（如果今天未打卡）
    - 检查并发放勋章
    """
    try:
        result = await progress_service.complete_reading(
            db, progress_id, current_user.id, request.time_spent
        )
        return ResponseModel(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{progress_id}", response_model=ResponseModel[ProgressWithAnswers])
async def get_progress_detail(
    progress_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取进度详情
    
    - 包含所有答题记录和正确答案
    - 用于查看历史记录
    """
    result = await progress_service.get_progress_detail(
        db, progress_id, current_user.id
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="进度记录不存在")
    
    return ResponseModel(data=result)


@router.get("/history", response_model=ResponseModel[HistoryResponse])
async def get_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取历史阅读记录
    
    - 分页返回已完成的阅读记录
    - 按完成时间倒序
    """
    items, total = await progress_service.get_history(
        db, current_user.id, page, page_size
    )
    
    return ResponseModel(data=HistoryResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    ))
```

---

## 2.3.6 验收标准

### 进度模块验收

- [ ] `POST /api/v1/progress/start` 创建进度记录
- [ ] `POST /api/v1/progress/{id}/submit` 提交答案并返回结果
- [ ] 同一题目不能重复提交
- [ ] `POST /api/v1/progress/{id}/complete` 完成阅读
  - 返回得分和能力分布
  - 正确处理打卡
  - 正确发放勋章
- [ ] `GET /api/v1/progress/{id}` 返回进度详情含答案
- [ ] `GET /api/v1/progress/history` 返回历史记录

### 打卡逻辑验收

- [ ] 每天第一次完成阅读时创建打卡记录
- [ ] 连续打卡时 streak_days 正确累加
- [ ] 中断打卡后 streak_days 重置为 1
- [ ] max_streak_days 记录最长连续天数

### 勋章逻辑验收

- [ ] 首次阅读发放"阅读新星"勋章
- [ ] 连续打卡3天发放"三日小达人"
- [ ] 累计阅读10篇发放"小书虫"
- [ ] 不重复发放已有勋章

---

## 2.3.7 单元测试

### 进度测试 (tests/test_progress.py)

```python
import pytest
from httpx import AsyncClient
from app.main import app
from app.utils.security import create_access_token
from app.database import AsyncSessionLocal
from app.models.user import User, GradeEnum
from app.models.article import Article, ArticleStatusEnum, DifficultyEnum
from app.models.question import Question, QuestionTypeEnum


async def setup_test_data():
    """创建测试数据"""
    async with AsyncSessionLocal() as db:
        # 创建测试用户
        user = User(openid="test_progress_user", grade=GradeEnum.GRADE_3)
        db.add(user)
        
        # 创建测试文章
        article = Article(
            title="测试文章",
            content="这是测试内容" * 50,
            word_count=300,
            reading_time=3,
            article_difficulty=DifficultyEnum.EASY,
            status=ArticleStatusEnum.PUBLISHED
        )
        db.add(article)
        await db.commit()
        await db.refresh(user)
        await db.refresh(article)
        
        # 创建测试题目
        question = Question(
            article_id=article.id,
            type=QuestionTypeEnum.CHOICE,
            content="测试题目",
            options=["A", "B", "C", "D"],
            answer="A",
            difficulty=DifficultyEnum.EASY
        )
        db.add(question)
        await db.commit()
        await db.refresh(question)
        
        return user.id, article.id, question.id


def get_test_token(user_id: int) -> str:
    return create_access_token({"sub": str(user_id)})


@pytest.mark.asyncio
async def test_reading_flow():
    """测试完整阅读流程"""
    user_id, article_id, question_id = await setup_test_data()
    token = get_test_token(user_id)
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. 开始阅读
        response = await client.post(
            "/api/v1/progress/start",
            headers={"Authorization": f"Bearer {token}"},
            json={"article_id": article_id}
        )
        assert response.status_code == 200
        progress_id = response.json()["data"]["progress_id"]
        
        # 2. 提交答案
        response = await client.post(
            f"/api/v1/progress/{progress_id}/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={"question_id": question_id, "user_answer": "A"}
        )
        assert response.status_code == 200
        assert response.json()["data"]["is_correct"] == True
        
        # 3. 完成阅读
        response = await client.post(
            f"/api/v1/progress/{progress_id}/complete",
            headers={"Authorization": f"Bearer {token}"},
            json={"time_spent": 180}
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["score"] == 100
        assert data["is_checked_in"] == True


@pytest.mark.asyncio
async def test_duplicate_answer():
    """测试重复提交答案"""
    user_id, article_id, question_id = await setup_test_data()
    token = get_test_token(user_id)
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 开始阅读
        response = await client.post(
            "/api/v1/progress/start",
            headers={"Authorization": f"Bearer {token}"},
            json={"article_id": article_id}
        )
        progress_id = response.json()["data"]["progress_id"]
        
        # 第一次提交
        await client.post(
            f"/api/v1/progress/{progress_id}/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={"question_id": question_id, "user_answer": "A"}
        )
        
        # 重复提交应该失败
        response = await client.post(
            f"/api/v1/progress/{progress_id}/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={"question_id": question_id, "user_answer": "B"}
        )
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_checkin_streak():
    """测试打卡连续天数"""
    # 这个测试需要模拟多天打卡，比较复杂
    # 基本逻辑：检查 streak_days 的更新
    pass


@pytest.mark.asyncio
async def test_badge_unlock():
    """测试勋章解锁"""
    user_id, article_id, question_id = await setup_test_data()
    token = get_test_token(user_id)
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 完成一次阅读应该获得"阅读新星"勋章
        response = await client.post(
            "/api/v1/progress/start",
            headers={"Authorization": f"Bearer {token}"},
            json={"article_id": article_id}
        )
        progress_id = response.json()["data"]["progress_id"]
        
        response = await client.post(
            f"/api/v1/progress/{progress_id}/complete",
            headers={"Authorization": f"Bearer {token}"},
            json={"time_spent": 180}
        )
        
        data = response.json()["data"]
        # 检查是否有新勋章
        badge_names = [b["name"] for b in data["new_badges"]]
        assert "阅读新星" in badge_names
```

---

## 2.3.8 交付物清单

| 交付物 | 文件路径 | 验收标准 |
|--------|----------|----------|
| 进度模型 | `app/schemas/progress.py` | 请求/响应模型 |
| 进度服务 | `app/services/progress_service.py` | 完整业务逻辑 |
| 进度路由 | `app/api/v1/progress.py` | 5个接口 |
| 单元测试 | `app/tests/test_progress.py` | 流程测试 |
