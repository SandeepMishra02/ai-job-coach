from fastapi import APIRouter
from pydantic import BaseModel
from ai.job_tools import generate_cover_letter

router = APIRouter()

class InputData(BaseModel):
    resume: str
    job_description: str

@router.post("/generate-cover-letter")
def generate(data: InputData):
    # Call the logic from your ai module
    return {"cover_letter": generate_cover_letter(data.resume, data.job_description)}
