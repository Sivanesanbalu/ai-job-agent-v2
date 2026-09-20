import re

from app.agents.application_summary import generate_application_summary
from app.models.job import Job


def _clean_text(value: str) -> str:
    if not value:
        return ""

    text = str(value)

    replacements = {
        "andAI-powered": "and AI-powered",
        "Agentsaligns": "Agents aligns",
        "AIaligns": "AI aligns",
        "GenerativeAI": "Generative AI",
        "generativeai": "Generative AI",
        "AIAgents": "AI Agents",
        "AIagents": "AI Agents",
        "AIpowered": "AI-powered",
        "APIBrowser": "API Browser",
        "apiBrowser": "API Browser",
        "AIFrameworks": "AI Frameworks",
        "buildingpractical": "building practical",
        "alignswell": "aligns well",
        "FieldWorkflowTest": "Field Workflow Test",
        "FieldWorkflow": "Field Workflow",
        "WorkflowTest": "Workflow Test",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Add missing boundaries between lowercase and uppercase letters.
    text = re.sub(
        r"(?<=[a-z])(?=[A-Z])",
        " ",
        text,
    )

    # Normalize separators.
    text = re.sub(r"\s*\|\s*", " | ", text)
    text = re.sub(r"\s*,\s*", ", ", text)

    # Normalize whitespace.
    text = re.sub(r"\s+", " ", text).strip()

    return text


def generate_application_pitch(job: Job) -> str:
    summary = generate_application_summary(job)

    matched_skills = []

    for skill in summary.get("matched_candidate_skills", []):
        cleaned_skill = _clean_text(skill)

        if cleaned_skill:
            matched_skills.append(cleaned_skill)

    skills_text = ", ".join(matched_skills)

    if not skills_text:
        skills_text = "AI and Generative AI"

    job_title = _clean_text(
        summary.get("job_title") or job.title
    )

    raw_pitch = (
        "I am an AI Engineer specializing in Generative AI, LLMs, "
        "and AI-powered applications. "
        f"My experience with {skills_text} "
        f"aligns well with this {job_title} opportunity. "
        "I also have hands-on experience building practical AI "
        "solutions using Python and modern AI frameworks."
    )

    # Normalize the complete final output.
    return _clean_text(raw_pitch)
