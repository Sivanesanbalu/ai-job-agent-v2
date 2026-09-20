from app.config import REQUIRE_HUMAN_REVIEW
from app.agents.application_manager import start_application
from app.agents.application_queue import build_application_queue
from app.services.application_limits import can_apply_today
from app.services.job_queries import get_job_by_url


def execute_application_queue() -> list[dict]:
    if not can_apply_today():
        print("Daily application limit reached.")
        return []

    queue = build_application_queue()

    executed = []

    for package in queue:
        job_url = package["job"]["url"]

        job = get_job_by_url(job_url)

        if job is None:
            print(
                f"Skipping application because job was not found: "
                f"{job_url}"
            )
            continue

        if job.application_status != "approved_for_application":
            print(
                f"Skipping {job.title} at {job.company}: "
                f"invalid status '{job.application_status}'. "
                "Expected 'approved_for_application'."
            )
            continue

        try:
            start_application(job_url)
        except ValueError as error:
            print(
                f"Skipping {job.title} at {job.company}: "
                f"{error}"
            )
            continue

        package["execution_status"] = "started"
        package["requires_human_review"] = REQUIRE_HUMAN_REVIEW

        executed.append(package)

        print(
            f"Application started: "
            f"{package['job']['title']} | "
            f"{package['job']['company']}"
        )

    return executed
