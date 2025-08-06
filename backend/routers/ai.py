from fastapi import APIRouter
from pydantic import BaseModel
from ai.job_tools import generate_cover_letter

router = APIRouter()

class InputData(BaseModel):
    resume: str
    job_description: str

def generate_cover_letter(resume: str, job_description: str) -> str:
    return f"""Dear Hiring Manager,

I am writing to express my interest in the Software Engineering Intern position for Summer 2025.

During my internship experience, I contributed to the following:
{resume}

This role aligns perfectly with my skills and interests. Here's how:
{job_description}

I am confident my background in software engineering, coupled with my eagerness to learn, make me a great fit.

Thank you for your time and consideration.

Sincerely,  
John Doe
"""

@router.post("/generate-cover-letter")
def generate(data: InputData):
    return {"cover_letter": generate_cover_letter(data.resume, data.job_description)}
