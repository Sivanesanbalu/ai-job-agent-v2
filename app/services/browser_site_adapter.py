from abc import ABC, abstractmethod

from app.models.application_execution_result import (
    ApplicationExecutionResult,
)
from app.models.browser_site import BrowserSite
from app.models.browser_site_capabilities import (
    BrowserSiteCapabilities,
)


class BrowserSiteAdapter(ABC):
    """Common interface for LinkedIn, Naukri, Indeed and other sites."""

    @property
    @abstractmethod
    def site(self) -> BrowserSite:
        """Return the site represented by this adapter."""
        raise NotImplementedError

    @property
    @abstractmethod
    def capabilities(self) -> BrowserSiteCapabilities:
        """Return capabilities supported by this adapter."""
        raise NotImplementedError

    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """Return True when this adapter supports the URL."""
        raise NotImplementedError

    @abstractmethod
    def open_application(
        self,
        url: str,
    ) -> ApplicationExecutionResult:
        """Open the application page."""
        raise NotImplementedError

    @abstractmethod
    def inspect_application(self) -> dict:
        """Inspect the current application form/page."""
        raise NotImplementedError

    @abstractmethod
    def fill_application(
        self,
        package: dict,
    ) -> ApplicationExecutionResult:
        """Fill supported application fields."""
        raise NotImplementedError

    @abstractmethod
    def submit_application(
        self,
        package: dict | None = None,
    ) -> ApplicationExecutionResult:
        """Submit the application when permitted by the workflow."""
        raise NotImplementedError

    def close(self) -> None:
        """Release browser resources."""
        return None
