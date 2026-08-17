"""
Engineer API router.
GET  /engineer/tickets
GET  /engineer/tickets/{ticket_id}
POST /engineer/tickets/{ticket_id}/remarks
POST /engineer/tickets/{ticket_id}/resolve
POST /engineer/tickets/{ticket_id}/close
GET  /engineer/tickets/{ticket_id}/history
GET  /engineer/dashboard
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from backend.core.database import get_db
from backend.schemas.ticket import (
    TicketResponse, EngineerRemarksRequest,
    ResolveTicketRequest, CloseTicketRequest, TicketHistoryItem
)
from backend.services.auth_service import AuthService
from backend.services.ticket_service import TicketService
from backend.routers.user import _build_ticket_response

router = APIRouter(prefix="/engineer", tags=["engineer"])
logger = logging.getLogger(__name__)


def _require_engineer(engineer_id: int, db: Session):
    engineer = AuthService.get_user_by_id(db, engineer_id)
    if not engineer:
        raise HTTPException(status_code=403, detail="Engineer not found")
    if engineer.role != "engineer":
        raise HTTPException(status_code=403, detail="Engineer access required")
    if engineer.status != "approved":
        raise HTTPException(status_code=403, detail="Engineer account not yet approved")
    return engineer


@router.get("/dashboard")
def get_engineer_dashboard(engineer_id: int, db: Session = Depends(get_db)):
    """Return KPI data for engineer dashboard."""
    engineer = _require_engineer(engineer_id, db)

    all_tickets = TicketService.get_engineer_tickets(db, engineer_id)

    open_count = sum(1 for t in all_tickets if t.status == "pending")
    escalated_count = sum(1 for t in all_tickets if t.status == "escalated")
    resolved_count = sum(1 for t in all_tickets if t.status == "resolved")
    closed_count = sum(1 for t in all_tickets if t.status == "closed")
    high_priority = sum(1 for t in all_tickets if t.priority in ("P1", "P2"))

    # Priority breakdown
    priority_counts = {"P1": 0, "P2": 0, "P3": 0, "P4": 0}
    for t in all_tickets:
        if t.priority and str(t.priority) in priority_counts:
            priority_counts[str(t.priority)] += 1

    # Category breakdown
    category_counts = {}
    for t in all_tickets:
        cat = str(t.category) if t.category else "Unclassified"
        category_counts[cat] = category_counts.get(cat, 0) + 1

    # Recent activity — last 10 updated tickets
    recent = sorted(all_tickets, key=lambda t: t.updated_at, reverse=True)[:10]
    recent_activity = []
    for t in recent:
        recent_activity.append({
            "ticket_id": t.id,
            "title": t.title,
            "status": str(t.status),
            "updated_at": t.updated_at.isoformat(),
        })

    return {
        "engineer_name": engineer.name,
        "kpi": {
            "open": open_count,
            "escalated": escalated_count,
            "resolved": resolved_count,
            "closed": closed_count,
            "high_priority": high_priority,
            "total": len(all_tickets),
        },
        "priority_counts": priority_counts,
        "category_counts": category_counts,
        "recent_activity": recent_activity,
    }


@router.get("/tickets", response_model=list[TicketResponse])
def get_engineer_tickets(
    engineer_id: int,
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    _require_engineer(engineer_id, db)
    tickets = TicketService.get_engineer_tickets(
        db, engineer_id, status=status, priority=priority,
        category=category, severity=severity, search=search
    )
    return [_build_ticket_response(t) for t in tickets]


@router.get("/tickets/{ticket_id}", response_model=TicketResponse)
def get_ticket_detail(ticket_id: int, engineer_id: int, db: Session = Depends(get_db)):
    _require_engineer(engineer_id, db)
    ticket = TicketService.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if ticket.assigned_engineer_id != engineer_id:
        raise HTTPException(status_code=403, detail="This ticket is not assigned to you")
    return _build_ticket_response(ticket)


@router.post("/tickets/{ticket_id}/remarks")
def add_remarks(ticket_id: int, data: EngineerRemarksRequest, db: Session = Depends(get_db)):
    _require_engineer(data.engineer_id, db)
    ticket, error = TicketService.add_remarks(db, ticket_id, data.engineer_id, data.remarks)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {"message": "Remarks updated", "ticket_id": ticket_id}


@router.post("/tickets/{ticket_id}/resolve")
def resolve_ticket(ticket_id: int, data: ResolveTicketRequest, db: Session = Depends(get_db)):
    _require_engineer(data.engineer_id, db)
    ticket, error = TicketService.resolve_ticket(db, ticket_id, data)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {"message": "Ticket resolved successfully", "ticket_id": ticket_id, "status": str(ticket.status)}


@router.post("/tickets/{ticket_id}/close")
def close_ticket(ticket_id: int, data: CloseTicketRequest, db: Session = Depends(get_db)):
    # Allow both engineer and admin to close
    user = AuthService.get_user_by_id(db, data.closed_by_id)
    if not user or user.role not in ("engineer", "admin"):
        raise HTTPException(status_code=403, detail="Not authorized")
    ticket, error = TicketService.close_ticket(db, ticket_id, data)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {"message": "Ticket closed successfully", "ticket_id": ticket_id, "status": str(ticket.status)}


@router.get("/tickets/{ticket_id}/history", response_model=list[TicketHistoryItem])
def get_ticket_history(ticket_id: int, engineer_id: int, db: Session = Depends(get_db)):
    _require_engineer(engineer_id, db)
    history = TicketService.get_ticket_history(db, ticket_id)
    return [
        TicketHistoryItem(
            id=h.id,
            old_status=h.old_status,
            new_status=h.new_status,
            remarks=h.remarks,
            changed_by_name=h.changed_by.name if h.changed_by else "System",
            created_at=h.created_at,
        )
        for h in history
    ]
