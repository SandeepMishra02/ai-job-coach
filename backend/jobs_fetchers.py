from __future__ import annotations
import httpx
from typing import List, Dict, Any

def fetch_lever(company: str) -> List[Dict[str, Any]]:
    """
    Lever postings for a company slug. Returns [] on 404 or errors.
    """
    url = f"https://api.lever.co/v0/postings/{company}?mode=json"
    try:
        r = httpx.get(url, timeout=20)
        if r.status_code == 404:
            return []
        r.raise_for_status()
        data = r.json()
        out: List[Dict[str, Any]] = []
        for j in data:
            out.append({
                "source": "lever",
                "company": j.get("company", company),
                "title": j.get("text"),
                "location": (j.get("categories") or {}).get("location"),
                "url": j.get("hostedUrl"),
                "createdAt": j.get("createdAt"),
                "updatedAt": j.get("updatedAt"),
            })
        return out
    except Exception:
        return []

def fetch_greenhouse(board_token: str) -> List[Dict[str, Any]]:
    """
    Greenhouse board jobs. Returns [] on 404 or errors.
    """
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"
    try:
        r = httpx.get(url, timeout=20)
        if r.status_code == 404:
            return []
        r.raise_for_status()
        data = r.json()
        out: List[Dict[str, Any]] = []
        for j in data.get("jobs", []):
            out.append({
                "source": "greenhouse",
                "company": board_token,
                "title": j.get("title"),
                "location": (j.get("location") or {}).get("name"),
                "url": j.get("absolute_url"),
                "createdAt": j.get("created_at"),
                "updatedAt": j.get("updated_at"),
            })
        return out
    except Exception:
        return []


