"""Pydantic schemas for User endpoints."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator


class UserRegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "user"  # "user" or "engineer"

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        if v not in ("user", "engineer"):
            raise ValueError("Role must be 'user' or 'engineer'")
        return v


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UserLoginResponse(BaseModel):
    message: str
    user: UserResponse
