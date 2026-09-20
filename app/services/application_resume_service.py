from __future__ import annotations

from app.agents.application_preparer import prepare_application
from app.models.application_execution_result import ApplicationExecutionResult
from app.models.job import Job
from app.services.application_human_input import merge_human_input
from app.services.application_resume_validator import validate_resume_input
from app.services.application_state_mapper import map_browser_state
from app.models.application_workflow_state import ApplicationWorkflowState


class ApplicationResumeService:
    """
    Human-controlled resume/refill service.

    Responsibilities:
    1. Prepare the original application package.
    2. Merge explicitly supplied human input.
    3. Validate required fields.
    4. Open the application URL in the browser.
    5. Inspect the browser page.
    6. Refuse to continue when login/CAPTCHA/human verification is needed.
    7. Fill only fields supported by the browser/site adapter.
    8. Re-inspect the page.
    9. Return ready_for_submission only when required fields are satisfied.

    IMPORTANT:
    This service NEVER submits the application.
    Final submission remains behind the existing human confirmation gate.
    """

    def __init__(self, executor):
        self.executor = executor

    def _result(
        self,
        status: str,
        message: str,
        **extra,
    ) -> dict:
        result = {
            "status": status,
            "message": message,
            "requires_human_confirmation": True,
        }

        result.update(extra)
        return result

    def _get_page_state(self):
        """
        Obtain normalized browser workflow state.

        BrowserExecutor already exposes get_application_workflow_state().
        The fallback keeps this service compatible with simpler test executors.
        """
        if hasattr(self.executor, "get_application_workflow_state"):
            return self.executor.get_application_workflow_state()

        if hasattr(self.executor, "inspect_application_state"):
            inspection = self.executor.inspect_application_state()

            if hasattr(inspection, "state"):
                return map_browser_state(inspection.state)

            if isinstance(inspection, dict):
                state = inspection.get("state")
                return map_browser_state(state)

        return None

    def resume(
        self,
        job,
        human_input=None,
    ):
        human_input = human_input or {}

        if job.application_status != "application_started":
            return self._result(
                status="invalid_state",
                message=(
                    "Application is not waiting for "
                    "human input."
                ),
                job=job,
            )

        package = prepare_application(job)

        missing_before = validate_resume_input(
            package,
            {},
        )

        updated_package = merge_human_input(
            package,
            human_input,
        )

        missing_after = validate_resume_input(
            updated_package,
            human_input,
        )

        # -------------------------------------------------
        # If required candidate information is still
        # missing, we still continue to the browser.
        #
        # Safe fields should be filled automatically.
        # Only the missing/unsafe fields should require
        # human input.
        # -------------------------------------------------

        open_result = self.executor.open_application(
            job.url
        )

        if open_result.status not in {
            "opened",
        }:
            return self._result(
                status="failed",
                message=(
                    "Unable to open the application page."
                ),
                job=job,
                application=updated_package,
                missing_before=missing_before,
                missing_after=missing_after,
            )

        workflow_state = self._get_page_state()

        if workflow_state == ApplicationWorkflowState.NEEDS_LOGIN:
            return self._result(
                status="needs_login",
                message=(
                    "Login is required before continuing."
                ),
                job=job,
                application=updated_package,
                missing_before=missing_before,
                missing_after=missing_after,
            )

        if (
            workflow_state
            == ApplicationWorkflowState.NEEDS_HUMAN_VERIFICATION
        ):
            return self._result(
                status="needs_human_verification",
                message=(
                    "Human verification is required "
                    "before continuing."
                ),
                job=job,
                application=updated_package,
                missing_before=missing_before,
                missing_after=missing_after,
            )

        if (
            workflow_state
            == ApplicationWorkflowState.APPLICATION_COMPLETE
        ):
            return self._result(
                status="application_complete",
                message=(
                    "The application page indicates "
                    "completion."
                ),
                job=job,
                application=updated_package,
                missing_before=missing_before,
                missing_after=missing_after,
            )

        if workflow_state != ApplicationWorkflowState.READY_TO_FILL:
            return self._result(
                status="needs_human_input",
                message=(
                    "The browser page needs human "
                    "inspection before filling."
                ),
                job=job,
                application=updated_package,
                missing_before=missing_before,
                missing_after=missing_after,
            )

        # -------------------------------------------------
        # Build safe fill plan
        # -------------------------------------------------

        fill_plan = self.executor.build_fill_plan(
            updated_package
        )

        required_fields_needing_input = []

        for item in fill_plan:
            if not item.get("required"):
                continue

            if item.get("action") != "fill":
                field_name = (
                    item.get("mapped_name")
                    or item.get("field", {}).get("name")
                    or item.get("field", {}).get("id")
                )

                if field_name:
                    required_fields_needing_input.append(
                        field_name
                    )

        # Remove duplicates while preserving order.
        required_fields_needing_input = list(
            dict.fromkeys(
                required_fields_needing_input
            )
        )

        # -------------------------------------------------
        # IMPORTANT:
        # Do NOT return early here.
        #
        # Even when phone or another required field needs
        # human input, safe fields must still be filled.
        # -------------------------------------------------

        fill_result = self.executor.fill_application(
            updated_package
        )

        if fill_result.status != "filled":
            return self._result(
                status="failed",
                message=(
                    "Browser application filling failed."
                ),
                job=job,
                application=updated_package,
                fill_plan=fill_plan,
                missing_before=missing_before,
                missing_after=missing_after,
                required_fields_needing_input=(
                    required_fields_needing_input
                ),
            )

        # Merge fields reported directly by the browser
        # executor.
        for field_name in (
            fill_result.required_fields_needing_input
        ):
            if field_name:
                required_fields_needing_input.append(
                    field_name
                )

        required_fields_needing_input = list(
            dict.fromkeys(
                required_fields_needing_input
            )
        )

        # -------------------------------------------------
        # Human input still required
        # -------------------------------------------------

        if (
            required_fields_needing_input
            or missing_after
        ):
            combined_missing = list(
                dict.fromkeys(
                    required_fields_needing_input
                    + missing_after
                )
            )

            return self._result(
                status="needs_human_input",
                message=(
                    "Safe fields were filled, but the "
                    "browser form still contains required "
                    "fields that need human input."
                ),
                job=job,
                application=updated_package,
                fill_plan=fill_plan,
                filled_fields=(
                    fill_result.filled_fields
                ),
                skipped_fields=(
                    fill_result.skipped_fields
                ),
                required_fields_needing_input=(
                    combined_missing
                ),
                missing_before=missing_before,
                missing_after=missing_after,
            )

        # -------------------------------------------------
        # Everything safe and required is filled.
        # Submission remains a separate human-confirmed
        # step.
        # -------------------------------------------------

        return self._result(
            status="ready_for_submission",
            message=(
                "Application fields were filled safely. "
                "Submission requires explicit human "
                "confirmation."
            ),
            job=job,
            application=updated_package,
            fill_plan=fill_plan,
            filled_fields=(
                fill_result.filled_fields
            ),
            skipped_fields=(
                fill_result.skipped_fields
            ),
            required_fields_needing_input=[],
            missing_before=missing_before,
            missing_after=missing_after,
        )

    def close(self) -> None:
        """
        Close the browser executor.
        """
        if hasattr(self.executor, "close"):
            self.executor.close()
