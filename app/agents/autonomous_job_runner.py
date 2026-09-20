from __future__ import annotations

import sqlite3
from pathlib import Path

from app.agents.application_manager import (
    transition_application_status,
)
from app.agents.application_workflow import (
    run_application_workflow,
)
from app.config import MIN_MATCH_SCORE
from app.intelligence.ai_job_analyzer import (
    AIJobAnalyzer,
)
from app.models.job import Job
from app.services.application_repository import (
    record_application_attempt,
)
from app.services.browser_executor import (
    BrowserExecutor,
)
from app.services.job_browser import JobBrowser
from app.services.job_page_reader import (
    JobPageReader,
)
from app.services.portal_job_discovery import (
    discover_real_jobs,
    portal_results_to_jobs,
)


DB_PATH = Path("jobs.db")


# ============================================================
# DATABASE
# ============================================================

def upsert_job(
    job: Job,
) -> None:
    connection = sqlite3.connect(
        DB_PATH
    )

    try:
        connection.execute(
            """
            INSERT INTO jobs (
                title,
                company,
                location,
                url,
                description,
                experience_years,
                salary,
                source,
                match_score,
                application_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(url) DO UPDATE SET
                title=excluded.title,
                company=excluded.company,
                location=excluded.location,
                description=excluded.description,
                experience_years=excluded.experience_years,
                salary=excluded.salary,
                source=excluded.source,
                match_score=excluded.match_score
            """,
            (
                job.title,
                job.company,
                job.location,
                job.url,
                job.description,
                job.experience_years,
                job.salary,
                str(job.source),
                job.match_score,
                job.application_status,
            ),
        )

        connection.commit()

    finally:
        connection.close()


def already_processed(
    url: str,
) -> bool:
    connection = sqlite3.connect(
        DB_PATH
    )

    try:
        row = connection.execute(
            """
            SELECT application_status
            FROM jobs
            WHERE url = ?
            """,
            (url,),
        ).fetchone()

        if not row:
            return False

        return row[0] in {
            "submitted",
            "application_started",
            "ready_for_submission",
            "approved_for_application",
            "application_candidate",
        }

    finally:
        connection.close()


# ============================================================
# AUTH / SECURITY RECORDING
# ============================================================

def record_verification_required(
    job: Job,
    reason: str,
) -> None:
    """
    Record authentication/security blocking without attempting
    to bypass it.

    The job is NOT sent to the AI matcher when the page is blocked.
    """

    message = (
        reason.strip()
        or "Authentication or security verification required"
    )

    print(
        f"  VERIFICATION REQUIRED: {message}"
    )

    try:
        record_application_attempt(
            job.url,
            "verification_required",
            message,
        )
    except Exception as exc:
        print(
            f"  WARNING: Could not record verification attempt: {exc}"
        )

    try:
        connection = sqlite3.connect(
            DB_PATH
        )

        try:
            connection.execute(
                """
                UPDATE jobs
                SET application_status = ?
                WHERE url = ?
                """,
                (
                    "verification_required",
                    job.url,
                ),
            )

            connection.commit()

        finally:
            connection.close()

    except Exception as exc:
        print(
            f"  WARNING: Could not update verification status: {exc}"
        )


def record_invalid_job_page(
    job: Job,
    reason: str,
) -> None:
    """
    Record pages that are not usable job-detail pages.
    """

    message = (
        reason.strip()
        or "Invalid or incomplete job detail page"
    )

    print(
        f"  INVALID JOB PAGE: {message}"
    )

    try:
        record_application_attempt(
            job.url,
            "invalid_job_page",
            message,
        )
    except Exception as exc:
        print(
            f"  WARNING: Could not record invalid page: {exc}"
        )


# ============================================================
# JOB ENRICHMENT
# ============================================================

def enrich_job(
    job: Job,
    job_browser: JobBrowser,
):
    """
    Open the real job URL in a dedicated browser page and
    read it with JobPageReader.

    Returns:
        (Job, JobPageReadResult)
    """

    page = job_browser.open(
        job.url
    )

    page_reader = JobPageReader(
        page
    )

    page_result = page_reader.read()

    # Only copy extracted fields when present.
    if page_result.title:
        job.title = page_result.title

    if page_result.company:
        job.company = page_result.company

    if page_result.location:
        job.location = page_result.location

    if page_result.description:
        job.description = page_result.description

    if page_result.salary:
        job.salary = page_result.salary

    return job, page_result


