from app.agents.application_preparer import prepare_application
from app.agents.application_validator import validate_application_package
from app.services.application_limits import get_remaining_applications_today
from app.services.job_queries import get_approved_jobs


def build_application_queue() -> list[dict]:
    queue = []

    approved_jobs = get_approved_jobs()
    remaining_slots = get_remaining_applications_today()

    for job in approved_jobs:
        if len(queue) >= remaining_slots:
            break

        package = prepare_application(job)

        valid, errors = validate_application_package(package)

        if not valid:
            print(
                f"Skipping {job.title} at {job.company}: "
                f"{', '.join(errors)}"
            )
            continue

        queue.append(package)

    return queue
