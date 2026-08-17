"""Pydantic schemas for Ticket endpoints."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AskAIRequest(BaseModel):
    title: str
    description: str
    user_id: int


class AskAIResponse(BaseModel):
    answer: str
    full_response: str
    context_used: bool
    retrieval_summary: str


class CreateTicketRequest(BaseModel):
    title: str
    description: str
    user_id: int
    ai_solution: Optional[str] = None


class TicketHistoryItem(BaseModel):
    id: int
    old_status: Optional[str]
    new_status: str
    remarks: Optional[str]
    changed_by_name: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    user_id: int
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    assigned_engineer_id: Optional[int] = None
    assigned_engineer_name: Optional[str] = None
    status: str
    category: Optional[str] = None
    severity: Optional[str] = None
    priority: Optional[str] = None
    ai_solution: Optional[str] = None
    ai_analysis: Optional[str] = None
    ai_recommendation: Optional[str] = None
    engineer_remarks: Optional[str] = None
    resolution_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    history: list[TicketHistoryItem] = []

    model_config = {"from_attributes": True}


class AssignEngineerRequest(BaseModel):
    ticket_id: int
    engineer_id: int
    admin_id: int


class EngineerRemarksRequest(BaseModel):
    engineer_id: int
    remarks: str


class ResolveTicketRequest(BaseModel):
    engineer_id: int
    engineer_remarks: Optional[str] = None
    resolution_notes: str


class CloseTicketRequest(BaseModel):
    closed_by_id: int
