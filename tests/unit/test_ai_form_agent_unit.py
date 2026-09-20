import pytest
from app.services.ai_form_agent import AIFormAgent


def test_ai_form_agent_standard_contact_answers():
    package = {
        "candidate": {
            "name": "Sivanesan B",
            "first_name": "Sivanesan",
            "last_name": "B",
            "email": "apsiva69@gmail.com",
            "phone": "+918438692752",
            "city": "Coimbatore",
            "state": "Tamil Nadu",
            "country": "India",
            "pincode": "623707",
            "linkedin_url": "https://linkedin.com/in/sivanesan-b-871ba7264",
            "github_url": "https://github.com/Sivanesanbalu",
            "portfolio_url": "https://sivanesanbalu.netlify.app",
            "experience_years": 2,
            "notice_period_days": 15,
            "work_authorization": "Authorized to work in India",
        },
        "job": {
            "title": "AI Engineer",
            "company": "Tech Corp",
        },
        "matched_skills": ["Python", "FastAPI", "Next.js", "Playwright"],
    }

    agent = AIFormAgent(package)

    assert agent.answer_field("first_name", "First Name") == "Sivanesan"
    assert agent.answer_field("last_name", "Last Name") == "B"
    assert agent.answer_field("email", "Email Address") == "apsiva69@gmail.com"
    assert agent.answer_field("phone", "Mobile Number") == "+918438692752"
    assert agent.answer_field("city", "Current City") == "Coimbatore"
    assert agent.answer_field("linkedin", "LinkedIn Profile URL") == "https://linkedin.com/in/sivanesan-b-871ba7264"
    assert agent.answer_field("github", "GitHub Profile URL") == "https://github.com/Sivanesanbalu"


def test_ai_form_agent_screening_questions():
    package = {
        "candidate": {
            "name": "Sivanesan B",
            "notice_period_days": 15,
            "experience_years": 2,
        },
        "job": {
            "title": "Full Stack AI Engineer",
            "company": "NextGen AI",
        },
        "matched_skills": ["Python", "PyTorch"],
    }

    agent = AIFormAgent(package)

    # Work authorization
    auth_ans = agent.answer_field("work_auth", "Are you legally authorized to work in India?", options=["Yes", "No"])
    assert auth_ans == "Yes"

    # Sponsorship
    spon_ans = agent.answer_field("sponsorship", "Will you require visa sponsorship?", options=["Yes", "No"])
    assert spon_ans == "No"

    # Notice period
    notice_ans = agent.answer_field("notice", "Notice period", options=["Immediate", "15 days", "30 days", "60 days"])
    assert notice_ans == "15 days"

    # Experience
    exp_ans = agent.answer_field("exp", "How many years of experience do you have?")
    assert exp_ans == 2


def test_ai_form_agent_pitch_generation():
    package = {
        "candidate": {
            "name": "Sivanesan B",
            "headline": "AI Engineer",
        },
        "job": {
            "title": "Senior AI Engineer",
            "company": "OpenAI Partner",
        },
        "matched_skills": ["LLM", "Agents", "FastAPI"],
    }

    agent = AIFormAgent(package)
    pitch = agent.generate_pitch()

    assert "Senior AI Engineer" in pitch
    assert "OpenAI Partner" in pitch
    assert len(pitch) > 50
