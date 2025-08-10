from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Literal, Optional
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from fastapi import Request

from ai.job_tools import generate_cover_letter

router = APIRouter()

# --- Rate limiting (10 requests per minute per IP) ---
limiter = Limiter(key_func=get_remote_address)

@router.middleware("http")
async def ratelimit_middleware(request: Request, call_next):
    try:
        response = await limiter.limit("10/minute")(call_next)(request)
        return response
    except RateLimitExceeded as exc:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Please wait a minute and try again."},
        )

# --- Request/Response models ---
class GenerateRequest(BaseModel):
    resume: str = Field(min_length=1, max_length=20000)
    job_description: str = Field(min_length=1, max_length=20000)
    style: Optional[Literal["concise", "enthusiastic", "professional", "entry-level"]] = "professional"
    user_name: Optional[str] = None
    company_name: Optional[str] = None

class GenerateResponse(BaseModel):
    cover_letter: str

# --- Endpoint ---
@router.post("/generate-cover-letter", response_model=GenerateResponse)
def generate(req: GenerateRequest) -> GenerateResponse:
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
    except Exception as e:
        # Hide internals, return a user-friendly message
        raise HTTPException(status_code=500, detail="Failed to generate cover letter. Please try again.")

