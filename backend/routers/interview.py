# backend/routers/interview.py
from __future__ import annotations
from typing import List, Optional, Dict
from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..ai.job_tools import generate_interview_questions, score_answer

router = APIRouter(prefix="/interview", tags=["interview"])

class QuestionsRequest(BaseModel):
    job_description: str = Field(min_length=1, max_length=20000)
    seniority: Optional[str] = "entry"

class QuestionsResponse(BaseModel):
    questions: List[str]

@router.post("/questions", response_model=QuestionsResponse)
def questions(req: QuestionsRequest) -> QuestionsResponse:
    qs = generate_interview_questions(req.job_description, req.seniority)
    return QuestionsResponse(questions=qs)

class CoachRequest(BaseModel):
    question: str
    answer: str
    job_keywords: Optional[List[str]] = None

class CoachResponse(BaseModel):
    score: float
    feedback: str
    tips: List[str]

@router.post("/coach", response_model=CoachResponse)
def coach(req: CoachRequest) -> CoachResponse:
    out = score_answer(req.question, req.answer, req.job_keywords or [])
    return CoachResponse(**out)
