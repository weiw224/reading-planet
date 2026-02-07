import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user_optional, get_current_user, get_admin_user
from app.utils.exceptions import AuthenticationError, NotFoundError
from app.models.user import User, GradeEnum


@pytest.mark.asyncio
async def test_get_current_user_optional_no_auth_header():
    """测试没有认证头时返回None"""
    with patch('app.api.deps.get_db') as mock_get_db:
        mock_session = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_session
        
        result = await get_current_user_optional(authorization=None, db=mock_session)
        
        assert result is None


@pytest.mark.asyncio
async def test_get_current_user_optional_invalid_token_format():
    """测试无效的token格式返回None"""
    with patch('app.api.deps.get_db') as mock_get_db:
        mock_session = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_session
        
        result = await get_current_user_optional(authorization="InvalidFormat", db=mock_session)
        
        assert result is None


@pytest.mark.asyncio
async def test_get_current_user_optional_invalid_token():
    """测试无效的token返回None"""
    with patch('app.api.deps.get_db') as mock_get_db:
        mock_session = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_session
        
        result = await get_current_user_optional(authorization="Bearer invalid_token", db=mock_session)
        
        assert result is None


@pytest.mark.asyncio
async def test_get_current_user_optional_valid_token():
    """测试有效的token返回用户"""
    from app.utils.security import create_access_token
    
    with patch('app.api.deps.get_db') as mock_get_db:
        mock_session = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_session
        
        token = create_access_token({"sub": "123", "role": "user"})
        
        mock_user = User(
            id=123,
            openid="test_openid",
            nickname="测试用户",
            avatar_url="http://example.com/avatar.jpg",
            grade=GradeEnum.GRADE_3
        )
        
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        result = await get_current_user_optional(authorization=f"Bearer {token}", db=mock_session)
        
        assert result is not None
        assert result.id == 123
        assert result.nickname == "测试用户"


@pytest.mark.asyncio
async def test_get_current_user_optional_database_error():
    """测试数据库错误时返回None"""
    from app.utils.security import create_access_token
    from sqlalchemy.exc import SQLAlchemyError
    
    with patch('app.api.deps.get_db') as mock_get_db:
        mock_session = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_session
        
        token = create_access_token({"sub": "123", "role": "user"})
        
        mock_session.execute = AsyncMock(side_effect=SQLAlchemyError("Database error"))
        
        result = await get_current_user_optional(authorization=f"Bearer {token}", db=mock_session)
        
        assert result is None


@pytest.mark.asyncio
async def test_get_current_user_with_user():
    """测试有用户时返回用户"""
    mock_user = User(
        id=123,
        openid="test_openid",
        nickname="测试用户"
    )
    
    result = await get_current_user(user=mock_user)
    
    assert result is not None
    assert result.id == 123
    assert result.nickname == "测试用户"


@pytest.mark.asyncio
async def test_get_current_user_without_user():
    """测试没有用户时抛出异常"""
    with pytest.raises(AuthenticationError) as exc_info:
        await get_current_user(user=None)
    
    assert exc_info.value.detail["code"] == 1001
    assert exc_info.value.detail["message"] == "请先登录"


@pytest.mark.asyncio
async def test_get_admin_user_no_auth():
    """测试没有认证头时抛出异常"""
    with patch('app.api.deps.get_db') as mock_get_db:
        mock_session = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_session
        
        with pytest.raises(AuthenticationError) as exc_info:
            await get_admin_user(authorization=None, db=mock_session)
        
        assert exc_info.value.detail["code"] == 1001
        assert exc_info.value.detail["message"] == "请先登录"


@pytest.mark.asyncio
async def test_get_admin_user_invalid_token_format():
    """测试无效的token格式时抛出异常"""
    with patch('app.api.deps.get_db') as mock_get_db:
        mock_session = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_session
        
        with pytest.raises(AuthenticationError) as exc_info:
            await get_admin_user(authorization="InvalidFormat", db=mock_session)
        
        assert exc_info.value.detail["code"] == 1001
        assert exc_info.value.detail["message"] == "Token 格式错误"


