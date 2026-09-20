from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from playwright.sync_api import Page


# ============================================================
# AUTH / SECURITY SIGNALS
# ============================================================

AUTH_PATTERNS = [
    "sign in with google",
    "continue with google",
    "google account",
    "choose an account",
    "sign in",
    "log in",
    "login",
    "join linkedin",
    "authentication required",
    "login required",
    "sign in required",
    "create an account",
]

SECURITY_PATTERNS = [
    "captcha",
    "recaptcha",
    "verify you are human",
    "verify you're human",
    "cloudflare",
    "checking your browser",
    "security verification",
    "security check",
    "unusual traffic",
    "access denied",
    "challenge required",
    "robot check",
    "are you a robot",
    "human verification",
    "one-time password",
    "otp",
    "multi-factor authentication",
    "mfa",
    "identity verification",
]

INVALID_PAGE_MARKERS = [
    "skip to main content",
    "get notified about new",
    "join linkedin",
]


@dataclass
class JobPageReadResult:
    success: bool
    blocked: bool = False
    verification_required: bool = False
    reason: str = ""

    title: str = ""
    company: str = ""
    location: str = ""
    description: str = ""
    salary: Optional[str] = None
    experience: Optional[str] = None
    seniority_signal: Optional[str] = None


class JobPageReader:
    """
    Reads a real job detail page.

    IMPORTANT:
    - Never bypass authentication/security challenges.
    - Login / Google login / CAPTCHA / Cloudflare / OTP / MFA
      are returned as verification_required.
    - Search-page shells are never treated as real job pages.
    """

    def __init__(self, page: Page):
        self.page = page

    # ========================================================
    # BASIC PAGE TEXT
    # ========================================================

    def _body_text(self) -> str:
        try:
            return self.page.locator("body").inner_text(timeout=5000)
        except Exception:
            return ""

    def _normalized_text(self) -> str:
        text = self._body_text()
        return re.sub(r"\s+", " ", text).strip().lower()

    # ========================================================
    # AUTH / SECURITY DETECTION
    # ========================================================

    def detect_authentication(self) -> Optional[str]:
        """
        Detect authentication ONLY when it actually blocks access
        to the job/application page.

        Public LinkedIn job pages frequently contain:
            - Sign in
            - Join now
            - Email
            - hidden password inputs
            - Sign in to see who you already know

        These are NOT authentication blocks.

        A job page is considered authentication-blocked only when:
            1. A visible password input exists, OR
            2. A visible Google authentication control exists, OR
            3. The page clearly states that authentication is required
               to access the job content.
        """

        # --------------------------------------------------------
        # 1. Visible password input
        # --------------------------------------------------------

        try:
            password_inputs = self.page.locator(
                "input[type='password']"
            )

            for i in range(
                min(password_inputs.count(), 20)
            ):
                try:
                    element = password_inputs.nth(i)

                    if element.is_visible():
                        return "Login/authentication required"

                except Exception:
                    continue

        except Exception:
            pass

        # --------------------------------------------------------
        # 2. Visible Google authentication controls
        # --------------------------------------------------------

        google_selectors = [
            "button",
            "a",
            "[role='button']",
            "[role='link']",
        ]

        google_phrases = [
            "sign in with google",
            "continue with google",
            "choose an account",
        ]

        for selector in google_selectors:
            try:
                elements = self.page.locator(selector)

                for i in range(
                    min(elements.count(), 100)
                ):
                    try:
                        element = elements.nth(i)

                        if not element.is_visible():
                            continue

                        element_text = (
                            element
                            .inner_text(timeout=500)
                            .strip()
                            .lower()
                        )

                        if any(
                            phrase in element_text
                            for phrase in google_phrases
                        ):
                            return (
                                "Google/login authentication required"
                            )

                    except Exception:
                        continue

            except Exception:
                continue

        # --------------------------------------------------------
        # 3. Explicit blocking message.
        #
        # These phrases are intentionally very specific.
        # Generic "sign in" / "login" is NOT sufficient.
        # --------------------------------------------------------

        text = self._normalized_text()

        blocking_phrases = [
            "you must sign in to view this job",
            "you must log in to view this job",
            "sign in required to view this job",
            "login required to view this job",
            "authentication required to view this job",
            "please sign in to view this job",
            "please log in to view this job",
            "sign in required to continue to this job",
            "login required to continue to this job",
        ]

        for phrase in blocking_phrases:
            if phrase in text:
                return "Login/authentication required"

        # --------------------------------------------------------
        # IMPORTANT:
        #
        # Do NOT inspect generic dialogs here.
        #
        # LinkedIn has a legitimate public-page dialog:
        #
        # "Sign in to see who you already know..."
        #
        # That dialog does NOT prevent us from reading the job.
        # --------------------------------------------------------

        return None


    def detect_security_challenge(self) -> Optional[str]:
        text = self._normalized_text()

        for pattern in SECURITY_PATTERNS:
            if pattern in text:
                return f"Security verification required: {pattern}"

        return None

    def detect_invalid_job_shell(self) -> Optional[str]:
        """
        Detect pages that genuinely failed to expose a job.

        IMPORTANT:
        LinkedIn public job pages contain navigation text such as:

            Skip to main content
            Sign in
            Join now
            Get notified about new ...

        Those strings are NOT sufficient to classify the page as
        invalid.

        We determine validity primarily from actual job content.
        """

        title = self._extract_title()
        description = self._extract_description()

        # --------------------------------------------------------
        # If we have a real title and substantial job description,
        # the page is usable even if LinkedIn navigation text exists.
        # --------------------------------------------------------

        if (
            title
            and len(title.strip()) >= 4
            and len(description.strip()) >= 200
        ):
            return None

        # --------------------------------------------------------
        # Only now inspect obvious shell markers.
        # --------------------------------------------------------

        text = self._normalized_text()

        shell_markers = [
            "skip to main content",
            "join linkedin",
            "authentication required",
            "sign in required to view this job",
            "login required to view this job",
        ]

        marker_count = sum(
            1
            for marker in shell_markers
            if marker in text
        )

        if marker_count >= 2:
            return (
                "Invalid job page: authentication/search shell detected"
            )

        # --------------------------------------------------------
        # A LinkedIn page with "Join LinkedIn" but no usable job
        # description is likely an authentication shell.
        # --------------------------------------------------------

        if (
            "join linkedin" in text
            and len(description.strip()) < 200
        ):
            return (
                "Invalid job page: LinkedIn authentication shell"
            )

        return None


    def detect_page_block(self) -> Optional[str]:
        # Security challenges always take priority.
        security_reason = self.detect_security_challenge()

        if security_reason:
            return security_reason

        # Authentication only when it genuinely blocks access.
        auth_reason = self.detect_authentication()

        if auth_reason:
            return auth_reason

        # Invalid shell detection happens after checking whether
        # usable job content exists.
        invalid_reason = self.detect_invalid_job_shell()

        if invalid_reason:
            return invalid_reason

        return None


    def _first_text(self, selectors: list[str]) -> str:
        for selector in selectors:
            try:
                locator = self.page.locator(selector)
                count = min(locator.count(), 5)

                for i in range(count):
                    try:
                        text = locator.nth(i).inner_text(timeout=1500).strip()
                        if text:
                            return text
                    except Exception:
                        continue
            except Exception:
                continue

        return ""

    def _extract_title(self) -> str:
        return self._first_text([
            "h1",
            "[data-test-job-title]",
            ".top-card-layout__title",
            ".job-details-jobs-unified-top-card__job-title",
            ".jobs-unified-top-card__job-title",
            "h1.t-24",
        ])

    # ========================================================
    # COMPANY
    # ========================================================

    def _extract_company(self) -> str:
        return self._first_text([
            "[data-test-employer-name]",
            ".topcard__org-name-link",
            ".top-card-layout__card a[data-tracking-control-name*='company']",
            ".jobs-unified-top-card__company-name",
            ".job-details-jobs-unified-top-card__company-name",
        ])

    # ========================================================
    # LOCATION
    # ========================================================

    def _extract_location(self) -> str:
        text = self._first_text([
            "[data-test-job-location]",
            ".topcard__flavor--bullet",
            ".job-details-jobs-unified-top-card__primary-description",
            ".jobs-unified-top-card__bullet",
        ])

        if text:
            return text

        # Fallback: inspect metadata lines.
        try:
            selectors = [
                ".top-card-layout__second-subline",
                ".jobs-unified-top-card__primary-description-container",
            ]

            for selector in selectors:
                locator = self.page.locator(selector)

                if locator.count():
                    raw = locator.first.inner_text(timeout=2000)
                    lines = [
                        x.strip()
                        for x in raw.splitlines()
                        if x.strip()
                    ]

                    for line in lines:
                        if any(
                            token in line.lower()
                            for token in [
                                "coimbatore",
                                "chennai",
                                "bengaluru",
                                "bangalore",
                                "hyderabad",
                                "pune",
                                "gurugram",
                                "gurgaon",
                                "india",
                            ]
                        ):
                            return line
        except Exception:
            pass

        return ""

    # ========================================================
    # DESCRIPTION
    # ========================================================

    def _extract_description(self) -> str:
        selectors = [
            "#job-details",
            ".show-more-less-html__markup",
            ".jobs-description__content",
            ".jobs-box__html-content",
            "[data-test-job-description]",
            ".description__text",
            ".job-details-module",
        ]

        best = ""

        for selector in selectors:
            try:
                locator = self.page.locator(selector)
                count = min(locator.count(), 5)

                for i in range(count):
                    try:
                        text = locator.nth(i).inner_text(timeout=2000).strip()

                        if len(text) > len(best):
                            best = text
                    except Exception:
                        continue
            except Exception:
                continue

        # Only fallback to body when it genuinely looks like a job detail
        # page. This prevents recommendation/search listings from becoming
        # part of the job description.
        if len(best) < 200:
            try:
                body = self._body_text()

                lower = body.lower()

                description_signals = [
                    "responsibilities",
                    "requirements",
                    "qualifications",
                    "job description",
                    "what you'll do",
                    "what you will do",
                    "skills required",
                ]

                signal_count = sum(
                    1 for signal in description_signals
                    if signal in lower
                )

                if signal_count >= 2:
                    best = body
            except Exception:
                pass

        return re.sub(r"\s+", " ", best).strip()

    # ========================================================
    # EXPERIENCE
    # ========================================================

    def _extract_experience(self, title: str, description: str) -> Optional[str]:
        text = f"{title}\n{description}"

        patterns = [
            r"\b(\d+)\s*\+\s*(?:years?|yrs?)\b",
            r"\bminimum\s*(?:of\s*)?(\d+)\s*(?:years?|yrs?)\b",
            r"\b(\d+)\s*(?:to|-|–)\s*(\d+)\s*(?:years?|yrs?)\b",
            r"\b(\d+)\s*-\s*(\d+)\s*(?:years?|yrs?)\b",
            r"\b(\d+)\s*(?:years?|yrs?)\s*(?:of\s*)?experience\b",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)

            if match:
                groups = match.groups()

                if len(groups) == 1:
                    return f"{groups[0]}+ years"

                return f"{groups[0]}-{groups[1]} years"

        # Common fresh-graduate signals.
        lower = text.lower()

        fresher_patterns = [
            "fresher",
            "freshers",
            "entry level",
            "entry-level",
            "0-1 years",
            "0 to 1 years",
            "0–1 years",
            "0-2 years",
            "0 to 2 years",
            "graduates welcome",
            "recent graduate",
        ]

        if any(p in lower for p in fresher_patterns):
            return "0-1 years"

        return None

    # ========================================================
    # SALARY
    # ========================================================

    def _extract_salary(self, description: str) -> Optional[str]:
        text = description

        patterns = [
            r"(?:₹|rs\.?|inr)\s*[\d,]+(?:\.\d+)?\s*(?:lpa|lakhs?|lacs?)?"
            r"\s*(?:-|to|–)\s*"
            r"(?:₹|rs\.?|inr)?\s*[\d,]+(?:\.\d+)?\s*(?:lpa|lakhs?|lacs?)?",

            r"\b\d+(?:\.\d+)?\s*(?:-|to|–)\s*\d+(?:\.\d+)?\s*lpa\b",

            r"\b\d+(?:\.\d+)?\s*lpa\b",

            r"\b(?:₹|rs\.?|inr)\s*[\d,]+(?:\.\d+)?\b",
        ]

        for pattern in patterns:
            match = re.search(
                pattern,
                text,
                re.IGNORECASE,
            )

            if match:
                return match.group(0).strip()

        # Dedicated salary elements.
        selectors = [
            "[data-test-job-salary]",
            ".salary",
            ".compensation",
            ".jobs-unified-top-card__job-insight",
        ]

        for selector in selectors:
            try:
                locator = self.page.locator(selector)

                for i in range(min(locator.count(), 10)):
                    text = locator.nth(i).inner_text(
                        timeout=1000
                    ).strip()

                    if any(
                        token in text.lower()
                        for token in ["₹", "rs", "inr", "lpa", "salary"]
                    ):
                        return text
            except Exception:
                continue

        return None

    # ========================================================
    # SENIORITY
    # ========================================================

    def _extract_seniority(
        self,
        title: str,
        description: str,
    ) -> Optional[str]:
        text = f"{title} {description}".lower()

        signals = [
            "principal",
            "director",
            "vice president",
            "vp ",
            "manager",
            "head of",
            "technical lead",
            "tech lead",
            "team lead",
            "lead engineer",
            "architect",
            "senior",
            "sr.",
            "staff engineer",
        ]

        for signal in signals:
            if signal in text:
                return signal.strip()

        return None

    # ========================================================
    # MAIN READ
    # ========================================================

    def read(self) -> JobPageReadResult:
        # First: security/authentication.
        block_reason = self.detect_page_block()

        if block_reason:
            lower = block_reason.lower()

            verification = any(
                token in lower
                for token in [
                    "google",
                    "login",
                    "authentication",
                    "security",
                    "captcha",
                    "cloudflare",
                    "otp",
                    "mfa",
                    "identity",
                ]
            )

            return JobPageReadResult(
                success=False,
                blocked=True,
                verification_required=verification,
                reason=block_reason,
            )

        title = self._extract_title()
        company = self._extract_company()
        location = self._extract_location()
        description = self._extract_description()

        # A real job page should have at least a useful title and
        # meaningful description.
        if not title or len(description) < 200:
            return JobPageReadResult(
                success=False,
                blocked=False,
                verification_required=False,
                reason="Unable to obtain a valid job detail page",
                title=title,
                company=company,
                location=location,
                description=description,
            )

        # Reject obvious LinkedIn shell content.
        invalid = self.detect_invalid_job_shell()

        if invalid:
            return JobPageReadResult(
                success=False,
                blocked=False,
                verification_required=False,
                reason=invalid,
                title=title,
                company=company,
                location=location,
                description=description,
            )

        experience = self._extract_experience(
            title,
            description,
        )

        salary = self._extract_salary(description)

        seniority = self._extract_seniority(
            title,
            description,
        )

        return JobPageReadResult(
            success=True,
            blocked=False,
            verification_required=False,
            reason="",
            title=title,
            company=company,
            location=location,
            description=description,
            salary=salary,
            experience=experience,
            seniority_signal=seniority,
        )


def read_job_page(page: Page) -> JobPageReadResult:
    reader = JobPageReader(page)
    return reader.read()
