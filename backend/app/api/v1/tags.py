from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List

from app.database import get_db
from app.schemas.common import ResponseModel
from app.services.tag_service import tag_service

router = APIRouter()


@router.get("/", response_model=ResponseModel[Dict[str, List[dict]]])
async def get_all_tags(
    db: AsyncSession = Depends(get_db)
):
    """
    获取所有标签（按分类）
    
    返回格式:
    {
        "grade": [{"id": 1, "name": "1年级"}, ...],
        "genre": [{"id": 7, "name": "童话"}, ...],
        ...
    }
    """
    tags = await tag_service.get_all_tags(db)
    return ResponseModel(data=tags)


@router.get("/categories", response_model=ResponseModel[List[dict]])
async def get_tag_categories():
    """
    获取标签分类列表
    
    返回:
    [
        {"code": "grade", "name": "年级适配"},
        {"code": "genre", "name": "文体类型"},
        ...
    ]
    """
    categories = await tag_service.get_tag_categories()
    return ResponseModel(data=categories)
