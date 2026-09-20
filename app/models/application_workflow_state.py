from enum import Enum


class ApplicationWorkflowState(str, Enum):
    READY_TO_FILL = "ready_to_fill"
    NEEDS_LOGIN = "needs_login"
    NEEDS_HUMAN_VERIFICATION = "needs_human_verification"
    APPLICATION_COMPLETE = "application_complete"
    JOB_PAGE_DETECTED = "job_page_detected"
    UNKNOWN_PAGE = "unknown_page"
    NEEDS_HUMAN_INPUT = "needs_human_input"
    READY_FOR_SUBMISSION = "ready_for_submission"
    FAILED = "failed"
