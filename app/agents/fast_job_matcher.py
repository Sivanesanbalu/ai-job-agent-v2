from __future__ import annotations

from dataclasses import dataclass

from app.config import MIN_MATCH_SCORE, ROLES
from app.data.candidate_profile import CANDIDATE_PROFILE
from app.models.job import Job


# ---------------------------------------------------------------------------
# Skill weights
# ---------------------------------------------------------------------------

CORE_SKILLS: dict[str, int] = {
    "generative ai": 12,
    "llm": 12,
    "rag": 10,
    "ai agents": 10,
    "prompt engineering": 10,
    "python": 8,
    "langchain": 7,
    "langgraph": 6,
    "fastapi": 5,
    "pytorch": 4,
    "faiss": 4,
    "docker": 4,
    "ai automation": 10,
}


ROLE_KEYWORDS = tuple(
    role.strip().lower()
    for role in ROLES
    if role.strip()
)


# ---------------------------------------------------------------------------
# Match result
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class MatchResult:
    job: Job
    score: int
    matched_skills: tuple[str, ...]
    role_match: bool


# ---------------------------------------------------------------------------
# Fast matching engine
# ---------------------------------------------------------------------------

class FastMatchEngine:
    """
    Fast candidate/job matching engine.

    Score structure:

        Role alignment      -> 30 points
        Skill alignment     -> 70 points

    Skill weights are capped at 70.
    """

    __slots__ = (
        "_roles",
        "_skills",
        "_min_score",
        "_candidate_roles",
        "_candidate_skills",
    )

    def __init__(
        self,
        roles: tuple[str, ...] = ROLE_KEYWORDS,
        skills: dict[str, int] = CORE_SKILLS,
        min_score: int = MIN_MATCH_SCORE,
    ):
        self._roles = roles
        self._skills = tuple(
            (skill.lower(), weight)
            for skill, weight in skills.items()
        )
        self._min_score = min_score

        self._candidate_roles = tuple(
            role.strip().lower()
            for role in CANDIDATE_PROFILE.preferred_roles
            if role and role.strip()
        )

        self._candidate_skills = frozenset(
            skill.strip().lower()
            for skill in CANDIDATE_PROFILE.skills
            if skill and skill.strip()
        )

    # ------------------------------------------------------------------
    # Text preparation
    # ------------------------------------------------------------------

    @staticmethod
    def _text(job: Job) -> str:
        return (
            f"{job.title} "
            f"{job.description}"
        ).lower()

    # ------------------------------------------------------------------
    # Role matching
    # ------------------------------------------------------------------

    def role_match(self, title: str) -> bool:
        title_lower = title.lower()

        return any(
            role in title_lower
            for role in self._roles
        )

    def candidate_role_match(self, title: str) -> bool:
        title_lower = title.lower()

        return any(
            role in title_lower
            for role in self._candidate_roles
        )

    # ------------------------------------------------------------------
    # Detailed score
    # ------------------------------------------------------------------

    def score(self, job: Job) -> MatchResult:
        text = self._text(job)

        matched: list[str] = []
        skill_score = 0

        for skill, weight in self._skills:
            if skill in text:
                matched.append(skill)
                skill_score += weight

        # Skill score is capped at 70.
        skill_score = min(skill_score, 70)

        # Strong exact target-role alignment.
        target_role_match = self.role_match(job.title)

        # Candidate-profile role alignment.
        profile_role_match = self.candidate_role_match(job.title)

        if target_role_match:
            role_score = 20
        else:
            role_score = 0

        if profile_role_match:
            role_score += 10

        role_score = min(role_score, 30)

        final_score = min(
            skill_score + role_score,
            100,
        )

        job.match_score = final_score

        return MatchResult(
            job=job,
            score=final_score,
            matched_skills=tuple(matched),
            role_match=target_role_match,
        )

    # ------------------------------------------------------------------
    # Batch scoring
    # ------------------------------------------------------------------

    def score_many(
        self,
        jobs: list[Job],
    ) -> list[MatchResult]:
        results: list[MatchResult] = []

        append = results.append
        score = self.score

        for job in jobs:
            result = score(job)

            if result.score >= self._min_score:
                append(result)

        return results


FAST_MATCH_ENGINE = FastMatchEngine()