@pytest.mark.asyncio
async def test_get_admin_user_invalid_token():
    """测试无效的token时抛出异常"""
    with patch('app.api.deps.get_db') as mock_get_db:
        mock_session = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_session
        
        with pytest.raises(AuthenticationError) as exc_info:
            await get_admin_user(authorization="Bearer invalid_token", db=mock_session)
        
        assert exc_info.value.detail["code"] == 1001
        assert exc_info.value.detail["message"] == "Token 无效或已过期"


@pytest.mark.asyncio
async def test_get_admin_user_not_admin():
    """测试非管理员用户时抛出异常"""
    from app.utils.security import create_access_token
    
    with patch('app.api.deps.get_db') as mock_get_db:
        mock_session = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_session
        
        token = create_access_token({"sub": "123", "role": "user"})
        
        with pytest.raises(AuthenticationError) as exc_info:
            await get_admin_user(authorization=f"Bearer {token}", db=mock_session)
        
        assert exc_info.value.detail["code"] == 1001
        assert exc_info.value.detail["message"] == "需要管理员权限"


@pytest.mark.asyncio
async def test_get_admin_user_missing_user_id():
    """测试token中缺少用户ID时抛出异常"""
    from app.utils.security import create_access_token
    
    with patch('app.api.deps.get_db') as mock_get_db:
        mock_session = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_session
        
        token = create_access_token({"role": "admin"})
        
        with pytest.raises(AuthenticationError) as exc_info:
            await get_admin_user(authorization=f"Bearer {token}", db=mock_session)
        
        assert exc_info.value.detail["code"] == 1001
        assert exc_info.value.detail["message"] == "Token 中缺少用户信息"


@pytest.mark.asyncio
async def test_get_admin_user_not_found():
    """测试管理员用户不存在时抛出异常"""
    from app.utils.security import create_access_token
    
    with patch('app.api.deps.get_db') as mock_get_db:
        mock_session = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_session
        
        token = create_access_token({"sub": "999", "role": "admin"})
        
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        with pytest.raises(NotFoundError) as exc_info:
            await get_admin_user(authorization=f"Bearer {token}", db=mock_session)
        
        assert exc_info.value.detail["code"] == 1003
        assert exc_info.value.detail["message"] == "管理员用户不存在"


@pytest.mark.asyncio
async def test_get_admin_user_success():
    """测试成功获取管理员用户"""
    from app.utils.security import create_access_token
    
    with patch('app.api.deps.get_db') as mock_get_db:
        mock_session = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_session
        
        token = create_access_token({"sub": "123", "role": "admin"})
        
        mock_user = User(
            id=123,
            openid="admin_openid",
            nickname="管理员",
            avatar_url="http://example.com/admin.jpg",
            grade=GradeEnum.GRADE_6
        )
        
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        result = await get_admin_user(authorization=f"Bearer {token}", db=mock_session)
        
        assert result is not None
        assert isinstance(result, User)
        assert result.id == 123
        assert result.nickname == "管理员"


@pytest.mark.asyncio
async def test_get_admin_user_database_error():
    """测试数据库错误时抛出异常"""
    from app.utils.security import create_access_token
    from sqlalchemy.exc import SQLAlchemyError
    
    with patch('app.api.deps.get_db') as mock_get_db:
        mock_session = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_session
        
        token = create_access_token({"sub": "123", "role": "admin"})
        
        mock_session.execute = AsyncMock(side_effect=SQLAlchemyError("Database error"))
        
        with pytest.raises(AuthenticationError) as exc_info:
            await get_admin_user(authorization=f"Bearer {token}", db=mock_session)
        
        assert exc_info.value.detail["code"] == 1001
        assert exc_info.value.detail["message"] == "数据库查询失败"
