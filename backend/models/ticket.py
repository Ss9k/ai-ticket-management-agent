"""
Ticket model — core support ticket entity.
Stores user-reported problem, AI results, engineer work, and lifecycle metadata.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship

from backend.core.database import Base
import enum


class TicketStatus(str, enum.Enum):
    pending = "pending"
    escalated = "escalated"
    resolved = "resolved"
    closed = "closed"


class TicketCategory(str, enum.Enum):
    Hardware = "Hardware"
    Software = "Software"
    Network = "Network"
    VPN = "VPN"
    Password_Reset = "Password Reset"
    Email = "Email"
    Printer = "Printer"
    Security = "Security"
    Cloud = "Cloud"
    Database = "Database"
    Other = "Other"


class TicketSeverity(str, enum.Enum):
    Low = "Low"
    Medium = "Medium"
    High = "High"
    Critical = "Critical"


class TicketPriority(str, enum.Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(512), nullable=False)
    description = Column(Text, nullable=False)

    # Ownership
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_engineer_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Lifecycle
    status = Column(SAEnum(TicketStatus), nullable=False, default=TicketStatus.pending)

    # Classification (filled by AI)
    category = Column(SAEnum(TicketCategory), nullable=True)
    severity = Column(SAEnum(TicketSeverity), nullable=True)
    priority = Column(SAEnum(TicketPriority), nullable=True)

    # AI content
    ai_solution = Column(Text, nullable=True)       # full AI answer shown to user
    ai_analysis = Column(Text, nullable=True)       # structured analysis for engineer
    ai_recommendation = Column(Text, nullable=True) # engineer-facing recommendation

    # Engineer work
    engineer_remarks = Column(Text, nullable=True)
    resolution_notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="tickets", foreign_keys=[user_id])
    assigned_engineer = relationship("User", back_populates="assigned_tickets", foreign_keys=[assigned_engineer_id])
    history = relationship("TicketHistory", back_populates="ticket", cascade="all, delete-orphan", order_by="TicketHistory.created_at.desc()")

    def __repr__(self):
        return f"<Ticket id={self.id} status={self.status} priority={self.priority}>"
