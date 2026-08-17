"""
TicketHistory model — immutable audit trail for every ticket status change.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from backend.core.database import Base


class TicketHistory(Base):
    __tablename__ = "ticket_history"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    changed_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    old_status = Column(String(50), nullable=True)
    new_status = Column(String(50), nullable=False)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    ticket = relationship("Ticket", back_populates="history")
    changed_by = relationship("User", back_populates="ticket_history", foreign_keys=[changed_by_user_id])

    def __repr__(self):
        return f"<TicketHistory ticket={self.ticket_id} {self.old_status}->{self.new_status}>"
