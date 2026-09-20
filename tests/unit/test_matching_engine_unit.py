import pytest
from app.db.models import JobListing, Preferences, Profile, Resume
from app.services.matching_engine import match_job_for_user, parse_salary_lpa

def test_parse_salary_lpa():
    assert parse_salary_lpa("₹25 LPA") == 25.0
    assert parse_salary_lpa("30-40 Lakhs Per Annum") == 30.0
    assert parse_salary_lpa("18.5 lpa") == 18.5
    assert parse_salary_lpa("Not Disclosed") is None
    assert parse_salary_lpa("$120,000 / year") is None

def test_matching_high_relevance():
    job = JobListing(
        id=101,
        title="Senior Python Backend Developer",
        company="TechCorp Global",
        location="Remote",
        description="Looking for an expert Python developer proficient in FastAPI, Redis, Docker, and PostgreSQL.",
        experience_years=4,
        salary="28 LPA",
    )
    prefs = Preferences(
        preferred_roles=["Python Developer", "Backend Engineer"],
        preferred_locations=["Remote"],
        remote_friendly=True,
        min_salary_lpa=20.0,
        max_experience_years=6,
        min_match_score=70,
    )
    profile = Profile(
        skills=["Python", "FastAPI", "Redis", "Docker", "PostgreSQL", "Git"],
        experience_years=5.0,
    )

    result = match_job_for_user(job=job, preferences=prefs, profile=profile)
    assert result.match_score >= 75
    assert result.apply_decision is True
    assert result.experience_match is True
    assert result.salary_match is True
    assert result.location_match is True
    assert "Python" in result.matched_skills
    assert "FastAPI" in result.matched_skills

def test_matching_salary_too_low():
    job = JobListing(
        id=102,
        title="Junior Python Dev",
        company="StartupX",
        location="Remote",
        description="Python, FastAPI developer wanted.",
        experience_years=1,
        salary="8 LPA",
    )
    prefs = Preferences(
        preferred_roles=["Python Dev"],
        preferred_locations=["Remote"],
        remote_friendly=True,
        min_salary_lpa=25.0,  # Candidate asks 25 LPA
        max_experience_years=5,
        min_match_score=70,
    )
    profile = Profile(skills=["Python", "FastAPI"], experience_years=4.0)

    result = match_job_for_user(job=job, preferences=prefs, profile=profile)
    assert result.salary_match is False
    assert result.apply_decision is False
    assert result.match_score <= 40  # Hard penalty applied

def test_matching_experience_exceeded():
    job = JobListing(
        id=103,
        title="Principal Software Architect",
        company="Enterprise Ltd",
        location="Remote",
        description="Requires 15+ years leading architecture in Python and distributed systems.",
        experience_years=15,
        salary="60 LPA",
    )
    prefs = Preferences(
        preferred_roles=["Software Engineer"],
        preferred_locations=["Remote"],
        remote_friendly=True,
        min_salary_lpa=20.0,
        max_experience_years=8,  # Candidate only comfortable up to 8 yrs
        min_match_score=70,
    )
    profile = Profile(skills=["Python"], experience_years=6.0)

    result = match_job_for_user(job=job, preferences=prefs, profile=profile)
    assert result.experience_match is False
    assert result.apply_decision is False
