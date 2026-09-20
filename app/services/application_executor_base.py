from abc import ABC, abstractmethod

from app.models.application_execution_result import ApplicationExecutionResult


class ApplicationExecutor(ABC):
    """
    Common interface for all application executors.

    The executor is responsible for opening, filling, and submitting
    applications. Whether automatic submission is enabled is controlled
    by the application workflow/configuration layer.
    """

    @abstractmethod
    def open_application(
        self,
        job_url: str,
    ) -> ApplicationExecutionResult:
        """Open the job application page."""
        raise NotImplementedError

    @abstractmethod
    def fill_application(
        self,
        package: dict,
    ) -> ApplicationExecutionResult:
        """Fill the application using the configured candidate data."""
        raise NotImplementedError

    @abstractmethod
    def submit_application(
        self,
        package: dict | None = None,
    ) -> ApplicationExecutionResult:
        """Submit the application when the workflow permits submission."""
        raise NotImplementedError
