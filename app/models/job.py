from pydantic import BaseModel, Field

from app.models.job_source import JobSourceName


class Job(BaseModel):
    title: str
    company: str
    location: str
    url: str
    description: str = ""
    experience_years: float | None = None
    salary: str | None = None
    source: JobSourceName
    match_score: int | None = Field(default=None, ge=0, le=100)
    application_status: str = "discovered"
