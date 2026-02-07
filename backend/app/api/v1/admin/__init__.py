from fastapi import APIRouter
from app.api.v1.admin import articles, questions, dashboard

router = APIRouter()

router.include_router(articles.router, prefix="/articles", tags=["管理-文章"])
router.include_router(questions.router, prefix="/questions", tags=["管理-题目"])
router.include_router(dashboard.router, prefix="/dashboard", tags=["管理-仪表盘"])
