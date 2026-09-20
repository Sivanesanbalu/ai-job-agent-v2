from app.agents.application_summary import generate_application_summary
from app.config import REQUIRE_HUMAN_REVIEW
from app.models.job import Job
from app.data.candidate_profile import CANDIDATE_PROFILE


def _generate_application_pitch(job: Job, matched_skills: list[str]) -> str:
    skills_text = ", ".join(matched_skills)

    if skills_text:
        return (
            "I am an AI Engineer specializing in Generative AI, LLMs, "
            "and AI-powered applications. My experience with "
            f"{skills_text} aligns well with this {job.title} opportunity. "
            "I also have hands-on experience building practical AI "
            "solutions using Python and modern AI frameworks."
        )

    return (
        "I am an AI Engineer specializing in Generative AI, LLMs, "
        "and AI-powered applications. I have hands-on experience "
        "building practical AI solutions using Python and modern "
        "AI frameworks, and I am interested in contributing to "
        f"the {job.title} opportunity at {job.company}."
    )


def prepare_application(job: Job) -> dict:
    summary = generate_application_summary(job)

    matched_skills = summary.get(
        "matched_candidate_skills",
        [],
    )

    pitch = _generate_application_pitch(
        job,
        matched_skills,
    )

    email = CANDIDATE_PROFILE.email

    if email:
        email = email.strip()

    return {
        "job": {
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "url": job.url,
            "match_score": job.match_score,
        },
        "candidate": {
            "name": CANDIDATE_PROFILE.name,
            "email": email,
            "headline": CANDIDATE_PROFILE.headline,
            "education": CANDIDATE_PROFILE.education,
            "notice_period_days": CANDIDATE_PROFILE.notice_period_days,
        },
        "matched_skills": matched_skills,
        "application_pitch": pitch,
        "requires_human_review": REQUIRE_HUMAN_REVIEW,
    }
