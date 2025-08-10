# backend/routers/ai.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Literal, Optional

from ..rate_limit import limiter
from ..ai.job_tools import generate_cover_letter, tailor_resume

router = APIRouter(prefix="/ai", tags=["ai"])

# --------- Models ---------

class GenerateRequest(BaseModel):
    resume: str = Field(min_length=1, max_length=20000)
    job_description: str = Field(min_length=1, max_length=20000)
    style: Optional[Literal["concise", "enthusiastic", "professional", "entry-level"]] = "professional"
    user_name: Optional[str] = None
    company_name: Optional[str] = None
    length: Optional[Literal["short", "medium", "long"]] = "medium"

class GenerateResponse(BaseModel):
    cover_letter: str

@router.post("/generate-cover-letter", response_model=GenerateResponse)
def generate(req: GenerateRequest) -> GenerateResponse:
    try:
        letter = generate_cover_letter(
            resume=req.resume,
            job_desc=req.job_description,
            style=req.style or "professional",
            user_name=req.user_name,
            company_name=req.company_name,
            length=req.length or "medium",
        )
        return GenerateResponse(cover_letter=letter)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to generate cover letter. Please try again.")

# --------- Resume tailoring ---------

class TailorRequest(BaseModel):
    resume: str = Field(min_length=1, max_length=50000)
    job_description: str = Field(min_length=1, max_length=50000)
    focus: Optional[str] = "skills"
    bullets: Optional[int] = 6

class TailorResponse(BaseModel):
    tailored: str

@router.post("/tailor-resume", response_model=TailorResponse)
def tailor(req: TailorRequest) -> TailorResponse:
    try:
        text = tailor_resume(req.resume, req.job_description, req.focus or "skills", req.bullets or 6)
        return TailorResponse(tailored=text)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to tailor resume.")
