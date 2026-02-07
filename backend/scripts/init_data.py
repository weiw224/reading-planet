"""
初始化基础数据
运行方式: python -m scripts.init_data
"""
import asyncio
from app.database import AsyncSessionLocal
from app.models.tag import Tag, TagCategoryEnum
from app.models.ability import AbilityDimension, AbilityCategoryEnum
from app.models.badge import Badge, BadgeCategoryEnum, BadgeConditionTypeEnum


async def init_tags():
    """初始化标签数据"""
    tags = [
        # 年级
        {"name": "1年级", "category": TagCategoryEnum.GRADE, "display_order": 1},
        {"name": "2年级", "category": TagCategoryEnum.GRADE, "display_order": 2},
        {"name": "3年级", "category": TagCategoryEnum.GRADE, "display_order": 3},
        {"name": "4年级", "category": TagCategoryEnum.GRADE, "display_order": 4},
        {"name": "5年级", "category": TagCategoryEnum.GRADE, "display_order": 5},
        {"name": "6年级", "category": TagCategoryEnum.GRADE, "display_order": 6},
        
        # 文体类型
        {"name": "童话", "category": TagCategoryEnum.GENRE, "display_order": 1},
        {"name": "寓言", "category": TagCategoryEnum.GENRE, "display_order": 2},
        {"name": "科普", "category": TagCategoryEnum.GENRE, "display_order": 3},
        {"name": "散文", "category": TagCategoryEnum.GENRE, "display_order": 4},
        {"name": "古诗词", "category": TagCategoryEnum.GENRE, "display_order": 5},
        {"name": "文言文", "category": TagCategoryEnum.GENRE, "display_order": 6},
        {"name": "神话传说", "category": TagCategoryEnum.GENRE, "display_order": 7},
        {"name": "历史故事", "category": TagCategoryEnum.GENRE, "display_order": 8},
        
        # 来源系列
        {"name": "伊索寓言", "category": TagCategoryEnum.SOURCE, "display_order": 1},
        {"name": "安徒生童话", "category": TagCategoryEnum.SOURCE, "display_order": 2},
        {"name": "格林童话", "category": TagCategoryEnum.SOURCE, "display_order": 3},
        {"name": "中国神话", "category": TagCategoryEnum.SOURCE, "display_order": 4},
        {"name": "唐诗三百首", "category": TagCategoryEnum.SOURCE, "display_order": 5},
        {"name": "宋词精选", "category": TagCategoryEnum.SOURCE, "display_order": 6},
        {"name": "成语故事", "category": TagCategoryEnum.SOURCE, "display_order": 7},
        
        # 主题标签
        {"name": "勇气", "category": TagCategoryEnum.THEME, "display_order": 1},
        {"name": "友谊", "category": TagCategoryEnum.THEME, "display_order": 2},
        {"name": "诚实", "category": TagCategoryEnum.THEME, "display_order": 3},
        {"name": "善良", "category": TagCategoryEnum.THEME, "display_order": 4},
        {"name": "智慧", "category": TagCategoryEnum.THEME, "display_order": 5},
        {"name": "自然", "category": TagCategoryEnum.THEME, "display_order": 6},
        {"name": "科学", "category": TagCategoryEnum.THEME, "display_order": 7},
        {"name": "亲情", "category": TagCategoryEnum.THEME, "display_order": 8},
        
        # 文化来源
        {"name": "中国传统", "category": TagCategoryEnum.CULTURE, "display_order": 1},
        {"name": "西方经典", "category": TagCategoryEnum.CULTURE, "display_order": 2},
        {"name": "日本故事", "category": TagCategoryEnum.CULTURE, "display_order": 3},
        {"name": "印度寓言", "category": TagCategoryEnum.CULTURE, "display_order": 4},
        
        # 改编程度
        {"name": "原文", "category": TagCategoryEnum.ADAPTATION, "display_order": 1},
        {"name": "简化版", "category": TagCategoryEnum.ADAPTATION, "display_order": 2},
        {"name": "白话改编", "category": TagCategoryEnum.ADAPTATION, "display_order": 3},
    ]
    
    async with AsyncSessionLocal() as session:
        for tag_data in tags:
            tag = Tag(**tag_data)
            session.add(tag)
        await session.commit()
        print(f"✓ 创建了 {len(tags)} 个标签")


async def init_abilities():
    """初始化能力维度数据"""
    abilities = [
        # 信息获取能力
        {
            "name": "细节提取",
            "code": "detail_extraction",
            "category": AbilityCategoryEnum.INFORMATION,
            "description": "找到文中明确写出的具体信息",
            "display_order": 1
        },
        {
            "name": "关键信息定位",
            "code": "key_info_location",
            "category": AbilityCategoryEnum.INFORMATION,
            "description": "定位时间、地点、人物等关键要素",
            "display_order": 2
        },
        
        # 理解与概括能力
        {
            "name": "主旨概括",
            "code": "main_idea",
            "category": AbilityCategoryEnum.COMPREHENSION,
            "description": "归纳文章中心思想、主要内容",
            "display_order": 3
        },
        {
            "name": "词语理解",
            "code": "vocabulary",
            "category": AbilityCategoryEnum.COMPREHENSION,
            "description": "结合语境理解词语含义",
            "display_order": 4
        },
        {
            "name": "段落大意",
            "code": "paragraph_summary",
            "category": AbilityCategoryEnum.COMPREHENSION,
            "description": "理解段落主要内容及段落间关系",
            "display_order": 5
        },
        
        # 分析与推理能力
        {
            "name": "人物分析",
            "code": "character_analysis",
            "category": AbilityCategoryEnum.ANALYSIS,
            "description": "分析人物性格、特点、动机",
            "display_order": 6
        },
        {
            "name": "情感理解",
            "code": "emotion_understanding",
            "category": AbilityCategoryEnum.ANALYSIS,
            "description": "体会人物情感变化、作者情感态度",
            "display_order": 7
        },
        {
            "name": "逻辑推理",
            "code": "logical_inference",
            "category": AbilityCategoryEnum.ANALYSIS,
            "description": "根据已知信息推断隐含意思",
            "display_order": 8
        },
        {
            "name": "因果关系",
            "code": "cause_effect",
            "category": AbilityCategoryEnum.ANALYSIS,
            "description": "理解事件之间的因果逻辑",
            "display_order": 9
        },
        
        # 评价与表达能力
        {
            "name": "观点表达",
            "code": "opinion_expression",
            "category": AbilityCategoryEnum.EXPRESSION,
            "description": "发表个人看法、评价人物或事件",
            "display_order": 10
        },
    ]
    
    async with AsyncSessionLocal() as session:
        for ability_data in abilities:
            ability = AbilityDimension(**ability_data)
            session.add(ability)
        await session.commit()
        print(f"✓ 创建了 {len(abilities)} 个能力维度")


