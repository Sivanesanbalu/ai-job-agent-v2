from pydantic import BaseModel, HttpUrl


class ApplicationConfirmationRequest(BaseModel):
    job_url: HttpUrl
    confirmed: bool = False
