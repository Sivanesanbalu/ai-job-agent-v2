from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import quote, urlparse

from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    sync_playwright,
)

from app.config import LOCATIONS
from app.intelligence.resume_intelligence import (
    load_resume_profile,
)
from app.models.job import Job


@dataclass
class PortalSearchResult:
    title: str
    company: str
    location: str
    url: str
    source: str
    snippet: str = ""


class PortalSecurityChallenge(Exception):
    pass


class PortalJobDiscovery:
    """
    Discovers jobs directly from public job-portal search pages.

    The agent does not bypass CAPTCHA, Cloudflare, OTP, MFA,
    login walls, or identity verification.

    Search strategy is generated from the resume rather than
    requiring the user to provide job URLs.
    """

    PORTALS = {
        "linkedin": {
            "search_url": (
                "https://www.linkedin.com/jobs/search/"
                "?keywords={keyword}"
                "&location={location}"
            ),
        },
        "naukri": {
            "search_url": (
                "https://www.naukri.com/"
                "{keyword}-jobs-in-{location}"
            ),
        },
        "indeed": {
            "search_url": (
                "https://in.indeed.com/jobs"
                "?q={keyword}"
                "&l={location}"
            ),
        },
    }

    def __init__(
        self,
        headless: bool = False,
        timeout_ms: int = 25000,
    ):
        self.headless = headless
        self.timeout_ms = timeout_ms

        self.playwright = None
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None

    # ------------------------------------------------------------------
    # Browser lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        self.playwright = sync_playwright().start()

        try:
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
            )
        except Exception as e:
            if "Executable doesn't exist" in str(e) or "playwright install" in str(e):
                import subprocess, sys
                subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
                self.browser = self.playwright.chromium.launch(
                    headless=self.headless,
                )
            else:
                raise e

        self.context = (
            self.browser.new_context(
                viewport={
                    "width": 1440,
                    "height": 1000,
                },
                locale="en-IN",
                timezone_id="Asia/Kolkata",
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
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

    # ------------------------------------------------------------------
    # Security detection
    # ------------------------------------------------------------------

    @staticmethod
    def detect_security_challenge(
        page: Page,
    ) -> bool:
        try:
            body = page.locator(
                "body"
            ).inner_text(
                timeout=5000
            )
        except Exception:
            return False

        text = body.lower()

        security_terms = [
            "captcha",
            "verify you are human",
            "verification required",
            "security verification",
            "unusual traffic",
            "checking your browser",
            "cloudflare",
            "access denied",
            "robot check",
        ]

        return any(
            term in text
            for term in security_terms
        )

    @staticmethod
    def detect_login_wall(
        page: Page,
        source: str,
    ) -> bool:
        try:
            body = page.locator(
                "body"
            ).inner_text(
                timeout=5000
            )
        except Exception:
            return False

        text = body.lower()

        if source == "linkedin":
            login_terms = [
                "sign in to view",
                "join now",
                "sign in",
            ]

            # Don't mark every occurrence of "sign in" as
            # a login wall because LinkedIn can show the
            # sign-in button on public search pages.
            if (
                "sign in to view" in text
                or "join linkedin" in text
            ):
                return True

        if source == "naukri":
            if (
                "login to apply" in text
                and "job description" not in text
            ):
                return True

        if source == "indeed":
            if (
                "sign in" in text
                and "job search" not in text
            ):
                return True

        return False

    # ------------------------------------------------------------------
    # Query generation
    # ------------------------------------------------------------------

    def build_role_queries(
        self,
        profile: dict,
    ) -> list[str]:
        resume_roles = [
            str(role).strip()
            for role in profile.get(
                "roles",
                [],
            )
            if str(role).strip()
        ]

        resume_skills = [
            str(skill).strip()
            for skill in profile.get(
                "skills",
                [],
            )
            if str(skill).strip()
        ]

        # Important:
        # These are discovery terms, NOT an application whitelist.
        broad_roles = [
            "AI Engineer",
            "AI Developer",
            "AI Software Engineer",
            "AI Application Engineer",
            "AI Solutions Engineer",
            "Generative AI Engineer",
            "GenAI Engineer",
            "LLM Engineer",
            "LLM Developer",
            "AI Agent Engineer",
            "AI Automation Engineer",
            "Machine Learning Engineer",
            "ML Engineer",
            "Machine Learning Developer",
            "NLP Engineer",
            "Computer Vision Engineer",
            "Python AI Developer",
            "AI Platform Engineer",
        ]

        skills_for_search = [
            "RAG",
            "LLM",
            "Generative AI",
            "AI Agents",
            "LangChain",
            "Python AI",
            "AI Automation",
        ]

        terms: list[str] = []

        for value in (
            resume_roles
            + broad_roles
            + skills_for_search
        ):
            if value not in terms:
                terms.append(value)

        # Only keep a manageable number per run.
        return terms[:30]

    def build_search_plan(
        self,
        profile: dict,
        max_queries: int = 30,
    ) -> list[tuple[str, str, str]]:
        roles = self.build_role_queries(
            profile
        )

        locations = list(
            dict.fromkeys(
                LOCATIONS
                + profile.get(
                    "locations",
                    [],
                )
            )
        )

        plan = []

        for portal in self.PORTALS:
            for role in roles:
                for location in locations:
                    plan.append(
                        (
                            portal,
                            role,
                            location,
                        )
                    )

        return plan[:max_queries]

    # ------------------------------------------------------------------
    # URL helpers
    # ------------------------------------------------------------------

    @staticmethod
    def normalize_location(
        location: str,
    ) -> str:
        return (
            location
            .strip()
            .replace(",", " ")
        )

    @staticmethod
    def normalize_keyword(
        keyword: str,
    ) -> str:
        return " ".join(
            keyword.split()
        ).strip()

    def build_url(
        self,
        portal: str,
        keyword: str,
        location: str,
    ) -> str:
        template = self.PORTALS[
            portal
        ]["search_url"]

        keyword_clean = (
            self.normalize_keyword(
                keyword
            )
        )

        location_clean = (
            self.normalize_location(
                location
            )
        )

        if portal == "naukri":
            keyword_path = re.sub(
                r"[^a-zA-Z0-9]+",
                "-",
                keyword_clean.lower(),
            ).strip("-")

            location_path = re.sub(
                r"[^a-zA-Z0-9]+",
                "-",
                location_clean.lower(),
            ).strip("-")

            return template.format(
                keyword=keyword_path,
                location=location_path,
            )

        return template.format(
            keyword=quote(
                keyword_clean
            ),
            location=quote(
                location_clean
            ),
        )

    # ------------------------------------------------------------------
    # Generic link extraction
    # ------------------------------------------------------------------

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
    def portal_from_url(
        url: str,
    ) -> str:
        host = urlparse(
            url
        ).netloc.lower()

        if "linkedin.com" in host:
            return "linkedin"

        if "naukri.com" in host:
            return "naukri"

        if "indeed.com" in host:
            return "indeed"

        return "web"

    # ------------------------------------------------------------------
    # LinkedIn
    # ------------------------------------------------------------------

    def search_linkedin(
        self,
        page: Page,
        keyword: str,
        location: str,
    ) -> list[PortalSearchResult]:
        url = self.build_url(
            "linkedin",
            keyword,
            location,
        )

        print(
            f"[LINKEDIN] "
            f"{keyword} | {location}"
        )

        try:
            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=self.timeout_ms,
            )

            page.wait_for_timeout(1500)

        except Exception as exc:
            print(
                f"  navigation failed: {exc}"
            )
            return []

        if self.detect_security_challenge(
            page
        ):
            raise PortalSecurityChallenge(
                "LinkedIn security verification"
            )

        selectors = [
            "a.base-card__full-link",
            "a.base-card__full-link[href]",
            "a[href*='/jobs/view/']",
        ]

        results = []

        seen = set()

        for selector in selectors:
            links = page.locator(
                selector
            )

            count = min(
                links.count(),
                100,
            )

            for index in range(count):
                try:
                    link = links.nth(index)

                    href = link.get_attribute(
                        "href"
                    )

                    if not href:
                        continue

                    clean = self.clean_url(
                        href
                    )

                    if clean in seen:
                        continue

                    seen.add(clean)

                    title = (
                        link.inner_text()
                        .strip()
                    )

                    if not title:
                        title = keyword

                    card = (
                        link.locator(
                            "xpath=ancestor::div[contains(@class, 'base-card')] | ancestor::li"
                        )
                        .first
                    )

                    card_text = ""
                    try:
                        card_text = card.inner_text(timeout=1000)
                    except Exception:
                        pass

                    company = ""
                    try:
                        comp_elem = card.locator(".base-search-card__subtitle, .job-search-card__subtitle, a[data-tracking-control-name*='company']").first
                        if comp_elem.count() > 0:
                            company = comp_elem.inner_text().strip()
                    except Exception:
                        pass

                    if not company:
                        m = re.search(r'-at-([a-z0-9-]+)-\d+$', clean)
                        if m:
                            company = m.group(1).replace('-', ' ').title()
                        else:
                            company = self._extract_company(card_text)

                    job_location = ""
                    try:
                        loc_elem = card.locator(".job-search-card__location, .base-search-card__metadata span").first
                        if loc_elem.count() > 0:
                            job_location = loc_elem.inner_text().strip()
                    except Exception:
                        pass

                    if not job_location:
                        job_location = self._extract_location(card_text, location)

                    results.append(
                        PortalSearchResult(
                            title=title,
                            company=company or "Hiring Company",
                            location=job_location or location,
                            url=clean,
                            source="linkedin",
                            snippet=card_text[:1000],
                        )
                    )

                except Exception:
                    continue

        return results

    # ------------------------------------------------------------------
    # Naukri
    # ------------------------------------------------------------------

    def search_naukri(
        self,
        page: Page,
        keyword: str,
        location: str,
    ) -> list[PortalSearchResult]:
        url = self.build_url(
            "naukri",
            keyword,
            location,
        )

        print(
            f"[NAUKRI] "
            f"{keyword} | {location}"
        )

        try:
            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=self.timeout_ms,
            )

            page.wait_for_timeout(1800)

        except Exception as exc:
            print(
                f"  navigation failed: {exc}"
            )
            return []

        if self.detect_security_challenge(
            page
        ):
            raise PortalSecurityChallenge(
                "Naukri security verification"
            )

        selectors = [
            "a.title",
            "a[href*='/job-listings-']",
            "a[href*='/job-listings/']",
            "a[href*='naukri.com/job-listings']",
        ]

        results = []

        seen = set()

        for selector in selectors:
            links = page.locator(
                selector
            )

            count = min(
                links.count(),
                100,
            )

            for index in range(count):
                try:
                    link = links.nth(index)

                    href = link.get_attribute(
                        "href"
                    )

                    if not href:
                        continue

                    if not href.startswith(
                        "http"
                    ):
                        continue

                    clean = self.clean_url(
                        href
                    )

                    if clean in seen:
                        continue

                    seen.add(clean)

                    title = (
                        link.inner_text()
                        .strip()
                    )

                    if not title:
                        title = keyword

                    try:
                        card = (
                            link.locator(
                                "xpath=ancestor::*"
                            ).first
                        )

                        card_text = (
                            card.inner_text(
                                timeout=1000
                            )
                        )
                    except Exception:
                        card_text = ""

                    company = (
                        self._extract_company(
                            card_text
                        )
                    )

                    job_location = (
                        self._extract_location(
                            card_text,
                            location,
                        )
                    )

                    results.append(
                        PortalSearchResult(
                            title=title,
                            company=company,
                            location=job_location,
                            url=clean,
                            source="naukri",
                            snippet=card_text[:1000],
                        )
                    )

                except Exception:
                    continue

        return results

    # ------------------------------------------------------------------
    # Indeed
    # ------------------------------------------------------------------

    def search_indeed(
        self,
        page: Page,
        keyword: str,
        location: str,
    ) -> list[PortalSearchResult]:
        url = self.build_url(
            "indeed",
            keyword,
            location,
        )

        print(
            f"[INDEED] "
            f"{keyword} | {location}"
        )

        try:
            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=self.timeout_ms,
            )

            page.wait_for_timeout(1800)

        except Exception as exc:
            print(
                f"  navigation failed: {exc}"
            )
            return []

        if self.detect_security_challenge(
            page
        ):
            raise PortalSecurityChallenge(
                "Indeed security verification"
            )

        selectors = [
            "a.jcs-JobTitle",
            "a[data-jk]",
            "a[href*='/viewjob']",
        ]

        results = []

        seen = set()

        for selector in selectors:
            links = page.locator(
                selector
            )

            count = min(
                links.count(),
                100,
            )

            for index in range(count):
                try:
                    link = links.nth(index)

                    href = link.get_attribute(
                        "href"
                    )

                    if not href:
                        continue

                    if href.startswith(
                        "/"
                    ):
                        href = (
                            "https://in.indeed.com"
                            + href
                        )

                    if not href.startswith(
                        "http"
                    ):
                        continue

                    clean = self.clean_url(
                        href
                    )

                    if clean in seen:
                        continue

                    seen.add(clean)

                    title = (
                        link.inner_text()
                        .strip()
                    )

                    if not title:
                        title = keyword

                    try:
                        card = (
                            link.locator(
                                "xpath=ancestor::div[contains(@class, 'cardOutline')] | ancestor::div[contains(@class, 'job_seen_beacon')] | ancestor::li"
                            ).first
                        )

                        card_text = ""
                        try:
                            card_text = card.inner_text(timeout=1000)
                        except Exception:
                            pass

                        company = ""
                        try:
                            comp_elem = card.locator("span[data-testid='company-name'], .companyName, span.company").first
                            if comp_elem.count() > 0:
                                company = comp_elem.inner_text().strip()
                        except Exception:
                            pass

                        if not company:
                            company = self._extract_company(card_text)

                        job_location = ""
                        try:
                            loc_elem = card.locator("div[data-testid='text-location'], .companyLocation").first
                            if loc_elem.count() > 0:
                                job_location = loc_elem.inner_text().strip()
                        except Exception:
                            pass

                        if not job_location:
                            job_location = self._extract_location(card_text, location)

                        results.append(
                            PortalSearchResult(
                                title=title,
                                company=company or "Hiring Company",
                                location=job_location or location,
                                url=clean,
                                source="indeed",
                                snippet=card_text[:1000],
                            )
                        )
                    except Exception:
                        continue

                except Exception:
                    continue

        return results

    # ------------------------------------------------------------------
    # Text helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_company(
        text: str,
    ) -> str:
        lines = [
            " ".join(line.split())
            for line in text.splitlines()
            if line.strip()
        ]

        if not lines:
            return "Unknown"

        # Avoid returning obvious metadata as company.
        ignored = {
            "easy apply",
            "apply",
            "be an early applicant",
            "actively hiring",
        }

        for line in lines:
            if (
                line.lower() not in ignored
                and len(line) <= 150
            ):
                return line

        return "Unknown"

    @staticmethod
    def _extract_location(
        text: str,
        fallback: str,
    ) -> str:
        lines = [
            " ".join(line.split())
            for line in text.splitlines()
            if line.strip()
        ]

        location_terms = [
            "coimbatore",
            "chennai",
            "bengaluru",
            "bangalore",
            "hyderabad",
            "pune",
            "gurugram",
            "gurgaon",
            "gujarat",
            "remote",
        ]

        for line in lines:
            lower = line.lower()

            if any(
                term in lower
                for term in location_terms
            ):
                return line[:200]

        return fallback

    # ------------------------------------------------------------------
    # Unified discovery
    # ------------------------------------------------------------------

    def search_portal(
        self,
        portal: str,
        keyword: str,
        location: str,
    ) -> list[PortalSearchResult]:
        if self.context is None:
            self.start()

        assert self.context is not None

        page = self.context.new_page()

        try:
            if portal == "linkedin":
                return self.search_linkedin(
                    page,
                    keyword,
                    location,
                )

            if portal == "naukri":
                return self.search_naukri(
                    page,
                    keyword,
                    location,
                )

            if portal == "indeed":
                return self.search_indeed(
                    page,
                    keyword,
                    location,
                )

            return []

        finally:
            page.close()

    def discover(
        self,
        max_queries: int = 15,
    ) -> list[PortalSearchResult]:
        profile = load_resume_profile()

        plan = self.build_search_plan(
            profile,
            max_queries=max_queries,
        )

        print("=" * 70)
        print("REAL JOB PORTAL DISCOVERY")
        print("=" * 70)
        print(
            f"Search operations: {len(plan)}"
        )

        discovered: dict[
            str,
            PortalSearchResult,
        ] = {}

        security_blocked = set()

        for index, (
            portal,
            keyword,
            location,
        ) in enumerate(
            plan,
            1,
        ):
            print(
                f"\n[{index}/{len(plan)}] "
                f"{portal} | "
                f"{keyword} | "
                f"{location}"
            )

            if portal in security_blocked:
                print(
                    f"  {portal} skipped after "
                    f"security challenge"
                )
                continue

            try:
                results = self.search_portal(
                    portal,
                    keyword,
                    location,
                )

                for result in results:
                    if result.url not in discovered:
                        discovered[
                            result.url
                        ] = result

                print(
                    f"  found: {len(results)}"
                )

            except PortalSecurityChallenge as exc:
                print(
                    f"  SECURITY STOP: {exc}"
                )

                security_blocked.add(
                    portal
                )

            except Exception as exc:
                print(
                    f"  source error: {exc}"
                )

        results = list(
            discovered.values()
        )

        print("\n" + "=" * 70)
        print(
            f"UNIQUE JOBS DISCOVERED: "
            f"{len(results)}"
        )
        print(
            f"Security-blocked portals: "
            f"{sorted(security_blocked)}"
        )
        print("=" * 70)

        return results


