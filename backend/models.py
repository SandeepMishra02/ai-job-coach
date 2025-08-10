# backend/models.py
from __future__ import annotations
from datetime import datetime
from typing import Optional, Literal
from sqlmodel import SQLModel, Field

ApplicationStatus = Literal[
    "applied", "interview", "offer", "rejected", "withdrawn", "accepted"
]

class Application(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    role: str
    company: str
    status: ApplicationStatus = Field(default="applied")

    applied_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    location: Optional[str] = None
    job_url: Optional[str] = None
    source: Optional[str] = None        # e.g., LinkedIn / referral / careers page
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    resume_version: Optional[str] = None
    notes: Optional[str] = None
