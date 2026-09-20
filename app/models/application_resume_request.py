from pydantic import BaseModel, Field


class ApplicationResumeRequest(BaseModel):
    job_url: str
    human_input: dict[str, str] = Field(
        default_factory=dict
    )
