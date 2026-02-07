from fastapi import HTTPException, status


class AppException(HTTPException):
    """应用自定义异常基类"""
    def __init__(self, code: int, message: str, status_code: int = 400):
        super().__init__(status_code=status_code, detail={"code": code, "message": message})


class AuthenticationError(AppException):
    """认证错误"""
    def __init__(self, message: str = "认证失败"):
        super().__init__(code=1001, message=message, status_code=status.HTTP_401_UNAUTHORIZED)


class AuthorizationError(AppException):
    """授权错误"""
    def __init__(self, message: str = "权限不足"):
        super().__init__(code=1002, message=message, status_code=status.HTTP_403_FORBIDDEN)


class NotFoundError(AppException):
    """资源不存在"""
    def __init__(self, message: str = "资源不存在"):
        super().__init__(code=1003, message=message, status_code=status.HTTP_404_NOT_FOUND)


class ValidationError(AppException):
    """验证错误"""
    def __init__(self, message: str = "参数验证失败"):
        super().__init__(code=1004, message=message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
