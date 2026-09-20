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
            elements => elements.map(element => ({
                type: element.type || "",
                name: element.name || "",
                id: element.id || "",
                placeholder: element.placeholder || "",
                aria_label: element.getAttribute("aria-label") || "",
                autocomplete: element.getAttribute("autocomplete") || "",
                accept: element.getAttribute("accept") || "",
                value: element.value || "",
                required: element.required || false,
                visible: !!(
                    element.offsetWidth ||
                    element.offsetHeight ||
                    element.getClientRects().length
                )
            }))
            """
        )

        textareas = self.page.locator("textarea").evaluate_all(
            """
            elements => elements.map(element => ({
                name: element.name || "",
                id: element.id || "",
                placeholder: element.placeholder || "",
                aria_label: element.getAttribute("aria-label") || "",
                value: element.value || "",
                required: element.required || false,
                visible: !!(
                    element.offsetWidth ||
                    element.offsetHeight ||
                    element.getClientRects().length
                )
            }))
            """
        )

        selects = self.page.locator("select").evaluate_all(
            """
            elements => elements.map(element => ({
                name: element.name || "",
                id: element.id || "",
                aria_label: element.getAttribute("aria-label") || "",
                value: element.value || "",
                required: element.required || false,
                visible: !!(
                    element.offsetWidth ||
                    element.offsetHeight ||
                    element.getClientRects().length
                ),
                options: Array.from(element.options || []).map(option => ({
                    text: (option.textContent || "").trim(),
                    value: option.value || ""
                }))
            }))
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

    def inspect_page_state(self) -> BrowserPageInspection:
        """Detect the current browser/application page state."""

        if self.page is None:
            raise RuntimeError("Application page is not open.")

        info = self.inspect_application_page()

        visible_inputs = [
            item for item in info["inputs"]
            if item.get("visible", False)
            and item.get("type", "").lower() != "hidden"
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

        has_form = bool(
            visible_inputs
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

        if any(
            signal in page_text
            for signal in self.SECURITY_SIGNALS
        ):
            state = BrowserPageState.HUMAN_VERIFICATION_REQUIRED

            for signal in self.SECURITY_SIGNALS:
                if signal in page_text:
                    signals.append(signal)

            requires_human_action = True

        elif any(
            signal in page_text
            for signal in self.SUCCESS_SIGNALS
        ):
            state = BrowserPageState.APPLICATION_COMPLETE

            for signal in self.SUCCESS_SIGNALS:
                if signal in page_text:
                    signals.append(signal)

            requires_human_action = False

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
                )
            )
        ):
            state = BrowserPageState.APPLICATION_FORM
            signals.append("application form signals detected")
            requires_human_action = False

        elif any(
            signal in page_text
            for signal in (
                "sign in",
                "log in",
                "login",
            )
        ):
            state = BrowserPageState.LOGIN_REQUIRED
            signals.append("login required")
            requires_human_action = True

        elif (
            "job" in url
            or "job" in title
            or "career" in url
            or "careers" in url
        ):
            state = BrowserPageState.JOB_PAGE
            signals.append("job page signals detected")
            requires_human_action = False

        else:
            state = BrowserPageState.UNKNOWN
            requires_human_action = True

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

        if field_id:
            return self.page.locator(
                f"#{field_id}"
            ).first

        if field_name:
            return self.page.locator(
                f'[name="{field_name}"]'
            ).first

        raise ValueError(
            "Cannot locate field without id or name."
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
