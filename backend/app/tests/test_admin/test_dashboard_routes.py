import pytest
from app.utils.security import create_access_token


@pytest.fixture
def admin_headers():
    token = create_access_token({"sub": "admin", "role": "admin"})
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_dashboard_require_auth(async_client):
    response = await async_client.get("/api/v1/admin/dashboard/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_dashboard(async_client, admin_headers):
    response = await async_client.get("/api/v1/admin/dashboard/", headers=admin_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "total_users" in data["data"]
    assert "active_users_today" in data["data"]
    assert "active_users_week" in data["data"]
    assert "total_articles" in data["data"]
    assert "published_articles" in data["data"]
    assert "total_questions" in data["data"]
    assert "total_readings" in data["data"]
    assert "checkins_today" in data["data"]


@pytest.mark.asyncio
async def test_dashboard_with_data(async_client, admin_headers, test_user, test_article, test_question):
    response = await async_client.get("/api/v1/admin/dashboard/", headers=admin_headers)
    
    assert response.status_code == 200
    data = response.json()
    stats = data["data"]
    
    assert stats["total_users"] >= 1
    assert stats["total_articles"] >= 1
    assert stats["total_questions"] >= 1
    assert isinstance(stats["active_users_today"], int)
    assert isinstance(stats["active_users_week"], int)
    assert isinstance(stats["published_articles"], int)
    assert isinstance(stats["total_readings"], int)
    assert isinstance(stats["checkins_today"], int)
