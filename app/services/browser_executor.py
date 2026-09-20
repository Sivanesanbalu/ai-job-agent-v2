from app.models.application_execution_result import (
    ApplicationExecutionResult,
)
from app.services.application_executor_base import ApplicationExecutor
from app.services.application_state_mapper import (
    map_browser_state,
)
from app.services.browser_site_adapter_factory import (
    BrowserSiteAdapterFactory,
)


class BrowserExecutor(ApplicationExecutor):
    """
    Browser-based application executor.

    The workflow/configuration layer controls whether submission
    is allowed. This executor performs the actual browser operation.
    """

    def __init__(
        self,
        user_id: int | None = None,
        headless: bool = True,
        resume_path: str | None = None,
        photo_path: str | None = None,
        application_answers: dict | None = None,
    ):
        self.adapter_factory = BrowserSiteAdapterFactory(
            user_id=user_id,
            headless=headless,
            resume_path=resume_path,
            photo_path=photo_path,
            application_answers=application_answers,
        )
        self.adapter = None

    def open_application(
        self,
        job_url: str,
    ) -> ApplicationExecutionResult:
        if not job_url or not job_url.strip():
            return ApplicationExecutionResult(
                status="blocked",
                message="Job URL cannot be empty.",
            )

        try:
            self.adapter = self.adapter_factory.get_adapter(
                job_url
            )

            result = self.adapter.open_application(
                job_url
            )

            if result.url is None:
                result.url = job_url

            return result

        except Exception as error:
            return ApplicationExecutionResult(
                status="failed",
                url=job_url,
                message=(
                    "Failed to open application page: "
                    f"{error}"
                ),
            )

    def inspect_application_page(self) -> dict:
        if self.adapter is None:
            raise RuntimeError(
                "Application page is not open."
            )

        page_info = self.adapter.inspect_application()

        page_info["adapter"] = (
            self.adapter.__class__.__name__
        )

        page_info["site"] = (
            self.adapter.site.value
        )

        return page_info

    def inspect_application_state(self):
        if self.adapter is None:
            raise RuntimeError(
                "Application page is not open."
            )

        engine = getattr(
            self.adapter,
            "engine",
            None,
        )

        if engine is None:
            raise RuntimeError(
                "Selected adapter does not expose "
                "a browser engine."
            )

        return engine.inspect_page_state()

    def get_application_workflow_state(self):
        page_state = self.inspect_application_state()

        return map_browser_state(
            page_state.state
        )

    def build_fill_plan(
        self,
        package: dict,
    ) -> list[dict]:
        if self.adapter is None:
            raise RuntimeError(
                "Application page is not open."
            )

        engine = getattr(
            self.adapter,
            "engine",
            None,
        )

        if engine is None:
            raise RuntimeError(
                "Selected adapter does not expose "
                "a browser engine."
            )

        return engine.build_fill_plan(
            package,
            supported_fields=(
                self.adapter.capabilities.supported_fields
            ),
        )

    def fill_application(
        self,
        package: dict,
    ) -> ApplicationExecutionResult:
        if self.adapter is None:
            return ApplicationExecutionResult(
                status="blocked",
                message="Application page is not open.",
            )

        result = self.adapter.fill_application(
            package
        )

        if result.job_title is None:
            result.job_title = package["job"]["title"]

        if result.company is None:
            result.company = package["job"]["company"]

        return result

    def click_apply_button(self) -> dict:
        """Click apply button if adapter exposes click_apply_button."""
        if self.adapter is None:
            return {"clicked": False, "reason": "Application page is not open."}
        return self.adapter.click_apply_button()

    def fill_and_advance_application(
        self,
        package: dict,
        max_steps: int = 6,
    ) -> ApplicationExecutionResult:
        """Autonomously fill forms, upload resume, and advance multi-step wizards until submitted."""
        if self.adapter is None:
            return ApplicationExecutionResult(
                status="blocked",
                message="Application page is not open.",
            )

        result = self.adapter.fill_and_advance_application(
            package,
            max_steps=max_steps,
        )

        if package is not None:
            if result.job_title is None and "job" in package:
                result.job_title = package["job"].get("title")
            if result.company is None and "job" in package:
                result.company = package["job"].get("company")

        return result

    def submit_application(
        self,
        package: dict | None = None,
    ) -> ApplicationExecutionResult:
        """
        Submit the currently open application.

        The application workflow decides whether automatic
        submission is enabled. No separate confirmation object
        is required here.
        """

        if self.adapter is None:
            return ApplicationExecutionResult(
                status="blocked",
                message="Application page is not open.",
            )

        try:
            result = self.adapter.submit_application(
                package
            )

            if package is not None:
                if result.job_title is None:
                    result.job_title = package["job"]["title"]

                if result.company is None:
                    result.company = package["job"]["company"]

            return result

        except Exception as error:
            return ApplicationExecutionResult(
                status="failed",
                message=(
                    "Browser submission failed: "
                    f"{error}"
                ),
            )

    def close(self) -> None:
        if self.adapter is not None:
            try:
                self.adapter.close()
            except Exception:
                pass

        try:
            self.adapter_factory.close()
        except Exception:
            pass

        self.adapter = None
