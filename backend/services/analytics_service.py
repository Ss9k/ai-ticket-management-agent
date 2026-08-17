"""
Analytics service — aggregates ticket and engineer performance data.
"""
import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.models.ticket import Ticket, TicketStatus
from backend.models.user import User, UserRole, UserStatus
from backend.schemas.analytics import (
    AnalyticsSummary, TicketStatusCounts, CategoryCount,
    PriorityCount, ResolutionTrendItem, EngineerPerformance
)

logger = logging.getLogger(__name__)


class AnalyticsService:

    @staticmethod
    def get_summary(db: Session) -> AnalyticsSummary:
        logger.info("Generating analytics summary")

        # Status counts
        rows = db.query(Ticket.status, func.count(Ticket.id)).group_by(Ticket.status).all()
        status_map = {r[0]: r[1] for r in rows}
        status_counts = TicketStatusCounts(
            pending=status_map.get(TicketStatus.pending, 0),
            escalated=status_map.get(TicketStatus.escalated, 0),
            resolved=status_map.get(TicketStatus.resolved, 0),
            closed=status_map.get(TicketStatus.closed, 0),
            total=sum(status_map.values()),
        )

        # Category counts
        cat_rows = db.query(Ticket.category, func.count(Ticket.id)).group_by(Ticket.category).all()
        category_counts = [
            CategoryCount(category=r[0].value if r[0] else "Unclassified", count=r[1])
            for r in cat_rows if r[0]
        ]

        # Priority counts
        pri_rows = db.query(Ticket.priority, func.count(Ticket.id)).group_by(Ticket.priority).all()
        priority_counts = [
            PriorityCount(priority=r[0].value if r[0] else "Unassigned", count=r[1])
            for r in pri_rows if r[0]
        ]

        # Resolution trends — last 30 days
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        trend_rows = (
            db.query(
                func.date(Ticket.resolved_at).label("day"),
                func.count(Ticket.id)
            )
            .filter(Ticket.resolved_at >= thirty_days_ago)
            .group_by(func.date(Ticket.resolved_at))
            .order_by(func.date(Ticket.resolved_at))
            .all()
        )
        resolution_trends = [
            ResolutionTrendItem(date=str(r[0]), count=r[1]) for r in trend_rows
        ]

        # Engineer performance
        engineers = (
            db.query(User)
            .filter(User.role == UserRole.engineer, User.status == UserStatus.approved)
            .all()
        )
        engineer_performance = []
        for eng in engineers:
            all_assigned = db.query(Ticket).filter(Ticket.assigned_engineer_id == eng.id).count()
            resolved = db.query(Ticket).filter(
                Ticket.assigned_engineer_id == eng.id,
                Ticket.status == TicketStatus.resolved,
            ).count()
            closed = db.query(Ticket).filter(
                Ticket.assigned_engineer_id == eng.id,
                Ticket.status == TicketStatus.closed,
            ).count()
            open_count = db.query(Ticket).filter(
                Ticket.assigned_engineer_id == eng.id,
                Ticket.status.in_([TicketStatus.pending, TicketStatus.escalated]),
            ).count()
            rate = round((resolved / all_assigned) * 100, 1) if all_assigned > 0 else 0.0
            engineer_performance.append(
                EngineerPerformance(
                    engineer_id=eng.id,
                    engineer_name=eng.name,
                    assigned=all_assigned,
                    resolved=resolved,
                    closed=closed,
                    open=open_count,
                    resolution_rate=rate,
                )
            )

        return AnalyticsSummary(
            status_counts=status_counts,
            category_counts=category_counts,
            priority_counts=priority_counts,
            resolution_trends=resolution_trends,
            engineer_performance=engineer_performance,
        )
