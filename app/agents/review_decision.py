from app.agents.application_manager import (
    approve_application,
    reject_application,
)


VALID_DECISIONS = {
    "approve",
    "reject",
}


def process_review_decision(
    job_url: str,
    decision: str,
) -> str:
    decision = decision.lower().strip()

    if decision not in VALID_DECISIONS:
        raise ValueError(
            "Decision must be 'approve' or 'reject'"
        )

    if decision == "approve":
        approve_application(job_url)
        return "approved_for_application"

    reject_application(job_url)
    return "rejected_by_user"
