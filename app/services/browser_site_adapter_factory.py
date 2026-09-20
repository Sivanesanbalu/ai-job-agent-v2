from urllib.parse import urlparse

from app.models.browser_site import BrowserSite
from app.services.browser_engine import BrowserEngine
from app.services.browser_site_adapter import BrowserSiteAdapter
from app.services.generic_site_adapter import GenericSiteAdapter
from app.services.linkedin_adapter import LinkedInAdapter
from app.services.naukri_adapter import NaukriAdapter
from app.services.indeed_adapter import IndeedAdapter


class BrowserSiteAdapterFactory:
    """Select the appropriate browser adapter for a job URL.

    All adapters share one BrowserEngine so Chromium is started
    only once per BrowserExecutor session.
    """

    def __init__(
        self,
        user_id: int | None = None,
        headless: bool = True,
        resume_path: str | None = None,
        photo_path: str | None = None,
        application_answers: dict | None = None,
    ):
        self.engine = BrowserEngine(
            user_id=user_id,
            headless=headless,
            resume_path=resume_path,
            photo_path=photo_path,
            application_answers=application_answers,
        )

        self.adapters: list[BrowserSiteAdapter] = [
            LinkedInAdapter(self.engine),
            NaukriAdapter(self.engine),
            IndeedAdapter(self.engine),
            GenericSiteAdapter(self.engine),
        ]

    def get_adapter(
        self,
        url: str,
    ) -> BrowserSiteAdapter:
        """Return the first adapter that can handle the URL."""

        if not url or not url.strip():
            raise ValueError(
                "Job URL cannot be empty."
            )

        parsed = urlparse(url.strip())

        if parsed.scheme not in {
            "http",
            "https",
            "file",
        }:
            raise ValueError(
                "Job URL must use http, https, or file."
            )

        for adapter in self.adapters:
            if adapter.can_handle(url):
                return adapter

        raise ValueError(
            f"No browser adapter available for URL: {url}"
        )

    def close(self) -> None:
        """Close the shared browser engine once."""

        self.engine.close()
