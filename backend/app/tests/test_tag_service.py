import pytest
from app.models.tag import Tag, TagCategoryEnum
from app.models.ability import AbilityDimension, AbilityCategoryEnum


@pytest.mark.asyncio
async def test_get_all_tags_empty(db_session):
    """测试获取所有标签 - 空数据库"""
    from app.services.tag_service import TagService

    result = await TagService.get_all_tags(db_session)
    
    assert result == {}


@pytest.mark.asyncio
async def test_get_all_tags_with_data(db_session):
    """测试获取所有标签 - 有数据"""
    from app.services.tag_service import TagService

    tag1 = Tag(name="1年级", category=TagCategoryEnum.GRADE, display_order=1)
    tag2 = Tag(name="2年级", category=TagCategoryEnum.GRADE, display_order=2)
    tag3 = Tag(name="童话", category=TagCategoryEnum.GENRE, display_order=1)
    tag4 = Tag(name="寓言", category=TagCategoryEnum.GENRE, display_order=2)
    
    db_session.add_all([tag1, tag2, tag3, tag4])
    await db_session.commit()
    
    result = await TagService.get_all_tags(db_session)
    
    assert "grade" in result
    assert "genre" in result
    assert len(result["grade"]) == 2
    assert len(result["genre"]) == 2
    assert result["grade"][0]["name"] == "1年级"
    assert result["grade"][1]["name"] == "2年级"
    assert result["genre"][0]["name"] == "童话"
    assert result["genre"][1]["name"] == "寓言"


@pytest.mark.asyncio
async def test_get_tag_categories():
    """测试获取标签分类列表"""
    from app.services.tag_service import TagService

    categories = await TagService.get_tag_categories()
    
    assert len(categories) == 6
    assert categories[0]["code"] == "grade"
    assert categories[0]["name"] == "年级适配"
    assert categories[1]["code"] == "genre"
    assert categories[1]["name"] == "文体类型"
    assert categories[2]["code"] == "source"
    assert categories[2]["name"] == "来源系列"
    assert categories[3]["code"] == "theme"
    assert categories[3]["name"] == "主题标签"
    assert categories[4]["code"] == "culture"
    assert categories[4]["name"] == "文化来源"
    assert categories[5]["code"] == "adaptation"
    assert categories[5]["name"] == "改编程度"


@pytest.mark.asyncio
async def test_get_all_abilities_empty(db_session):
    """测试获取所有能力维度 - 空数据库"""
    from app.services.tag_service import TagService

    result = await TagService.get_all_abilities(db_session)
    
    assert result == []


@pytest.mark.asyncio
async def test_get_all_abilities_with_data(db_session):
    """测试获取所有能力维度 - 有数据"""
    from app.services.tag_service import TagService

    ability1 = AbilityDimension(
        name="细节提取",
        code="detail_extraction",
        category=AbilityCategoryEnum.COMPREHENSION,
        description="提取文章细节信息",
        display_order=1
    )
    ability2 = AbilityDimension(
        name="主旨概括",
        code="main_idea",
        category=AbilityCategoryEnum.COMPREHENSION,
        description="概括文章主旨",
        display_order=2
    )
    
    db_session.add_all([ability1, ability2])
    await db_session.commit()
    
    result = await TagService.get_all_abilities(db_session)
    
    assert len(result) == 2
    assert result[0]["name"] == "细节提取"
    assert result[0]["code"] == "detail_extraction"
    assert result[0]["category"] == "comprehension"
    assert result[0]["description"] == "提取文章细节信息"
    assert result[1]["name"] == "主旨概括"
    assert result[1]["code"] == "main_idea"
