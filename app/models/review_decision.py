from pydantic import BaseModel, HttpUrl


class ReviewDecisionRequest(BaseModel):
    job_url: HttpUrl
