from __future__ import annotations

import re
from urllib.parse import urlparse

from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    sync_playwright,
)

from app.models.job import Job


class JobPageExtractor:
    """
    Opens discovered job pages and extracts visible job information.

    It does not bypass security challenges.
    """

    def __init__(
        self,
        headless: bool = True,
        timeout_ms: int = 20000,
    ):
        self.headless = headless
        self.timeout_ms = timeout_ms
        self.playwright = None
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None

    def start(self):
        self.playwright = sync_playwright().start()

        self.browser = (
            self.playwright.chromium.launch(
                headless=self.headless
            )
        )

        self.context = (
            self.browser.new_context(
                viewport={
                    "width": 1440,
                    "height": 1000,
                },
                locale="en-IN",
            )
        )

    def close(self):
        if self.context:
            self.context.close()
            self.context = None

        if self.browser:
            self.browser.close()
            self.browser = None

        if self.playwright:
            self.playwright.stop()
            self.playwright = None

    @staticmethod
    def _first(
        page: Page,
        selectors: list[str],
    ) -> str:
        for selector in selectors:
            try:
                locator = page.locator(
                    selector
                ).first

                if locator.count() == 0:
                    continue

                text = (
                    locator.inner_text()
                    .strip()
                )

                if text:
                    return " ".join(
                        text.split()
                    )
            except Exception:
                continue

        return ""

    @staticmethod
    def _body(
        page: Page,
    ) -> str:
        try:
            return page.locator(
                "body"
            ).inner_text()
        except Exception:
            return ""

    @staticmethod
    def _salary(
        text: str,
    ) -> str | None:
        patterns = [
            r"₹\s*\d+(?:\.\d+)?\s*[-–]\s*"
            r"₹?\s*\d+(?:\.\d+)?\s*(?:LPA|Lakhs?)",
            r"\d+(?:\.\d+)?\s*[-–]\s*"
            r"\d+(?:\.\d+)?\s*LPA",
            r"\d+(?:\.\d+)?\s*LPA",
        ]

        for pattern in patterns:
            match = re.search(
                pattern,
                text,
                re.IGNORECASE,
            )

            if match:
                return match.group(0)

        return None

    @staticmethod
    def _experience(
        text: str,
    ) -> float | None:
        patterns = [
            r"(\d+(?:\.\d+)?)\s*[-–to]+\s*"
            r"(\d+(?:\.\d+)?)\s*years?",
            r"(\d+(?:\.\d+)?)\s*\+?\s*years?",
        ]

        for pattern in patterns:
            match = re.search(
                pattern,
                text,
                re.IGNORECASE,
            )

            if match:
                try:
                    return float(
                        match.group(1)
                    )
                except ValueError:
                    pass

        lower = text.lower()

        if any(
            item in lower
            for item in [
                "fresher",
                "freshers",
                "entry level",
                "0-1 years",
                "0 - 1 years",
            ]
        ):
            return 0.0

        return None

    @staticmethod
    def _company(
        page: Page,
        url: str,
    ) -> str:
        selectors = [
            "[data-company-name]",
            ".company-name",
            ".companyName",
            "[class*='company']",
            "a[href*='/company/']",
        ]

        value = JobPageExtractor._first(
            page,
            selectors,
        )

        if value:
            return value

        host = urlparse(
            url
        ).netloc

        return host

    def extract(
        self,
        url: str,
    ) -> Job | None:
        if self.context is None:
            self.start()

        assert self.context is not None

        page = self.context.new_page()

        try:
            try:
                page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=self.timeout_ms,
                )
            except Exception:
                return None

            body = self._body(page)

            if not body:
                return None

            lower = body.lower()

            security_terms = [
                "captcha",
                "verify you are human",
                "checking your browser",
                "unusual traffic",
                "cloudflare",
            ]

            if any(
                term in lower
                for term in security_terms
            ):
                print(
                    f"[SECURITY] {url}"
                )
                return None

            title = self._first(
                page,
                [
                    "h1",
                    "[data-job-title]",
                    ".job-title",
                    ".jobsearch-JobInfoHeader-title",
                ],
            )

            if not title:
                title = (
                    page.title()
                    .strip()
                )

            company = self._company(
                page,
                url,
            )

            location = self._first(
                page,
                [
                    "[data-location]",
                    ".location",
                    ".job-location",
                    "[class*='location']",
                ],
            )

            salary = self._salary(
                body
            )

            experience = self._experience(
                body
            )

            source = (
                "linkedin"
                if "linkedin.com" in url
                else "naukri"
                if "naukri.com" in url
                else "indeed"
                if "indeed.com" in url
                else "web"
            )

            return Job(
                title=title[:300],
                company=company[:300],
                location=(
                    location[:300]
                    if location
                    else "Unknown"
                ),
                url=url,
                description=body[:15000],
                experience_years=experience,
                salary=salary,
                source=source,
            )

        finally:
            page.close()


def extract_job_pages(
    urls: list[str],
    headless: bool = True,
) -> list[Job]:
    extractor = JobPageExtractor(
        headless=headless
    )

    jobs = []

    try:
        extractor.start()

        for index, url in enumerate(
            urls,
            1,
        ):
            print(
                f"[PAGE {index}/{len(urls)}] "
                f"{url}"
            )

            job = extractor.extract(
                url
            )

            if job:
                jobs.append(job)

    finally:
        extractor.close()

    return jobs