def discover_real_jobs(
    max_queries: int = 15,
    headless: bool = False,
) -> list[PortalSearchResult]:
    engine = PortalJobDiscovery(
        headless=headless
    )

    try:
        engine.start()

        return engine.discover(
            max_queries=max_queries
        )

    finally:
        engine.close()


def portal_results_to_jobs(
    results: list[PortalSearchResult],
) -> list[Job]:
    jobs = []

    for result in results:
        jobs.append(
            Job(
                title=result.title,
                company=result.company,
                location=result.location,
                url=result.url,
                description=result.snippet,
                experience_years=None,
                salary=None,
                source=result.source,
            )
        )

    return jobs


def discover_real_jobs_for_criteria(
    roles: list[str],
    locations: list[str],
    limit: int = 30,
    headless: bool = True,
) -> list[PortalSearchResult]:
    """Search live portals (LinkedIn, Indeed) for candidate roles & locations."""
    engine = PortalJobDiscovery(headless=headless)
    discovered: dict[str, PortalSearchResult] = {}

    target_roles = [r for r in roles if r.strip()][:3] or ["Software Engineer"]
    target_locations = [l for l in locations if l.strip()][:2] or ["India"]

    try:
        engine.start()
        for role in target_roles:
            if len(discovered) >= limit:
                break
            for loc in target_locations:
                if len(discovered) >= limit:
                    break
                # Try LinkedIn
                try:
                    ln_res = engine.search_portal("linkedin", role, loc)
                    for r in ln_res:
                        if r.url not in discovered:
                            discovered[r.url] = r
                except Exception as e:
                    print(f"LinkedIn discovery notice for {role}: {e}")

                if len(discovered) >= limit:
                    break

                # Try Indeed
                try:
                    ind_res = engine.search_portal("indeed", role, loc)
                    for r in ind_res:
                        if r.url not in discovered:
                            discovered[r.url] = r
                except Exception as e:
                    print(f"Indeed discovery notice for {role}: {e}")

        return list(discovered.values())[:limit]
    finally:
        engine.close()

