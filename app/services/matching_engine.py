from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional
import requests
from pydantic import BaseModel
from app.core.config import settings
from app.db.models import JobListing, Preferences, Profile, Resume

logger = logging.getLogger(__name__)


class MatchResult(BaseModel):
    match_score: int
    relevance: str
    matched_skills: List[str]
    missing_skills: List[str]
    experience_match: bool
    location_match: bool
    salary_match: bool
    reason: str
    apply_decision: bool


def parse_salary_lpa(salary_str: Optional[str]) -> Optional[float]:
    if not salary_str:
        return None
    text = salary_str.lower()
    if not any(token in text for token in ["lpa", "lakh", "lac", "₹", "rs.", "inr"]):
        return None
    matches = re.findall(r"(\d+(?:\.\d+)?)", text)
    if not matches:
        return None
    try:
        return float(matches[0])
    except ValueError:
        return None


def match_job_for_user(
    job: JobListing,
    preferences: Preferences,
    profile: Optional[Profile] = None,
    resume: Optional[Resume] = None,
) -> MatchResult:
    # 1. Gather candidate skills and data
    candidate_skills: List[str] = []
    if profile and profile.skills:
        candidate_skills.extend(profile.skills)
    if resume and resume.parsed_data and "skills" in resume.parsed_data:
        for s in resume.parsed_data["skills"]:
            if s not in candidate_skills:
                candidate_skills.append(s)

    candidate_exp = (
        profile.experience_years if profile else (
            resume.parsed_data.get("experience_years", 0.0) if resume and resume.parsed_data else 0.0
        )
    )

    # 2. Check hard constraints
    # Experience check
    experience_match = True
    if job.experience_years is not None and preferences.max_experience_years is not None:
        if job.experience_years > preferences.max_experience_years:
            experience_match = False

    # Salary check
    salary_match = True
    job_lpa = parse_salary_lpa(job.salary)
    if job_lpa is not None and preferences.min_salary_lpa is not None:
        if job_lpa < preferences.min_salary_lpa:
            salary_match = False

    # Location check
    location_match = True
    job_loc = (job.location or "").lower()
    preferred_locs = [l.lower() for l in (preferences.preferred_locations or [])]
    if preferred_locs and job_loc:
        matches_loc = any(loc in job_loc for loc in preferred_locs)
        is_remote = "remote" in job_loc or preferences.remote_friendly
        location_match = matches_loc or is_remote

    # 3. Analyze skills & technical fit
    job_text = f"{job.title} {job.description}".lower()
    matched_skills = []
    missing_skills = []

    for skill in candidate_skills:
        if skill.lower() in job_text:
            matched_skills.append(skill)

    # Check preferred roles
    role_matched = False
    preferred_roles = preferences.preferred_roles or []
    for r in preferred_roles:
        if r.lower() in job.title.lower() or job.title.lower() in r.lower():
            role_matched = True
            break

    # 4. Determine score
    # Skill overlap component (up to 50 pts)
    total_skills = len(candidate_skills) or 1
    skill_pct = min(1.0, len(matched_skills) / max(3, min(8, total_skills)))
    skill_score = int(skill_pct * 50)

    # Role relevance component (up to 30 pts)
    role_score = 30 if role_matched else 15

    # Location & Experience bonus (up to 20 pts)
    bonus_score = (10 if location_match else 0) + (10 if experience_match else 0)

    base_score = skill_score + role_score + bonus_score

    # Hard rejection penalties
    if not salary_match:
        base_score = min(base_score, 40)
    if not experience_match:
        base_score = min(base_score, 45)

    final_score = max(0, min(100, base_score))

    relevance = "High" if final_score >= 80 else ("Medium" if final_score >= 60 else "Low")
    apply_decision = (
        final_score >= preferences.min_match_score
        and salary_match
        and experience_match
        and location_match
    )

    reason_parts = []
    if role_matched:
        reason_parts.append(f"Role title aligns with target preference.")
    if matched_skills:
        reason_parts.append(f"Matches {len(matched_skills)} key candidate skills: {', '.join(matched_skills[:4])}.")
    if not salary_match:
        reason_parts.append(f"Salary ₹{job.salary} is below preferred minimum ₹{preferences.min_salary_lpa} LPA.")
    if not experience_match:
        reason_parts.append(f"Experience required ({job.experience_years} yrs) exceeds preferred max ({preferences.max_experience_years} yrs)..")
    if not location_match:
        reason_parts.append(f"Location '{job.location}' does not match preferred locations.")

    reason = " ".join(reason_parts) or f"Match score {final_score}% based on candidate profile and job requirements."

    return MatchResult(
        match_score=final_score,
        relevance=relevance,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        experience_match=experience_match,
        location_match=location_match,
        salary_match=salary_match,
        reason=reason,
        apply_decision=apply_decision,
    )
