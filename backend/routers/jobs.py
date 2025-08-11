from __future__ import annotations
from fastapi import APIRouter, HTTPException
from typing import List, Dict

from ..jobs_fetchers import fetch_lever, fetch_greenhouse

router = APIRouter(tags=["jobs"])

# A small curated set; feel free to adjust:
LEVER_COMPANIES = [
    "vercel", "datadog", "plaid", "doordash",  # remove "ramp" if it 404s
]
GREENHOUSE_BOARDS = [
    "stripe", "openai", "snowflake",
]

# In-memory store (swap for DB later)
_JOBS_CACHE: List[Dict] = []

@router.get("/jobs")
def list_jobs() -> List[Dict]:
    return _JOBS_CACHE

@router.post("/jobs/refresh")
def refresh_jobs() -> Dict:
    """
    Serial refresh: call sources one by one; any individual 404/5xx is skipped.
    This avoids asyncio complexity on some hosts and is resilient to bad slugs.
    """
    try:
        jobs: List[Dict] = []

        for c in LEVER_COMPANIES:
            jobs.extend(fetch_lever(c))

        for b in GREENHOUSE_BOARDS:
            jobs.extend(fetch_greenhouse(b))

        # Optionally sort newest first if timestamps exist
        jobs.sort(key=lambda j: j.get("updatedAt") or j.get("createdAt") or "", reverse=True)

        global _JOBS_CACHE
        _JOBS_CACHE = jobs

        return {
            "status": "ok",
            "counts": {
                "total": len(jobs),
                "lever": sum(1 for j in jobs if j.get("source") == "lever"),
                "greenhouse": sum(1 for j in jobs if j.get("source") == "greenhouse"),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refresh failed: {e}")


