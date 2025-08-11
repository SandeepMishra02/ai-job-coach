from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
import os
import httpx
from openai import OpenAI

router = APIRouter(prefix="/interview", tags=["interview"])

# --------- Models ---------

class Msg(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

class CoachRequest(BaseModel):
    # your existing client sends { message }, so history is optional
    message: str = Field(min_length=1, max_length=5000)
    history: Optional[List[Msg]] = None  # you can start sending this later if you want

class CoachResponse(BaseModel):
    reply: str


# --------- OpenAI client ---------

def _get_openai_client() -> Optional[OpenAI]:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        return None
    # The SDK reads OPENAI_API_KEY automatically, but we construct explicitly for clarity.
    return OpenAI(api_key=key)


SYSTEM_PROMPT = (
    "You are an expert interview coach for software engineering candidates. "
    "Give concise, practical answers that follow structure: context → actions → impact. "
    "Prefer STAR for behavioral questions and include examples and metrics. "
    "Keep answers ~5-10 sentences unless the user asks for more. "
    "Avoid hallucinations; if unsure, say what you’d verify."
)


async def _ask_gpt(message: str, history: Optional[List[Msg]]) -> str:
    """
    Call OpenAI chat completions (non-streaming).
    Uses gpt-4o-mini (cheap & strong). Adjust if you prefer a different model.
    """
    client = _get_openai_client()
    if client is None:
        # No key set — return a friendly explanation so UI still behaves
        raise HTTPException(
            status_code=503,
            detail="Interview coach is offline (missing OPENAI_API_KEY)."
        )

    messages: List[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        # Only take the last 6 turns to control token usage
        for m in history[-6:]:
            messages.append({"role": m.role, "content": m.content})
    messages.append({"role": "user", "content": message})

    # Use a short timeout so the UI stays snappy even if the API hiccups
    try:
        with httpx.Client(timeout=15.0) as _:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.5,
                max_tokens=500,
            )
        content = resp.choices[0].message.content or ""
        return content.strip()
    except Exception as e:
        # Log in real app; here we keep it user-friendly
        raise HTTPException(status_code=502, detail=f"Coach error: {type(e).__name__}")


# --------- Route ----------

@router.post("/coach", response_model=CoachResponse)
async def coach(req: CoachRequest) -> CoachResponse:
    """
    Accepts:
      - message: the user's new question
      - history: optional short array of {role, content} (user/assistant/system)
    Returns:
      - reply: GPT-crafted coaching answer
    """
    text = req.message.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Empty message.")

    reply = await _ask_gpt(text, req.history)
    return CoachResponse(reply=reply)





