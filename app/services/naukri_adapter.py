from app.models.application_execution_result import (
    ApplicationExecutionResult,
)
from app.models.browser_site import BrowserSite
from app.models.browser_site_capabilities import (
    BrowserSiteCapabilities,
)
from app.services.browser_engine import BrowserEngine
from app.services.browser_site_adapter import BrowserSiteAdapter


class NaukriAdapter(BrowserSiteAdapter):
    """Naukri application adapter."""

    NAUKRI_HOSTS = {
        "naukri.com",
        "www.naukri.com",
    }

    def __init__(self, engine: BrowserEngine):
        self.engine = engine

    @property
    def site(self) -> BrowserSite:
        return BrowserSite.NAUKRI

    @property
    def capabilities(self) -> BrowserSiteCapabilities:
        return BrowserSiteCapabilities(
            site=BrowserSite.NAUKRI,
        )

    def can_handle(self, url: str) -> bool:
        if not url:
            return False

        normalized_url = url.strip().lower()

        return any(
            host in normalized_url
            for host in self.NAUKRI_HOSTS
        )

    def open_application(
        self,
        url: str,
    ) -> ApplicationExecutionResult:
        try:
            self.engine.goto(url)

            return ApplicationExecutionResult(
                status="opened",
                url=url,
                message="Naukri application page opened.",
            )

        except Exception as error:
            return ApplicationExecutionResult(
                status="failed",
                url=url,
                message=(
                    f"Failed to open Naukri page: {error}"
                ),
            )

    def inspect_application(self) -> dict:
        return self.engine.inspect_application_page()

    def fill_application(
        self,
        package: dict,
    ) -> ApplicationExecutionResult:
        result = self.engine.fill_application(
            package,
            supported_fields=self.capabilities.supported_fields,
        )

        result.job_title = package["job"]["title"]
        result.company = package["job"]["company"]

        return result

    def submit_application(
        self,
        package: dict | None = None,
    ) -> ApplicationExecutionResult:
        result = self.engine.submit_application(
            package
        )

        if package:
            result.job_title = package["job"]["title"]
            result.company = package["job"]["company"]

        return result

    def close(self) -> None:
        self.engine.close()
