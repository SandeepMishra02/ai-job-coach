from fastapi import APIRouter, HTTPException
import httpx
import asyncio
from jobs_fetchers import fetch_for_slug, Job

router = APIRouter(prefix="/jobs", tags=["jobs"])

# Curated list of company slugs you want to track
# These must match the slug on Lever or Greenhouse
COMPANY_SLUGS = [
    "databricks",
    "doordash",
    "snowflake",
    "airbnb",
    "nvidia",
    "roblox",
    "openai",         # Greenhouse
    "fastly",         # Greenhouse
    "brex",           # Lever
    "discord",        # Greenhouse
]

# In-memory cache for quick reads (could be DB in production)
JOBS_CACHE: list[Job] = []

@router.get("")
def list_jobs() -> list[Job]:
    """Return cached jobs, newest first."""
    return sorted(JOBS_CACHE, key=lambda j: int(j.get("ts") or 0), reverse=True)

@router.post("/refresh")
def refresh_jobs():
    """Refresh job listings from all company slugs."""
    async def _run():
        jobs: list[Job] = []
        async with httpx.AsyncClient(follow_redirects=True) as client:
            tasks = [fetch_for_slug(client, slug) for slug in COMPANY_SLUGS]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        for res in results:
            if isinstance(res, Exception):
                continue
            jobs.extend(res)
        return jobs

    try:
        new_jobs = asyncio.run(_run())
        global JOBS_CACHE
        JOBS_CACHE = new_jobs
        return {"ok": True, "count": len(JOBS_CACHE)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refresh failed: {e}")





