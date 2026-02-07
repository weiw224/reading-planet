from fastapi import APIRouter
from app.api.v1 import auth, users, articles, questions, progress, admin

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(articles.router, prefix="/articles", tags=["文章"])
api_router.include_router(questions.router, prefix="/questions", tags=["题目"])
api_router.include_router(progress.router, prefix="/progress", tags=["学习进度"])
api_router.include_router(admin.router, prefix="/admin", tags=["管理后台"])
