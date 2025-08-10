# backend/ai/job_tools.py
from textwrap import fill
from typing import List

# ---------- Cover letter (existing) ----------

def _tone_prefix(style: str) -> str:
    style = (style or "professional").lower()
    if style == "concise":
        return "I’m excited to submit my application."
    if style == "enthusiastic":
        return "I’m thrilled to apply and contribute immediately."
    if style == "entry-level":
        return "As a motivated early-career engineer, I’m eager to learn and make an impact."
    return "I’m excited to apply and bring my experience to your team."

def _length_blocks(length: str):
    # Returns (intro_len, middle_len, closing_len) rough paragraph sentence counts
    length = (length or "medium").lower()
    if length == "short":
        return (1, 2, 1)
    if length == "long":
        return (2, 4, 2)
    return (1, 3, 1)

def _summarize(text: str, max_sentences: int) -> str:
    sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
    return ". ".join(sentences[:max_sentences]) + ("." if sentences else "")

def generate_cover_letter(
    resume: str,
    job_desc: str,
    style: str = "professional",
    user_name: str | None = None,
    company_name: str | None = None,
    length: str = "medium",
) -> str:
    intro_n, middle_n, close_n = _length_blocks(length)

    resume_highlights = _summarize(resume, middle_n)
    job_needs = _summarize(job_desc, middle_n)
    tone = _tone_prefix(style)

    header = []
    header.append("[Your Name]")
    header.append("[Your Address]")
    header.append("[City, State, Zip]")
    header.append("[Your Email]")
    header.append("[Your Phone Number]")
    header.append("[Date]")
    header_text = "\n".join(header)

    salutation_company = company_name or "[Company's Name]"
    hiring_manager = "[Hiring Manager's Name]"

    intro = f"{tone} My background aligns well with what {salutation_company} is looking for."

    middle_parts = [
        f"In your description, I noticed you value: {job_needs}",
        f"My relevant experience includes: {resume_highlights}",
        "I’m comfortable with modern development practices and collaborating across teams.",
    ]
    middle = " ".join(middle_parts[:middle_n])

    close = "Thank you for your time and consideration. I’d welcome the chance to discuss how I can help your team."
    if style == "enthusiastic":
        close = "Thank you for your time and consideration — I’d love to discuss how I can help your team move faster."

    signature_name = user_name or "[Your Name]"

    body = (
        f"Dear {hiring_manager},\n\n"
        f"{intro}\n\n"
        f"{middle}\n\n"
        f"{close}\n\n"
        f"Sincerely,\n{signature_name}"
    )

    wrapped_body = "\n".join(fill(line, width=98) if line.strip() else "" for line in body.splitlines())
    return header_text + "\n\n" + wrapped_body + "\n"

# ---------- Resume tailoring ----------

def _extract_keywords(text: str, n: int = 12) -> List[str]:
    import re
    words = re.findall(r"[A-Za-z][A-Za-z0-9\+\#\-]{1,}", text.lower())
    stop = {"and","or","with","for","the","a","an","in","to","of","on","as","is","are","be","this","that","you","we"}
    freq = {}
    for w in words:
        if w in stop or len(w) < 3:
            continue
        freq[w] = freq.get(w, 0) + 1
    return [w for w,_ in sorted(freq.items(), key=lambda kv: kv[1], reverse=True)[:n]]

def tailor_resume(
    resume: str,
    job_desc: str,
    focus: str = "skills",
    bullets: int = 6
) -> str:
    """Deterministic tailoring: pulls keywords from JD and aligns resume bullets."""
    jd_keys = _extract_keywords(job_desc, 15)
    res_keys = _extract_keywords(resume, 15)

    intersection = [k for k in res_keys if k in jd_keys]
    gap = [k for k in jd_keys if k not in res_keys][:max(0, bullets - len(intersection))]

    lines = []
    lines.append("SUMMARY")
    lines.append(
        "Adaptable engineer matching the role’s needs, with strengths across "
        + ", ".join(intersection[:5] or res_keys[:5])
        + "."
    )
    lines.append("")
    lines.append("TARGETED HIGHLIGHTS")
    for k in intersection[:bullets]:
        lines.append(f"• Hands-on experience with {k}, applied in production or projects.")
    for k in gap:
        lines.append(f"• Familiarity with {k}; quickly pick up new tools/tech through focused practice.")
    lines.append("")
    lines.append("SELECTED EXPERIENCE (TRIMMED)")
    lines.append(_summarize(resume, 6))
    return "\n".join(lines)

# ---------- Interview questions & coaching ----------

def generate_interview_questions(job_desc: str, seniority: str = "entry") -> List[str]:
    keys = _extract_keywords(job_desc, 12)
    base = [
        "Walk me through a recent project you’re proud of. What was your role and impact?",
        "How do you approach debugging complex issues end-to-end?",
        "Describe a time you improved a system’s performance or reliability.",
        "How do you ensure code quality and maintainability under deadlines?",
        "Tell me about collaborating with cross-functional partners.",
    ]
    tech = [f"Deep dive: What’s your experience with {k}?" for k in keys[:5]]
    if seniority.lower() in {"mid", "senior"}:
        base.append("How do you plan and decompose ambiguous work for the team?")
        base.append("Give an example of influencing architecture decisions.")
    return tech + base

def score_answer(question: str, answer: str, job_keywords: List[str]) -> dict:
    length = len(answer.split())
    has_examples = any(x in answer.lower() for x in ["for example", "e.g.", "for instance", "i built", "i designed"])
    keyword_hits = sum(1 for k in job_keywords if k.lower() in answer.lower())

    score = 0.0
    score += min(4.0, length / 40.0)        # ~160 words hits 4 pts
    if has_examples:
        score += 3.0
    score += min(3.0, keyword_hits * 0.6)

    tips = []
    if length < 80: tips.append("Add more detail—aim for 120–180 words with one concrete example.")
    if not has_examples: tips.append("Include a specific example (metrics, ownership, result).")
    if keyword_hits < 2 and job_keywords:
        tips.append("Weave in role-specific keywords from the job description.")

    return {
        "score": round(min(10.0, score), 2),
        "feedback": "Clear and strong" if score > 7 else "Good start—add more specifics",
        "tips": tips or ["Nice work—keep answers structured: context → actions → results."],
    }
