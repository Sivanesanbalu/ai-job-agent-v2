from __future__ import annotations

from heapq import nlargest

from app.agents.fast_job_matcher import (
    FAST_MATCH_ENGINE,
    MatchResult,
)
from app.models.job import Job


def select_top_jobs(
    jobs: list[Job],
    limit: int | None = None,
) -> list[Job]:
    """
    Score matching jobs and return candidates.

    limit=None means return every job that satisfies the
    minimum match score.
    """

    if not jobs:
        return []

    results: list[MatchResult] = (
        FAST_MATCH_ENGINE.score_many(jobs)
    )

    if not results:
        return []

    if limit is None:
        # Keep every matching job.
        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return [
            result.job
            for result in results
        ]

    top_results = nlargest(
        limit,
        results,
        key=lambda result: result.score,
    )

    return [
        result.job
        for result in top_results
    ]
