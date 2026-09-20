from pydantic import BaseModel


class SubmissionConfirmation(BaseModel):
    confirmed: bool = False
    confirmed_by: str = "human"
