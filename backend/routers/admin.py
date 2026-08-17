"""
Admin API router.
GET  /admin/engineers/pending
POST /admin/engineers/approve
GET  /admin/tickets/pending
GET  /admin/engineers
POST /admin/assign
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.schemas.user import UserResponse
from backend.schemas.ticket import AssignEngineerRequest, TicketResponse
from backend.services.auth_service import AuthService
from backend.services.ticket_service import TicketService
from backend.routers.user import _build_ticket_response

router = APIRouter(prefix="/admin", tags=["admin"])
logger = logging.getLogger(__name__)


def _require_admin(admin_id: int, db: Session):
    admin = AuthService.get_user_by_id(db, admin_id)
    if not admin or admin.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return admin


@router.get("/engineers/pending", response_model=list[UserResponse])
def get_pending_engineers(admin_id: int, db: Session = Depends(get_db)):
    _require_admin(admin_id, db)
    engineers = AuthService.get_pending_engineers(db)
    return [UserResponse.model_validate(e) for e in engineers]


@router.post("/engineers/approve")
def approve_engineer(engineer_id: int, admin_id: int, db: Session = Depends(get_db)):
    _require_admin(admin_id, db)
    engineer, error = AuthService.approve_engineer(db, engineer_id, admin_id)
    if error:
        raise HTTPException(status_code=404, detail=error)
    return {"message": f"Engineer {engineer.name} approved successfully", "engineer_id": engineer.id}


@router.get("/engineers", response_model=list[UserResponse])
def get_approved_engineers(admin_id: int, db: Session = Depends(get_db)):
    _require_admin(admin_id, db)
    engineers = AuthService.get_approved_engineers(db)
    return [UserResponse.model_validate(e) for e in engineers]


@router.get("/tickets/pending", response_model=list[TicketResponse])
def get_pending_tickets(admin_id: int, db: Session = Depends(get_db)):
    _require_admin(admin_id, db)
    tickets = TicketService.get_all_tickets(db, status="pending")
    return [_build_ticket_response(t) for t in tickets]


@router.get("/tickets", response_model=list[TicketResponse])
def get_all_tickets(admin_id: int, db: Session = Depends(get_db)):
    _require_admin(admin_id, db)
    tickets = TicketService.get_all_tickets(db)
    return [_build_ticket_response(t) for t in tickets]


@router.post("/assign")
def assign_engineer(data: AssignEngineerRequest, db: Session = Depends(get_db)):
    _require_admin(data.admin_id, db)
    ticket, error = TicketService.assign_engineer(db, data)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {"message": "Engineer assigned successfully", "ticket_id": ticket.id, "status": ticket.status}
