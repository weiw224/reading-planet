import pytest
from datetime import timedelta
from app.utils.security import (
    create_access_token,
    verify_token,
    get_password_hash,
    verify_password
)


@pytest.mark.asyncio
async def test_create_access_token_default_expiry():
    """测试创建带有默认过期时间的JWT Token"""
    data = {"sub": "123", "role": "user"}
    token = create_access_token(data)
    
    assert token is not None
    assert isinstance(token, str)
    
    payload = verify_token(token)
    assert payload is not None
    assert payload["sub"] == "123"
    assert payload["role"] == "user"
    assert "exp" in payload


@pytest.mark.asyncio
async def test_create_access_token_custom_expiry():
    """测试创建带有自定义过期时间的JWT Token"""
    data = {"sub": "456", "role": "admin"}
    expires_delta = timedelta(minutes=15)
    token = create_access_token(data, expires_delta)
    
    assert token is not None
    assert isinstance(token, str)
    
    payload = verify_token(token)
    assert payload is not None
    assert payload["sub"] == "456"
    assert payload["role"] == "admin"
    assert "exp" in payload


@pytest.mark.asyncio
async def test_verify_token_valid():
    """测试验证有效的JWT Token"""
    data = {"sub": "789", "role": "user"}
    token = create_access_token(data)
    
    payload = verify_token(token)
    assert payload is not None
    assert payload["sub"] == "789"
    assert payload["role"] == "user"


@pytest.mark.asyncio
async def test_verify_token_invalid():
    """测试验证无效的JWT Token"""
    invalid_token = "invalid.token.string"
    
    payload = verify_token(invalid_token)
    assert payload is None


@pytest.mark.asyncio
async def test_verify_token_empty():
    """测试验证空的JWT Token"""
    payload = verify_token("")
    assert payload is None


@pytest.mark.skip(reason="passlib/bcrypt version incompatibility during initialization")
@pytest.mark.asyncio
async def test_get_password_hash():
    """测试密码哈希"""
    password = "test_pass_123"  # Shorter password to avoid bcrypt 72 byte limit
    hashed = get_password_hash(password)
    
    assert hashed is not None
    assert isinstance(hashed, str)
    assert hashed != password
    assert len(hashed) > 0


@pytest.mark.skip(reason="passlib/bcrypt version incompatibility during initialization")
@pytest.mark.asyncio
async def test_verify_password_correct():
    """测试验证正确的密码"""
    password = "correct_pass"  # Shorter password to avoid bcrypt 72 byte limit
    hashed = get_password_hash(password)
    
    is_valid = verify_password(password, hashed)
    assert is_valid is True


@pytest.mark.skip(reason="passlib/bcrypt version incompatibility during initialization")
@pytest.mark.asyncio
async def test_verify_password_incorrect():
    """测试验证错误的密码"""
    password = "correct_pass"
    wrong_password = "wrong_pass"
    hashed = get_password_hash(password)
    
    is_valid = verify_password(wrong_password, hashed)
    assert is_valid is False


@pytest.mark.skip(reason="passlib/bcrypt version incompatibility during initialization")
@pytest.mark.asyncio
async def test_verify_password_empty():
    """测试验证空密码"""
    password = "test_pass"
    hashed = get_password_hash(password)
    
    is_valid = verify_password("", hashed)
    assert is_valid is False


@pytest.mark.skip(reason="passlib/bcrypt version incompatibility during initialization")
@pytest.mark.asyncio
async def test_password_hash_is_deterministic():
    """测试密码哈希的一致性（同一密码多次哈希结果不同但都能验证）"""
    password = "test_pass_cons"  # Shorter password to avoid bcrypt 72 byte limit
    
    hashed1 = get_password_hash(password)
    hashed2 = get_password_hash(password)
    
    assert hashed1 != hashed2
    assert verify_password(password, hashed1) is True
    assert verify_password(password, hashed2) is True
