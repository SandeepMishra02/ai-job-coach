from fastapi import APIRouter, HTTPException
from sqlalchemy import func
from sqlmodel import select

from ..db import get_session
from ..models import Application

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
def overview():
    try:
        with get_session() as s:
            # Total
            total = s.exec(select(func.count(Application.id))).one()

            # By status
            status_rows = s.exec(
                select(Application.status, func.count(Application.id))
                .group_by(Application.status)
            ).all()
            by_status = {k: v for k, v in status_rows if k is not None}

            # By company
            company_rows = s.exec(
                select(Application.company, func.count(Application.id))
                .group_by(Application.company)
            ).all()
            by_company = {k: v for k, v in company_rows if k is not None}

            # By month (choose the existing date field)
            date_col = getattr(Application, "date_applied", None) or getattr(Application, "applied_at", None)
            if date_col is None:
                by_month = {}
            else:
                month_rows = s.exec(
                    select(func.strftime("%Y-%m", date_col), func.count(Application.id))
                    .group_by(func.strftime("%Y-%m", date_col))
                ).all()
                by_month = {k or "unknown": v for k, v in month_rows}

            return {
                "total_applications": total,
                "by_status": by_status,
                "by_company": by_company,
                "by_month": by_month,
                "avg_days_to_response": None,  # placeholder for later
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compute analytics: {e}")







