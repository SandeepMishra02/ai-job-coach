from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Literal, Optional

from fastapi import Request
from fastapi.responses import JSONResponse

from rate_limit import limiter  # use the shared limiter
from ai.job_tools import generate_cover_letter  # adjust path if needed

router = APIRouter()

# --- Request/Response models ---
class GenerateRequest(BaseModel):
    resume: str = Field(min_length=1, max_length=20000)
    job_description: str = Field(min_length=1, max_length=20000)
    style: Optional[Literal["concise", "enthusiastic", "professional", "entry-level"]] = "professional"
    user_name: Optional[str] = None
    company_name: Optional[str] = None

class GenerateResponse(BaseModel):
    cover_letter: str

# --- Endpoint with per-route limit ---
@router.post("/generate-cover-letter", response_model=GenerateResponse)
@limiter.limit("10/minute")
def generate(req: GenerateRequest, request: Request) -> GenerateResponse:
    try:
        letter = generate_cover_letter(
            resume=req.resume,
            job_desc=req.job_description,
            style=req.style or "professional",
            user_name=req.user_name,
            company_name=req.company_name,
        )
        return GenerateResponse(cover_letter=letter)
    except HTTPException:
        raise
    except Exception:
        # Hide internals, return a user-friendly message
        raise HTTPException(status_code=500, detail="Failed to generate cover letter. Please try again.")


