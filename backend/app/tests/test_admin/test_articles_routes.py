import pytest
from app.utils.security import create_access_token
from app.schemas.admin.article import ArticleCreateRequest, DifficultyEnum


@pytest.fixture
def admin_headers():
    token = create_access_token({"sub": "admin", "role": "admin"})
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_admin_require_auth(async_client):
    response = await async_client.get("/api/v1/admin/articles/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_article(async_client, admin_headers):
    response = await async_client.post(
        "/api/v1/admin/articles/",
        headers=admin_headers,
        json={
            "title": "测试文章",
            "content": "这是测试内容" * 10,
            "article_difficulty": 1,
            "tag_ids": []
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["title"] == "测试文章"
    assert data["data"]["status"] == "draft"


@pytest.mark.asyncio
async def test_get_article_list(async_client, admin_headers, test_article):
    response = await async_client.get("/api/v1/admin/articles/", headers=admin_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["total"] >= 1
    assert len(data["data"]["items"]) >= 1


@pytest.mark.asyncio
async def test_get_article_detail(async_client, admin_headers, test_article):
    response = await async_client.get(
        f"/api/v1/admin/articles/{test_article.id}",
        headers=admin_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["id"] == test_article.id
    assert data["data"]["title"] == test_article.title


@pytest.mark.asyncio
async def test_update_article(async_client, admin_headers, test_article):
    response = await async_client.put(
        f"/api/v1/admin/articles/{test_article.id}",
        headers=admin_headers,
        json={
            "title": "更新后的标题"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["title"] == "更新后的标题"


@pytest.mark.asyncio
async def test_delete_article(async_client, admin_headers, test_article):
    response = await async_client.delete(
        f"/api/v1/admin/articles/{test_article.id}",
        headers=admin_headers
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "删除成功"


@pytest.mark.asyncio
async def test_publish_article(async_client, admin_headers, test_article):
    response = await async_client.post(
        f"/api/v1/admin/articles/{test_article.id}/publish",
        headers=admin_headers
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "发布成功"


@pytest.mark.asyncio
async def test_archive_article(async_client, admin_headers, test_article):
    response = await async_client.post(
        f"/api/v1/admin/articles/{test_article.id}/archive",
        headers=admin_headers
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "归档成功"


@pytest.mark.asyncio
async def test_get_article_not_found(async_client, admin_headers):
    response = await async_client.get(
        "/api/v1/admin/articles/99999",
        headers=admin_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_article_not_found(async_client, admin_headers):
    response = await async_client.put(
        "/api/v1/admin/articles/99999",
        headers=admin_headers,
        json={"title": "新标题"}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_article_not_found(async_client, admin_headers):
    response = await async_client.delete(
        "/api/v1/admin/articles/99999",
        headers=admin_headers
    )
    assert response.status_code == 404
