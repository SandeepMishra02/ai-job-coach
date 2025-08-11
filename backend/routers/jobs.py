from __future__ import annotations
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime, timezone

from jobs_fetchers import fetch_lever, fetch_greenhouse

router = APIRouter(tags=["jobs"])

# Tune these lists as you like; removed slugs that 404
LEVER_COMPANIES = [
    "vercel", "datadog", "plaid", "doordash",
]
GREENHOUSE_BOARDS = [
    "stripe", "openai", "snowflake",
]

_JOBS_CACHE: List[Dict[str, Any]] = []


def _to_ts(v: Any) -> float:
    """
    Normalize various timestamp formats to a float Unix timestamp.
    - int/float epoch or ms epoch
    - ISO8601 string (with or without Z)
    - anything else -> 0
    """
    if v is None:
        return 0.0
    if isinstance(v, (int, float)):
        # Heuristic: Lever returns ms; if it's too large, divide.
        return float(v / 1000.0) if v > 10_000_000_000 else float(v)
    if isinstance(v, str):
        s = v.strip()
        # numeric-as-string
        if s.isdigit():
            iv = int(s)
            return float(iv / 1000.0) if iv > 10_000_000_000 else float(iv)
        # ISO8601
        try:
            # handle trailing Z
            if s.endswith("Z"):
                s = s.replace("Z", "+00:00")
            dt = datetime.fromisoformat(s)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.timestamp()
        except Exception:
            return 0.0
    return 0.0


@router.get("/jobs")
def list_jobs() -> List[Dict[str, Any]]:
    return _JOBS_CACHE


@router.post("/jobs/refresh")
def refresh_jobs() -> Dict[str, Any]:
    """
    Serial refresh; each source is tolerant of 404/5xx and returns [].
    We normalize timestamps to a 'ts' field and sort newest-first.
    """
    try:
        jobs: List[Dict[str, Any]] = []

        for c in LEVER_COMPANIES:
            jobs.extend(fetch_lever(c))

        for b in GREENHOUSE_BOARDS:
            jobs.extend(fetch_greenhouse(b))

        # normalize timestamps (+ keep display fields)
        for j in jobs:
            ts = _to_ts(j.get("updatedAt")) or _to_ts(j.get("createdAt"))
            j["ts"] = ts

        jobs.sort(key=lambda x: x.get("ts", 0.0), reverse=True)

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




