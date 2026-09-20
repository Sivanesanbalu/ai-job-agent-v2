from concurrent.futures import ThreadPoolExecutor, as_completed

from app.models.job import Job
from app.services.base_discovery import JobSource
from app.services.source_registry import SourceRegistry


class DiscoveryManager:
    """Discover jobs from registered sources concurrently."""

    def __init__(
        self,
        registry: SourceRegistry,
        max_workers: int = 6,
    ):
        self.registry = registry
        self.max_workers = max(
            1,
            min(max_workers, 12),
        )

    def _search_source(
        self,
        source: JobSource,
    ) -> list[Job]:
        """Search one source safely."""
        try:
            return source.search()
        except Exception as error:
            print(
                f"Source failed: "
                f"{source.__class__.__name__}: {error}"
            )
            return []

    def discover(self) -> list[Job]:
        """Search all sources concurrently."""

        sources = self.registry.get_sources()

        if not sources:
            return []

        all_jobs: list[Job] = []

        # One source does not need thread overhead.
        if len(sources) == 1:
            return self._remove_duplicates(
                self._search_source(sources[0])
            )

        workers = min(
            self.max_workers,
            len(sources),
        )

        with ThreadPoolExecutor(
            max_workers=workers
        ) as executor:

            futures = {
                executor.submit(
                    self._search_source,
                    source,
                ): source
                for source in sources
            }

            for future in as_completed(futures):
                try:
                    jobs = future.result()
                    all_jobs.extend(jobs)
                except Exception as error:
                    source = futures[future]
                    print(
                        f"Source failed: "
                        f"{source.__class__.__name__}: "
                        f"{error}"
                    )

        return self._remove_duplicates(all_jobs)

    def _remove_duplicates(
        self,
        jobs: list[Job],
    ) -> list[Job]:
        """Remove duplicate jobs by URL."""

        unique_jobs: list[Job] = []
        seen_urls: set[str] = set()

        for job in jobs:
            normalized_url = job.url.strip()

            if not normalized_url:
                continue

            if normalized_url in seen_urls:
                continue

            seen_urls.add(normalized_url)
            unique_jobs.append(job)

        return unique_jobs
