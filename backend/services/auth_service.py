"""
Authentication and user management service.
Handles registration, login, and user lookup.
"""
import logging
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash

from backend.models.user import User, UserRole, UserStatus
from backend.schemas.user import UserRegisterRequest

logger = logging.getLogger(__name__)


class AuthService:

    @staticmethod
    def register(db: Session, data: UserRegisterRequest) -> tuple[User | None, str]:
        """
        Register a new user or engineer.
        Returns (user, error_message). error_message is empty on success.
        """
        existing = db.query(User).filter(User.email == data.email).first()
        if existing:
            return None, "Email already registered."

        role = UserRole(data.role)

        # Engineers start pending; users and admins are auto-approved
        if role == UserRole.engineer:
            status = UserStatus.pending
        else:
            status = UserStatus.approved

        hashed = generate_password_hash(data.password)
        user = User(
            name=data.name,
            email=data.email,
            password=hashed,
            role=role,
            status=status,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Registered new {role} user: {user.email} (status={status})")
        return user, ""

    @staticmethod
    def login(db: Session, email: str, password: str) -> tuple[User | None, str]:
        """
        Validate credentials.
        Returns (user, error_message). error_message is empty on success.
        """
        user = db.query(User).filter(User.email == email).first()
        if not user:
            logger.warning(f"Login attempt with unknown email: {email}")
            return None, "Invalid email or password."

        if not check_password_hash(user.password, password):
            logger.warning(f"Failed login attempt for: {email}")
            return None, "Invalid email or password."

        if user.role == UserRole.engineer and user.status == UserStatus.pending:
            logger.info(f"Pending engineer attempted login: {email}")
            return None, "Your engineer account is pending admin approval."

        if user.status == UserStatus.rejected:
            return None, "Your account has been rejected. Contact support."

        logger.info(f"Successful login: {email} (role={user.role})")
        return user, ""

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User | None:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_pending_engineers(db: Session) -> list[User]:
        return (
            db.query(User)
            .filter(User.role == UserRole.engineer, User.status == UserStatus.pending)
            .all()
        )

    @staticmethod
    def approve_engineer(db: Session, engineer_id: int, admin_id: int) -> tuple[User | None, str]:
        engineer = db.query(User).filter(
            User.id == engineer_id,
            User.role == UserRole.engineer,
        ).first()
        if not engineer:
            return None, "Engineer not found."
        engineer.status = UserStatus.approved
        db.commit()
        db.refresh(engineer)
        logger.info(f"Admin {admin_id} approved engineer {engineer.email}")
        return engineer, ""

    @staticmethod
    def get_approved_engineers(db: Session) -> list[User]:
        return (
            db.query(User)
            .filter(User.role == UserRole.engineer, User.status == UserStatus.approved)
            .all()
        )
