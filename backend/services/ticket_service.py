"""
Ticket service — all ticket lifecycle operations.
Every status transition records a TicketHistory entry.
"""
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from backend.models.ticket import Ticket, TicketStatus
from backend.models.ticket_history import TicketHistory
from backend.models.user import User, UserRole
from backend.schemas.ticket import (
    CreateTicketRequest, AssignEngineerRequest,
    ResolveTicketRequest, CloseTicketRequest
)

logger = logging.getLogger(__name__)


def _record_history(db: Session, ticket_id: int, changed_by_id: int,
                    old_status: str | None, new_status: str, remarks: str | None = None):
    history = TicketHistory(
        ticket_id=ticket_id,
        changed_by_user_id=changed_by_id,
        old_status=old_status,
        new_status=new_status,
        remarks=remarks,
    )
    db.add(history)


def _ticket_with_relations(db: Session, ticket_id: int) -> Ticket | None:
    return (
        db.query(Ticket)
        .options(
            joinedload(Ticket.user),
            joinedload(Ticket.assigned_engineer),
            joinedload(Ticket.history).joinedload(TicketHistory.changed_by),
        )
        .filter(Ticket.id == ticket_id)
        .first()
    )


class TicketService:

    @staticmethod
    def create_ticket(db: Session, data: CreateTicketRequest) -> Ticket:
        ticket = Ticket(
            title=data.title,
            description=data.description,
            user_id=data.user_id,
            ai_solution=data.ai_solution,
            status=TicketStatus.pending,
        )
        db.add(ticket)
        db.flush()  # get ticket.id before history

        _record_history(db, ticket.id, data.user_id, None, TicketStatus.pending, "Ticket created")
        db.commit()
        db.refresh(ticket)
        logger.info(f"Ticket #{ticket.id} created by user {data.user_id}")
        return ticket

    @staticmethod
    def update_ai_classification(db: Session, ticket_id: int,
                                  category: str, severity: str, priority: str,
                                  ai_analysis: str, ai_recommendation: str) -> Ticket | None:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            return None
        ticket.category = category
        ticket.severity = severity
        ticket.priority = priority
        ticket.ai_analysis = ai_analysis
        ticket.ai_recommendation = ai_recommendation
        db.commit()
        db.refresh(ticket)
        return ticket

    @staticmethod
    def assign_engineer(db: Session, data: AssignEngineerRequest) -> tuple[Ticket | None, str]:
        ticket = db.query(Ticket).filter(Ticket.id == data.ticket_id).first()
        if not ticket:
            return None, "Ticket not found."

        engineer = db.query(User).filter(
            User.id == data.engineer_id,
            User.role == UserRole.engineer,
        ).first()
        if not engineer:
            return None, "Engineer not found."

        old_status = ticket.status
        ticket.assigned_engineer_id = data.engineer_id
        ticket.status = TicketStatus.escalated
        ticket.updated_at = datetime.now(timezone.utc)

        _record_history(
            db, ticket.id, data.admin_id,
            old_status, TicketStatus.escalated,
            f"Assigned to engineer {engineer.name}"
        )
        db.commit()
        db.refresh(ticket)
        logger.info(f"Ticket #{ticket.id} assigned to engineer {engineer.email} by admin {data.admin_id}")
        return ticket, ""

    @staticmethod
    def add_remarks(db: Session, ticket_id: int, engineer_id: int, remarks: str) -> tuple[Ticket | None, str]:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            return None, "Ticket not found."
        if ticket.assigned_engineer_id != engineer_id:
            return None, "Not authorized for this ticket."

        ticket.engineer_remarks = remarks
        ticket.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(ticket)
        return ticket, ""

    @staticmethod
    def resolve_ticket(db: Session, ticket_id: int, data: ResolveTicketRequest) -> tuple[Ticket | None, str]:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            return None, "Ticket not found."
        if ticket.assigned_engineer_id != data.engineer_id:
            return None, "Not authorized for this ticket."
        if ticket.status == TicketStatus.resolved:
            return None, "Ticket is already resolved."
        if ticket.status == TicketStatus.closed:
            return None, "Cannot resolve a closed ticket."

        old_status = ticket.status
        if data.engineer_remarks:
            ticket.engineer_remarks = data.engineer_remarks
        ticket.resolution_notes = data.resolution_notes
        ticket.status = TicketStatus.resolved
        ticket.resolved_at = datetime.now(timezone.utc)
        ticket.updated_at = datetime.now(timezone.utc)

        _record_history(
            db, ticket.id, data.engineer_id, old_status, TicketStatus.resolved,
            data.resolution_notes
        )
        db.commit()
        db.refresh(ticket)
        logger.info(f"Ticket #{ticket.id} resolved by engineer {data.engineer_id}")
        return ticket, ""

    @staticmethod
    def close_ticket(db: Session, ticket_id: int, data: CloseTicketRequest) -> tuple[Ticket | None, str]:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            return None, "Ticket not found."
        if ticket.status != TicketStatus.resolved:
            return None, "Only resolved tickets can be closed."

        old_status = ticket.status
        ticket.status = TicketStatus.closed
        ticket.closed_at = datetime.now(timezone.utc)
        ticket.updated_at = datetime.now(timezone.utc)

        _record_history(
            db, ticket.id, data.closed_by_id, old_status, TicketStatus.closed, "Ticket closed"
        )
        db.commit()
        db.refresh(ticket)
        logger.info(f"Ticket #{ticket.id} closed by user {data.closed_by_id}")
        return ticket, ""

    @staticmethod
    def get_ticket(db: Session, ticket_id: int) -> Ticket | None:
        return _ticket_with_relations(db, ticket_id)

    @staticmethod
    def get_user_tickets(db: Session, user_id: int) -> list[Ticket]:
        return (
            db.query(Ticket)
            .options(joinedload(Ticket.assigned_engineer))
            .filter(Ticket.user_id == user_id)
            .order_by(Ticket.created_at.desc())
            .all()
        )

    @staticmethod
    def get_engineer_tickets(db: Session, engineer_id: int,
                              status: str | None = None,
                              priority: str | None = None,
                              category: str | None = None,
                              severity: str | None = None,
                              search: str | None = None) -> list[Ticket]:
        query = (
            db.query(Ticket)
            .options(joinedload(Ticket.user), joinedload(Ticket.assigned_engineer))
            .filter(Ticket.assigned_engineer_id == engineer_id)
        )
        if status:
            query = query.filter(Ticket.status == status)
        if priority:
            query = query.filter(Ticket.priority == priority)
        if category:
            query = query.filter(Ticket.category == category)
        if severity:
            query = query.filter(Ticket.severity == severity)
        if search:
            like = f"%{search}%"
            query = query.filter(
                or_(
                    Ticket.title.ilike(like),
                    Ticket.id.cast(db.bind.dialect.name == "postgresql" and "text" or "VARCHAR").ilike(like),
                )
            )
        return query.order_by(Ticket.updated_at.desc()).all()

    @staticmethod
    def get_all_tickets(db: Session, status: str | None = None) -> list[Ticket]:
        query = (
            db.query(Ticket)
            .options(joinedload(Ticket.user), joinedload(Ticket.assigned_engineer))
        )
        if status:
            query = query.filter(Ticket.status == status)
        return query.order_by(Ticket.created_at.desc()).all()

    @staticmethod
    def get_ticket_history(db: Session, ticket_id: int) -> list[TicketHistory]:
        return (
            db.query(TicketHistory)
            .options(joinedload(TicketHistory.changed_by))
            .filter(TicketHistory.ticket_id == ticket_id)
            .order_by(TicketHistory.created_at.desc())
            .all()
        )
