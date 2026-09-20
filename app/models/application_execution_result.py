from pydantic import BaseModel, Field


class ApplicationExecutionResult(BaseModel):
    status: str
    message: str = ""
    url: str | None = None
    job_title: str | None = None
    company: str | None = None
    filled_fields: list[str] = Field(default_factory=list)
    skipped_fields: list[str] = Field(default_factory=list)
    required_fields_needing_input: list[str] = Field(default_factory=list)
