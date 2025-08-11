from fastapi import APIRouter, HTTPException
from sqlmodel import select
from typing import List

from db import get_session
from models import Application

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("/", response_model=List[Application])
def list_apps():
    try:
        with get_session() as session:
            rows = session.exec(select(Application)).all()
            return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list applications: {e}")


@router.post("/", response_model=Application)
def create_app(app: Application):
    try:
        with get_session() as session:
            session.add(app)
            session.commit()
            session.refresh(app)
            return app
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create application: {e}")


@router.put("/{app_id}", response_model=Application)
def update_app(app_id: int, patch: dict):
    try:
        with get_session() as session:
            obj = session.get(Application, app_id)
            if not obj:
                raise HTTPException(status_code=404, detail="Application not found")
            for k, v in (patch or {}).items():
                setattr(obj, k, v)
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update application: {e}")


@router.delete("/{app_id}", status_code=204)
def delete_app(app_id: int):
    try:
        with get_session() as session:
            obj = session.get(Application, app_id)
            if not obj:
                raise HTTPException(status_code=404, detail="Application not found")
            session.delete(obj)
            session.commit()
            return
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete application: {e}")

