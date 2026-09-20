from __future__ import annotations

from app.agents.fast_job_matcher import (
    CORE_SKILLS,
    FAST_MATCH_ENGINE,
)
from app.models.job import Job


def calculate_match_score(
    job: Job,
    verbose: bool = True,
) -> int:
    """
    Calculate and attach a match score.

    verbose=True:
        Show detailed scoring information.

    verbose=False:
        Silent high-throughput mode.
    """

    result = FAST_MATCH_ENGINE.score(job)

    if verbose:
        skills = ", ".join(result.matched_skills)

        skill_score = sum(
            CORE_SKILLS[skill]
            for skill in result.matched_skills
        )

        role_score = 20 if result.role_match else 0

        print()
        print(f"Job: {job.title}")
        print(f"Matched Skills: {skills}")
        print(f"Skill Score: {skill_score}")
        print(
            "Role Match: "
            f"{'Yes' if result.role_match else 'No'}"
        )
        print(f"Role Score: {role_score}")
        print(f"Final Score: {result.score}")

    return result.score
