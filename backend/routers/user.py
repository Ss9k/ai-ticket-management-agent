"""
User API router.
POST /user/ai
POST /user/create-ticket
GET  /user/tickets
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.schemas.ticket import AskAIRequest, AskAIResponse, CreateTicketRequest, TicketResponse
from backend.services.auth_service import AuthService
from backend.services.ticket_service import TicketService
from backend.services.ai_service import AIService

router = APIRouter(prefix="/user", tags=["user"])
logger = logging.getLogger(__name__)


def _require_user(user_id: int, db: Session):
    user = AuthService.get_user_by_id(db, user_id)
    if not user or user.role not in ("user", "admin"):
        raise HTTPException(status_code=403, detail="Access denied")
    return user


@router.post("/ai", response_model=AskAIResponse)
def ask_ai(data: AskAIRequest, db: Session = Depends(get_db)):
    """Get AI solution for a described problem."""
    _require_user(data.user_id, db)

    result = AIService.ask_ai(title=data.title, description=data.description)
    return AskAIResponse(
        answer=result["full_response"],
        full_response=result["full_response"],
        context_used=result["context_used"],
        retrieval_summary=result["retrieval_summary"],
    )


@router.post("/create-ticket", response_model=TicketResponse, status_code=201)
def create_ticket(data: CreateTicketRequest, background_tasks: BackgroundTasks,
                  db: Session = Depends(get_db)):
    """Create a ticket after AI solution didn't resolve the problem."""
    user = AuthService.get_user_by_id(db, data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    ticket = TicketService.create_ticket(db, data)

    # Run AI classification asynchronously
    background_tasks.add_task(
        AIService.classify_and_update_ticket,
        db=db,
        ticket_id=ticket.id,
        title=data.title,
        description=data.description,
    )

    return _build_ticket_response(ticket)


@router.get("/tickets", response_model=list[TicketResponse])
def get_user_tickets(user_id: int, db: Session = Depends(get_db)):
    """Get all tickets created by a user."""
    user = AuthService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    tickets = TicketService.get_user_tickets(db, user_id)
    return [_build_ticket_response(t) for t in tickets]


def _build_ticket_response(ticket) -> TicketResponse:
    from backend.schemas.ticket import TicketHistoryItem
    history_items = []
    if ticket.history:
        for h in ticket.history:
            history_items.append(TicketHistoryItem(
                id=h.id,
                old_status=h.old_status,
                new_status=h.new_status,
                remarks=h.remarks,
                changed_by_name=h.changed_by.name if h.changed_by else "System",
                created_at=h.created_at,
            ))

    return TicketResponse(
        id=ticket.id,
        title=ticket.title,
        description=ticket.description,
        user_id=ticket.user_id,
        user_name=ticket.user.name if ticket.user else None,
        user_email=ticket.user.email if ticket.user else None,
        assigned_engineer_id=ticket.assigned_engineer_id,
        assigned_engineer_name=ticket.assigned_engineer.name if ticket.assigned_engineer else None,
        status=ticket.status,
        category=ticket.category,
        severity=ticket.severity,
        priority=ticket.priority,
        ai_solution=ticket.ai_solution,
        ai_analysis=ticket.ai_analysis,
        ai_recommendation=ticket.ai_recommendation,
        engineer_remarks=ticket.engineer_remarks,
        resolution_notes=ticket.resolution_notes,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        resolved_at=ticket.resolved_at,
        closed_at=ticket.closed_at,
        history=history_items,
    )
