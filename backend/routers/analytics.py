# backend/routers/analytics.py
from __future__ import annotations
from datetime import datetime
from typing import Dict
from fastapi import APIRouter, Depends
from sqlmodel import select, Session

from ..db import get_session
from ..models import Application

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/status-counts")
def status_counts(session: Session = Depends(get_session)) -> Dict[str, int]:
    rows = list(session.exec(select(Application)))
    counts: Dict[str, int] = {}
    for r in rows:
        counts[r.status] = counts.get(r.status, 0) + 1
    return counts

@router.get("/conversion")
def conversion(session: Session = Depends(get_session)) -> Dict[str, float]:
    rows = list(session.exec(select(Application)))
    n_applied = len(rows)
    n_interview = sum(1 for r in rows if r.status == "interview")
    n_offer = sum(1 for r in rows if r.status == "offer")
    n_accepted = sum(1 for r in rows if r.status == "accepted")

    def rate(n: int, d: int) -> float:
        return round((n / d) * 100.0, 2) if d else 0.0

    return {
        "applied": n_applied,
        "interview_rate": rate(n_interview, n_applied),
        "offer_rate": rate(n_offer, n_applied),
        "accept_rate": rate(n_accepted, n_applied),
    }

@router.get("/time-to-status")
def time_to_status(session: Session = Depends(get_session)) -> Dict[str, float]:
    """
    Avg days from applied_at to last updated_at by final status.
    """
    from statistics import mean

    rows = list(session.exec(select(Application)))
    groups: Dict[str, list] = {}
    for r in rows:
        days = max(0, (r.updated_at - r.applied_at).days)
        groups.setdefault(r.status, []).append(days)

    return {status: round(mean(vals), 2) for status, vals in groups.items() if vals}
