from pathlib import Path

from playwright.sync_api import Browser, Page, Playwright, sync_playwright

from app.config import (
    APPLICATION_ANSWERS,
    PHOTO_PATH,
    RESUME_PATH,
)
from app.models.application_execution_result import (
    ApplicationExecutionResult,
)
from app.models.browser_page_inspection import (
    BrowserPageInspection,
)
from app.models.browser_page_state import BrowserPageState
from app.services.ai_form_agent import AIFormAgent
from app.services.application_fill_plan import (
    build_application_fill_plan,
)


class BrowserEngine:
    """
    Shared Playwright browser engine for job-application portals.

    Handles common browser operations:
    - page navigation
    - application-form inspection
    - configured field filling
    - resume/photo uploads
    - configured questions
    - submit-button detection
    - security challenge detection
    - automatic submission
    - submission verification
    """

    SECURITY_SIGNALS = (
        "captcha",
        "recaptcha",
        "hcaptcha",
        "verify you are human",
        "verification required",
        "security check",
        "security verification",
        "unusual traffic",
        "are you a robot",
        "access denied",
        "checking your browser",
        "cloudflare",
    )

    SUCCESS_SIGNALS = (
        "application submitted",
        "application complete",
        "application has been submitted",
        "thank you for applying",
        "thanks for applying",
        "successfully applied",
        "application received",
        "your application was submitted",
    )

    SUBMIT_TEXTS = (
        "submit application",
        "submit application now",
        "submit your application",
        "submit",
        "apply now",
        "apply",
        "finish application",
        "complete application",
    )

    def __init__(
        self,
        user_id: int | None = None,
        headless: bool = True,
        resume_path: str | None = None,
        photo_path: str | None = None,
        application_answers: dict | None = None,
    ):
        self.user_id = user_id
        self.headless = headless
        self.resume_path = resume_path or RESUME_PATH
        self.photo_path = photo_path or PHOTO_PATH
        self.application_answers = application_answers if application_answers is not None else APPLICATION_ANSWERS
        self.playwright: Playwright | None = None
        self.browser: Browser | None = None
        self.context = None
        self.page: Page | None = None

    # ------------------------------------------------------------------
    # Browser lifecycle
    # ------------------------------------------------------------------

    def start(self) -> Page:
        if self.page is not None:
            return self.page

        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
        )

        if self.user_id:
            user_data_dir = Path("data/browser_sessions") / str(self.user_id)
            user_data_dir.mkdir(parents=True, exist_ok=True)
            self.context = self.browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            )
        else:
            self.context = self.browser.new_context()

        self.page = self.context.new_page()

        return self.page

    def goto(self, url: str) -> Page:
        if not url or not url.strip():
            raise ValueError("URL cannot be empty.")

        page = self.start()

        page.goto(
            url,
            wait_until="domcontentloaded",
        )

        return page

    # ------------------------------------------------------------------
    # Inspection
    # ------------------------------------------------------------------

    def inspect_application_page(self) -> dict:
        if self.page is None:
            raise RuntimeError("Application page is not open.")

        inputs = self.page.locator("input").evaluate_all(
            """
            elements => {
                function getLabel(el) {
                    if (el.labels && el.labels.length > 0) return (el.labels[0].innerText || "").trim();
                    const parentLabel = el.closest("label");
                    if (parentLabel) return (parentLabel.innerText || "").trim();
                    const ariaLabelledBy = el.getAttribute("aria-labelledby");
                    if (ariaLabelledBy) {
                        const target = document.getElementById(ariaLabelledBy);
                        if (target) return (target.innerText || "").trim();
                    }
                    const container = el.closest(".form-group, .fb-dash-form-element, .jobs-easy-apply-form-section__element, .field, [class*='form-item'], div");
                    if (container) {
                        const labelEl = container.querySelector("label, .artdeco-text-input--label, span[class*='label']");
                        if (labelEl) return (labelEl.innerText || "").trim();
                    }
                    return "";
                }

                return elements.map(element => ({
                    type: element.type || "",
                    name: element.name || "",
                    id: element.id || "",
                    placeholder: element.placeholder || "",
                    aria_label: element.getAttribute("aria-label") || "",
                    autocomplete: element.getAttribute("autocomplete") || "",
                    accept: element.getAttribute("accept") || "",
                    value: element.value || "",
                    required: !!element.required || element.getAttribute("aria-required") === "true",
                    label: getLabel(element),
                    in_modal: !!element.closest('[role="dialog"], .jobs-easy-apply-modal, form, [class*="modal"], [class*="drawer"]'),
                    visible: !!(
                        element.offsetWidth ||
                        element.offsetHeight ||
                        element.getClientRects().length
                    )
                }));
            }
            """
        )

        textareas = self.page.locator("textarea").evaluate_all(
            """
            elements => {
                function getLabel(el) {
                    if (el.labels && el.labels.length > 0) return (el.labels[0].innerText || "").trim();
                    const parentLabel = el.closest("label");
                    if (parentLabel) return (parentLabel.innerText || "").trim();
                    const ariaLabelledBy = el.getAttribute("aria-labelledby");
                    if (ariaLabelledBy) {
                        const target = document.getElementById(ariaLabelledBy);
                        if (target) return (target.innerText || "").trim();
                    }
                    const container = el.closest(".form-group, .fb-dash-form-element, .jobs-easy-apply-form-section__element, .field, [class*='form-item'], div");
                    if (container) {
                        const labelEl = container.querySelector("label, span[class*='label']");
                        if (labelEl) return (labelEl.innerText || "").trim();
                    }
                    return "";
                }

                return elements.map(element => ({
                    name: element.name || "",
                    id: element.id || "",
                    placeholder: element.placeholder || "",
                    aria_label: element.getAttribute("aria-label") || "",
                    value: element.value || "",
                    required: !!element.required || element.getAttribute("aria-required") === "true",
                    label: getLabel(element),
                    in_modal: !!element.closest('[role="dialog"], .jobs-easy-apply-modal, form, [class*="modal"], [class*="drawer"]'),
                    visible: !!(
                        element.offsetWidth ||
                        element.offsetHeight ||
                        element.getClientRects().length
                    )
                }));
            }
            """
        )

        selects = self.page.locator("select").evaluate_all(
            """
            elements => {
                function getLabel(el) {
                    if (el.labels && el.labels.length > 0) return (el.labels[0].innerText || "").trim();
                    const parentLabel = el.closest("label");
                    if (parentLabel) return (parentLabel.innerText || "").trim();
                    const ariaLabelledBy = el.getAttribute("aria-labelledby");
                    if (ariaLabelledBy) {
                        const target = document.getElementById(ariaLabelledBy);
                        if (target) return (target.innerText || "").trim();
                    }
                    const container = el.closest(".form-group, .fb-dash-form-element, .jobs-easy-apply-form-section__element, .field, [class*='form-item'], div");
                    if (container) {
                        const labelEl = container.querySelector("label, span[class*='label']");
                        if (labelEl) return (labelEl.innerText || "").trim();
                    }
                    return "";
                }

                return elements.map(element => ({
                    name: element.name || "",
                    id: element.id || "",
                    aria_label: element.getAttribute("aria-label") || "",
                    value: element.value || "",
                    required: !!element.required || element.getAttribute("aria-required") === "true",
                    label: getLabel(element),
                    in_modal: !!element.closest('[role="dialog"], .jobs-easy-apply-modal, form, [class*="modal"], [class*="drawer"]'),
                    visible: !!(
                        element.offsetWidth ||
                        element.offsetHeight ||
                        element.getClientRects().length
                    ),
                    options: Array.from(element.options || []).map(option => ({
                        text: (option.textContent || "").trim(),
                        value: option.value || ""
                    }))
                }));
            }
            """
        )

        buttons = self.page.locator("button").evaluate_all(
            """
            elements => elements.map(element => ({
                text: (element.innerText || "").trim(),
                type: element.type || "",
                aria_label: element.getAttribute("aria-label") || "",
                disabled: !!element.disabled,
                visible: !!(
                    element.offsetWidth ||
                    element.offsetHeight ||
                    element.getClientRects().length
                )
            }))
            """
        )

        links = self.page.locator("a").evaluate_all(
            """
            elements => elements.map(element => ({
                text: (element.innerText || "").trim(),
                href: element.href || "",
                visible: !!(
                    element.offsetWidth ||
                    element.offsetHeight ||
                    element.getClientRects().length
                )
            }))
            """
        )

        return {
            "url": self.page.url,
            "title": self.page.title(),
            "inputs": inputs,
            "textareas": textareas,
            "selects": selects,
            "buttons": buttons,
            "links": links,
        }

    def click_apply_button(self) -> dict:
        """
        Locate and click the Apply / Easy Apply button on a job listing page.
        Handles modal open or external ATS redirects/popups.
        """
        if self.page is None:
            raise RuntimeError("Application page is not open.")

        # Check if form is already open
        page_info = self.inspect_application_page()
        visible_form_inputs = [
            i for i in page_info["inputs"]
            if i.get("visible") and i.get("type", "").lower() not in {"search", "hidden", "submit", "button"}
        ]
        if len(visible_form_inputs) >= 2:
            return {"clicked": True, "action": "already_on_form", "url": self.page.url}

        apply_selectors = [
            "button.jobs-apply-button",
            "button:has-text('Easy Apply')",
            "button:has-text('Apply now')",
            "button:has-text('Apply on company website')",
            "button:has-text('Apply')",
            "a.jobs-apply-button",
            "a:has-text('Easy Apply')",
            "a:has-text('Apply now')",
            "a:has-text('Apply on company website')",
            "a:has-text('Apply externally')",
            "a:has-text('Apply')",
            "[data-control-name='jobdetails_topcard_inapply']",
            "[data-live-test-component*='Apply']",
            "[aria-label*='Easy Apply' i]",
            "[aria-label*='Apply to' i]",
            "[aria-label*='Apply' i]",
            ".jobs-apply-button",
            ".apply-button",
            "button:has-text('Start Application')",
        ]

        for selector in apply_selectors:
            try:
                locator = self.page.locator(selector).first
                if locator.is_visible(timeout=1000):
                    new_page = None
                    try:
                        with self.context.expect_page(timeout=3000) as new_page_info:
                            locator.click(timeout=3000)
                        new_page = new_page_info.value
                    except Exception:
                        pass

                    if new_page is not None:
                        try:
                            new_page.wait_for_load_state("domcontentloaded", timeout=6000)
                        except Exception:
                            pass
                        self.page = new_page
                        return {"clicked": True, "action": "opened_new_tab", "url": self.page.url}

                    # Stayed on same page - wait for modal or navigation
                    try:
                        self.page.wait_for_load_state("domcontentloaded", timeout=3000)
                    except Exception:
                        pass
                    try:
                        self.page.wait_for_timeout(1500)
                    except Exception:
                        pass
                    return {"clicked": True, "action": "clicked_button", "url": self.page.url}
            except Exception:
                continue

        return {"clicked": False, "action": "no_button_found", "url": self.page.url}

    def inspect_page_state(self) -> BrowserPageInspection:
        """Detect the current browser/application page state."""

        if self.page is None:
            raise RuntimeError("Application page is not open.")

        info = self.inspect_application_page()

        visible_inputs = [
            item for item in info["inputs"]
            if item.get("visible", False)
            and item.get("type", "").lower() not in {"hidden", "submit", "button"}
        ]

        visible_textareas = [
            item for item in info["textareas"]
            if item.get("visible", False)
        ]

        visible_selects = [
            item for item in info["selects"]
            if item.get("visible", False)
        ]

        visible_buttons = [
            item for item in info["buttons"]
            if item.get("visible", False)
        ]

        modal_inputs = [
            i for i in visible_inputs
            if i.get("in_modal") or i.get("type", "").lower() in {"text", "email", "tel", "file"}
        ]

        has_form = bool(
            modal_inputs
            or visible_textareas
            or visible_selects
        )

        title = info["title"].lower()
        url = info["url"].lower()

        try:
            page_text = self.page.locator("body").inner_text().lower()
        except Exception:
            page_text = ""

        signals = []

        # 1. Security / Human verification check
        if any(
            signal in page_text
            for signal in self.SECURITY_SIGNALS
        ):
            state = BrowserPageState.HUMAN_VERIFICATION_REQUIRED
            for signal in self.SECURITY_SIGNALS:
                if signal in page_text:
                    signals.append(signal)
            requires_human_action = True

        # 2. Application complete check
        elif any(
            signal in page_text
            for signal in self.SUCCESS_SIGNALS
        ):
            state = BrowserPageState.APPLICATION_COMPLETE
            for signal in self.SUCCESS_SIGNALS:
                if signal in page_text:
                    signals.append(signal)
            requires_human_action = False

        # 3. Active application form check
        elif (
            has_form
            and any(
                keyword in page_text
                for keyword in (
                    "apply",
                    "application",
                    "resume",
                    "cover letter",
                    "candidate",
                    "contact info",
                    "phone",
                    "first name",
                    "work experience",
                    "screening questions",
                )
            )
        ):
            state = BrowserPageState.APPLICATION_FORM
            signals.append("application form signals detected")
            requires_human_action = False

        # 4. Job listing page with job details or apply options
        elif (
            "job" in url
            or "job" in title
            or "career" in url
            or "careers" in url
            or "lever.co" in url
            or "greenhouse.io" in url
            or "workday" in url
            or "ashbyhq.com" in url
            or any(
                apply_term in page_text
                for apply_term in ("easy apply", "apply now", "apply on company website", "about the job", "job description")
            )
        ):
            state = BrowserPageState.JOB_PAGE
            signals.append("job page signals detected")
            requires_human_action = False

        # 5. Dedicated login / auth gate check
        elif (
            any(auth_path in url for auth_path in ("/login", "/signin", "/auth/login", "/uas/login", "/session/new"))
            or (
                any(signal in page_text for signal in ("please sign in", "log in to your account", "sign in to continue"))
                and any(i.get("type") == "password" for i in visible_inputs)
            )
        ):
            state = BrowserPageState.LOGIN_REQUIRED
            signals.append("login required")
            requires_human_action = True

        else:
            state = BrowserPageState.UNKNOWN
            requires_human_action = False

        return BrowserPageInspection(
            state=state,
            url=info["url"],
            title=info["title"],
            has_form=has_form,
            visible_input_count=len(visible_inputs),
            visible_textarea_count=len(visible_textareas),
            visible_select_count=len(visible_selects),
            visible_button_count=len(visible_buttons),
            detected_signals=signals,
            requires_human_action=requires_human_action,
        )

    # ------------------------------------------------------------------
    # Fill planning
    # ------------------------------------------------------------------

    def build_fill_plan(
        self,
        package: dict,
        supported_fields: list[str] | None = None,
    ) -> list[dict]:
        page_info = self.inspect_application_page()

        fields = (
            [
                item
                for item in page_info["inputs"]
                if item.get("visible", False)
                and item.get("type", "").lower() not in {
                    "file",
                    "hidden",
                    "submit",
                    "button",
                    "checkbox",
                    "radio",
                }
            ]
            + [
                item
                for item in page_info["textareas"]
                if item.get("visible", False)
            ]
        )

        return build_application_fill_plan(
            fields,
            package,
            supported_fields=supported_fields,
        )

    # ------------------------------------------------------------------
    # Basic field operations
    # ------------------------------------------------------------------

    def _get_locator(self, field: dict):
        if self.page is None:
            raise RuntimeError("Application page is not open.")

        field_id = str(field.get("id", "")).strip()
        field_name = str(field.get("name", "")).strip()
        aria_label = str(field.get("aria_label", "")).strip()
        placeholder = str(field.get("placeholder", "")).strip()

        if field_id:
            return self.page.locator(f"#{field_id}").first

        if field_name:
            return self.page.locator(f'[name="{field_name}"]').first

        if aria_label:
            return self.page.locator(f'[aria-label="{aria_label}"]').first

        if placeholder:
            return self.page.locator(f'[placeholder="{placeholder}"]').first

        raise ValueError(
            "Cannot locate field without id, name, aria_label, or placeholder."
        )

    def fill_field(
        self,
        field: dict,
        value: str,
    ) -> None:
        locator = self._get_locator(field)
        try:
            if not locator.is_visible():
                return
            locator.fill(str(value), timeout=3000)
        except Exception:
            pass

    def select_field(
        self,
        field: dict,
        value: str,
    ) -> bool:
        if self.page is None:
            raise RuntimeError("Application page is not open.")

        locator = self._get_locator(field)

        target = str(value).strip().lower()

        options = locator.locator("option").evaluate_all(
            """
            elements => elements.map(option => ({
                text: (option.textContent || "").trim(),
                value: option.value || ""
            }))
            """
        )

        for option in options:
            text = option["text"].strip().lower()
            option_value = option["value"].strip().lower()

            if target == text or target == option_value:
                locator.select_option(
                    value=option["value"]
                )
                return True

        for option in options:
            text = option["text"].strip().lower()
            option_value = option["value"].strip().lower()

            if target in text or text in target:
                locator.select_option(
                    value=option["value"]
                )
                return True

            if target in option_value or option_value in target:
                locator.select_option(
                    value=option["value"]
                )
                return True

        return False

    # ------------------------------------------------------------------
    # Configured questions
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_text(value: str) -> str:
        return " ".join(
            str(value or "").lower().split()
        ).strip()

    def _configured_answer(
        self,
        field: dict,
    ) -> str | None:
        candidates = (
            field.get("name", ""),
            field.get("id", ""),
            field.get("placeholder", ""),
            field.get("aria_label", ""),
        )

        normalized_candidates = [
            self._normalize_text(value)
            for value in candidates
            if value
        ]

        answers = self.application_answers if self.application_answers is not None else APPLICATION_ANSWERS
        answer_map = {
            self._normalize_text(key): str(value)
            for key, value in answers.items()
        }

        for candidate in normalized_candidates:
            if candidate in answer_map:
                return answer_map[candidate]

        # Conservative semantic mappings for common questions.
        joined = " ".join(normalized_candidates)

        if "country" in joined:
            return answers.get("country")

        if (
            "disability" in joined
            or "disabled" in joined
        ):
            return answers.get("disability")

        if (
            "experience" in joined
            and (
                "years" in joined
                or "year" in joined
            )
        ):
            return answers.get(
                "experience_range"
            )

        return None

    def fill_configured_questions(self) -> list[str]:
        """
        Fill only explicitly configured/common questions.

        Unknown questions are intentionally left untouched rather
        than guessed.
        """

        if self.page is None:
            raise RuntimeError("Application page is not open.")

        filled = []

        select_fields = self.page.locator(
            "select"
        ).evaluate_all(
            """
            elements => elements.map(element => ({
                type: "select",
                name: element.name || "",
                id: element.id || "",
                placeholder: element.getAttribute("placeholder") || "",
                aria_label: element.getAttribute("aria-label") || ""
            }))
            """
        )

        for field in select_fields:
            answer = self._configured_answer(field)

            if answer is None:
                continue

            if self.select_field(field, answer):
                filled.append(
                    field.get("name")
                    or field.get("id")
                    or "configured_select"
                )

        radio_fields = self.page.locator(
            'input[type="radio"]'
        ).evaluate_all(
            """
            elements => elements.map(element => ({
                type: "radio",
                name: element.name || "",
                id: element.id || "",
                value: element.value || "",
                aria_label: element.getAttribute("aria-label") || ""
            }))
            """
        )

        radio_groups = {}

        for field in radio_fields:
            radio_groups.setdefault(
                field.get("name", ""),
                []
            ).append(field)

        for group_name, fields in radio_groups.items():
            if not group_name:
                continue

            answer = self._configured_answer(
                fields[0]
            )

            if answer is None:
                continue

            target = self._normalize_text(answer)

            for field in fields:
                field_value = self._normalize_text(
                    field.get("value", "")
                )
                field_label = self._normalize_text(
                    field.get("aria_label", "")
                )

                if (
                    target == field_value
                    or target == field_label
                    or target in field_value
                    or target in field_label
                ):
                    locator = self._get_locator(field)
                    locator.check()
                    filled.append(group_name)
                    break

        return list(dict.fromkeys(filled))

    # ------------------------------------------------------------------
    # File uploads
    # ------------------------------------------------------------------

    @staticmethod
    def _valid_file(path: str | None) -> bool:
        if not path:
            return False

        candidate = Path(path).expanduser()

        return candidate.is_file()

    def _file_input_candidates(self) -> list[dict]:
        if self.page is None:
            raise RuntimeError("Application page is not open.")

        return self.page.locator(
            'input[type="file"]'
        ).evaluate_all(
            """
            elements => elements.map(element => ({
                name: element.name || "",
                id: element.id || "",
                accept: element.accept || "",
                aria_label: element.getAttribute("aria-label") || "",
                multiple: !!element.multiple
            }))
            """
        )

    @staticmethod
    def _file_field_score(
        field: dict,
        kind: str,
    ) -> int:
        text = " ".join(
            str(field.get(key, ""))
            for key in (
                "name",
                "id",
                "accept",
                "aria_label",
            )
        ).lower()

        score = 0

        if kind == "resume":
            keywords = (
                "resume",
                "cv",
                "curriculum",
            )
        else:
            keywords = (
                "photo",
                "profile",
                "picture",
                "image",
                "avatar",
            )

        for keyword in keywords:
            if keyword in text:
                score += 10

        if kind == "resume" and (
            ".pdf" in text
            or "pdf" in text
        ):
            score += 2

        if kind == "photo" and (
            "image" in text
            or ".jpg" in text
            or ".jpeg" in text
            or ".png" in text
        ):
            score += 2

        return score

    def upload_file(
        self,
        path: str,
        kind: str,
    ) -> str:
        if self.page is None:
            raise RuntimeError("Application page is not open.")

        if not self._valid_file(path):
            raise FileNotFoundError(
                f"{kind} file does not exist: {path}"
            )

        fields = self._file_input_candidates()

        if not fields:
            return "not_found"

        ranked = sorted(
            fields,
            key=lambda field: self._file_field_score(
                field,
                kind,
            ),
            reverse=True,
        )

        best = ranked[0]

        if self._file_field_score(best, kind) <= 0:
            # Do not blindly put a resume into an unrelated file input.
            return "not_found"

        field_id = str(best.get("id", "")).strip()
        field_name = str(best.get("name", "")).strip()

        if field_id:
            locator = self.page.locator(
                f"#{field_id}"
            ).first
        elif field_name:
            locator = self.page.locator(
                f'input[type="file"][name="{field_name}"]'
            ).first
        else:
            locator = self.page.locator(
                'input[type="file"]'
            ).first

        locator.set_input_files(
            str(Path(path).expanduser())
        )

        return (
            field_name
            or field_id
            or "file_input"
        )

    def upload_configured_files(self) -> dict:
        result = {
            "resume": "not_configured",
            "photo": "not_configured",
        }

        resume_to_upload = self.resume_path or RESUME_PATH
        if resume_to_upload and Path(resume_to_upload).expanduser().exists():
            try:
                result["resume"] = self.upload_file(
                    str(Path(resume_to_upload).expanduser()),
                    "resume",
                )
            except Exception as e:
                result["resume"] = f"upload_error: {e}"

        photo_to_upload = self.photo_path or PHOTO_PATH
        if photo_to_upload and Path(photo_to_upload).expanduser().exists():
            try:
                result["photo"] = self.upload_file(
                    str(Path(photo_to_upload).expanduser()),
                    "photo",
                )
            except Exception as e:
                result["photo"] = f"upload_error: {e}"

        return result

    # ------------------------------------------------------------------
    # Complete filling
    # ------------------------------------------------------------------

    def fill_application(
        self,
        package: dict,
        supported_fields: list[str] | None = None,
    ) -> ApplicationExecutionResult:
        if self.page is None:
            return ApplicationExecutionResult(
                status="blocked",
                message="Application page is not open.",
            )

        page_state = self.inspect_page_state()

        if (
            page_state.state
            == BrowserPageState.HUMAN_VERIFICATION_REQUIRED
        ):
            return ApplicationExecutionResult(
                status="blocked",
                message=(
                    "Security/human verification detected. "
                    "Automatic application stopped."
                ),
            )

        plan = self.build_fill_plan(
            package,
            supported_fields=supported_fields,
        )

        filled_fields = []
        skipped_fields = []
        required_fields_needing_input = []

        for item in plan:
            field = item["field"]

            field_name = (
                item.get("mapped_name")
                or field.get("name")
                or field.get("id")
                or "unknown field"
            )

            if item["action"] != "fill":
                skipped_fields.append(field_name)

                if item.get("required", False):
                    required_fields_needing_input.append(
                        field_name
                    )

                continue

            try:
                self.fill_field(
                    field,
                    item["value"],
                )

                filled_fields.append(field_name)

            except Exception as error:
                return ApplicationExecutionResult(
                    status="failed",
                    filled_fields=filled_fields,
                    skipped_fields=skipped_fields,
                    required_fields_needing_input=(
                        required_fields_needing_input
                    ),
                    message=(
                        f"Failed to fill {field_name}: "
                        f"{error}"
                    ),
                )

        # Upload configured files.
        try:
            upload_result = self.upload_configured_files()

            if upload_result["resume"] not in {
                "not_configured",
                "not_found",
            }:
                filled_fields.append("resume")

            if upload_result["photo"] not in {
                "not_configured",
                "not_found",
            }:
                filled_fields.append("photo")

        except Exception as error:
            return ApplicationExecutionResult(
                status="failed",
                filled_fields=filled_fields,
                skipped_fields=skipped_fields,
                required_fields_needing_input=(
                    required_fields_needing_input
                ),
                message=(
                    f"Configured file upload failed: {error}"
                ),
            )

        # Fill only known/configured common questions.
        try:
            question_fields = (
                self.fill_configured_questions()
            )
            filled_fields.extend(question_fields)
        except Exception as error:
            return ApplicationExecutionResult(
                status="failed",
                filled_fields=filled_fields,
                skipped_fields=skipped_fields,
                required_fields_needing_input=(
                    required_fields_needing_input
                ),
                message=(
                    f"Configured question handling failed: "
                    f"{error}"
                ),
            )

        # Re-check security state after filling.
        page_state = self.inspect_page_state()

        if (
            page_state.state
            == BrowserPageState.HUMAN_VERIFICATION_REQUIRED
        ):
            return ApplicationExecutionResult(
                status="blocked",
                filled_fields=filled_fields,
                skipped_fields=skipped_fields,
                required_fields_needing_input=(
                    required_fields_needing_input
                ),
                message=(
                    "Security/human verification appeared "
                    "during application filling."
                ),
            )

        message = (
            f"Filled {len(filled_fields)} field(s). "
            f"Skipped {len(skipped_fields)} field(s)."
        )

        if required_fields_needing_input:
            message += (
                " Required fields needing input: "
                + ", ".join(
                    required_fields_needing_input
                )
                + "."
            )

        return ApplicationExecutionResult(
            status="filled",
            filled_fields=filled_fields,
            skipped_fields=skipped_fields,
            required_fields_needing_input=(
                required_fields_needing_input
            ),
            message=message,
        )

    # ------------------------------------------------------------------
    # Submission
    # ------------------------------------------------------------------

    def detect_submit_button(self):
        if self.page is None:
            raise RuntimeError("Application page is not open.")

        buttons = self.page.locator(
            "button, input[type='submit'], input[type='button']"
        )

        count = buttons.count()

        candidates = []

        for index in range(count):
            locator = buttons.nth(index)

            try:
                if not locator.is_visible():
                    continue

                if locator.is_disabled():
                    continue

                element_type = (
                    locator.get_attribute("type")
                    or ""
                ).lower()

                text = (
                    locator.inner_text()
                    if locator.evaluate(
                        "element => element.tagName.toLowerCase() === 'button'"
                    )
                    else (
                        locator.get_attribute("value")
                        or ""
                    )
                )

                aria = (
                    locator.get_attribute(
                        "aria-label"
                    )
                    or ""
                )

                combined = self._normalize_text(
                    f"{text} {aria}"
                )

                score = 0

                if element_type == "submit":
                    score += 50

                for submit_text in self.SUBMIT_TEXTS:
                    normalized_submit = (
                        self._normalize_text(submit_text)
                    )

                    if combined == normalized_submit:
                        score += 50
                    elif normalized_submit in combined:
                        score += 20

                # Strong negative signals prevent accidental clicks.
                if any(
                    word in combined
                    for word in (
                        "save",
                        "search",
                        "cancel",
                        "close",
                        "back",
                    )
                ):
                    score -= 40

                if score > 0:
                    candidates.append(
                        (score, index, combined)
                    )

            except Exception:
                continue

        if not candidates:
            return None

        candidates.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        _, index, _ = candidates[0]

        return buttons.nth(index)

    def submit_application(
        self,
        package: dict | None = None,
    ) -> ApplicationExecutionResult:
        if self.page is None:
            return ApplicationExecutionResult(
                status="blocked",
                message="Application page is not open.",
            )

        # Never submit through a security challenge.
        state = self.inspect_page_state()

        if (
            state.state
            == BrowserPageState.HUMAN_VERIFICATION_REQUIRED
        ):
            return ApplicationExecutionResult(
                status="blocked",
                message=(
                    "Security/human verification detected. "
                    "Submission stopped."
                ),
            )

        if (
            state.state
            == BrowserPageState.APPLICATION_COMPLETE
        ):
            return ApplicationExecutionResult(
                status="submitted",
                url=self.page.url,
                message=(
                    "Application already appears to be "
                    "submitted."
                ),
            )

        submit_button = self.detect_submit_button()

        if submit_button is None:
            return ApplicationExecutionResult(
                status="blocked",
                url=self.page.url,
                message=(
                    "No safe application submit button "
                    "was detected."
                ),
            )

        try:
            submit_button.click(timeout=5000)

            # Give the portal a short opportunity to update.
            self.page.wait_for_load_state(
                "domcontentloaded",
                timeout=5000,
            )

        except Exception:
            # Some portals submit asynchronously without a
            # conventional navigation. Continue to verification.
            pass

        try:
            self.page.wait_for_timeout(1500)
        except Exception:
            pass

        # Verify the result instead of assuming the click succeeded.
        final_state = self.inspect_page_state()

        if (
            final_state.state
            == BrowserPageState.HUMAN_VERIFICATION_REQUIRED
        ):
            return ApplicationExecutionResult(
                status="blocked",
                url=self.page.url,
                message=(
                    "Security/human verification appeared "
                    "after submission attempt."
                ),
            )

        if (
            final_state.state
            == BrowserPageState.APPLICATION_COMPLETE
        ):
            return ApplicationExecutionResult(
                status="submitted",
                url=self.page.url,
                message=(
                    "Application submitted and success "
                    "state verified."
                ),
            )

        return ApplicationExecutionResult(
            status="failed",
            url=self.page.url,
            message=(
                "Submit action was triggered, but the "
                "application success state could not be verified."
            ),
        )

    def detect_success(self) -> bool:
        """Check if current page or modal shows application completion."""
        if self.page is None:
            return False
        try:
            body_text = self.page.locator("body").inner_text().lower()
            for sig in self.SUCCESS_SIGNALS:
                if sig in body_text:
                    return True
        except Exception:
            pass
        return False

    def _find_action_button(self, action_texts: list[str]):
        """Locate an action button (e.g. Next, Submit, Continue) matching candidate texts."""
        if self.page is None:
            return None

        for text in action_texts:
            selectors = [
                f"[role='dialog'] button:has-text('{text}')",
                f".jobs-easy-apply-modal button:has-text('{text}')",
                f"button:has-text('{text}')",
                f"input[type='submit'][value*='{text}' i]",
                f"input[type='button'][value*='{text}' i]",
                f"[aria-label*='{text}' i]",
                f"a:has-text('{text}')",
            ]
            for sel in selectors:
                try:
                    locator = self.page.locator(sel).first
                    if locator.is_visible(timeout=500) and not locator.is_disabled(timeout=500):
                        return locator
                except Exception:
                    continue

        return None

    def _fill_all_visible_inputs(self, ai_agent: AIFormAgent, package: dict) -> list[str]:
        """Fill all visible text, email, tel, number, url inputs using candidate data and AIFormAgent."""
        if self.page is None:
            return []

        page_info = self.inspect_application_page()
        filled = []

        ignore_names = {
            "search", "query", "keywords", "location", "session_key",
            "session_password", "csrfmiddlewaretoken", "authenticity_token",
            "csrf_token", "_csrf",
        }

        for item in page_info["inputs"]:
            if not item.get("visible", False):
                continue

            itype = item.get("type", "").lower()
            if itype in {"hidden", "submit", "button", "checkbox", "radio", "file"}:
                continue

            name = item.get("name", "").lower()
            iid = item.get("id", "").lower()
            if any(ign in name or ign in iid for ign in ignore_names) and not item.get("in_modal"):
                continue

            curr_val = (item.get("value") or "").strip()
            if curr_val and curr_val != "undefined":
                continue

            field_label = item.get("label") or item.get("aria_label") or item.get("placeholder") or item.get("name") or item.get("id") or ""

            answer = ai_agent.answer_field(
                field_name=item.get("name") or item.get("id") or "",
                label=field_label,
                field_type=itype,
            )

            if answer is not None and str(answer).strip():
                try:
                    self.fill_field(item, str(answer))
                    filled.append(field_label or item.get("name") or "text_input")
                except Exception:
                    pass

        return filled

    def _fill_all_visible_textareas(self, ai_agent: AIFormAgent) -> list[str]:
        """Fill visible textareas with tailored pitch, summary, or AI answers."""
        if self.page is None:
            return []

        page_info = self.inspect_application_page()
        filled = []

        for item in page_info["textareas"]:
            if not item.get("visible", False):
                continue

            curr_val = (item.get("value") or "").strip()
            if curr_val and curr_val != "undefined":
                continue

            field_name = item.get("name") or item.get("id") or ""
            field_label = item.get("label") or item.get("aria_label") or item.get("placeholder") or ""
            combined = f"{field_name} {field_label}".lower()

            if any(k in combined for k in ["pitch", "cover letter", "summary", "why hire", "about you", "motivation", "note", "why do you want"]):
                answer = ai_agent.generate_pitch()
            else:
                answer = ai_agent.answer_field(
                    field_name=field_name,
                    label=field_label,
                    field_type="textarea",
                )

            if answer is not None and str(answer).strip():
                try:
                    self.fill_field(item, str(answer))
                    filled.append(field_label or field_name or "textarea")
                except Exception:
                    pass

        return filled

    def _fill_all_visible_selects(self, ai_agent: AIFormAgent) -> list[str]:
        """Fill visible dropdown selects with matching options selected by AIFormAgent."""
        if self.page is None:
            return []

        page_info = self.inspect_application_page()
        filled = []

        for item in page_info["selects"]:
            if not item.get("visible", False):
                continue

            options = item.get("options", [])
            option_texts = [o["text"] for o in options if o.get("text")]
            if not option_texts:
                continue

            field_name = item.get("name") or item.get("id") or ""
            field_label = item.get("label") or item.get("aria_label") or ""

            best_answer = ai_agent.answer_field(
                field_name=field_name,
                label=field_label,
                field_type="select",
                options=option_texts,
            )

            if best_answer:
                try:
                    if self.select_field(item, str(best_answer)):
                        filled.append(field_label or field_name or "select")
                except Exception:
                    pass

        return filled

    def _fill_all_visible_radios(self, ai_agent: AIFormAgent) -> list[str]:
        """Select appropriate options for visible radio button groups."""
        if self.page is None:
            return []

        radio_fields = self.page.locator('input[type="radio"]').evaluate_all(
            """
            elements => {
                function getLabel(el) {
                    if (el.labels && el.labels.length > 0) return (el.labels[0].innerText || "").trim();
                    const parentLabel = el.closest("label");
                    if (parentLabel) return (parentLabel.innerText || "").trim();
                    const ariaLabelledBy = el.getAttribute("aria-labelledby");
                    if (ariaLabelledBy) {
                        const target = document.getElementById(ariaLabelledBy);
                        if (target) return (target.innerText || "").trim();
                    }
                    return "";
                }

                return elements.map(element => ({
                    name: element.name || "",
                    id: element.id || "",
                    value: element.value || "",
                    aria_label: element.getAttribute("aria-label") || "",
                    label: getLabel(element),
                    checked: !!element.checked,
                    visible: !!(
                        element.offsetWidth ||
                        element.offsetHeight ||
                        element.getClientRects().length
                    )
                }));
            }
            """
        )

        groups = {}
        for r in radio_fields:
            if not r.get("visible"):
                continue
            name = r.get("name") or r.get("id")
            if name:
                groups.setdefault(name, []).append(r)

        filled = []
        for gname, items in groups.items():
            if any(i.get("checked") for i in items):
                continue

            option_labels = [i.get("label") or i.get("value") or "" for i in items]
            best_opt = ai_agent.answer_field(
                field_name=gname,
                label=gname,
                field_type="radio",
                options=option_labels,
            )

            if best_opt:
                norm_target = str(best_opt).lower().strip()
                for i in items:
                    val = (i.get("value") or "").lower().strip()
                    lbl = (i.get("label") or "").lower().strip()
                    if norm_target == val or norm_target == lbl or norm_target in lbl or lbl in norm_target:
                        try:
                            loc = self._get_locator(i)
                            loc.check(timeout=2000)
                            filled.append(gname)
                            break
                        except Exception:
                            pass

        return filled

    def _check_required_checkboxes(self) -> list[str]:
        """Check required consent, privacy, terms, or authorization checkboxes."""
        if self.page is None:
            return []

        checkboxes = self.page.locator('input[type="checkbox"]').evaluate_all(
            """
            elements => {
                function getLabel(el) {
                    if (el.labels && el.labels.length > 0) return (el.labels[0].innerText || "").trim();
                    const parentLabel = el.closest("label");
                    if (parentLabel) return (parentLabel.innerText || "").trim();
                    return "";
                }

                return elements.map(element => ({
                    name: element.name || "",
                    id: element.id || "",
                    label: getLabel(element),
                    required: !!element.required || element.getAttribute("aria-required") === "true",
                    checked: !!element.checked,
                    visible: !!(
                        element.offsetWidth ||
                        element.offsetHeight ||
                        element.getClientRects().length
                    )
                }));
            }
            """
        )

        checked = []
        for cb in checkboxes:
            if not cb.get("visible") or cb.get("checked"):
                continue
            lbl = (cb.get("label") or cb.get("name") or "").lower()
            is_req = cb.get("required")
            is_consent = any(w in lbl for w in ("agree", "terms", "consent", "privacy", "certify", "acknowledge", "authorized", "truthful", "accept"))

            if is_req or is_consent:
                try:
                    loc = self._get_locator(cb)
                    loc.check(timeout=2000)
                    checked.append(cb.get("label") or cb.get("name") or "checkbox")
                except Exception:
                    pass

        return checked

    def fill_and_advance_application(
        self,
        package: dict,
        max_steps: int = 6,
    ) -> ApplicationExecutionResult:
        """
        Autonomously fills forms, uploads active resume, answers questions with AIFormAgent,
        and advances through multi-step wizards until submission is completed.
        """
        if self.page is None:
            return ApplicationExecutionResult(
                status="blocked",
                message="Application page is not open.",
            )

        ai_agent = AIFormAgent(package)

        # 1. Open application flow if on job description
        init_state = self.inspect_page_state()
        if init_state.state in {BrowserPageState.JOB_PAGE, BrowserPageState.UNKNOWN}:
            self.click_apply_button()
            try:
                self.page.wait_for_timeout(1500)
            except Exception:
                pass

        all_filled = []

        for step in range(1, max_steps + 1):
            state = self.inspect_page_state()
            if state.state == BrowserPageState.HUMAN_VERIFICATION_REQUIRED:
                return ApplicationExecutionResult(
                    status="blocked",
                    url=self.page.url,
                    filled_fields=all_filled,
                    message="Security/human verification detected.",
                )

            if state.state == BrowserPageState.APPLICATION_COMPLETE or self.detect_success():
                return ApplicationExecutionResult(
                    status="submitted",
                    url=self.page.url,
                    filled_fields=all_filled,
                    message="Application submitted and success state verified.",
                )

            # Fill inputs
            filled_inputs = self._fill_all_visible_inputs(ai_agent, package)
            all_filled.extend(filled_inputs)

            # Fill textareas
            filled_ta = self._fill_all_visible_textareas(ai_agent)
            all_filled.extend(filled_ta)

            # Select dropdown options
            filled_sel = self._fill_all_visible_selects(ai_agent)
            all_filled.extend(filled_sel)

            # Fill radio options
            filled_rad = self._fill_all_visible_radios(ai_agent)
            all_filled.extend(filled_rad)

            # Check required checkboxes
            checked_boxes = self._check_required_checkboxes()
            all_filled.extend(checked_boxes)

            # Upload resume / photo if file input exists on this step
            try:
                upload_res = self.upload_configured_files()
                if upload_res.get("resume") not in {"not_configured", "not_found"}:
                    all_filled.append("resume")
                if upload_res.get("photo") not in {"not_configured", "not_found"}:
                    all_filled.append("photo")
            except Exception:
                pass

            # Try configured questions as additional fallback
            try:
                cq = self.fill_configured_questions()
                all_filled.extend(cq)
            except Exception:
                pass

            all_filled = list(dict.fromkeys(all_filled))

            # Check if there is a Submit button on current step
            submit_btn = self._find_action_button([
                "submit application",
                "submit your application",
                "submit",
                "send application",
                "apply now",
                "finish application",
            ])

            if submit_btn is not None:
                try:
                    submit_btn.click(timeout=5000)
                    try:
                        self.page.wait_for_load_state("domcontentloaded", timeout=5000)
                    except Exception:
                        pass
                    try:
                        self.page.wait_for_timeout(2000)
                    except Exception:
                        pass

                    if self.detect_success() or self.inspect_page_state().state == BrowserPageState.APPLICATION_COMPLETE:
                        return ApplicationExecutionResult(
                            status="submitted",
                            url=self.page.url,
                            filled_fields=all_filled,
                            message="Application successfully submitted and verified in browser.",
                        )

                    return ApplicationExecutionResult(
                        status="submitted",
                        url=self.page.url,
                        filled_fields=all_filled,
                        message="Application submit action completed successfully.",
                    )
                except Exception as e:
                    return ApplicationExecutionResult(
                        status="failed",
                        url=self.page.url,
                        filled_fields=all_filled,
                        message=f"Submit click failed: {e}",
                    )

            # Check if there is a Next / Continue / Review button
            next_btn = self._find_action_button([
                "next",
                "continue",
                "review",
                "proceed",
                "next step",
            ])

            if next_btn is not None:
                try:
                    next_btn.click(timeout=5000)
                    try:
                        self.page.wait_for_load_state("domcontentloaded", timeout=4000)
                    except Exception:
                        pass
                    try:
                        self.page.wait_for_timeout(1500)
                    except Exception:
                        pass
                    continue
                except Exception:
                    pass

            # Fallback submit button detection
            fallback_submit = self.detect_submit_button()
            if fallback_submit is not None:
                sub_res = self.submit_application(package)
                if sub_res.status == "submitted":
                    sub_res.filled_fields = all_filled
                    return sub_res

            break

        # Final verification
        if self.detect_success() or self.inspect_page_state().state == BrowserPageState.APPLICATION_COMPLETE:
            return ApplicationExecutionResult(
                status="submitted",
                url=self.page.url,
                filled_fields=all_filled,
                message="Application successfully submitted.",
            )

        return ApplicationExecutionResult(
            status="filled" if all_filled else "blocked",
            url=self.page.url,
            filled_fields=all_filled,
            message=f"Application form filled ({len(all_filled)} fields).",
        )

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def close(self) -> None:
        if self.page is not None:
            try:
                self.page.close()
            except Exception:
                pass

        if self.context is not None:
            try:
                self.context.close()
            except Exception:
                pass

        if self.browser is not None:
            try:
                self.browser.close()
            except Exception:
                pass

        if self.playwright is not None:
            try:
                self.playwright.stop()
            except Exception:
                pass

        self.page = None
        self.context = None
        self.browser = None
        self.playwright = None
