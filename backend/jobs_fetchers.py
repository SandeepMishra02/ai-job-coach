from __future__ import annotations

import time
from typing import Dict, List, Literal, Optional, Tuple

import httpx

Platform = Literal["lever", "greenhouse"]
Job = Dict[str, object]

HEADERS = {"User-Agent": "ai-job-coach/1.0 (+jobs-fetcher)"}

# -------------- Quick platform detection --------------

async def detect_platform(client: httpx.AsyncClient, slug: str) -> Optional[Platform]:
    """
    Return "lever" | "greenhouse" if the slug resolves on either platform, else None.
    We do cheap HEADs and accept 200/301/302 as existence.
    """
    try:
        # Try Lever
        r1 = await client.head(f"https://jobs.lever.co/{slug}", timeout=6.0)
        if r1.status_code in (200, 301, 302):
            return "lever"
        # Try Greenhouse
        r2 = await client.head(f"https://boards.greenhouse.io/{slug}", timeout=6.0)
        if r2.status_code in (200, 301, 302):
            return "greenhouse"
    except Exception:
        pass
    return None

# -------------- Fetchers --------------

async def fetch_lever(client: httpx.AsyncClient, slug: str) -> List[Job]:
    """
    Lever postings API: https://api.lever.co/v0/postings/<slug>?mode=json
    """
    url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
    try:
        r = await client.get(url, headers=HEADERS, timeout=12.0)
        if r.status_code != 200:
            return []
        data = r.json() or []
    except Exception:
        return []

    jobs: List[Job] = []
    now = int(time.time())
    for item in data:
        # Lever fields are fairly consistent
        title = (item.get("text") or "").strip()
        loc = ""
        if isinstance(item.get("categories"), dict):
            loc = (item["categories"].get("location") or "").strip()
        hosted_url = (item.get("hostedUrl") or "").strip()
        created = item.get("createdAt") or 0  # ms
        updated = item.get("updatedAt") or created

        # Normalize to seconds
        created_s = int(created / 1000) if isinstance(created, (int, float)) else 0
        updated_s = int(updated / 1000) if isinstance(updated, (int, float)) else created_s

        jobs.append(
            {
                "source": "lever",
                "company": slug,
                "title": title or "(Untitled role)",
                "location": loc or "n/a",
                "url": hosted_url or f"https://jobs.lever.co/{slug}",
                "createdAt": created_s,
                "updatedAt": updated_s,
                "ts": updated_s or created_s or now,
            }
        )
    return jobs


async def fetch_greenhouse(client: httpx.AsyncClient, slug: str) -> List[Job]:
    """
    Greenhouse boards API: https://boards-api.greenhouse.io/v1/boards/<slug>/jobs?content=true
    """
    url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
    try:
        r = await client.get(url, headers=HEADERS, timeout=12.0)
        if r.status_code != 200:
            return []
        payload = r.json() or {}
        data = payload.get("jobs") or []
    except Exception:
        return []

    jobs: List[Job] = []
    now = int(time.time())
    for item in data:
        title = (item.get("title") or "").strip()
        hosted_url = (item.get("absolute_url") or "").strip()

        # Best-effort location extraction
        loc = ""
        if isinstance(item.get("location"), dict):
            loc = (item["location"].get("name") or "").strip()
        elif isinstance(item.get("offices"), list) and item["offices"]:
            loc = (item["offices"][0].get("name") or "").strip()

        # Timestamps vary by org; we’ll prefer updated->created->now
        updated_s = _coerce_ts(item.get("updated_at"))
        created_s = _coerce_ts(item.get("created_at"))
        ts = updated_s or created_s or now

        jobs.append(
            {
                "source": "greenhouse",
                "company": slug,
                "title": title or "(Untitled role)",
                "location": loc or "n/a",
                "url": hosted_url or f"https://boards.greenhouse.io/{slug}",
                "createdAt": created_s,
                "updatedAt": updated_s,
                "ts": ts,
            }
        )
    return jobs


def _coerce_ts(val) -> int:
    """
    Accepts int (s or ms), ISO8601 string, or None. Returns unix seconds.
    """
    if val is None:
        return 0
    # numeric
    if isinstance(val, (int, float)):
        return int(val / 1000) if val > 10_000_000_000 else int(val)
    # string (ISO or numeric)
    s = str(val).strip()
    if s.isdigit():
        n = int(s)
        return int(n / 1000) if n > 10_000_000_000 else n
    try:
        # Greenhouse times are usually ISO with timezone
        from datetime import datetime
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return int(dt.timestamp())
    except Exception:
        return 0

# -------------- Orchestrator --------------

async def fetch_for_slug(client: httpx.AsyncClient, slug: string) -> List[Job]:  # type: ignore[name-defined]
    """
    Detect platform, then fetch. Returns [] if nothing works.
    """
    platform = await detect_platform(client, slug)
    if platform == "lever":
        return await fetch_lever(client, slug)
    if platform == "greenhouse":
        return await fetch_greenhouse(client, slug)
    return []



