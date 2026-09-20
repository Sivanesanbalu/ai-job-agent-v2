from pydantic import BaseModel, HttpUrl


class ApplicationReadyRequest(BaseModel):
    job_url: HttpUrl
