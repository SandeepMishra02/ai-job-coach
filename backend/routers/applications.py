# backend/routers/applications.py
from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select, Session

from ..db import get_session
from ..models import Application, ApplicationStatus

router = APIRouter(prefix="/applications", tags=["applications"])

@router.get("/", response_model=List[Application])
def list_apps(
    status: Optional[ApplicationStatus] = Query(None),
    q: Optional[str] = Query(None),
    session: Session = Depends(get_session),
) -> List[Application]:
    stmt = select(Application)
    if status:
        stmt = stmt.where(Application.status == status)
    if q:
        like = f"%{q}%"
        stmt = stmt.where((Application.role.ilike(like)) | (Application.company.ilike(like)))
    return list(session.exec(stmt))

@router.get("/{app_id}", response_model=Application)
def get_app(app_id: int, session: Session = Depends(get_session)) -> Application:
    app = session.get(Application, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app

@router.post("/", response_model=Application)
def create_app(data: Application, session: Session = Depends(get_session)) -> Application:
    data.id = None
    now = datetime.utcnow()
    data.applied_at = data.applied_at or now
    data.updated_at = now
    session.add(data)
    session.commit()
    session.refresh(data)
    return data

@router.put("/{app_id}", response_model=Application)
def update_app(app_id: int, patch: Application, session: Session = Depends(get_session)) -> Application:
    app = session.get(Application, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    for k, v in patch.dict(exclude_unset=True).items():
        setattr(app, k, v)
    app.updated_at = datetime.utcnow()
    session.add(app)
    session.commit()
    session.refresh(app)
    return app

@router.delete("/{app_id}")
def delete_app(app_id: int, session: Session = Depends(get_session)) -> dict:
    app = session.get(Application, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    session.delete(app)
    session.commit()
    return {"ok": True}

@router.post("/{app_id}/status", response_model=Application)
def change_status(app_id: int, status: ApplicationStatus, session: Session = Depends(get_session)) -> Application:
    app = session.get(Application, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    app.status = status
    app.updated_at = datetime.utcnow()
    session.add(app)
    session.commit()
    session.refresh(app)
    return app

@router.post("/{app_id}/note", response_model=Application)
def add_note(app_id: int, note: str, session: Session = Depends(get_session)) -> Application:
    app = session.get(Application, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    notes = (app.notes or "").strip()
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    new_block = f"[{ts}] {note}"
    app.notes = (notes + "\n" + new_block).strip() if notes else new_block
    app.updated_at = datetime.utcnow()
    session.add(app)
    session.commit()
    session.refresh(app)
    return app
