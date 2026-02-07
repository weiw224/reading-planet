import pytest
from httpx import AsyncClient
from datetime import date
from unittest.mock import patch


@pytest.mark.asyncio
async def test_get_current_user_info(async_client: AsyncClient, db_session, auth_headers):
    """测试获取当前用户信息"""
    response = await async_client.get(
        "/api/v1/users/me",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "id" in data["data"]
    assert "nickname" in data["data"]
    assert "avatar_url" in data["data"]
    assert "grade" in data["data"]
    assert "total_readings" in data["data"]
    assert "streak_days" in data["data"]
    assert "max_streak_days" in data["data"]


@pytest.mark.asyncio
async def test_get_current_user_info_unauthorized(async_client: AsyncClient):
    """测试未登录获取用户信息"""
    response = await async_client.get("/api/v1/users/me")
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_user_nickname(async_client: AsyncClient, db_session, auth_headers, test_user):
    """测试更新用户昵称"""
    response = await async_client.put(
        "/api/v1/users/me",
        json={"nickname": "新昵称"},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["nickname"] == "新昵称"


@pytest.mark.asyncio
async def test_update_user_grade(async_client: AsyncClient, db_session, auth_headers, test_user):
    """测试更新用户年级"""
    from app.models.user import GradeEnum
    
    response = await async_client.put(
        "/api/v1/users/me",
        json={"grade": "3年级"},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["grade"] == "3年级"


@pytest.mark.asyncio
async def test_update_user_avatar(async_client: AsyncClient, db_session, auth_headers, test_user):
    """测试更新用户头像"""
    response = await async_client.put(
        "/api/v1/users/me",
        json={"avatar_url": "https://example.com/avatar.jpg"},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["avatar_url"] == "https://example.com/avatar.jpg"


@pytest.mark.asyncio
async def test_get_user_stats(async_client: AsyncClient, db_session, auth_headers, test_user):
    """测试获取用户统计数据"""
    response = await async_client.get(
        "/api/v1/users/me/stats",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "total_readings" in data["data"]
    assert "total_questions" in data["data"]
    assert "correct_rate" in data["data"]
    assert "streak_days" in data["data"]
    assert "max_streak_days" in data["data"]
    assert "total_badges" in data["data"]
    assert "total_time" in data["data"]
    assert data["data"]["total_readings"] == 0
    assert data["data"]["total_questions"] == 0


@pytest.mark.asyncio
async def test_get_user_stats_with_data(
    async_client: AsyncClient, 
    db_session, 
    auth_headers, 
    test_user,
    test_article,
    test_question
):
    """测试获取用户统计数据 - 有学习数据"""
    from app.models.progress import UserProgress, QuestionAnswer
    from app.models.ability import AbilityDimension, AbilityCategoryEnum
    
    ability = AbilityDimension(
        name="细节提取",
        code="detail_extraction",
        category=AbilityCategoryEnum.COMPREHENSION,
        display_order=1
    )
    db_session.add(ability)
    await db_session.commit()
    
    progress = UserProgress(
        user_id=test_user.id,
        article_id=test_article.id,
        score=85,
        correct_count=3,
        total_count=4,
        time_spent=300
    )
    db_session.add(progress)
    await db_session.commit()
    
    answer1 = QuestionAnswer(
        progress_id=progress.id,
        question_id=test_question.id,
        user_answer="A",
        is_correct=True
    )
    answer2 = QuestionAnswer(
        progress_id=progress.id,
        question_id=test_question.id,
        user_answer="B",
        is_correct=False
    )
    db_session.add(answer1)
    db_session.add(answer2)
    await db_session.commit()
    
    test_user.total_readings = 1
    await db_session.commit()
    
    response = await async_client.get(
        "/api/v1/users/me/stats",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["total_readings"] == 1
    assert data["data"]["total_questions"] == 2
    assert data["data"]["correct_rate"] == 50.0
    assert data["data"]["total_time"] == 5


@pytest.mark.asyncio
async def test_get_ability_radar(async_client: AsyncClient, db_session, auth_headers, test_user):
    """测试获取能力雷达图数据"""
    from app.models.ability import AbilityDimension, AbilityCategoryEnum
    
    ability1 = AbilityDimension(
        name="细节提取",
        code="detail_extraction",
        category=AbilityCategoryEnum.COMPREHENSION,
        display_order=1
    )
    ability2 = AbilityDimension(
        name="主旨概括",
        code="main_idea",
        category=AbilityCategoryEnum.COMPREHENSION,
        display_order=2
    )
    db_session.add(ability1)
    db_session.add(ability2)
    await db_session.commit()
    
    response = await async_client.get(
        "/api/v1/users/me/abilities",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert len(data["data"]["abilities"]) == 2
    assert data["data"]["abilities"][0]["ability_name"] == "细节提取"
    assert data["data"]["abilities"][0]["score"] == 0
    assert data["data"]["abilities"][0]["correct_count"] == 0
    assert data["data"]["abilities"][0]["total_count"] == 0


@pytest.mark.asyncio
async def test_get_ability_radar_with_scores(
    async_client: AsyncClient, 
    db_session, 
    auth_headers, 
    test_user
):
    """测试获取能力雷达图数据 - 有分数"""
    from app.models.ability import AbilityDimension, AbilityCategoryEnum
    from app.models.user_ability import UserAbility
    
    ability = AbilityDimension(
        name="细节提取",
        code="detail_extraction",
        category=AbilityCategoryEnum.COMPREHENSION,
        display_order=1
    )
    db_session.add(ability)
    await db_session.commit()
    
    user_ability = UserAbility(
        user_id=test_user.id,
        ability_id=ability.id,
        correct_count=8,
        total_count=10,
        score=80.0
    )
    db_session.add(user_ability)
    await db_session.commit()
    
    response = await async_client.get(
        "/api/v1/users/me/abilities",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["abilities"][0]["score"] == 80.0
    assert data["data"]["abilities"][0]["correct_count"] == 8
    assert data["data"]["abilities"][0]["total_count"] == 10


@pytest.mark.asyncio
async def test_get_checkins(async_client: AsyncClient, db_session, auth_headers, test_user):
    """测试获取打卡记录"""
    from app.models.checkin import CheckIn
    from datetime import date
    
    today = date.today()
    checkin = CheckIn(
        user_id=test_user.id,
        check_date=today
    )
    db_session.add(checkin)
    test_user.streak_days = 5
    await db_session.commit()
    
    response = await async_client.get(
        f"/api/v1/users/me/checkins?year={today.year}&month={today.month}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["current_streak"] == 5
    assert len(data["data"]["records"]) == 1
    assert data["data"]["records"][0]["date"] == today.isoformat()


@pytest.mark.asyncio
async def test_get_checkins_default_params(async_client: AsyncClient, db_session, auth_headers, test_user):
    """测试获取打卡记录 - 默认年月"""
    from app.models.checkin import CheckIn
    from datetime import date
    
    today = date.today()
    checkin = CheckIn(
        user_id=test_user.id,
        check_date=today
    )
    db_session.add(checkin)
    await db_session.commit()
    
    response = await async_client.get(
        "/api/v1/users/me/checkins",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert len(data["data"]["records"]) == 1


@pytest.mark.asyncio
async def test_get_checkins_empty(async_client: AsyncClient, db_session, auth_headers, test_user):
    """测试获取打卡记录 - 无打卡"""
    response = await async_client.get(
        "/api/v1/users/me/checkins",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert len(data["data"]["records"]) == 0
    assert data["data"]["current_streak"] == 0


@pytest.mark.asyncio
async def test_get_badges(async_client: AsyncClient, db_session, auth_headers, test_user):
    """测试获取勋章列表"""
    from app.models.badge import Badge, BadgeCategoryEnum, BadgeConditionTypeEnum, UserBadge
    
    badge1 = Badge(
        name="初出茅庐",
        description="完成首次阅读",
        category=BadgeCategoryEnum.READING,
        condition_type=BadgeConditionTypeEnum.FIRST_READING,
        condition_value=1,
        display_order=1
    )
    badge2 = Badge(
        name="坚持不懈",
        description="连续打卡7天",
        category=BadgeCategoryEnum.PERSISTENCE,
        condition_type=BadgeConditionTypeEnum.STREAK_DAYS,
        condition_value=7,
        display_order=2
    )
    db_session.add(badge1)
    db_session.add(badge2)
    await db_session.commit()
    
    user_badge = UserBadge(
        user_id=test_user.id,
        badge_id=badge1.id
    )
    db_session.add(user_badge)
    await db_session.commit()
    
    response = await async_client.get(
        "/api/v1/users/me/badges",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["total_count"] == 2
    assert data["data"]["earned_count"] == 1
    assert len(data["data"]["badges"]) == 2
    
    earned_badges = [b for b in data["data"]["badges"] if b["earned"]]
    assert len(earned_badges) == 1
    assert earned_badges[0]["name"] == "初出茅庐"
    assert earned_badges[0]["earned_at"] is not None


@pytest.mark.asyncio
async def test_get_badges_empty(async_client: AsyncClient, db_session, auth_headers, test_user):
    """测试获取勋章列表 - 无勋章"""
    response = await async_client.get(
        "/api/v1/users/me/badges",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["total_count"] == 0
    assert data["data"]["earned_count"] == 0
    assert len(data["data"]["badges"]) == 0