# ============================================================
# MAIN AUTONOMOUS RUN
# ============================================================

def run(
    max_discovery_queries: int = 12,
    max_jobs_to_analyze: int = 30,
    auto_apply: bool = True,
):
    print("=" * 70)
    print("AI JOB AGENT — AUTONOMOUS ONLINE RUN")
    print("=" * 70)

    print(
        "\nPHASE 1: DISCOVERY"
    )

    discovered = discover_real_jobs(
        max_queries=max_discovery_queries,
        headless=False,
    )

    jobs = portal_results_to_jobs(
        discovered
    )

    print(
        f"\nDiscovered URLs: {len(jobs)}"
    )

    # --------------------------------------------------------
    # Deduplicate URLs
    # --------------------------------------------------------

    unique = {}

    for job in jobs:
        if job.url:
            unique[job.url] = job

    jobs = list(
        unique.values()
    )

    jobs = jobs[
        :max_jobs_to_analyze
    ]

    print(
        f"Jobs selected for deep analysis: "
        f"{len(jobs)}"
    )

    # --------------------------------------------------------
    # AI analyzer
    # --------------------------------------------------------

    analyzer = AIJobAnalyzer()

    print(
        f"AI model: "
        f"{analyzer.model or 'NONE'}"
    )

    if not analyzer.is_available():
        raise RuntimeError(
            "\nOllama is not available.\n"
            "Start Ollama and install a local model first.\n"
            "Example:\n"
            "  ollama serve\n"
            "  ollama list\n"
        )

    # --------------------------------------------------------
    # Browser reader/executor
    # --------------------------------------------------------

    job_browser = JobBrowser(
        headless=False
    )

    executor = BrowserExecutor()

    applied = []
    rejected = []
    blocked = []
    failed = []
    verification_required = []
    invalid_pages = []

    try:
        job_browser.start()

        print(
            "\nPHASE 2: JOB PAGE ENRICHMENT + AI MATCHING"
        )

        for index, job in enumerate(
            jobs,
            1,
        ):
            print(
                "\n" + "-" * 70
            )

            print(
                f"[{index}/{len(jobs)}] "
                f"{job.title}"
            )

            # ------------------------------------------------
            # Existing processed-job protection
            # ------------------------------------------------

            if already_processed(
                job.url
            ):
                print(
                    "  SKIP: already processed"
                )
                continue

            try:
                # ============================================
                # OPEN + READ REAL JOB PAGE
                # ============================================

                job, page = enrich_job(
                    job,
                    job_browser,
                )

                # ============================================
                # AUTH / SECURITY GATE
                # ============================================

                if (
                    getattr(
                        page,
                        "blocked",
                        False,
                    )
                    or getattr(
                        page,
                        "verification_required",
                        False,
                    )
                ):
                    reason = getattr(
                        page,
                        "reason",
                        "",
                    )

                    record_verification_required(
                        job,
                        reason,
                    )

                    verification_required.append(
                        job
                    )

                    print(
                        "  ACTION: moving to next job"
                    )

                    continue

                # ============================================
                # INVALID PAGE GATE
                # ============================================

                if not getattr(
                    page,
                    "success",
                    False,
                ):
                    reason = getattr(
                        page,
                        "reason",
                        "",
                    )

                    record_invalid_job_page(
                        job,
                        reason,
                    )

                    invalid_pages.append(
                        job
                    )

                    print(
                        "  ACTION: moving to next job"
                    )

                    continue

                # ============================================
                # VALID JOB PAGE
                # ============================================

                print(
                    f"  Title   : {job.title}"
                )

                print(
                    f"  Company : {job.company}"
                )

                print(
                    f"  Location: {job.location}"
                )

                print(
                    f"  Salary  : "
                    f"{job.salary or 'UNKNOWN'}"
                )

                print(
                    f"  Description chars: "
                    f"{len(job.description or '')}"
                )

                # ============================================
                # AI RESUME MATCHING
                # ============================================

                decision = analyzer.analyze(
                    job
                )

                job.match_score = (
                    decision.score
                )

                print(
                    f"  AI score: "
                    f"{decision.score}"
                )

                print(
                    f"  Relevance: "
                    f"{decision.relevance}"
                )

                print(
                    f"  Skills: "
                    f"{', '.join(decision.matched_skills[:8])}"
                )

                print(
                    f"  Decision: "
                    f"{'APPLY' if decision.apply else 'SKIP'}"
                )

                print(
                    f"  Reason: "
                    f"{decision.reason}"
                )

                # Save enriched job + score.
                upsert_job(
                    job
                )

                # ============================================
                # AI REJECTION
                # ============================================

                if (
                    not decision.apply
                    or decision.score < MIN_MATCH_SCORE
                ):
                    rejected.append(
                        job
                    )

                    continue

                # ============================================
                # APPLICATION CANDIDATE
                # ============================================

                transition_application_status(
                    job.url,
                    "application_candidate",
                    (
                        "AI selected job automatically; "
                        f"match score={decision.score}"
                    ),
                )

                job.application_status = (
                    "application_candidate"
                )

                # ============================================
                # TEST MODE
                # ============================================

                if not auto_apply:
                    print(
                        "  AUTO APPLY DISABLED"
                    )

                    continue

                # ============================================
                # AUTOMATIC APPLICATION
                # ============================================

                print(
                    "  STARTING APPLICATION..."
                )

                result = (
                    run_application_workflow(
                        job,
                        executor,
                    )
                )

                status = result.get(
                    "status"
                )

                print(
                    f"  APPLICATION STATUS: "
                    f"{status}"
                )

                # ============================================
                # RESULT CLASSIFICATION
                # ============================================

                if status == "submitted":
                    applied.append(
                        job
                    )

                elif status in {
                    "blocked",
                    "needs_human_input",
                    "verification_required",
                }:
                    blocked.append(
                        job
                    )

                else:
                    failed.append(
                        job
                    )

            except Exception as exc:
                print(
                    f"  ERROR: {exc}"
                )

                failed.append(
                    job
                )

                # IMPORTANT:
                # One job must never terminate the whole run.
                continue

        # ====================================================
        # SUMMARY
        # ====================================================

        print(
            "\n" + "=" * 70
        )

        print(
            "AUTONOMOUS RUN SUMMARY"
        )

        print(
            "=" * 70
        )

        print(
            f"Discovered             : "
            f"{len(discovered)}"
        )

        print(
            f"Deep analyzed          : "
            f"{len(jobs)}"
        )

        print(
            f"AI selected            : "
            f"{len(applied) + len(blocked) + len(failed)}"
        )

        print(
            f"Submitted              : "
            f"{len(applied)}"
        )

        print(
            f"Blocked/application    : "
            f"{len(blocked)}"
        )

        print(
            f"Verification required  : "
            f"{len(verification_required)}"
        )

        print(
            f"Invalid job pages      : "
            f"{len(invalid_pages)}"
        )

        print(
            f"Failed                 : "
            f"{len(failed)}"
        )

        print(
            f"AI rejected            : "
            f"{len(rejected)}"
        )

        print(
            "=" * 70
        )

        # ----------------------------------------------------
        # Submitted
        # ----------------------------------------------------

        if applied:
            print(
                "\nSUBMITTED JOBS:"
            )

            for job in applied:
                print(
                    f"  ✓ {job.title} | "
                    f"{job.company}"
                )

        # ----------------------------------------------------
        # Verification
        # ----------------------------------------------------

        if verification_required:
            print(
                "\nVERIFICATION / LOGIN REQUIRED:"
            )

            for job in verification_required:
                print(
                    f"  ! {job.title} | "
                    f"{job.company}"
                )

                print(
                    f"    {job.url}"
                )

        # ----------------------------------------------------
        # Invalid pages
        # ----------------------------------------------------

        if invalid_pages:
            print(
                "\nINVALID JOB PAGES:"
            )

            for job in invalid_pages:
                print(
                    f"  - {job.title} | "
                    f"{job.company}"
                )

        # ----------------------------------------------------
        # Application blocked
        # ----------------------------------------------------

        if blocked:
            print(
                "\nBLOCKED / HUMAN INPUT REQUIRED:"
            )

            for job in blocked:
                print(
                    f"  ! {job.title} | "
                    f"{job.company}"
                )

        print(
            "\nRUN COMPLETE"
        )

    finally:
        job_browser.close()

        try:
            executor.close()
        except Exception:
            pass


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run(
        max_discovery_queries=3,
        max_jobs_to_analyze=10,
        auto_apply=False,
    )
