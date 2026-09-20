from app.models.application_workflow_state import (
    ApplicationWorkflowState,
)
from app.models.browser_page_state import BrowserPageState


def map_browser_state(
    browser_state: BrowserPageState,
) -> ApplicationWorkflowState:
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
        browser_state,
        ApplicationWorkflowState.UNKNOWN_PAGE,
    )
