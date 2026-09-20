from __future__ import annotations

import time
from threading import Lock
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.models.job import Job
from app.services.base_discovery import JobSource


class HTTPJobSource(JobSource):
    """
    High-performance JSON HTTP job source.

    Features:
    - Persistent HTTP connection
    - Connection pooling
    - Retry with exponential backoff
    - Configurable timeout
    - Optional in-memory TTL cache
    - Response normalization
    - Invalid-record protection
    - Source-level timing information
    """

    _cache: dict[str, tuple[float, Any]] = {}
    _cache_lock = Lock()

    def __init__(
        self,
        url: str,
        source_name: str = "company_site",
        timeout: float = 10.0,
        headers: dict[str, str] | None = None,
        cache_ttl: float = 30.0,
        pool_connections: int = 10,
        pool_maxsize: int = 20,
    ):
        self.url = url
        self.source_name = source_name
        self.timeout = timeout
        self.cache_ttl = max(0.0, cache_ttl)

        self.headers = headers or {
            "Accept": "application/json",
            "User-Agent": "AI-Job-Agent/1.0",
        }

        # --------------------------------------------------------------
        # Persistent HTTP session
        # --------------------------------------------------------------

        self.session = requests.Session()

        retry = Retry(
            total=2,
            connect=2,
            read=2,
            status=2,
            backoff_factor=0.25,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({"GET"}),
            raise_on_status=False,
        )

        adapter = HTTPAdapter(
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            max_retries=retry,
        )

        self.session.mount(
            "http://",
            adapter,
        )

        self.session.mount(
            "https://",
            adapter,
        )

    # ------------------------------------------------------------------
    # Cache
    # ------------------------------------------------------------------

    def _get_cached_payload(self) -> Any | None:
        if self.cache_ttl <= 0:
            return None

        now = time.monotonic()

        with self._cache_lock:
            cached = self._cache.get(self.url)

            if cached is None:
                return None

            created_at, payload = cached

            if now - created_at >= self.cache_ttl:
                self._cache.pop(self.url, None)
                return None

            return payload

    def _set_cached_payload(
        self,
        payload: Any,
    ) -> None:
        if self.cache_ttl <= 0:
            return

        with self._cache_lock:
            self._cache[self.url] = (
                time.monotonic(),
                payload,
            )

    # ------------------------------------------------------------------
    # HTTP fetch
    # ------------------------------------------------------------------

    def _fetch_payload(self) -> Any:
        cached = self._get_cached_payload()

        if cached is not None:
            return cached

        response = self.session.get(
            self.url,
            headers=self.headers,
            timeout=self.timeout,
        )

        response.raise_for_status()

        payload = response.json()

        self._set_cached_payload(payload)

        return payload

    # ------------------------------------------------------------------
    # JSON normalization
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_records(
        payload: Any,
    ) -> list[dict[str, Any]]:

        if isinstance(payload, list):
            return [
                record
                for record in payload
                if isinstance(record, dict)
            ]

        if isinstance(payload, dict):
            records = payload.get(
                "jobs",
                [],
            )

            if isinstance(records, list):
                return [
                    record
                    for record in records
                    if isinstance(record, dict)
                ]

        raise ValueError(
            "Job source response must be a JSON list "
            "or an object containing a 'jobs' list."
        )

    # ------------------------------------------------------------------
    # Record normalization
    # ------------------------------------------------------------------

    def _normalize_record(
        self,
        record: dict[str, Any],
    ) -> Job | None:

        title = str(
            record.get("title", "")
        ).strip()

        company = str(
            record.get("company", "")
        ).strip()

        location = str(
            record.get("location", "")
        ).strip()

        url = str(
            record.get("url", "")
        ).strip()

        if not title or not company or not url:
            return None

        description = str(
            record.get(
                "description",
                "",
            )
        )

        experience = record.get(
            "experience_years"
        )

        salary = record.get(
            "salary"
        )

        return Job(
            title=title,
            company=company,
            location=location,
            url=url,
            description=description,
            experience_years=experience,
            salary=salary,
            source=self.source_name,
        )

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def search(self) -> list[Job]:

        started = time.perf_counter()

        payload = self._fetch_payload()

        records = self._extract_records(
            payload
        )

        jobs: list[Job] = []

        append = jobs.append
        normalize = self._normalize_record

        for record in records:
            job = normalize(record)

            if job is not None:
                append(job)

        elapsed = (
            time.perf_counter()
            - started
        )

        print(
            f"[HTTP] {self.source_name}: "
            f"{len(jobs)} jobs "
            f"in {elapsed:.4f}s"
        )

        return jobs

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def close(self) -> None:
        self.session.close()
