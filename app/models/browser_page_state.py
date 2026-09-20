from enum import Enum


class BrowserPageState(str, Enum):
    UNKNOWN = "unknown"
    JOB_PAGE = "job_page"
    APPLICATION_FORM = "application_form"
    LOGIN_REQUIRED = "login_required"
    HUMAN_VERIFICATION_REQUIRED = "human_verification_required"
    APPLICATION_COMPLETE = "application_complete"
    ERROR_PAGE = "error_page"
