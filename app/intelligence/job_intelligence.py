from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Any

from app.models.job import Job


@dataclass
class JobAnalysis:
    title: str
    company: str
    location: str
    url: str

    matched_skills: list[str]

    detected_experience_min: float | None
    detected_experience_max: float | None

    detected_salary_min: float | None
    detected_salary_max: float | None

    role_relevance: float
    skill_relevance: float
    experience_relevance: float
    overall_score: int

    decision: str
    reasons: list[str]

    def to_dict(self):
        return asdict(self)

    @property
    def final_score(self) -> int:
        return self.overall_score

    @property
    def recommendation(self) -> str:
        return self.decision

    @property
    def detected_roles(self) -> list[str]:
        return []

    @property
    def detected_skills(self) -> list[str]:
        return self.matched_skills

    @property
    def minimum_salary_lpa(self) -> float | None:
        return self.detected_salary_min

    @property
    def minimum_experience_years(self) -> float | None:
        return self.detected_experience_min


class ResumeJobAnalyzer:
    """
    Compares a real job against the actual resume profile.

    No hard-coded role whitelist is used as the final decision.
    A job can match through related role wording and skills.
    """

    def __init__(
        self,
        resume_profile: dict[str, Any],
        minimum_score: int = 70,
    ):
        self.profile = resume_profile
        self.minimum_score = minimum_score

        self.skills = {
            skill.lower()
            for skill in resume_profile.get(
                "skills",
                [],
            )
        }

    @staticmethod
    def job_text(job: Job) -> str:
        return (
            f"{job.title} "
            f"{job.company} "
            f"{job.location} "
            f"{job.description} "
            f"{job.salary or ''}"
        ).lower()

    def detect_job_skills(
        self,
        text: str,
    ) -> list[str]:
        aliases = {
            "python": "Python",
            "generative ai": "Generative AI",
            "genai": "Generative AI",
            "llm": "LLMs",
            "llms": "LLMs",
            "rag": "RAG",
            "retrieval augmented generation": "RAG",
            "ai agent": "AI Agents",
            "ai agents": "AI Agents",
            "agentic ai": "AI Agents",
            "prompt engineering": "Prompt Engineering",
            "langchain": "LangChain",
            "langgraph": "LangGraph",
            "pytorch": "PyTorch",
            "hugging face": "Hugging Face",
            "huggingface": "Hugging Face",
            "faiss": "FAISS",
            "fastapi": "FastAPI",
            "docker": "Docker",
            "sql": "SQL",
            "nlp": "NLP",
            "computer vision": "Computer Vision",
            "opencv": "Computer Vision",
            "embeddings": "Embeddings",
            "fine-tuning": "Fine-tuning",
            "machine learning": "Machine Learning",
            "deep learning": "Deep Learning",
            "ai automation": "AI Automation",
            "scikit-learn": "Scikit-learn",
            "sklearn": "Scikit-learn",
        }

        found = []

        for alias, canonical in aliases.items():
            if alias in text and canonical not in found:
                found.append(canonical)

        return found

    def extract_experience(
        self,
        text: str,
    ) -> tuple[float | None, float | None]:
        patterns = [
            r"(\d+(?:\.\d+)?)\s*(?:-|to)\s*"
            r"(\d+(?:\.\d+)?)\s*years?",
            r"(\d+(?:\.\d+)?)\s*\+?\s*years?",
        ]

        for pattern in patterns:
            match = re.search(
                pattern,
                text,
                re.IGNORECASE,
            )

            if not match:
                continue

            if len(match.groups()) == 2:
                return (
                    float(match.group(1)),
                    float(match.group(2)),
                )

            value = float(match.group(1))
            return value, value

        fresher_terms = [
            "fresher",
            "freshers",
            "0-1 years",
            "0 - 1 years",
            "0 to 1 years",
            "entry level",
            "entry-level",
        ]

        if any(
            term in text
            for term in fresher_terms
        ):
            return 0.0, 1.0

        return None, None

    def extract_salary(
        self,
        job: Job,
        text: str,
    ) -> tuple[float | None, float | None]:
        source = (
            f"{job.salary or ''} {text}"
        )

        patterns = [
            r"(\d+(?:\.\d+)?)\s*[-–]\s*"
            r"(\d+(?:\.\d+)?)\s*lpa",
            r"₹?\s*(\d+(?:\.\d+)?)\s*"
            r"(?:lpa|lakhs?)",
        ]

        for pattern in patterns:
            match = re.search(
                pattern,
                source,
                re.IGNORECASE,
            )

            if not match:
                continue

            if len(match.groups()) == 2:
                return (
                    float(match.group(1)),
                    float(match.group(2)),
                )

            value = float(match.group(1))
            return value, value

        return None, None

    def role_relevance(
        self,
        job: Job,
    ) -> float:
        """
        Role relevance is based on the resume's skills and
        roles appearing in the job, rather than requiring an
        exact title match.
        """
        title = job.title.lower()
        description = job.description.lower()

        resume_roles = [
            role.lower()
            for role in self.profile.get(
                "roles",
                [],
            )
        ]

        direct = sum(
            1
            for role in resume_roles
            if role in title
        )

        if direct:
            return 100.0

        ai_terms = [
            "ai",
            "artificial intelligence",
            "machine learning",
            "generative",
            "genai",
            "llm",
            "nlp",
            "computer vision",
            "automation",
            "agent",
            "python",
            "data science",
        ]

        title_hits = sum(
            1
            for term in ai_terms
            if term in title
        )

        description_hits = sum(
            1
            for term in ai_terms
            if term in description
        )

        if title_hits >= 2:
            return 90.0

        if title_hits == 1 and description_hits >= 3:
            return 80.0

        if description_hits >= 5:
            return 70.0

        if description_hits >= 2:
            return 55.0

        return 20.0

    def skill_relevance(
        self,
        detected_skills: list[str],
    ) -> tuple[float, list[str]]:
        if not detected_skills:
            return 0.0, []

        matched = []

        for skill in detected_skills:
            if skill.lower() in self.skills:
                matched.append(skill)

        score = (
            len(matched)
            / len(detected_skills)
        ) * 100

        return min(100.0, score), matched

    def experience_relevance(
        self,
        minimum: float | None,
        maximum: float | None,
    ) -> float:
        candidate = self.profile.get(
            "experience_years"
        )

        if minimum is None:
            return 70.0

        if candidate is None:
            return 50.0

        if candidate < minimum:
            return 0.0

        if maximum is not None:
            if candidate > maximum:
                return 0.0

        return 100.0

    def analyze(
        self,
        job: Job,
    ) -> JobAnalysis:
        text = self.job_text(job)

        detected_skills = self.detect_job_skills(
            text
        )

        minimum_exp, maximum_exp = (
            self.extract_experience(text)
        )

        minimum_salary, maximum_salary = (
            self.extract_salary(
                job,
                text,
            )
        )

        role_score = self.role_relevance(job)

        skill_score, matched_skills = (
            self.skill_relevance(
                detected_skills
            )
        )

        experience_score = (
            self.experience_relevance(
                minimum_exp,
                maximum_exp,
            )
        )

        overall = round(
            role_score * 0.40
            + skill_score * 0.40
            + experience_score * 0.20
        )

        reasons = []

        if role_score >= 80:
            reasons.append(
                "Strong role relevance"
            )

        if matched_skills:
            reasons.append(
                "Matched resume skills: "
                + ", ".join(matched_skills)
            )

        if experience_score >= 80:
            reasons.append(
                "Experience is compatible"
            )

        if minimum_salary is not None:
            reasons.append(
                f"Detected salary from ₹{minimum_salary:g} LPA"
            )

        decision = (
            "APPLY"
            if overall >= self.minimum_score
            else "SKIP"
        )

        return JobAnalysis(
            title=job.title,
            company=job.company,
            location=job.location,
            url=job.url,
            matched_skills=matched_skills,
            detected_experience_min=minimum_exp,
            detected_experience_max=maximum_exp,
            detected_salary_min=minimum_salary,
            detected_salary_max=maximum_salary,
            role_relevance=role_score,
            skill_relevance=skill_score,
            experience_relevance=experience_score,
            overall_score=max(
                0,
                min(100, overall),
            ),
            decision=decision,
            reasons=reasons,
        )

    def analyze_many(
        self,
        jobs: list[Job],
    ) -> list[JobAnalysis]:
        return sorted(
            (
                self.analyze(job)
                for job in jobs
            ),
            key=lambda result: result.overall_score,
            reverse=True,
        )


JobIntelligence = ResumeJobAnalyzer
