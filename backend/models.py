from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import SQLModel, Field


# --- Proper Enum for status ---
class ApplicationStatus(str, Enum):
    APPLIED = "applied"
    INTERVIEWING = "interviewing"
    OFFER = "offer"
    REJECTED = "rejected"
    SAVED = "saved"  # optional "saved/bookmarked" bucket


# --- Base model shared by table + schemas ---
class ApplicationBase(SQLModel):
    company: str
    role: str
    url: Optional[str] = None
    status: ApplicationStatus = Field(default=ApplicationStatus.APPLIED)
    notes: Optional[str] = None
    applied_at: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# --- DB table ---
class Application(ApplicationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


# --- Request/response schemas ---
class ApplicationCreate(ApplicationBase):
    pass


class ApplicationRead(ApplicationBase):
    id: int


class ApplicationUpdate(SQLModel):
    company: Optional[str] = None
    role: Optional[str] = None
    url: Optional[str] = None
    status: Optional[ApplicationStatus] = None
    notes: Optional[str] = None
    applied_at: Optional[datetime] = None
