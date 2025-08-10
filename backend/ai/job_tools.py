import os
from openai import OpenAI

# Reads OPENAI_API_KEY from env automatically if not passed
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Model controls from env (with safe defaults)
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.6"))
MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "600"))

def _style_instructions(style: str) -> str:
    style = (style or "").lower()
    if style == "concise":
        return "Be concise (150–220 words), direct tone, bullet highlights where useful."
    if style == "enthusiastic":
        return "Use warm and enthusiastic tone, 180–260 words."
    if style == "entry-level":
        return "Assume limited experience; emphasize projects, coursework, and eagerness to learn; 180–240 words."
    # professional default
    return "Professional tone, structured into intro, 1–2 impact paragraphs, and closing; 180–260 words."

def generate_cover_letter(
    resume: str,
    job_desc: str,
    style: str = "professional",
    user_name: str | None = None,
    company_name: str | None = None,
) -> str:
    """
    Generates a tailored cover letter using OpenAI Chat Completions API.
    """
    style_text = _style_instructions(style)
    user_hint = ""
    if user_name:
        user_hint += f"Candidate name: {user_name}.\n"
    if company_name:
        user_hint += f"Target company: {company_name}.\n"

    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert technical recruiter and cover-letter writer. "
                "Write tailored, specific, ATS-friendly cover letters with impact metrics."
            ),
        },
        {
            "role": "user",
            "content": (
                f"{user_hint}"
                f"STYLE:\n{style_text}\n\n"
                "INSTRUCTIONS:\n"
                "- Tailor to the job description and mirror key responsibilities/skills.\n"
                "- Pull 2–3 concrete achievements from the resume with metrics.\n"
                "- Avoid generic fluff and overuse of buzzwords.\n"
                "- Keep it one page, with a clear closing and call to action.\n\n"
                f"RESUME:\n{resume}\n\n"
                f"JOB DESCRIPTION:\n{job_desc}\n\n"
                "Write the final cover letter below:\n"
            ),
        },
    ]

    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )
    return resp.choices[0].message.content.strip()



