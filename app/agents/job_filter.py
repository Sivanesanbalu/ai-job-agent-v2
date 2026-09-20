import re

from app.config import (
    LOCATIONS,
    MAX_EXPERIENCE_YEARS,
    MIN_EXPERIENCE_YEARS,
    MIN_SALARY_LPA,
    ROLES,
)
from app.models.job import Job


def _normalize(value: str) -> str:
    return " ".join(
        str(value or "").lower().split()
    ).strip()


def _location_matches(job_location: str) -> bool:
    location = _normalize(job_location)

    if not location:
        return False

    for target in LOCATIONS:
        target_normalized = _normalize(target)

        if (
            location == target_normalized
            or target_normalized in location
        ):
            return True

    return False


def _parse_salary_range(salary: str | None) -> tuple[float, float] | None:
    """
    Extract an LPA salary range.

    Examples:
        ₹5-7 LPA       -> (5.0, 7.0)
        5 - 8 LPA      -> (5.0, 8.0)
        ₹6 LPA         -> (6.0, 6.0)
        6 LPA          -> (6.0, 6.0)

    Returns None when salary cannot be safely interpreted.
    """

    if not salary:
        return None

    text = _normalize(salary)

    if "lpa" not in text:
        return None

    numbers = re.findall(
        r"\d+(?:\.\d+)?",
        text,
    )

    if not numbers:
        return None

    values = [float(value) for value in numbers]

    if len(values) == 1:
        return values[0], values[0]

    return values[0], values[1]


def _salary_matches(salary: str | None) -> bool:
    """
    A salary matches when its stated lower bound reaches
    the configured minimum.

    Unknown/unparseable salary is rejected because the agent
    should not assume that an unknown salary satisfies the
    user's minimum requirement.
    """

    salary_range = _parse_salary_range(salary)

    if salary_range is None:
        return False

    minimum, _maximum = salary_range

    return minimum >= MIN_SALARY_LPA


def _experience_matches(
    experience_years: float | None,
) -> bool:
    if experience_years is None:
        # Unknown experience is allowed at filtering stage.
        # The application matcher can evaluate the job later.
        return True

    return (
        MIN_EXPERIENCE_YEARS
        <= experience_years
        <= MAX_EXPERIENCE_YEARS
    )


def filter_jobs(jobs: list[Job]) -> list[Job]:
    filtered_jobs: list[Job] = []

    target_roles = [
        _normalize(role)
        for role in ROLES
        if _normalize(role)
    ]

    for job in jobs:
        title = _normalize(job.title)

        role_match = any(
            role in title
            for role in target_roles
        )

        location_match = _location_matches(
            job.location
        )

        experience_match = _experience_matches(
            job.experience_years
        )

        salary_match = _salary_matches(
            job.salary
        )

        if (
            role_match
            and location_match
            and experience_match
            and salary_match
        ):
            filtered_jobs.append(job)

    return filtered_jobs
