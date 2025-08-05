from dotenv import load_dotenv
load_dotenv()
import os
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_cover_letter(resume: str, job_description: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",  
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant generating professional cover letters."
            },
            {
                "role": "user",
                "content": f"Generate a cover letter based on this resume:\n{resume}\n\nAnd this job description:\n{job_description}"
            }
        ],
        temperature=0.7,
        max_tokens=800
    )
    
    return response.choices[0].message.content


