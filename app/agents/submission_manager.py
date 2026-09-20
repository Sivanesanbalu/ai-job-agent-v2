from app.agents.application_manager import (
    mark_application_applied,
    mark_ready_for_submission as transition_to_ready_for_submission,
)
from app.models.job import Job
from app.services.application_executor_base import ApplicationExecutor


def mark_ready_for_submission(job_url: str) -> None:
    """Move an application into the ready-for-submission state."""
    transition_to_ready_for_submission(job_url)


def submit_application(
    job: Job,
    executor: ApplicationExecutor,
    package: dict | None = None,
) -> dict:
    """
    Submit an application through the configured executor.

    No confirmation object is required. The workflow/configuration
    determines whether automatic submission is enabled.
    """

    result = executor.submit_application(package)

    if result.status == "submitted":
        mark_application_applied(job.url)

    return {
        "status": result.status,
        "message": result.message,
        "result": result.model_dump(),
    }
