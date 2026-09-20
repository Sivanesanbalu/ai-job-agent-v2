from __future__ import annotations

from typing import Any

from app.config import (
    LOCATIONS,
    MIN_SALARY_LPA,
)


def build_search_profile(
    resume_profile: dict[str, Any],
) -> dict[str, Any]:
    """
    Build a broad search profile from the resume.

    The configured roles are suggestions, not a whitelist.
    Resume-derived capabilities remain the primary signal.
    """

    roles = list(
        resume_profile.get("roles", [])
    )

    skills = list(
        resume_profile.get("skills", [])
    )

    locations = list(
        resume_profile.get("locations", [])
    )

    for location in LOCATIONS:
        if location not in locations:
            locations.append(location)

    return {
        "roles": roles,
        "skills": skills,
        "locations": locations,
        "minimum_salary_lpa": MIN_SALARY_LPA,
        "experience_years": resume_profile.get(
            "experience_years"
        ),
        "resume_path": resume_profile.get(
            "resume_path"
        ),
    }


def build_search_queries(
    profile: dict[str, Any],
) -> list[str]:
    """
    Generate broad queries.

    The agent searches by both role families and skills,
    so unfamiliar but relevant job titles can still be found.
    """

    roles = profile.get("roles", [])
    skills = profile.get("skills", [])
    locations = profile.get("locations", [])

    queries = []

    primary_skills = [
        skill
        for skill in skills
        if skill.lower()
        in {
            "python",
            "generative ai",
            "llms",
            "rag",
            "ai agents",
            "prompt engineering",
            "langchain",
            "langgraph",
            "machine learning",
            "ai automation",
        }
    ]

    for role in roles:
        for location in locations:
            queries.append(
                f'"{role}" "{location}" jobs'
            )

    for skill in primary_skills:
        for location in locations:
            queries.append(
                f'"{skill}" "{location}" jobs'
            )

    # Broad searches for related roles.
    broad_terms = [
        "AI developer",
        "AI software engineer",
        "AI application engineer",
        "AI solutions engineer",
        "AI platform engineer",
        "machine learning developer",
        "LLM developer",
        "GenAI developer",
        "Python AI developer",
        "AI automation developer",
        "agentic AI engineer",
        "NLP engineer",
        "computer vision engineer",
    ]

    for role in broad_terms:
        for location in locations:
            queries.append(
                f'"{role}" "{location}" jobs'
            )

    # Deduplicate while preserving order.
    return list(dict.fromkeys(queries))
