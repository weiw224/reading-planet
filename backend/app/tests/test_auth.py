import pytest
from unittest.mock import patch
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_wechat_login_new_user(async_client: AsyncClient):
    """测试微信登录 - 新用户"""
    with patch('app.services.wechat_service.WechatService.code2session') as mock_code2session:
        mock_code2session.return_value = {
            "openid": "test_openid_123",
            "session_key": "test_session_key"
        }

        response = await async_client.post(
            "/api/v1/auth/wechat-login",
            json={"code": "test_code"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "access_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"
        assert data["data"]["expires_in"] == 604800
        assert data["data"]["is_new_user"] is True


@pytest.mark.asyncio
async def test_wechat_login_existing_user(async_client: AsyncClient, db_session):
    """测试微信登录 - 已存在用户"""
    from app.models.user import User
    from sqlalchemy import select

    existing_user = User(openid="existing_openid_456")
    db_session.add(existing_user)
    await db_session.commit()

    with patch('app.services.wechat_service.WechatService.code2session') as mock_code2session:
        mock_code2session.return_value = {
            "openid": "existing_openid_456",
            "session_key": "test_session_key"
        }

        response = await async_client.post(
            "/api/v1/auth/wechat-login",
            json={"code": "test_code"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "access_token" in data["data"]
        assert data["data"]["is_new_user"] is False


@pytest.mark.asyncio
async def test_wechat_login_invalid_code(async_client: AsyncClient):
    """测试微信登录 - 无效code"""
    with patch('app.services.wechat_service.WechatService.code2session') as mock_code2session:
        mock_code2session.return_value = None

        response = await async_client.post(
            "/api/v1/auth/wechat-login",
            json={"code": "invalid_code"}
        )

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data


@pytest.mark.asyncio
async def test_admin_login_success(async_client: AsyncClient):
    """测试管理员登录成功"""
    response = await async_client.post(
        "/api/v1/auth/admin-login",
        json={"username": "admin", "password": "admin123"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "access_token" in data["data"]
    assert data["data"]["token_type"] == "bearer"
    assert data["data"]["expires_in"] == 86400
    assert data["data"]["is_new_user"] is False


@pytest.mark.asyncio
async def test_admin_login_invalid_credentials(async_client: AsyncClient):
    """测试管理员登录失败"""
    response = await async_client.post(
        "/api/v1/auth/admin-login",
        json={"username": "wrong", "password": "wrong"}
    )

    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


