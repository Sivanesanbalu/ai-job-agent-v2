from __future__ import annotations

from typing import Iterable
from urllib.parse import quote, urlparse

import requests
from bs4 import BeautifulSoup

from app.intelligence.job_search_profile import (
    build_search_profile,
    build_search_queries,
)
from app.intelligence.resume_intelligence import (
    load_resume_profile,
)
from app.models.job import Job


SEARCH_ENGINES = {
    "bing": "https://www.bing.com/search?q={query}",
    "google": "https://www.google.com/search?q={query}",
}

JOB_DOMAINS = (
    "linkedin.com/jobs",
    "naukri.com",
    "indeed.com",
    "foundit.in",
    "cutshort.io",
    "wellfound.com",
    "instahyre.com",
    "glassdoor.co.in",
    "glassdoor.com",
)


class OnlineJobDiscovery:
    """
    Real public-web discovery layer.

    It searches public search-engine result pages and extracts
    job listing URLs. It does not bypass CAPTCHA, Cloudflare,
    login, OTP, MFA, or identity/security verification.

    The discovered URL is subsequently handled by the existing
    browser/application layer.
    """

    def __init__(
        self,
        timeout: float = 12.0,
    ):
        self.timeout = timeout

        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/139.0 Safari/537.36"
                ),
                "Accept-Language": (
                    "en-IN,en;q=0.9"
                ),
            }
        )

    def _fetch(
        self,
        url: str,
    ) -> str:
        try:
            response = self.session.get(
                url,
                timeout=self.timeout,
                allow_redirects=True,
            )

            if response.status_code != 200:
                return ""

            return response.text

        except requests.RequestException:
            return ""

    def _extract_links(
        self,
        html: str,
    ) -> list[str]:
        if not html:
            return []

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        links = []

        for anchor in soup.select(
            "a[href]"
        ):
            href = anchor.get(
                "href",
                "",
            ).strip()

            if not href:
                continue

            if href.startswith(
                "/url?q="
            ):
                href = (
                    href.split(
                        "/url?q=",
                        1,
                    )[1]
                    .split("&", 1)[0]
                )

            if not href.startswith(
                ("http://", "https://")
            ):
                continue

            links.append(href)

        return links

    def _is_job_url(
        self,
        url: str,
    ) -> bool:
        value = url.lower()

        return any(
            domain in value
            for domain in JOB_DOMAINS
        )

    def _clean_url(
        self,
        url: str,
    ) -> str:
        parsed = urlparse(url)

        return (
            f"{parsed.scheme}://"
            f"{parsed.netloc}"
            f"{parsed.path}"
        ).rstrip("/")

    def _source(
        self,
        url: str,
    ) -> str:
        host = urlparse(
            url
        ).netloc.lower()

        mapping = {
            "linkedin.com": "linkedin",
            "naukri.com": "naukri",
            "indeed.com": "indeed",
            "foundit.in": "foundit",
            "cutshort.io": "cutshort",
            "wellfound.com": "wellfound",
            "instahyre.com": "instahyre",
            "glassdoor": "glassdoor",
        }

        for domain, source in mapping.items():
            if domain in host:
                return source

        return "web"

    @staticmethod
    def _role_from_query(
        query: str,
        roles: Iterable[str],
    ) -> str:
        lower = query.lower()

        for role in roles:
            if role.lower() in lower:
                return role

        return "AI / Technology Role"

    @staticmethod
    def _location_from_query(
        query: str,
        locations: Iterable[str],
    ) -> str:
        lower = query.lower()

        for location in locations:
            if location.lower() in lower:
                return location

        return "Unknown"

    def _make_job(
        self,
        url: str,
        query: str,
        profile: dict,
    ) -> Job:
        role = self._role_from_query(
            query,
            profile.get("roles", []),
        )

        location = self._location_from_query(
            query,
            profile.get("locations", []),
        )

        return Job(
            title=role,
            company="Unknown",
            location=location,
            url=self._clean_url(url),
            description=(
                "Online job listing discovered through "
                "public web search. Actual job details will "
                "be extracted from the job page."
            ),
            experience_years=None,
            salary=None,
            source=self._source(url),
        )

    def search(self) -> list[Job]:
        resume_profile = load_resume_profile()

        profile = build_search_profile(
            resume_profile
        )

        queries = build_search_queries(
            profile
        )

        discovered: dict[str, Job] = {}

        print("=" * 70)
        print("ONLINE JOB DISCOVERY")
        print("=" * 70)
        print(
            f"Search queries : {len(queries)}"
        )

        for query_index, query in enumerate(
            queries,
            1,
        ):
            print(
                f"[SEARCH {query_index}/{len(queries)}] "
                f"{query}"
            )

            for engine_name, template in (
                SEARCH_ENGINES.items()
            ):
                search_url = template.format(
                    query=quote(query)
                )

                html = self._fetch(
                    search_url
                )

                if not html:
                    continue

                links = self._extract_links(
                    html
                )

                for link in links:
                    if not self._is_job_url(
                        link
                    ):
                        continue

                    clean = self._clean_url(
                        link
                    )

                    if clean in discovered:
                        continue

                    discovered[clean] = (
                        self._make_job(
                            clean,
                            query,
                            profile,
                        )
                    )

                if discovered:
                    break

        jobs = list(
            discovered.values()
        )

        print()
        print(
            f"REAL JOB URLS DISCOVERED: "
            f"{len(jobs)}"
        )

        return jobs


def discover_jobs() -> list[Job]:
    return OnlineJobDiscovery().search()
