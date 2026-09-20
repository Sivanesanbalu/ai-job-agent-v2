from __future__ import annotations

from typing import Any, Optional
from app.services.ai_form_agent import AIFormAgent


def get_candidate_field_value(
    field_name: str,
    package: dict,
    label: str = "",
    field_type: str = "text",
    options: Optional[list[str]] = None,
) -> Optional[Any]:
    candidate = package.get("candidate", {})

    if field_name == "name":
        return candidate.get("name")

    if field_name == "first_name":
        fn = candidate.get("first_name")
        if fn:
            return fn
        full_name = candidate.get("name", "").strip()
        return full_name.split()[0] if full_name else None

    if field_name == "last_name":
        ln = candidate.get("last_name")
        if ln:
            return ln
        full_name = candidate.get("name", "").strip()
        parts = full_name.split()
        return parts[-1] if len(parts) > 1 else ""

    if field_name == "email":
        return candidate.get("email")

    if field_name == "phone":
        return candidate.get("phone") or "+918438692752"

    if field_name == "linkedin":
        return candidate.get("linkedin_url") or "https://linkedin.com/in/sivanesan-b-871ba7264"

    if field_name == "github":
        return candidate.get("github_url") or "https://github.com/Sivanesanbalu"

    if field_name == "portfolio":
        return candidate.get("portfolio_url") or "https://sivanesanbalu.netlify.app"

    if field_name == "city":
        return candidate.get("city") or "Coimbatore"

    if field_name == "state":
        return candidate.get("state") or "Tamil Nadu"

    if field_name == "country":
        return candidate.get("country") or "India"

    if field_name == "address":
        return candidate.get("address") or "Coimbatore, Tamil Nadu, India"

    if field_name == "pincode":
        return candidate.get("pincode") or "623707"

    if field_name == "headline":
        return candidate.get("headline") or "Software Professional / AI Engineer"

    if field_name == "current_company":
        return candidate.get("current_company") or "Independent AI Engineer"

    if field_name == "experience":
        return str(candidate.get("experience_years", 1.0))

    if field_name == "notice_period":
        return f"{candidate.get('notice_period_days', 15)} days"

    if field_name == "current_salary":
        curr = candidate.get("current_salary_lpa", 0.0)
        return f"₹{curr} LPA" if curr > 0 else "Negotiable"

    if field_name == "expected_salary":
        exp = candidate.get("expected_salary_lpa", 8.0)
        return f"₹{exp} LPA"

    if field_name == "education":
        return candidate.get("education") or "B.Tech in Artificial Intelligence and Data Science"

    if field_name == "university":
        return "Anna University"

    if field_name == "work_authorization":
        return "Authorized to work in India"

    if field_name == "sponsorship":
        return "No"

    if field_name == "relocation":
        return "Yes"

    if field_name == "cover_letter":
        pitch = package.get("application_pitch")
        if pitch:
            return pitch
        agent = AIFormAgent(package)
        return agent.generate_open_ended_answer("cover letter")

    # Delegate to AIFormAgent for custom and semantic fields
    agent = AIFormAgent(package)
    return agent.answer_field(field_name, label=label, field_type=field_type, options=options)
