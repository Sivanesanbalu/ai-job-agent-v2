from __future__ import annotations

from app.services.demo_source import DemoJobSource
from app.services.http_job_source import HTTPJobSource
from app.services.source_registry import SourceRegistry


def create_source_registry(
    include_demo: bool = True,
    http_sources: list[dict] | None = None,
) -> SourceRegistry:
    """
    Build the complete job-source registry.

    Example:

        create_source_registry(
            include_demo=False,
            http_sources=[
                {
                    "url": "https://example.com/jobs",
                    "source_name": "company_site",
                    "timeout": 5.0,
                    "cache_ttl": 30.0,
                    "pool_connections": 10,
                    "pool_maxsize": 20,
                }
            ],
        )
    """

    registry = SourceRegistry()

    # --------------------------------------------------------------
    # Demo source
    # --------------------------------------------------------------

    if include_demo:
        registry.register(
            DemoJobSource()
        )

    # --------------------------------------------------------------
    # HTTP sources
    # --------------------------------------------------------------

    for config in http_sources or []:

        if not isinstance(config, dict):
            continue

        url = str(
            config.get("url", "")
        ).strip()

        if not url:
            continue

        source = HTTPJobSource(
            url=url,
            source_name=config.get(
                "source_name",
                "company_site",
            ),
            timeout=float(
                config.get(
                    "timeout",
                    10.0,
                )
            ),
            headers=config.get(
                "headers"
            ),
            cache_ttl=float(
                config.get(
                    "cache_ttl",
                    30.0,
                )
            ),
            pool_connections=int(
                config.get(
                    "pool_connections",
                    10,
                )
            ),
            pool_maxsize=int(
                config.get(
                    "pool_maxsize",
                    20,
                )
            ),
        )

        registry.register(source)

    return registry
