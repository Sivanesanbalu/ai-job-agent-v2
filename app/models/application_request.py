from pydantic import BaseModel, HttpUrl


class ApplicationRequest(BaseModel):
    job_url: HttpUrl