async def init_badges():
    """初始化勋章数据"""
    badges = [
        # 坚持类
        {
            "name": "阅读新星",
            "description": "首次完成阅读",
            "category": BadgeCategoryEnum.PERSISTENCE,
            "condition_type": BadgeConditionTypeEnum.FIRST_READING,
            "condition_value": 1,
            "display_order": 1
        },
        {
            "name": "三日小达人",
            "description": "连续打卡3天",
            "category": BadgeCategoryEnum.PERSISTENCE,
            "condition_type": BadgeConditionTypeEnum.STREAK_DAYS,
            "condition_value": 3,
            "display_order": 2
        },
        {
            "name": "周冠军",
            "description": "连续打卡7天",
            "category": BadgeCategoryEnum.PERSISTENCE,
            "condition_type": BadgeConditionTypeEnum.STREAK_DAYS,
            "condition_value": 7,
            "display_order": 3
        },
        {
            "name": "月度之星",
            "description": "连续打卡30天",
            "category": BadgeCategoryEnum.PERSISTENCE,
            "condition_type": BadgeConditionTypeEnum.STREAK_DAYS,
            "condition_value": 30,
            "display_order": 4
        },
        
        # 阅读量类
        {
            "name": "小书虫",
            "description": "累计阅读10篇",
            "category": BadgeCategoryEnum.READING,
            "condition_type": BadgeConditionTypeEnum.TOTAL_READINGS,
            "condition_value": 10,
            "display_order": 10
        },
        {
            "name": "博学多才",
            "description": "累计阅读50篇",
            "category": BadgeCategoryEnum.READING,
            "condition_type": BadgeConditionTypeEnum.TOTAL_READINGS,
            "condition_value": 50,
            "display_order": 11
        },
        {
            "name": "阅读狂人",
            "description": "累计阅读100篇",
            "category": BadgeCategoryEnum.READING,
            "condition_type": BadgeConditionTypeEnum.TOTAL_READINGS,
            "condition_value": 100,
            "display_order": 12
        },
        
        # 能力类
        {
            "name": "细节大师",
            "description": "细节提取正确率达90%",
            "category": BadgeCategoryEnum.ABILITY,
            "condition_type": BadgeConditionTypeEnum.ABILITY_ACCURACY,
            "condition_value": 90,
            "condition_extra": "detail_extraction",
            "display_order": 20
        },
        {
            "name": "推理达人",
            "description": "逻辑推理题累计答对20题",
            "category": BadgeCategoryEnum.ABILITY,
            "condition_type": BadgeConditionTypeEnum.ABILITY_COUNT,
            "condition_value": 20,
            "condition_extra": "logical_inference",
            "display_order": 21
        },
        {
            "name": "表达之星",
            "description": "完成10道简答题",
            "category": BadgeCategoryEnum.ABILITY,
            "condition_type": BadgeConditionTypeEnum.ABILITY_COUNT,
            "condition_value": 10,
            "condition_extra": "opinion_expression",
            "display_order": 22
        },
        
        # 探索类
        {
            "name": "童话爱好者",
            "description": "阅读10篇童话",
            "category": BadgeCategoryEnum.EXPLORE,
            "condition_type": BadgeConditionTypeEnum.GENRE_COUNT,
            "condition_value": 10,
            "condition_extra": "童话",
            "display_order": 30
        },
        {
            "name": "诗词达人",
            "description": "阅读10篇古诗词",
            "category": BadgeCategoryEnum.EXPLORE,
            "condition_type": BadgeConditionTypeEnum.GENRE_COUNT,
            "condition_value": 10,
            "condition_extra": "古诗词",
            "display_order": 31
        },
        {
            "name": "全能选手",
            "description": "阅读过所有文体",
            "category": BadgeCategoryEnum.EXPLORE,
            "condition_type": BadgeConditionTypeEnum.ALL_GENRES,
            "condition_value": 1,
            "display_order": 32
        },
    ]
    
    async with AsyncSessionLocal() as session:
        for badge_data in badges:
            badge = Badge(**badge_data)
            session.add(badge)
        await session.commit()
        print(f"✓ 创建了 {len(badges)} 个勋章")


async def main():
    """执行所有初始化"""
    print("开始初始化数据...")
    await init_tags()
    await init_abilities()
    await init_badges()
    print("✓ 所有基础数据初始化完成！")


if __name__ == "__main__":
    asyncio.run(main())
