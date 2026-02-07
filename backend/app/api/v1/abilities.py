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
