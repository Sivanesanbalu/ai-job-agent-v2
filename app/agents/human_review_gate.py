from app.agents.application_manager import require_human_review


def send_to_human_review(package: dict) -> dict:
    job = package["job"]

    message = (
        f"Review application for {job['title']} "
        f"at {job['company']}. "
        "Human approval is required before submission."
    )

    require_human_review(
        job["url"],
        message,
    )

    package["execution_status"] = "needs_human_review"
    package["requires_human_review"] = True

    return package
