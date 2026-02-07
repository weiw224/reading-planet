from typing import TypeVar, Generic, Optional, List
from pydantic import BaseModel

T = TypeVar('T')


class ResponseModel(BaseModel, Generic[T]):
    """通用响应模型"""
    code: int = 0
    message: str = "success"
    data: Optional[T] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应模型"""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class ErrorResponse(BaseModel):
    """错误响应模型"""
    code: int
    message: str
    detail: Optional[str] = None
