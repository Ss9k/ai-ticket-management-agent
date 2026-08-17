"""Pydantic schemas for Analytics and Reports."""
from typing import Any
from pydantic import BaseModel


class TicketStatusCounts(BaseModel):
    pending: int = 0
    escalated: int = 0
    resolved: int = 0
    closed: int = 0
    total: int = 0


class CategoryCount(BaseModel):
    category: str
    count: int


class PriorityCount(BaseModel):
    priority: str
    count: int


class ResolutionTrendItem(BaseModel):
    date: str
    count: int


class EngineerPerformance(BaseModel):
    engineer_id: int
    engineer_name: str
    assigned: int
    resolved: int
    closed: int
    open: int
    resolution_rate: float


class AnalyticsSummary(BaseModel):
    status_counts: TicketStatusCounts
    category_counts: list[CategoryCount]
    priority_counts: list[PriorityCount]
    resolution_trends: list[ResolutionTrendItem]
    engineer_performance: list[EngineerPerformance]
