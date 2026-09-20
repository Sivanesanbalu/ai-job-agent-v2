from app.config import RESUME_PATH
from app.intelligence.resume_intelligence import (
    ResumeIntelligence,
)
from app.services.browser_job_discovery import (
    BrowserJobDiscovery,
)
from app.services.job_page_extractor import (
    extract_job_pages,
)


def main():
    print("=" * 70)
    print("AI JOB AGENT — REAL ONLINE DISCOVERY TEST")
    print("=" * 70)

    resume = ResumeIntelligence(
        RESUME_PATH
    )

    profile = resume.build_profile()

    print(
        f"\nCandidate: {profile['name']}"
    )

    print(
        f"Resume experience: "
        f"{profile['experience_years']}"
    )

    print(
        f"Resume skills: "
        f"{len(profile['skills'])}"
    )

    print("\nStarting browser discovery...")

    discovery = BrowserJobDiscovery(
        headless=False
    )

    try:
        raw_results = discovery.discover(
            max_queries=20
        )
    finally:
        discovery.close()

    print(
        f"\nRaw online results: "
        f"{len(raw_results)}"
    )

    for result in raw_results[:20]:
        print(
            f"\n[{result.source}] "
            f"{result.title}"
        )
        print(
            f"URL: {result.url}"
        )

    urls = [
        result.url
        for result in raw_results[:10]
    ]

    if not urls:
        print(
            "\nNo public job URLs were found."
        )
        print(
            "This means the search provider returned "
            "no usable public job links or presented "
            "a security challenge."
        )
        return

    print(
        "\nExtracting actual job pages..."
    )

    jobs = extract_job_pages(
        urls,
        headless=False,
    )

    print("\n" + "=" * 70)
    print(
        f"ACTUAL JOB PAGES EXTRACTED: "
        f"{len(jobs)}"
    )
    print("=" * 70)

    for index, job in enumerate(
        jobs,
        1,
    ):
        print(
            f"\n[{index}] {job.title}"
        )
        print(
            f"Company : {job.company}"
        )
        print(
            f"Location: {job.location}"
        )
        print(
            f"Salary  : {job.salary}"
        )
        print(
            f"Exp     : {job.experience_years}"
        )
        print(
            f"Source  : {job.source}"
        )
        print(
            f"URL     : {job.url}"
        )

    print("\n" + "=" * 70)
    print("REAL DISCOVERY TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
