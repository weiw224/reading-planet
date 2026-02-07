import pytest
from fastapi import status
from app.utils.exceptions import (
    AppException,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ValidationError
)


def test_app_exception_basic():
    """测试基础应用异常"""
    exc = AppException(code=9999, message="测试错误", status_code=400)
    
    assert exc.status_code == 400
    assert exc.detail == {"code": 9999, "message": "测试错误"}


def test_app_exception_default_status_code():
    """测试应用异常默认状态码"""
    exc = AppException(code=9998, message="默认状态码错误")
    
    assert exc.status_code == 400


def test_authentication_error_default_message():
    """测试认证错误默认消息"""
    exc = AuthenticationError()
    
    assert exc.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.detail["code"] == 1001
    assert exc.detail["message"] == "认证失败"


def test_authentication_error_custom_message():
    """测试认证错误自定义消息"""
    exc = AuthenticationError(message="自定义认证错误")
    
    assert exc.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.detail["code"] == 1001
    assert exc.detail["message"] == "自定义认证错误"


def test_authorization_error_default_message():
    """测试授权错误默认消息"""
    exc = AuthorizationError()
    
    assert exc.status_code == status.HTTP_403_FORBIDDEN
    assert exc.detail["code"] == 1002
    assert exc.detail["message"] == "权限不足"


def test_authorization_error_custom_message():
    """测试授权错误自定义消息"""
    exc = AuthorizationError(message="没有访问权限")
    
    assert exc.status_code == status.HTTP_403_FORBIDDEN
    assert exc.detail["code"] == 1002
    assert exc.detail["message"] == "没有访问权限"


def test_not_found_error_default_message():
    """测试资源不存在错误默认消息"""
    exc = NotFoundError()
    
    assert exc.status_code == status.HTTP_404_NOT_FOUND
    assert exc.detail["code"] == 1003
    assert exc.detail["message"] == "资源不存在"


def test_not_found_error_custom_message():
    """测试资源不存在错误自定义消息"""
    exc = NotFoundError(message="用户不存在")
    
    assert exc.status_code == status.HTTP_404_NOT_FOUND
    assert exc.detail["code"] == 1003
    assert exc.detail["message"] == "用户不存在"


def test_validation_error_default_message():
    """测试验证错误默认消息"""
    exc = ValidationError()
    
    assert exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert exc.detail["code"] == 1004
    assert exc.detail["message"] == "参数验证失败"


def test_validation_error_custom_message():
    """测试验证错误自定义消息"""
    exc = ValidationError(message="邮箱格式错误")
    
    assert exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert exc.detail["code"] == 1004
    assert exc.detail["message"] == "邮箱格式错误"


def test_exception_codes_are_unique():
    """测试异常代码是否唯一"""
    auth_exc = AuthenticationError()
    authz_exc = AuthorizationError()
    not_found_exc = NotFoundError()
    validation_exc = ValidationError()
    
    codes = [
        auth_exc.detail["code"],
        authz_exc.detail["code"],
        not_found_exc.detail["code"],
        validation_exc.detail["code"]
    ]
    
    assert len(codes) == len(set(codes)), "异常代码必须唯一"


def test_exception_status_codes_are_correct():
    """测试异常状态码是否正确"""
    assert AuthenticationError().status_code == 401
    assert AuthorizationError().status_code == 403
    assert NotFoundError().status_code == 404
    assert ValidationError().status_code == 422


def test_app_exception_inheritance():
    """测试AppException是HTTPException的子类"""
    from fastapi import HTTPException
    
    exc = AppException(code=1, message="test")
    assert isinstance(exc, HTTPException)
