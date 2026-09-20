from app.models.application_execution_result import ApplicationExecutionResult
from app.models.submission_confirmation import SubmissionConfirmation
from app.services.application_executor_base import ApplicationExecutor


class DemoExecutor(ApplicationExecutor):

    def open_application(
        self,
        job_url: str,
    ) -> ApplicationExecutionResult:
        return ApplicationExecutionResult(
            status="opened",
            url=job_url,
            message="Demo application page opened",
        )

    def fill_application(
        self,
        package: dict,
    ) -> ApplicationExecutionResult:
        return ApplicationExecutionResult(
            status="filled",
            job_title=package["job"]["title"],
            company=package["job"]["company"],
            message="Demo application fields prepared",
        )

    def submit_application(
        self,
        confirmation: SubmissionConfirmation | None = None,
    ) -> ApplicationExecutionResult:
        if confirmation is None or not confirmation.confirmed:
            return ApplicationExecutionResult(
                status="blocked",
                message=(
                    "Submission requires explicit human confirmation."
                ),
            )

        return ApplicationExecutionResult(
            status="authorized",
            message=(
                "Human confirmation received. "
                "Demo submission is authorized."
            ),
        )
