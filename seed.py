"""
SupportPilot Seed Script

Creates initial admin account and sample data for development/testing.

Usage:
    python seed.py

Do NOT run automatically on startup.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.core.logging_config import setup_logging
from backend.core.database import init_db, SessionLocal
from backend.models.user import User, UserRole, UserStatus
from backend.models.ticket import Ticket, TicketStatus, TicketCategory, TicketSeverity, TicketPriority
from backend.models.ticket_history import TicketHistory
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone

setup_logging("INFO")

import logging
logger = logging.getLogger(__name__)


def seed():
    logger.info("Initialising database...")
    init_db()

    db = SessionLocal()
    try:
        # ── Admin ────────────────────────────────────────────────────────
        existing_admin = db.query(User).filter(User.email == "admin@supportpilot.com").first()
        if not existing_admin:
            admin = User(
                name="Admin",
                email="admin@supportpilot.com",
                password=generate_password_hash("admin123"),
                role=UserRole.admin,
                status=UserStatus.approved,
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            logger.info(f"Created admin: {admin.email}")
        else:
            admin = existing_admin
            logger.info("Admin already exists, skipping.")

        # ── Sample User ──────────────────────────────────────────────────
        existing_user = db.query(User).filter(User.email == "user@supportpilot.com").first()
        if not existing_user:
            user = User(
                name="Alice Smith",
                email="user@supportpilot.com",
                password=generate_password_hash("user123"),
                role=UserRole.user,
                status=UserStatus.approved,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Created sample user: {user.email}")
        else:
            user = existing_user
            logger.info("Sample user already exists, skipping.")

        # ── Sample Engineer ──────────────────────────────────────────────
        existing_eng = db.query(User).filter(User.email == "engineer@supportpilot.com").first()
        if not existing_eng:
            engineer = User(
                name="Bob Johnson",
                email="engineer@supportpilot.com",
                password=generate_password_hash("engineer123"),
                role=UserRole.engineer,
                status=UserStatus.approved,
            )
            db.add(engineer)
            db.commit()
            db.refresh(engineer)
            logger.info(f"Created sample engineer: {engineer.email}")
        else:
            engineer = existing_eng
            logger.info("Sample engineer already exists, skipping.")

        # ── Sample Tickets ───────────────────────────────────────────────
        ticket_count = db.query(Ticket).count()
        if ticket_count == 0:
            tickets_data = [
                {
                    "title": "Cannot connect to VPN from home",
                    "description": "I'm getting 'Authentication Failed' when connecting to VPN. Error code 691. I've verified my credentials are correct.",
                    "category": TicketCategory.VPN,
                    "severity": TicketSeverity.High,
                    "priority": TicketPriority.P2,
                    "status": TicketStatus.escalated,
                    "assigned_engineer_id": engineer.id,
                    "ai_analysis": "Authentication failure on VPN suggests credential mismatch or MFA token expiry.",
                    "ai_recommendation": "Verify credentials, check MFA token sync, and confirm VPN account is active.",
                },
                {
                    "title": "Outlook not opening after Windows update",
                    "description": "After the latest Windows update, Outlook crashes immediately on startup with no error message.",
                    "category": TicketCategory.Software,
                    "severity": TicketSeverity.Medium,
                    "priority": TicketPriority.P3,
                    "status": TicketStatus.pending,
                    "assigned_engineer_id": None,
                    "ai_analysis": "Post-update Outlook crash likely caused by add-in incompatibility or Office corruption.",
                    "ai_recommendation": "Try Outlook Safe Mode, repair Office installation, or check Windows update compatibility.",
                },
                {
                    "title": "Password reset not working",
                    "description": "The password reset email arrives but the link says 'link expired' even when I click it immediately.",
                    "category": TicketCategory.Password_Reset,
                    "severity": TicketSeverity.Medium,
                    "priority": TicketPriority.P3,
                    "status": TicketStatus.resolved,
                    "assigned_engineer_id": engineer.id,
                    "ai_analysis": "Expired reset link usually caused by clock skew on user device or email delay.",
                    "ai_recommendation": "Check device time sync, ensure link used within 15 minutes of receipt.",
                    "resolution_notes": "User's system clock was 25 minutes behind. Corrected time sync settings.",
                    "engineer_remarks": "Investigated device time settings, found NTP sync disabled.",
                },
            ]

            for t_data in tickets_data:
                resolution_notes = t_data.pop("resolution_notes", None)
                engineer_remarks = t_data.pop("engineer_remarks", None)

                ticket = Ticket(
                    user_id=user.id,
                    resolution_notes=resolution_notes,
                    engineer_remarks=engineer_remarks,
                    **t_data,
                )
                if ticket.status == TicketStatus.resolved:
                    ticket.resolved_at = datetime.now(timezone.utc)

                db.add(ticket)
                db.flush()

                history = TicketHistory(
                    ticket_id=ticket.id,
                    changed_by_user_id=admin.id,
                    old_status=None,
                    new_status=str(ticket.status),
                    remarks="Ticket created via seed",
                )
                db.add(history)

            db.commit()
            logger.info(f"Created {len(tickets_data)} sample tickets")
        else:
            logger.info(f"Tickets already exist ({ticket_count}), skipping.")

        logger.info("=" * 50)
        logger.info("Seed complete!")
        logger.info("=" * 50)
        logger.info("Credentials:")
        logger.info("  Admin:    admin@supportpilot.com / admin123")
        logger.info("  User:     user@supportpilot.com / user123")
        logger.info("  Engineer: engineer@supportpilot.com / engineer123")
        logger.info("=" * 50)

    finally:
        db.close()


if __name__ == "__main__":
    seed()
