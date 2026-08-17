"""
Analytics API router.
GET /analytics/
GET /reports/
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.schemas.analytics import AnalyticsSummary
from backend.services.auth_service import AuthService
from backend.services.analytics_service import AnalyticsService

router = APIRouter(tags=["analytics"])
logger = logging.getLogger(__name__)


def _require_admin(admin_id: int, db: Session):
    admin = AuthService.get_user_by_id(db, admin_id)
    if not admin or admin.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return admin


@router.get("/analytics/", response_model=AnalyticsSummary)
def get_analytics(admin_id: int, db: Session = Depends(get_db)):
    _require_admin(admin_id, db)
    return AnalyticsService.get_summary(db)


@router.get("/reports/", response_model=AnalyticsSummary)
def get_reports(admin_id: int, db: Session = Depends(get_db)):
    """Reports endpoint returns the same analytics data as analytics."""
    _require_admin(admin_id, db)
    return AnalyticsService.get_summary(db)
