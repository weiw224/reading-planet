import pytest
from app.utils.security import create_access_token
from app.schemas.admin.question import QuestionTypeEnum, DifficultyEnum


@pytest.fixture
def admin_headers():
    token = create_access_token({"sub": "admin", "role": "admin"})
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_admin_questions_require_auth(async_client):
    response = await async_client.get("/api/v1/admin/questions/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_question_choice(async_client, admin_headers, test_article):
    response = await async_client.post(
        "/api/v1/admin/questions/",
        headers=admin_headers,
        json={
            "article_id": test_article.id,
            "type": "choice",
            "content": "这是什么颜色？",
            "options": ["红色", "蓝色", "绿色", "黄色"],
            "answer": "红色",
            "difficulty": 1,
            "display_order": 1,
            "abilities": []
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["type"] == "choice"
    assert data["data"]["content"] == "这是什么颜色？"
    assert data["data"]["answer"] == "红色"


@pytest.mark.asyncio
async def test_create_question_judge(async_client, admin_headers, test_article):
    response = await async_client.post(
        "/api/v1/admin/questions/",
        headers=admin_headers,
        json={
            "article_id": test_article.id,
            "type": "judge",
            "content": "这是对的吗？",
            "answer": "对",
            "difficulty": 1
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["type"] == "judge"
    assert data["data"]["content"] == "这是对的吗？"


@pytest.mark.asyncio
async def test_create_question_choice_without_options(async_client, admin_headers, test_article):
    response = await async_client.post(
        "/api/v1/admin/questions/",
        headers=admin_headers,
        json={
            "article_id": test_article.id,
            "type": "choice",
            "content": "测试问题",
            "answer": "A"
        }
    )
    
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_question_list(async_client, admin_headers, test_question):
    response = await async_client.get("/api/v1/admin/questions/", headers=admin_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["total"] >= 1
    assert len(data["data"]["items"]) >= 1


@pytest.mark.asyncio
async def test_get_question_list_with_filters(async_client, admin_headers, test_question):
    response = await async_client.get(
        "/api/v1/admin/questions/?question_type=choice",
        headers=admin_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


@pytest.mark.asyncio
async def test_get_question_detail(async_client, admin_headers, test_question):
    response = await async_client.get(
        f"/api/v1/admin/questions/{test_question.id}",
        headers=admin_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["id"] == test_question.id
    assert data["data"]["content"] == test_question.content


@pytest.mark.asyncio
async def test_update_question(async_client, admin_headers, test_question):
    response = await async_client.put(
        f"/api/v1/admin/questions/{test_question.id}",
        headers=admin_headers,
        json={
            "content": "更新后的问题",
            "difficulty": 2
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["content"] == "更新后的问题"


@pytest.mark.asyncio
async def test_delete_question(async_client, admin_headers, test_question):
    response = await async_client.delete(
        f"/api/v1/admin/questions/{test_question.id}",
        headers=admin_headers
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "删除成功"


@pytest.mark.asyncio
async def test_get_question_not_found(async_client, admin_headers):
    response = await async_client.get(
        "/api/v1/admin/questions/99999",
        headers=admin_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_question_not_found(async_client, admin_headers):
    response = await async_client.put(
        "/api/v1/admin/questions/99999",
        headers=admin_headers,
        json={"content": "新问题"}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_question_not_found(async_client, admin_headers):
    response = await async_client.delete(
        "/api/v1/admin/questions/99999",
        headers=admin_headers
    )
    assert response.status_code == 404
