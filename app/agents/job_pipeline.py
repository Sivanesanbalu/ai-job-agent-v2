from __future__ import annotations

from app.agents.application_manager import transition_application_status
from app.agents.fast_candidate_selector import select_top_jobs
from app.agents.job_filter import filter_jobs
from app.config import MAX_APPLICATIONS_PER_DAY
from app.models.job import Job
from app.services.discovery_manager import DiscoveryManager
from app.services.job_repository import save_jobs


class JobPipeline:
    """
    Job discovery and candidate-selection pipeline.

    Flow:

        discover
          ↓
        filter
          ↓
        score
          ↓
        ALL matching candidates
          ↓
        mark application_candidate
          ↓
        bulk database
    """

    __slots__ = (
        "discovery_manager",
        "candidate_limit",
        "verbose",
    )

    def __init__(
        self,
        discovery_manager: DiscoveryManager,
        candidate_limit: int | None = None,
        verbose: bool = False,
    ):
        self.discovery_manager = discovery_manager

        # None means unlimited.
        if candidate_limit is None:
            self.candidate_limit = MAX_APPLICATIONS_PER_DAY
        else:
            self.candidate_limit = max(
                1,
                candidate_limit,
            )

        self.verbose = verbose

    def run(self) -> list[Job]:

        # --------------------------------------------------------------
        # 1. Discovery
        # --------------------------------------------------------------

        jobs = self.discovery_manager.discover()

        discovered_count = len(jobs)

        if self.verbose:
            print(
                f"Discovered: {discovered_count}"
            )

        if not jobs:
            return []

        # --------------------------------------------------------------
        # 2. Cheap filtering
        # --------------------------------------------------------------

        filtered_jobs = filter_jobs(jobs)

        filtered_count = len(filtered_jobs)

        if self.verbose:
            print(
                f"After filtering: {filtered_count}"
            )

        if not filtered_jobs:
            return []

        # --------------------------------------------------------------
        # 3. Fast scoring
        # --------------------------------------------------------------

        candidates = select_top_jobs(
            filtered_jobs,
            limit=self.candidate_limit,
        )

        # --------------------------------------------------------------
        # 4. Persist filtered jobs
        # --------------------------------------------------------------

        save_jobs(filtered_jobs)

        # --------------------------------------------------------------
        # 5. Mark selected jobs as application candidates
        # --------------------------------------------------------------

        application_candidates: list[Job] = []

        for job in candidates:
            try:
                transition_application_status(
                    job.url,
                    "application_candidate",
                    "Job selected automatically by match pipeline",
                )

                job.application_status = "application_candidate"
                application_candidates.append(job)

            except ValueError as error:
                # Already processed jobs should not crash the entire
                # discovery run.
                if self.verbose:
                    print(
                        f"Skipping candidate {job.url}: {error}"
                    )

        # --------------------------------------------------------------
        # 6. Production summary
        # --------------------------------------------------------------

        if self.verbose:
            print(
                f"Saved to database: "
                f"{filtered_count}"
            )

            print(
                f"Application candidates: "
                f"{len(application_candidates)}"
            )

        return application_candidates
