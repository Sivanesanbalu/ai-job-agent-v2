from pydantic import BaseModel, HttpUrl


class ApplicationHistoryRequest(BaseModel):
    job_url: HttpUrl
