from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from sqlmodel import select
from db import get_session
from models import JobPosting
from jobs_fetchers import fetch_greenhouse, fetch_lever
import asyncio
import os

router = APIRouter(prefix="/jobs", tags=["jobs"])

# Configure which boards to ingest (edit to taste or use env vars)
GREENHOUSE_BOARDS = (os.getenv("JOBS_GREENHOUSE", "roblox,datadog,asurion").split(","))
LEVER_COMPANIES   = (os.getenv("JOBS_LEVER", "ramp,stripe,pagerduty").split(","))

@router.get("", response_model=List[JobPosting])
def list_jobs(
    q: Optional[str] = None,
    company: Optional[str] = None,
    location: Optional[str] = None,
    remote: Optional[bool] = None,
    limit: int = Query(100, ge=1, le=200),
):
    with get_session() as session:
        stmt = select(JobPosting).order_by(JobPosting.posted_at.desc().nullslast(), JobPosting.created_at.desc())
        if q:
            q_like = f"%{q.lower()}%"
            # naive filter: match title or company
            stmt = stmt.where((JobPosting.title.ilike(q_like)) | (JobPosting.company.ilike(q_like)))
        if company:
            stmt = stmt.where(JobPosting.company.ilike(f"%{company}%"))
        if location:
            stmt = stmt.where(JobPosting.location.ilike(f"%{location}%"))
        if remote is not None:
            stmt = stmt.where(JobPosting.remote == remote)
        results = session.exec(stmt).all()
        return results[:limit]

@router.post("/refresh", summary="Fetch latest from Greenhouse & Lever and upsert")
def refresh_jobs():
    # Pull from sources concurrently
    async def _run():
        g_tasks = [fetch_greenhouse(b.strip()) for b in GREENHOUSE_BOARDS if b.strip()]
        l_tasks = [fetch_lever(c.strip()) for c in LEVER_COMPANIES if c.strip()]
        batches = await asyncio.gather(*(g_tasks + l_tasks))
        all_jobs = [item for batch in batches for item in batch]
        # Upsert by URL
        with get_session() as session:
            count_new = 0
            for j in all_jobs:
                if not j.get("url"):
                    continue
                existing = session.exec(select(JobPosting).where(JobPosting.url == j["url"])).first()
                if existing:
                    # update light fields
                    existing.title     = j.get("title") or existing.title
                    existing.company   = j.get("company") or existing.company
                    existing.location  = j.get("location") or existing.location
                    existing.remote    = existing.remote if (j.get("remote") is None) else bool(j.get("remote"))
                    existing.posted_at = j.get("posted_at") or existing.posted_at
                else:
                    session.add(JobPosting(**j))
                    count_new += 1
            session.commit()
            return {"added": count_new, "total": len(all_jobs)}
    try:
        return asyncio.run(_run())
    except RuntimeError:
        # If already in an event loop (some hosts), use create_task
        return asyncio.get_event_loop().run_until_complete(_run())
