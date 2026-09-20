from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any

import requests

from app.config import (
    MAX_EXPERIENCE_YEARS,
    MIN_EXPERIENCE_YEARS,
    MIN_MATCH_SCORE,
    MIN_SALARY_LPA,
)
from app.intelligence.resume_intelligence import (
    load_resume_profile,
)
from app.models.job import Job


OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://127.0.0.1:11434",
).rstrip("/")

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "",
).strip()


@dataclass
class AIJobDecision:
    apply: bool
    score: int
    relevance: str
    matched_skills: list[str]
    missing_skills: list[str]
    experience_match: bool
    location_match: bool
    salary_match: bool
    reason: str
    model: str


class AIJobAnalyzer:
    """
    Resume-driven autonomous job matching engine.

    The candidate resume/profile is the source of truth.

    The engine:
        1. Reads the actual job listing.
        2. Sends the candidate profile + job description to Ollama.
        3. Lets the model determine technical/job relevance.
        4. Applies deterministic safety constraints afterward.

    There is NO fixed job-title whitelist.

    A role can be considered if its actual responsibilities are
    relevant to the candidate's resume, even when the title is
    different from the candidate's preferred titles.

    Deterministic constraints:
        - Location must be relevant.
        - Explicit experience requirement above candidate range
          causes rejection.
        - Explicit salary below configured minimum causes rejection.
        - Unknown salary does NOT automatically reject.
        - Unknown experience does NOT automatically reject.

    The LLM is responsible for:
        - semantic role relevance
        - skill overlap
        - transferable skills
        - technical fit
        - seniority interpretation
        - overall match score
    """

    def __init__(
        self,
        timeout: float = 90.0,
    ):
        self.timeout = timeout
        self.profile = load_resume_profile()
        self.model = self._resolve_model()

    # ============================================================
    # OLLAMA
    # ============================================================

    def _resolve_model(self) -> str:
        if OLLAMA_MODEL:
            return OLLAMA_MODEL

        try:
            response = requests.get(
                f"{OLLAMA_BASE_URL}/api/tags",
                timeout=5,
            )

            response.raise_for_status()

            data = response.json()

            models = data.get(
                "models",
                [],
            )

            if models:
                name = models[0].get(
                    "name",
                    "",
                )

                if name:
                    return name

        except Exception:
            pass

        return ""

    def is_available(self) -> bool:
        if not self.model:
            return False

        try:
            response = requests.get(
                f"{OLLAMA_BASE_URL}/api/tags",
                timeout=5,
            )

            return response.ok

        except Exception:
            return False

    # ============================================================
    # NORMALIZATION
    # ============================================================

    @staticmethod
    def normalize_text(
        value: Any,
    ) -> str:
        return " ".join(
            str(value or "")
            .lower()
            .split()
        )

    # ============================================================
    # SALARY
    # ============================================================

    @staticmethod
    def parse_salary_lpa(
        salary: str | None,
    ) -> float | None:
        """
        Parse an explicitly stated salary.

        Examples:
            ₹5-7 LPA      -> 5.0
            5-8 LPA       -> 5.0
            6 LPA         -> 6.0
            ₹15 LPA       -> 15.0
            ₹5-18 Lacs    -> 5.0

        Unknown/unparseable salary returns None.
        """

        if not salary:
            return None

        text = str(
            salary
        ).lower()

        if not any(
            token in text
            for token in [
                "lpa",
                "lakh",
                "lac",
                "₹",
                "rs.",
                "inr",
            ]
        ):
            return None

        matches = re.findall(
            r"(\d+(?:\.\d+)?)",
            text,
        )

        if not matches:
            return None

        try:
            numbers = [
                float(value)
                for value in matches
            ]
        except Exception:
            return None

        if not numbers:
            return None

        # Salary ranges use the lower bound for the minimum
        # salary constraint.
        return min(numbers)

    # ============================================================
    # EXPERIENCE
    # ============================================================

    @staticmethod
    def parse_explicit_experience(
        title: str,
        description: str,
    ) -> float | None:
        """
        Extract an explicit minimum experience requirement.

        This intentionally avoids scanning arbitrary numbers.

        Examples detected:
            3+ years experience
            minimum 2 years experience
            2-4 years experience
            5 years of experience
            0-1 years
            1-2 years

        Generic numbers such as:
            202510
            2026
            5 projects
            10 clients

        are ignored.
        """

        text = (
            f"{title}\n{description}"
        )

        # --------------------------------------------------------
        # Explicit "X+ years"
        # --------------------------------------------------------

        patterns = [
            r"\b(\d+(?:\.\d+)?)\s*\+\s*(?:years?|yrs?)"
            r"(?:\s+of)?\s+experience\b",

            r"\bminimum\s+(?:of\s+)?"
            r"(\d+(?:\.\d+)?)\s*"
            r"(?:years?|yrs?)"
            r"(?:\s+of)?\s+experience\b",

            r"\b(\d+(?:\.\d+)?)\s*"
            r"(?:years?|yrs?)\s+"
            r"(?:of\s+)?experience\b",
        ]

        for pattern in patterns:
            match = re.search(
                pattern,
                text,
                re.IGNORECASE,
            )

            if match:
                try:
                    return float(
                        match.group(1)
                    )
                except Exception:
                    pass

        # --------------------------------------------------------
        # Explicit range.
        #
        # For "2-4 years", minimum is 2.
        # --------------------------------------------------------

        range_patterns = [
            r"\b(\d+(?:\.\d+)?)\s*"
            r"(?:-|–|to)\s*"
            r"(\d+(?:\.\d+)?)\s*"
            r"(?:years?|yrs?)\b",

            r"\b(\d+(?:\.\d+)?)\s*"
            r"(?:-|–|to)\s*"
            r"(\d+(?:\.\d+)?)\s*"
            r"(?:years?|yrs?)"
            r"(?:\s+of)?\s+experience\b",
        ]

        for pattern in range_patterns:
            match = re.search(
                pattern,
                text,
                re.IGNORECASE,
            )

            if match:
                try:
                    return min(
                        float(match.group(1)),
                        float(match.group(2)),
                    )
                except Exception:
                    pass

        # --------------------------------------------------------
        # Fresher / entry-level indicators.
        # --------------------------------------------------------

        lower = text.lower()

        fresher_patterns = [
            "fresher",
            "freshers",
            "fresh graduate",
            "recent graduate",
            "entry level",
            "entry-level",
            "0-1 years",
            "0 to 1 years",
            "0–1 years",
            "0-2 years",
            "0 to 2 years",
            "graduates welcome",
            "new graduates",
        ]

        if any(
            phrase in lower
            for phrase in fresher_patterns
        ):
            return 0.0

        return None

    # ============================================================
    # LOCATION
    # ============================================================

    def check_location(
        self,
        job: Job,
    ) -> bool:

        job_location = self.normalize_text(
            job.location
        )

        profile_locations = [
            self.normalize_text(value)
            for value in self.profile.get(
                "locations",
                [],
            )
        ]

        configured_locations = [
            "coimbatore",
            "chennai",
            "bengaluru",
            "bangalore",
            "hyderabad",
            "pune",
            "gurugram",
            "gurgaon",
            "gujarat",
        ]

        allowed = set(
            profile_locations
            + configured_locations
        )

        if "remote" in job_location:
            return True

        if "india" in job_location:
            # Only treat India-wide location as acceptable when the
            # listing explicitly says remote/work-from-anywhere or
            # the actual location contains one of the configured cities.
            if any(
                location in job_location
                for location in allowed
                if location
            ):
                return True

        return any(
            location in job_location
            or job_location in location
            for location in allowed
            if location
        )

    # ============================================================
    # DETERMINISTIC CONSTRAINTS
    # ============================================================

    def hard_constraint_check(
        self,
        job: Job,
    ) -> dict:
        """
        Deterministic checks performed AFTER extracting the real
        job page.

        Unknown salary is allowed to continue.

        Unknown experience is allowed to continue.

        The AI gets the actual description and decides semantic fit.
        """

        title = str(
            job.title or ""
        )

        description = str(
            job.description or ""
        )

        # --------------------------------------------------------
        # Salary
        # --------------------------------------------------------

        salary = self.parse_salary_lpa(
            job.salary
        )

        if salary is None:
            salary = self.parse_salary_lpa(
                description
            )

        if salary is None:
            salary_match = True
            salary_known = False
        else:
            salary_match = (
                salary >= MIN_SALARY_LPA
            )
            salary_known = True

        # --------------------------------------------------------
        # Location
        # --------------------------------------------------------

        location_match = (
            self.check_location(job)
        )

        # --------------------------------------------------------
        # Experience
        # --------------------------------------------------------

        explicit_experience = (
            self.parse_explicit_experience(
                title,
                description,
            )
        )

        if explicit_experience is None:
            experience_match = True
            experience_known = False

        else:
            experience_match = (
                MIN_EXPERIENCE_YEARS
                <= explicit_experience
                <= MAX_EXPERIENCE_YEARS
            )

            experience_known = True

        # --------------------------------------------------------
        # Do NOT independently reject "Senior" here.
        #
        # The title can say senior while the actual listing may
        # have unusual requirements. The LLM receives the title
        # and description and evaluates seniority.
        # --------------------------------------------------------

        return {
            "salary": salary,
            "salary_known": salary_known,
            "salary_match": salary_match,
            "experience": explicit_experience,
            "experience_known": experience_known,
            "experience_match": experience_match,
            "location_match": location_match,
        }

    # ============================================================
    # RESUME REPRESENTATION
    # ============================================================

    def resume_text(self) -> str:
        roles = self.profile.get(
            "roles",
            [],
        )

        skills = self.profile.get(
            "skills",
            [],
        )

        education = self.profile.get(
            "education",
            "",
        )

        experience = self.profile.get(
            "experience",
            "",
        )

        return f"""
CANDIDATE RESUME PROFILE

Name:
{self.profile.get("name", "Candidate")}

Headline:
{self.profile.get("headline", "")}

Relevant Roles:
{", ".join(map(str, roles))}

Technical Skills:
{", ".join(map(str, skills))}

Education:
{education}

Experience:
{experience}

The candidate is an early-career AI/ML candidate.
Use the actual profile above as the source of truth.
Do not invent skills, experience, qualifications, or certifications.
""".strip()

    # ============================================================
    # PROMPT
    # ============================================================

    def build_prompt(
        self,
        job: Job,
        constraints: dict,
    ) -> str:

        salary_status = (
            f"Known minimum salary: "
            f"{constraints['salary']} LPA"
            if constraints["salary_known"]
            else "Salary: not disclosed"
        )

        experience_status = (
            f"Explicit minimum experience: "
            f"{constraints['experience']} years"
            if constraints["experience_known"]
            else "Experience requirement: not explicitly stated"
        )

        return f"""
You are an expert technical recruiter performing a STRICT,
resume-driven job match.

Your task is NOT to judge the candidate generally.

Your task is to compare ONLY:

1. the candidate resume/profile
2. the actual job listing

Do not use a fixed job-title whitelist.

A job should be considered relevant when its actual work,
responsibilities, technologies, and required qualifications align
with the candidate's capabilities, even if the title is different.

IMPORTANT CANDIDATE RULES:

- Candidate experience is early-career.
- Candidate does NOT have multiple years of professional AI/ML
  experience.
- Do NOT invent experience.
- Do NOT assume missing technologies.
- Projects, internships, academic work, and demonstrated technical
  skills may count as relevant capability, but must not be described
  as professional years of experience.
- A job explicitly requiring more than the candidate's configured
  experience range should normally be rejected.
- Senior/lead/principal titles are strong negative signals, but
  evaluate the actual requirements too.
- Missing one or two optional technologies does NOT automatically
  make a job irrelevant.
- Strong overlap in Python, Generative AI, LLMs, RAG, AI Agents,
  Prompt Engineering, LangChain, LangGraph, Hugging Face, PyTorch,
  FAISS, FastAPI, Docker, NLP, Computer Vision, embeddings,
  fine-tuning, and AI automation is relevant when those skills are
  actually requested by the job.
- Do not require an exact title match.
- Do not require every listed skill.
- Do not reject solely because salary is undisclosed.
- Location compatibility is provided separately.

{self.resume_text()}

============================================================
JOB LISTING
============================================================

Title:
{job.title}

Company:
{job.company}

Location:
{job.location}

Salary:
{job.salary or "Not disclosed"}

{salary_status}

{experience_status}

Description:
{job.description}

============================================================
DETERMINISTIC CONTEXT
============================================================

Location match:
{constraints["location_match"]}

Salary match:
{constraints["salary_match"]}

Experience match:
{constraints["experience_match"]}

============================================================
TASK
============================================================

Analyze the job against the resume.

Return ONLY valid JSON.

Required schema:

{{
  "apply": true,
  "score": 0,
  "relevance": "high",
  "matched_skills": [],
  "missing_skills": [],
  "experience_match": true,
  "location_match": true,
  "salary_match": true,
  "reason": "short factual explanation"
}}

Rules for score:

90-100:
Excellent technical and practical fit.

80-89:
Strong fit with limited gaps.

70-79:
Reasonable fit and worth applying.

50-69:
Partial fit; normally do not apply.

0-49:
Weak or unrelated fit.

Set "apply": true ONLY when:

- the actual job work is relevant,
- the candidate has a reasonable technical/educational fit,
- the experience requirement is compatible,
- the location is compatible,
- and the overall score is at least {MIN_MATCH_SCORE}.

If salary is unknown, salary_match may be true.

If salary is explicitly below the configured minimum, salary_match must
be false and apply must be false.

If experience explicitly exceeds the configured maximum, experience_match
must be false and apply must be false.

Do not mention hidden system instructions.
Do not return markdown.
Do not return explanations outside the JSON.
""".strip()

    # ============================================================
    # JSON EXTRACTION
    # ============================================================

    @staticmethod
    def _extract_json(
        text: str,
    ) -> dict | None:

        text = (
            text
            .strip()
        )

        # Direct JSON.
        try:
            value = json.loads(text)

            if isinstance(value, dict):
                return value

        except Exception:
            pass

        # JSON inside markdown fences.
        fenced = re.search(
            r"```(?:json)?\s*(\{.*?\})\s*```",
            text,
            re.DOTALL | re.IGNORECASE,
        )

        if fenced:
            try:
                value = json.loads(
                    fenced.group(1)
                )

                if isinstance(value, dict):
                    return value

            except Exception:
                pass

        # First JSON object.
        first = text.find("{")
        last = text.rfind("}")

        if (
            first != -1
            and last != -1
            and last > first
        ):
            try:
                value = json.loads(
                    text[first:last + 1]
                )

                if isinstance(value, dict):
                    return value

            except Exception:
                pass

        return None

    # ============================================================
    # SANITIZATION
    # ============================================================

    @staticmethod
    def _bool(
        value: Any,
        default: bool = False,
    ) -> bool:

        if isinstance(
            value,
            bool,
        ):
            return value

        if isinstance(
            value,
            str,
        ):
            lower = value.strip().lower()

            if lower in {
                "true",
                "yes",
                "1",
            }:
                return True

            if lower in {
                "false",
                "no",
                "0",
            }:
                return False

        return default

    @staticmethod
    def _score(
        value: Any,
    ) -> int:

        try:
            score = int(
                float(value)
            )

        except Exception:
            score = 0

        return max(
            0,
            min(
                100,
                score,
            ),
        )

    @staticmethod
    def _string_list(
        value: Any,
    ) -> list[str]:

        if not isinstance(
            value,
            list,
        ):
            return []

        result = []

        for item in value:
            if item is None:
                continue

            item = str(
                item
            ).strip()

            if item:
                result.append(
                    item
                )

        return result

    # ============================================================
    # OLLAMA REQUEST
    # ============================================================

    def _call_ollama(
        self,
        prompt: str,
    ) -> dict | None:

        if not self.model:
            return None

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0,
            },
        }

        try:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json=payload,
                timeout=self.timeout,
            )

            response.raise_for_status()

            data = response.json()

            raw = data.get(
                "response",
                "",
            )

            return self._extract_json(
                raw
            )

        except Exception as error:
            print(
                f"  Ollama error: {error}"
            )

            return None

    # ============================================================
    # FALLBACK
    # ============================================================

    def _fallback_decision(
        self,
        job: Job,
        constraints: dict,
        reason: str,
    ) -> AIJobDecision:

        # If Ollama fails, do NOT blindly auto-apply.
        return AIJobDecision(
            apply=False,
            score=0,
            relevance="unknown",
            matched_skills=[],
            missing_skills=[],
            experience_match=constraints[
                "experience_match"
            ],
            location_match=constraints[
                "location_match"
            ],
            salary_match=constraints[
                "salary_match"
            ],
            reason=(
                "AI analysis unavailable. "
                + reason
            ),
            model=self.model,
        )

    # ============================================================
    # FINAL ANALYSIS
    # ============================================================

    def analyze(
        self,
        job: Job,
    ) -> AIJobDecision:

        constraints = (
            self.hard_constraint_check(
                job
            )
        )

        # --------------------------------------------------------
        # Location is a deterministic hard constraint.
        # --------------------------------------------------------

        if not constraints[
            "location_match"
        ]:

            return AIJobDecision(
                apply=False,
                score=0,
                relevance="low",
                matched_skills=[],
                missing_skills=[],
                experience_match=constraints[
                    "experience_match"
                ],
                location_match=False,
                salary_match=constraints[
                    "salary_match"
                ],
                reason=(
                    "Job location is outside the "
                    "configured candidate locations."
                ),
                model=self.model,
            )

        # --------------------------------------------------------
        # Explicit salary below minimum.
        # --------------------------------------------------------

        if (
            constraints["salary_known"]
            and not constraints["salary_match"]
        ):

            return AIJobDecision(
                apply=False,
                score=0,
                relevance="low",
                matched_skills=[],
                missing_skills=[],
                experience_match=constraints[
                    "experience_match"
                ],
                location_match=True,
                salary_match=False,
                reason=(
                    f"Explicit salary is below "
                    f"the configured ₹{MIN_SALARY_LPA:g} LPA minimum."
                ),
                model=self.model,
            )

        # --------------------------------------------------------
        # Explicit experience above maximum.
        # --------------------------------------------------------

        if (
            constraints["experience_known"]
            and not constraints["experience_match"]
        ):

            return AIJobDecision(
                apply=False,
                score=0,
                relevance="low",
                matched_skills=[],
                missing_skills=[],
                experience_match=False,
                location_match=True,
                salary_match=constraints[
                    "salary_match"
                ],
                reason=(
                    "Explicit experience requirement "
                    f"({constraints['experience']} years) "
                    "is outside the configured "
                    f"{MIN_EXPERIENCE_YEARS}-"
                    f"{MAX_EXPERIENCE_YEARS} year range."
                ),
                model=self.model,
            )

        # --------------------------------------------------------
        # AI analysis.
        # --------------------------------------------------------

        prompt = self.build_prompt(
            job,
            constraints,
        )

        result = self._call_ollama(
            prompt
        )

        if result is None:
            return self._fallback_decision(
                job,
                constraints,
                "No valid JSON response from Ollama.",
            )

        score = self._score(
            result.get(
                "score",
                0,
            )
        )

        relevance = str(
            result.get(
                "relevance",
                "unknown",
            )
        ).strip().lower()

        if relevance not in {
            "high",
            "medium",
            "low",
        }:
            relevance = "unknown"

        matched_skills = (
            self._string_list(
                result.get(
                    "matched_skills",
                    [],
                )
            )
        )

        missing_skills = (
            self._string_list(
                result.get(
                    "missing_skills",
                    [],
                )
            )
        )

        experience_match = (
            self._bool(
                result.get(
                    "experience_match",
                    constraints[
                        "experience_match"
                    ],
                ),
                constraints[
                    "experience_match"
                ],
            )
        )

        location_match = (
            self._bool(
                result.get(
                    "location_match",
                    constraints[
                        "location_match"
                    ],
                ),
                constraints[
                    "location_match"
                ],
            )
        )

        salary_match = (
            self._bool(
                result.get(
                    "salary_match",
                    constraints[
                        "salary_match"
                    ],
                ),
                constraints[
                    "salary_match"
                ],
            )
        )

        reason = str(
            result.get(
                "reason",
                "",
            )
        ).strip()

        # --------------------------------------------------------
        # FINAL SAFETY OVERRIDES
        #
        # The LLM cannot override deterministic constraints.
        # --------------------------------------------------------

        if not constraints[
            "location_match"
        ]:
            apply = False
            reason = (
                "Job location is outside "
                "configured locations."
            )

        elif (
            constraints["salary_known"]
            and not constraints["salary_match"]
        ):
            apply = False
            reason = (
                f"Explicit salary is below "
                f"₹{MIN_SALARY_LPA:g} LPA."
            )

        elif (
            constraints["experience_known"]
            and not constraints["experience_match"]
        ):
            apply = False
            reason = (
                "Explicit experience requirement "
                "exceeds the configured candidate range."
            )

        elif not experience_match:
            apply = False
            reason = (
                reason
                or "Experience does not match."
            )

        elif not location_match:
            apply = False
            reason = (
                reason
                or "Location does not match."
            )

        elif not salary_match:
            # This mainly catches an LLM incorrectly saying salary
            # doesn't match when the deterministic salary is valid.
            apply = False
            reason = (
                reason
                or "Salary requirement does not match."
            )

        else:
            apply = (
                self._bool(
                    result.get(
                        "apply",
                        False,
                    )
                )
                and score >= MIN_MATCH_SCORE
                and relevance in {
                    "high",
                    "medium",
                }
            )

        if not reason:
            reason = (
                "Job evaluated against the "
                "candidate resume."
            )

        return AIJobDecision(
            apply=apply,
            score=score,
            relevance=relevance,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            experience_match=experience_match,
            location_match=location_match,
            salary_match=salary_match,
            reason=reason,
            model=self.model,
        )
