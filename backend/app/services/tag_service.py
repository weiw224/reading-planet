from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.tag import Tag, TagCategoryEnum
from app.models.ability import AbilityDimension


class TagService:
    @staticmethod
    async def get_all_tags(db: AsyncSession) -> Dict[str, List[dict]]:
        result = await db.execute(
            select(Tag).order_by(Tag.category, Tag.display_order)
        )
        tags = result.scalars().all()
        
        categorized = {}
        for tag in tags:
            category = tag.category.value
            if category not in categorized:
                categorized[category] = []
            categorized[category].append({
                "id": tag.id,
                "name": tag.name,
                "description": tag.description
            })
        
        return categorized
    
    @staticmethod
    async def get_tag_categories() -> List[dict]:
        return [
            {"code": "grade", "name": "年级适配"},
            {"code": "genre", "name": "文体类型"},
            {"code": "source", "name": "来源系列"},
            {"code": "theme", "name": "主题标签"},
            {"code": "culture", "name": "文化来源"},
            {"code": "adaptation", "name": "改编程度"},
        ]
    
    @staticmethod
    async def get_all_abilities(db: AsyncSession) -> List[dict]:
        result = await db.execute(
            select(AbilityDimension).order_by(AbilityDimension.display_order)
        )
        abilities = result.scalars().all()
        
        return [
            {
                "id": a.id,
                "name": a.name,
                "code": a.code,
                "category": a.category.value,
                "description": a.description
            }
            for a in abilities
        ]


tag_service = TagService()
