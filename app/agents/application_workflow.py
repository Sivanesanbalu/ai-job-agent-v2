from app.agents.application_manager import (
    approve_application,
    mark_application_failed,
    mark_ready_for_submission,
    start_application,
)
from app.agents.application_preparer import prepare_application
from app.agents.submission_manager import submit_application
from app.config import (
    AUTO_SUBMIT,
    REQUIRE_HUMAN_REVIEW,
)
from app.models.application_workflow_state import (
    ApplicationWorkflowState,
)
from app.models.browser_page_state import BrowserPageState
from app.models.job import Job
from app.services.application_executor_base import ApplicationExecutor


def _get_workflow_state(executor):
    get_state = getattr(
        executor,
        "get_application_workflow_state",
        None,
    )

    if callable(get_state):
        return get_state()

    inspect_state = getattr(
        executor,
        "inspect_application_state",
        None,
    )

    if not callable(inspect_state):
        return None

    page_state = inspect_state()

    mapping = {
        BrowserPageState.APPLICATION_FORM:
            ApplicationWorkflowState.READY_TO_FILL,
        BrowserPageState.LOGIN_REQUIRED:
            ApplicationWorkflowState.NEEDS_LOGIN,
        BrowserPageState.HUMAN_VERIFICATION_REQUIRED:
            ApplicationWorkflowState.NEEDS_HUMAN_VERIFICATION,
        BrowserPageState.APPLICATION_COMPLETE:
            ApplicationWorkflowState.APPLICATION_COMPLETE,
        BrowserPageState.JOB_PAGE:
            ApplicationWorkflowState.JOB_PAGE_DETECTED,
        BrowserPageState.UNKNOWN:
            ApplicationWorkflowState.UNKNOWN_PAGE,
    }

    return mapping.get(
        page_state.state,
        ApplicationWorkflowState.UNKNOWN_PAGE,
    )


def _ensure_application_approved(job: Job) -> None:
    """
    Ensure the job is approved before starting the application.

    When REQUIRE_HUMAN_REVIEW=True:
        application_candidate -> needs_human_review
        and the workflow stops for human approval.

    When REQUIRE_HUMAN_REVIEW=False:
        application_candidate -> approved_for_application
        automatically.
    """

    if job.application_status == "approved_for_application":
        return

    if job.application_status != "application_candidate":
        raise ValueError(
            "Job must be application_candidate before approval."
        )

    if REQUIRE_HUMAN_REVIEW:
        from app.agents.application_manager import require_human_review

        require_human_review(
            job.url,
            "Human approval required before application.",
        )

        raise ValueError(
            "Job requires human approval before application."
        )

    # Autonomous mode: approve directly without entering
    # the human-review state.
    approve_application(
        job.url,
        message="Application approved automatically by autonomous workflow",
    )

def run_application_workflow(
    job: Job,
    executor: ApplicationExecutor,
) -> dict:
    """
    Complete the application workflow.

    When REQUIRE_HUMAN_REVIEW=False and AUTO_SUBMIT=True:

        candidate
          -> automatic approval
          -> open
          -> fill
          -> submit
          -> verify
          -> submitted
    """

    _ensure_application_approved(job)

    package = prepare_application(job)

    try:
        open_result = executor.open_application(
            job.url
        )

        if open_result.status != "opened":
            mark_application_failed(
                job.url,
                open_result.message
                or "Failed to open application page.",
            )

            return {
                "status": "failed",
                "stage": "open",
                "result": open_result.model_dump(),
                "application": package,
            }

        start_application(job.url)

        workflow_state = _get_workflow_state(
            executor
        )

        if workflow_state is not None:

            if (
                workflow_state
                == ApplicationWorkflowState
                .NEEDS_HUMAN_VERIFICATION
            ):
                return {
                    "status": workflow_state.value,
                    "stage": "page_state",
                    "workflow_state": workflow_state.value,
                    "open_result": open_result.model_dump(),
                    "application": package,
                    "requires_human_confirmation": False,
                }

            if (
                workflow_state
                == ApplicationWorkflowState
                .NEEDS_LOGIN
            ):
                return {
                    "status": workflow_state.value,
                    "stage": "page_state",
                    "workflow_state": workflow_state.value,
                    "open_result": open_result.model_dump(),
                    "application": package,
                    "requires_human_confirmation": False,
                }

            if (
                workflow_state
                == ApplicationWorkflowState
                .APPLICATION_COMPLETE
            ):
                return {
                    "status": (
                        ApplicationWorkflowState
                        .APPLICATION_COMPLETE
                        .value
                    ),
                    "stage": "complete",
                    "workflow_state": (
                        ApplicationWorkflowState
                        .APPLICATION_COMPLETE
                        .value
                    ),
                    "open_result": open_result.model_dump(),
                    "application": package,
                    "requires_human_confirmation": False,
                }

            if (
                workflow_state
                != ApplicationWorkflowState.READY_TO_FILL
            ):
                return {
                    "status": workflow_state.value,
                    "stage": "page_state",
                    "workflow_state": workflow_state.value,
                    "open_result": open_result.model_dump(),
                    "application": package,
                    "requires_human_confirmation": False,
                }

        fill_result = executor.fill_application(
            package
        )

        if fill_result.status != "filled":
            mark_application_failed(
                job.url,
                fill_result.message
                or "Failed to fill application.",
            )

            return {
                "status": fill_result.status,
                "stage": "fill",
                "result": fill_result.model_dump(),
                "application": package,
            }

        if fill_result.required_fields_needing_input:
            return {
                "status": (
                    ApplicationWorkflowState
                    .NEEDS_HUMAN_INPUT
                    .value
                ),
                "stage": "fill",
                "workflow_state": (
                    ApplicationWorkflowState
                    .NEEDS_HUMAN_INPUT
                    .value
                ),
                "result": fill_result.model_dump(),
                "application": package,
                "required_fields_needing_input": (
                    fill_result.required_fields_needing_input
                ),
                "requires_human_confirmation": False,
            }

        mark_ready_for_submission(job.url)

        if not AUTO_SUBMIT:
            return {
                "status": (
                    ApplicationWorkflowState
                    .READY_FOR_SUBMISSION
                    .value
                ),
                "stage": "ready",
                "workflow_state": (
                    ApplicationWorkflowState
                    .READY_FOR_SUBMISSION
                    .value
                ),
                "open_result": open_result.model_dump(),
                "fill_result": fill_result.model_dump(),
                "application": package,
                "requires_human_confirmation": True,
            }

        submission = submit_application(
            job,
            executor,
            package,
        )

        if submission["status"] == "submitted":
            return {
                "status": "submitted",
                "stage": "submitted",
                "workflow_state": "submitted",
                "open_result": open_result.model_dump(),
                "fill_result": fill_result.model_dump(),
                "submission": submission,
                "application": package,
                "requires_human_confirmation": False,
            }

        if submission["status"] == "blocked":
            return {
                "status": "blocked",
                "stage": "submission",
                "workflow_state": (
                    ApplicationWorkflowState
                    .READY_FOR_SUBMISSION
                    .value
                ),
                "open_result": open_result.model_dump(),
                "fill_result": fill_result.model_dump(),
                "submission": submission,
                "application": package,
                "requires_human_confirmation": False,
            }

        mark_application_failed(
            job.url,
            submission["message"]
            or "Application submission failed.",
        )

        return {
            "status": "failed",
            "stage": "submission",
            "submission": submission,
            "application": package,
            "requires_human_confirmation": False,
        }

    except Exception as error:
        try:
            mark_application_failed(
                job.url,
                str(error),
            )
        except ValueError:
            pass

        raise
