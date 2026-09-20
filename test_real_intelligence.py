from app.config import RESUME_PATH
from app.intelligence.resume_intelligence import (
    ResumeIntelligence,
)
from app.intelligence.job_intelligence import (
    ResumeJobAnalyzer,
)
from app.intelligence.job_search_profile import (
    build_search_profile,
    build_search_queries,
)


def main():
    print("=" * 70)
    print("AI JOB AGENT — RESUME INTELLIGENCE")
    print("=" * 70)

    resume = ResumeIntelligence(
        RESUME_PATH
    )

    profile = resume.build_profile()

    output = resume.save_profile(
        profile
    )

    print(
        f"\nResume: {RESUME_PATH}"
    )
    print(
        f"Profile saved: {output}"
    )

    print(
        f"\nName: {profile['name']}"
    )

    print(
        f"Email: {profile['email']}"
    )

    print(
        f"Experience: "
        f"{profile['experience_years']}"
    )

    print("\nResume Roles:")
    for role in profile["roles"]:
        print(
            f"  ✓ {role}"
        )

    print("\nResume Skills:")
    for skill in profile["skills"]:
        print(
            f"  ✓ {skill}"
        )

    search_profile = (
        build_search_profile(
            profile
        )
    )

    queries = build_search_queries(
        search_profile
    )

    print(
        f"\nGenerated search queries: "
        f"{len(queries)}"
    )

    print("\nExample queries:")

    for query in queries[:15]:
        print(
            f"  → {query}"
        )

    print("\n" + "=" * 70)
    print("RESUME INTELLIGENCE: PASS")
    print("=" * 70)


if __name__ == "__main__":
    main()
