from app.config import MIN_MATCH_SCORE
from app.models.job import Job


def select_application_candidates(jobs: list[Job]) -> list[Job]:
    candidates = []

    for job in jobs:
        if job.match_score is None:
            continue

        if job.match_score >= MIN_MATCH_SCORE:
            job.application_status = "application_candidate"
            candidates.append(job)
        else:
            job.application_status = "rejected"

    return candidates
