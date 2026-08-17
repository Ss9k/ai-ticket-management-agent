"""
User model — represents users, engineers, and admins.
Engineers are users with role='engineer'.
No separate Engineer table is needed.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship

from backend.core.database import Base

import enum


class UserRole(str, enum.Enum):
    user = "user"
    engineer = "engineer"
    admin = "admin"


class UserStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(512), nullable=False)
    role = Column(SAEnum(UserRole), nullable=False, default=UserRole.user)
    status = Column(SAEnum(UserStatus), nullable=False, default=UserStatus.approved)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    tickets = relationship("Ticket", back_populates="user", foreign_keys="Ticket.user_id")
    assigned_tickets = relationship(
        "Ticket", back_populates="assigned_engineer", foreign_keys="Ticket.assigned_engineer_id"
    )
    ticket_history = relationship("TicketHistory", back_populates="changed_by", foreign_keys="TicketHistory.changed_by_user_id")

    def __repr__(self):
        return f"<User id={self.id} email={self.email} role={self.role}>"
