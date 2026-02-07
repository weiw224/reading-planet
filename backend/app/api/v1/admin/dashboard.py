from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_admin_user
from app.schemas.common import ResponseModel
from app.schemas.admin.user import DashboardStats
from app.services.admin.dashboard_service import dashboard_service

router = APIRouter()


@router.get("/", response_model=ResponseModel[DashboardStats])
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    stats = await dashboard_service.get_stats(db)
    return ResponseModel(data=stats)
