from __future__ import annotations

from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    sync_playwright,
)


class JobBrowser:
    """
    Dedicated browser for reading public job-detail pages.

    This browser does NOT bypass:
      - CAPTCHA
      - Cloudflare
      - OTP
      - MFA
      - Google login
      - identity verification

    If the page requires authentication/security verification,
    JobPageReader detects it and the caller moves to the next job.
    """

    def __init__(
        self,
        headless: bool = False,
    ):
        self.headless = headless
        self.playwright: Playwright | None = None
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None

    def start(self) -> None:
        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
        )

        self.context = self.browser.new_context(
            viewport={
                "width": 1440,
                "height": 900,
            },
            ignore_https_errors=False,
        )

        self.page = self.context.new_page()

        self.page.set_default_timeout(
            8000
        )

    def open(
        self,
        url: str,
    ) -> Page:
        if self.page is None:
            raise RuntimeError(
                "JobBrowser has not been started."
            )

        self.page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=30000,
        )

        # Give dynamic job content a short chance to render.
        try:
            self.page.wait_for_load_state(
                "networkidle",
                timeout=8000,
            )
        except Exception:
            pass

        return self.page

    def close(self) -> None:
        try:
            if self.page is not None:
                self.page.close()
        except Exception:
            pass

        try:
            if self.context is not None:
                self.context.close()
        except Exception:
            pass

        try:
            if self.browser is not None:
                self.browser.close()
        except Exception:
            pass

        try:
            if self.playwright is not None:
                self.playwright.stop()
        except Exception:
            pass

        self.page = None
        self.context = None
        self.browser = None
        self.playwright = None
