from __future__ import annotations
import httpx
from typing import List, Dict

def fetch_lever(company: str) -> List[Dict]:
    """
    Returns a list of jobs from Lever for a given company slug.
    Ignores 404 (company/board not found) and returns [] instead of raising.
    """
    url = f"https://api.lever.co/v0/postings/{company}?mode=json"
    try:
        r = httpx.get(url, timeout=20)
        if r.status_code == 404:
            # Company not on Lever (or wrong slug) — just skip
            return []
        r.raise_for_status()
        data = r.json()
        jobs = []
        for j in data:
            jobs.append({
                "source": "lever",
                "company": j.get("company", company),
                "title": j.get("text"),
                "location": (j.get("categories") or {}).get("location"),
                "url": j.get("hostedUrl"),
                "createdAt": j.get("createdAt"),
                "updatedAt": j.get("updatedAt"),
            })
        return jobs
    except httpx.HTTPStatusError:
        # Non-404 errors: bubble up for logging upstream, or return [] to be lenient.
        return []
    except Exception:
        return []

def fetch_greenhouse(board_token: str) -> List[Dict]:
    """
    Greenhouse API (job board token differs per company).
    Returns [] on 404; tolerates failures.
    """
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"
    try:
        r = httpx.get(url, timeout=20)
        if r.status_code == 404:
            return []
        r.raise_for_status()
        data = r.json()
        jobs = []
        for j in data.get("jobs", []):
            jobs.append({
                "source": "greenhouse",
                "company": board_token,
                "title": j.get("title"),
                "location": (j.get("location") or {}).get("name"),
                "url": j.get("absolute_url"),
                "createdAt": j.get("updated_at") or j.get("created_at"),
                "updatedAt": j.get("updated_at"),
            })
        return jobs
    except httpx.HTTPStatusError:
        return []
    except Exception:
        return []

