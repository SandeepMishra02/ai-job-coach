import httpx
from datetime import datetime
from typing import Iterable, Dict, Any, List, Optional

def _parse_dt(text: Optional[str]) -> Optional[datetime]:
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except Exception:
        return None

# ---------- Greenhouse ----------
# Each org has a "board token". Examples:
#  https://boards-api.greenhouse.io/v1/boards/<board_token>/jobs
async def fetch_greenhouse(board_token: str) -> List[Dict[str, Any]]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json().get("jobs", [])
    jobs = []
    for j in data:
        jobs.append({
            "source": "greenhouse",
            "board": board_token,
            "company": j.get("offices", [{}])[0].get("name") or j.get("departments", [{}])[0].get("name") or "",
            "title": j.get("title", ""),
            "location": j.get("location", {}).get("name"),
            "url": j.get("absolute_url"),
            "remote": ("remote" in (j.get("location", {}).get("name") or "").lower()),
            "posted_at": _parse_dt(j.get("updated_at")),  # Greenhouse doesn't always expose posted date
        })
    return jobs

# ---------- Lever ----------
# Each org has a Lever handle:
#  https://api.lever.co/v0/postings/<company>?mode=json
async def fetch_lever(company: str) -> List[Dict[str, Any]]:
    url = f"https://api.lever.co/v0/postings/{company}?mode=json"
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json()
    jobs = []
    for j in data:
        jobs.append({
            "source": "lever",
            "board": company,
            "company": j.get("categories", {}).get("team") or company,
            "title": j.get("text") or "",
            "location": j.get("categories", {}).get("location"),
            "url": j.get("hostedUrl") or j.get("applyUrl"),
            "remote": any("remote" in (s or "").lower() for s in [j.get("categories", {}).get("location"), j.get("workplaceType")]),
            "posted_at": _parse_dt(j.get("createdAt")) or _parse_dt(j.get("updatedAt")),
        })
    return jobs
