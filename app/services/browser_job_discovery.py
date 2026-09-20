from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import quote, urlparse

from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    sync_playwright,
)

from app.config import LOCATIONS, ROLES
from app.models.job import Job


@dataclass
class RawJobResult:
    url: str
    title: str
    snippet: str
    source: str


class BrowserJobDiscovery:
    """
    Real browser-based job discovery.

    The browser performs the online search itself.

    No CAPTCHA, Cloudflare, OTP, MFA, login challenge,
    or other security mechanism is bypassed.
    """

    SEARCH_URLS = [
        (
            "bing",
            "https://www.bing.com/search?q={query}",
        ),
        (
            "google",
            "https://www.google.com/search?q={query}",
        ),
    ]

    JOB_DOMAINS = {
        "linkedin.com": "linkedin",
        "naukri.com": "naukri",
        "indeed.com": "indeed",
        "foundit.in": "foundit",
        "cutshort.io": "cutshort",
        "wellfound.com": "wellfound",
        "instahyre.com": "instahyre",
        "glassdoor.co.in": "glassdoor",
        "glassdoor.com": "glassdoor",
    }

    def __init__(
        self,
        headless: bool = True,
        timeout_ms: int = 20000,
    ):
        self.headless = headless
        self.timeout_ms = timeout_ms

        self.playwright: Playwright | None = None
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None

    def start(self) -> None:
        self.playwright = sync_playwright().start()

        self.browser = (
            self.playwright.chromium.launch(
                headless=self.headless,
            )
        )

        self.context = (
            self.browser.new_context(
                viewport={
                    "width": 1440,
                    "height": 1000,
                },
                locale="en-IN",
                user_agent=(
                    "Mozilla/5.0 (Macintosh; "
                    "Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/139.0 Safari/537.36"
                ),
            )
        )

    def close(self) -> None:
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
    def source_for_url(
        url: str,
    ) -> str:
        host = urlparse(
            url
        ).netloc.lower()

        for domain, source in (
            BrowserJobDiscovery.JOB_DOMAINS.items()
        ):
            if domain in host:
                return source

        return "web"

    @staticmethod
    def clean_url(
        url: str,
    ) -> str:
        parsed = urlparse(url)

        return (
            f"{parsed.scheme}://"
            f"{parsed.netloc}"
            f"{parsed.path}"
        ).rstrip("/")

    @staticmethod
    def is_job_url(
        url: str,
    ) -> bool:
        value = url.lower()

        return any(
            domain in value
            for domain in BrowserJobDiscovery.JOB_DOMAINS
        )

    def search_page(
        self,
        page: Page,
        query: str,
        engine_name: str,
        template: str,
    ) -> list[RawJobResult]:
        search_url = template.format(
            query=quote(query)
        )

        print(
            f"    [{engine_name}] {query}"
        )

        try:
            page.goto(
                search_url,
                wait_until="domcontentloaded",
                timeout=self.timeout_ms,
            )
        except Exception:
            return []

        text = (
            page.locator("body")
            .inner_text(timeout=5000)
            if page.locator("body").count()
            else ""
        )

        security_terms = [
            "captcha",
            "unusual traffic",
            "verify you are human",
            "checking your browser",
            "cloudflare",
        ]

        lower = text.lower()

        if any(
            term in lower
            for term in security_terms
        ):
            print(
                "    SECURITY CHALLENGE DETECTED"
            )
            return []

        results = []

        anchors = page.locator(
            "a[href]"
        )

        count = min(
            anchors.count(),
            100,
        )

        for index in range(count):
            anchor = anchors.nth(index)

            try:
                href = anchor.get_attribute(
                    "href"
                )

                if not href:
                    continue

                if not self.is_job_url(
                    href
                ):
                    continue

                clean = self.clean_url(
                    href
                )

                title = (
                    anchor.inner_text()
                    .strip()
                )

                if not title:
                    continue

                results.append(
                    RawJobResult(
                        url=clean,
                        title=title,
                        snippet="",
                        source=self.source_for_url(
                            clean
                        ),
                    )
                )

            except Exception:
                continue

        return results

    def build_queries(
        self,
    ) -> list[str]:
        queries = []

        # Role-based searches.
        for role in ROLES:
            for location in LOCATIONS:
                queries.append(
                    f'"{role}" '
                    f'"{location}" '
                    f'jobs'
                )

        # Broad AI searches.
        broad_roles = [
            "AI developer",
            "AI software engineer",
            "AI application engineer",
            "AI solutions engineer",
            "AI platform engineer",
            "AI developer",
            "GenAI developer",
            "LLM developer",
            "AI automation developer",
            "agentic AI engineer",
            "Python AI developer",
            "machine learning developer",
            "NLP engineer",
            "computer vision engineer",
        ]

        for role in broad_roles:
            for location in LOCATIONS:
                queries.append(
                    f'"{role}" '
                    f'"{location}" '
                    f'jobs'
                )

        # Skill-driven discovery.
        skill_searches = [
            "RAG LLM Python jobs",
            "Generative AI Python jobs",
            "AI agents Python jobs",
            "LangChain LLM jobs",
            "LangGraph AI jobs",
            "Prompt Engineering AI jobs",
            "LLM RAG jobs",
            "AI automation Python jobs",
        ]

        for search in skill_searches:
            for location in LOCATIONS:
                queries.append(
                    f'"{search}" '
                    f'"{location}"'
                )

        # Deduplicate.
        return list(
            dict.fromkeys(queries)
        )

    def discover(
        self,
        max_queries: int = 60,
    ) -> list[RawJobResult]:
        if self.context is None:
            self.start()

        assert self.context is not None

        page = self.context.new_page()

        discovered: dict[str, RawJobResult] = {}

        queries = self.build_queries()[
            :max_queries
        ]

        print("=" * 70)
        print("REAL ONLINE JOB DISCOVERY")
        print("=" * 70)
        print(
            f"Queries planned: {len(queries)}"
        )

        try:
            for query_index, query in enumerate(
                queries,
                1,
            ):
                print(
                    f"\nSEARCH "
                    f"{query_index}/{len(queries)}"
                )

                for engine_name, template in (
                    self.SEARCH_URLS
                ):
                    results = self.search_page(
                        page,
                        query,
                        engine_name,
                        template,
                    )

                    for result in results:
                        if result.url not in discovered:
                            discovered[
                                result.url
                            ] = result

                    if results:
                        break

        finally:
            page.close()

        results = list(
            discovered.values()
        )

        print("\n" + "=" * 70)
        print(
            f"REAL JOB URLS FOUND: "
            f"{len(results)}"
        )
        print("=" * 70)

        return results


def discover_online_job_urls(
    max_queries: int = 60,
    headless: bool = True,
) -> list[RawJobResult]:
    engine = BrowserJobDiscovery(
        headless=headless
    )

    try:
        return engine.discover(
            max_queries=max_queries
        )
    finally:
        engine.close()
