from textwrap import fill

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
    # Naive split for demo — not real NLP.
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
    """
    Simple, deterministic letter composer. No external APIs needed.
    """

    intro_n, middle_n, close_n = _length_blocks(length)

    # Tiny "summaries" for templating
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
    # Limit based on length
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

    # Wrap lines for decent formatting
    wrapped_body = "\n".join(fill(line, width=98) if line.strip() else "" for line in body.splitlines())

    return header_text + "\n\n" + wrapped_body + "\n"
