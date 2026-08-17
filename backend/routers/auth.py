"""
Authentication API router.
POST /auth/register
POST /auth/login
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.schemas.user import UserRegisterRequest, UserLoginRequest, UserLoginResponse, UserResponse
from backend.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)


@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: UserRegisterRequest, db: Session = Depends(get_db)):
    user, error = AuthService.register(db, data)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return user


@router.post("/login", response_model=UserLoginResponse)
def login(data: UserLoginRequest, db: Session = Depends(get_db)):
    user, error = AuthService.login(db, data.email, data.password)
    if error:
        raise HTTPException(status_code=401, detail=error)
    return UserLoginResponse(
        message="Login successful",
        user=UserResponse.model_validate(user),
    )
