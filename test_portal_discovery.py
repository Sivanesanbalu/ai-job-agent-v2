from app.services.portal_job_discovery import (
    discover_real_jobs,
    portal_results_to_jobs,
)


def main():
    print("=" * 70)
    print("REAL PORTAL DISCOVERY TEST")
    print("=" * 70)

    results = discover_real_jobs(
        max_queries=12,
        headless=False,
    )

    print("\n" + "=" * 70)
    print(
        f"PORTAL RESULTS: {len(results)}"
    )
    print("=" * 70)

    for index, result in enumerate(
        results[:30],
        1,
    ):
        print(
            f"\n[{index}] "
            f"{result.title}"
        )
        print(
            f"Company : {result.company}"
        )
        print(
            f"Location: {result.location}"
        )
        print(
            f"Source  : {result.source}"
        )
        print(
            f"URL     : {result.url}"
        )

    jobs = portal_results_to_jobs(
        results
    )

    print("\n" + "=" * 70)
    print(
        f"NORMALIZED JOB OBJECTS: {len(jobs)}"
    )
    print("=" * 70)

    for job in jobs[:10]:
        print(
            f"{job.source:10} | "
            f"{job.title[:60]:60} | "
            f"{job.url}"
        )

    print("\n" + "=" * 70)
    print("PORTAL DISCOVERY TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
