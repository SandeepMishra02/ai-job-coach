from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Literal

from env.ratelimit import limiter
from ai.job_tools import generate_cover_letter

router = APIRouter()

# Request/Response models
class GenerateRequest(BaseModel):
    resume: str = Field(min_length=1, max_length=25_000)
    job_description: str = Field(min_length=1, max_length=25_000)
    style: Optional[Literal["concise", "enthusiastic", "professional", "entry-level"]] = "professional"
    length: Optional[Literal["short", "medium", "long"]] = "medium"
    user_name: Optional[str] = None
    company_name: Optional[str] = None

class GenerateResponse(BaseModel):
    cover_letter: str

@router.post("/generate-cover-letter", response_model=GenerateResponse)
@limiter.limit("10/minute")
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



