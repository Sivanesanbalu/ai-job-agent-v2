from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional
import requests
from app.core.config import settings

logger = logging.getLogger(__name__)


class AIFormAgent:
    """
    AI-powered agent that analyzes a candidate's profile and resume
    to answer standard, custom, and open-ended job application questions.
    """

    def __init__(self, package: Dict[str, Any]):
        self.package = package
        self.candidate = package.get("candidate", {})
        self.job = package.get("job", {})
        self.skills = package.get("matched_skills", []) or self.candidate.get("skills", [])
        self.resume_text = package.get("resume_text", "")

    def answer_field(
        self,
        field_name: str,
        label: str = "",
        field_type: str = "text",
        options: Optional[List[str]] = None,
    ) -> Optional[Any]:
        """
        Determines the best answer for any form field or question.
        """
        prompt_text = f"{field_name} {label}".strip().lower()

        # 1. Contact details
        if any(k in prompt_text for k in ["first name", "firstname", "given name"]):
            return self.candidate.get("first_name") or self.candidate.get("name", "").split()[0]

        if any(k in prompt_text for k in ["last name", "lastname", "surname", "family name"]):
            parts = self.candidate.get("name", "").split()
            return self.candidate.get("last_name") or (parts[-1] if len(parts) > 1 else "")

        if any(k in prompt_text for k in ["full name", "fullname", "your name", "candidate name"]):
            return self.candidate.get("name")

        if any(k in prompt_text for k in ["email", "e-mail"]):
            return self.candidate.get("email")

        if any(k in prompt_text for k in ["phone", "mobile", "cell", "telephone", "contact number"]):
            return self.candidate.get("phone") or "+918438692752"

        # 2. URLs and Socials
        if "linkedin" in prompt_text:
            return self.candidate.get("linkedin_url") or "https://linkedin.com/in/sivanesan-b-871ba7264"

        if "github" in prompt_text:
            return self.candidate.get("github_url") or "https://github.com/Sivanesanbalu"

        if any(k in prompt_text for k in ["portfolio", "website", "personal site", "blog"]):
            return self.candidate.get("portfolio_url") or "https://sivanesanbalu.netlify.app"

        # 3. Location
        if any(k in prompt_text for k in ["city", "current city", "current location"]):
            return self.candidate.get("city") or "Coimbatore"

        if any(k in prompt_text for k in ["state", "province"]):
            return self.candidate.get("state") or "Tamil Nadu"

        if any(k in prompt_text for k in ["country"]):
            if options:
                return self._pick_matching_option(["India", "IN", "ind"], options) or "India"
            return self.candidate.get("country") or "India"

        if any(k in prompt_text for k in ["postal", "zip", "pincode", "pin code"]):
            return self.candidate.get("pincode") or "623707"

        if any(k in prompt_text for k in ["address", "street"]):
            return self.candidate.get("address") or "Coimbatore, Tamil Nadu, India"

        # 4. Work Authorization & Sponsorship
        if any(k in prompt_text for k in ["authorized to work", "legally authorized", "right to work"]):
            if options:
                return self._pick_matching_option(["yes", "authorized", "citizen"], options) or "Yes"
            return "Yes"

        if any(k in prompt_text for k in ["sponsorship", "require visa", "require sponsorship"]):
            if options:
                return self._pick_matching_option(["no", "do not require", "not required"], options) or "No"
            return "No"

        # 5. Experience & Notice Period
        if any(k in prompt_text for k in ["notice period", "availability", "how soon", "when can you start"]):
            days = self.candidate.get("notice_period_days", 15)
            if options:
                days_str = str(days)
                for opt in options:
                    if days_str in opt:
                        return opt
                return self._pick_matching_option(["immediate", "15 days", "1 month", "< 30 days"], options) or f"{days} days"
            return f"{days} days"

        if any(k in prompt_text for k in ["experience", "years of experience", "total experience"]):
            exp = self.candidate.get("experience_years", 1)
            if options:
                exp_str = str(exp)
                for opt in options:
                    if exp_str in opt:
                        return opt
                return self._pick_matching_option([str(exp), "1-3", "1 to 3", "0-2", "1 year"], options) or exp
            return exp


        # 6. Compensation
        if any(k in prompt_text for k in ["expected salary", "expected ctc", "desired compensation", "salary expectation"]):
            lpa = self.candidate.get("expected_salary_lpa", 8.0)
            return f"₹{lpa} LPA"

        if any(k in prompt_text for k in ["current salary", "current ctc"]):
            lpa = self.candidate.get("current_salary_lpa", 0.0)
            return f"₹{lpa} LPA" if lpa > 0 else "Negotiable"

        # 7. Education
        if any(k in prompt_text for k in ["education", "degree", "highest degree"]):
            deg = self.candidate.get("education") or "B.Tech in Artificial Intelligence and Data Science"
            if options:
                return self._pick_matching_option(["bachelor", "b.tech", "graduate", "undergraduate"], options) or deg
            return deg

        if any(k in prompt_text for k in ["university", "college", "school", "institution"]):
            return "Anna University"

        # 8. Willingness to relocate / hybrid / onsite
        if any(k in prompt_text for k in ["relocate", "willing to relocate", "relocation"]):
            if options:
                return self._pick_matching_option(["yes", "willing"], options) or "Yes"
            return "Yes"

        if any(k in prompt_text for k in ["hybrid", "onsite", "in-office", "work from office"]):
            if options:
                return self._pick_matching_option(["yes", "comfortable", "agreed"], options) or "Yes"
            return "Yes"

        # 9. Diversity / Voluntary disclosures
        if "gender" in prompt_text:
            if options:
                return self._pick_matching_option(["male", "prefer not to say"], options) or "Male"
            return "Male"

        if any(k in prompt_text for k in ["disability"]):
            if options:
                return self._pick_matching_option(["no", "do not have", "prefer not to say"], options) or "No"
            return "No"

        if any(k in prompt_text for k in ["veteran"]):
            if options:
                return self._pick_matching_option(["no", "not a veteran", "prefer not to say"], options) or "No"
            return "No"

        # 10. Open-ended custom screening questions
        if field_type in ["textarea", "text"] or len(label) > 20:
            return self.generate_open_ended_answer(label or field_name)

        if options:
            return options[0]

        return None

    def generate_open_ended_answer(self, question: str) -> str:
        """
        Synthesizes a tailored, professional response to open-ended employer questions
        using the candidate's active profile, technical skills, and resume.
        """
        q_lower = question.lower()
        company = self.job.get("company", "your organization")
        job_title = self.job.get("title", "this role")
        cand_name = self.candidate.get("first_name", "I")
        skills_str = ", ".join((self.skills or ["Python", "Generative AI", "LLMs", "FastAPI"])[:4])

        # Why work here / interest in company
        if any(k in q_lower for k in ["why", "interest", "what motivates", "fit for"]):
            return (
                f"I am passionate about building production-grade AI solutions and high-throughput systems. "
                f"My background in {skills_str} directly aligns with {company}'s focus on innovation. "
                f"I am eager to leverage my engineering capabilities to deliver measurable impact for {company}."
            )

        # Technical experience / background
        if any(k in q_lower for k in ["tell us about", "experience with", "describe your", "project"]):
            return (
                f"I have extensive hands-on experience building AI applications, RAG pipelines, and backend services "
                f"using {skills_str}. In my recent work, I architected autonomous agent workflows and integrated "
                f"REST APIs with PostgreSQL and vector databases, optimizing latency and ensuring reliability."
            )

        # Cover letter / pitch
        if any(k in q_lower for k in ["cover letter", "pitch", "summary", "additional information", "notes"]):
            return (
                f"Dear Hiring Team at {company},\n\n"
                f"I am writing to express my strong interest in the {job_title} position. With hands-on expertise "
                f"in {skills_str}, I specialize in developing scalable, intelligent software systems. "
                f"I welcome the opportunity to bring my technical skills and problem-solving mindset to your team.\n\n"
                f"Sincerely,\n{self.candidate.get('name', 'Candidate')}"
            )

        # Default smart response
        return (
            f"As an engineer specializing in {skills_str}, I bring strong technical rigor, rapid learning, "
            f"and a focus on delivering robust production software to {company}."
        )

    def generate_pitch(self) -> str:
        """
        Generates a concise, impactful pitch/cover letter for the specific job listing.
        """
        company = self.job.get("company", "your organization")
        job_title = self.job.get("title", "this role")
        skills_str = ", ".join((self.skills or ["Python", "FastAPI", "AI/LLM", "Next.js"])[:4])
        cand_name = self.candidate.get("name", "Candidate")

        return (
            f"Dear Hiring Team at {company},\n\n"
            f"I am writing to express my strong interest in the {job_title} position. With hands-on expertise "
            f"in {skills_str}, I specialize in developing scalable, intelligent software systems and AI agents. "
            f"I welcome the opportunity to bring my technical skills and problem-solving mindset to your team.\n\n"
            f"Sincerely,\n{cand_name}"
        )

    def _pick_matching_option(self, target_keywords: List[str], options: List[str]) -> Optional[str]:
        """Matches options against keyword priorities."""
        for opt in options:
            opt_lower = opt.lower()
            for kw in target_keywords:
                if kw in opt_lower or opt_lower in kw:
                    return opt
        return None
