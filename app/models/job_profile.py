from pydantic import BaseModel, Field


class JobProfile(BaseModel):
    roles: list[str]
    locations: list[str]
    max_experience_years: float = Field(ge=0)
    min_match_score: int = Field(ge=0, le=100)
    max_applications_per_day: int = Field(gt=0)
    auto_submit: bool = False
    require_human_review: bool = True
