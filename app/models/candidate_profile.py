from pydantic import BaseModel


class CandidateProfile(BaseModel):
    name: str
    email: str | None = None
    headline: str
    experience_years: float
    preferred_roles: list[str]
    preferred_locations: list[str]
    skills: list[str]
    education: str
    notice_period_days: int
