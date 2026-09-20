from app.intelligence.ai_job_analyzer import (
    AIJobAnalyzer,
)
from app.models.job import Job


def main():
    print("=" * 70)
    print("AI JOB ANALYZER TEST")
    print("=" * 70)

    analyzer = AIJobAnalyzer()

    print(
        f"Ollama model: "
        f"{analyzer.model or 'NONE'}"
    )

    print(
        f"Ollama available: "
        f"{analyzer.is_available()}"
    )

    jobs = [
        Job(
            title="AI Engineer",
            company="Example AI",
            location="Coimbatore",
            url="https://example.com/ai",
            description=(
                "Build Generative AI applications using "
                "Python, LLMs, RAG, LangChain and AI agents. "
                "0-1 years experience. Salary ₹5-8 LPA."
            ),
            salary="₹5-8 LPA",
            experience_years=1,
            source="linkedin",
        ),
        Job(
            title="Senior Data Scientist",
            company="Example Corp",
            location="Coimbatore",
            url="https://example.com/senior",
            description=(
                "Lead data science team. "
                "5+ years experience. "
                "Salary ₹15-20 LPA."
            ),
            salary="₹15-20 LPA",
            experience_years=5,
            source="linkedin",
        ),
        Job(
            title="Administrative Assistant",
            company="Example",
            location="Coimbatore",
            url="https://example.com/admin",
            description=(
                "Handle office administration, "
                "scheduling and documentation. "
                "0-1 years. Salary ₹5-6 LPA."
            ),
            salary="₹5-6 LPA",
            experience_years=1,
            source="linkedin",
        ),
    ]

    for job in jobs:
        print(
            "\n" + "-" * 70
        )

        print(
            f"JOB: {job.title}"
        )

        try:
            decision = analyzer.analyze(
                job
            )

            print(
                f"Apply      : {decision.apply}"
            )

            print(
                f"Score      : {decision.score}"
            )

            print(
                f"Relevance  : {decision.relevance}"
            )

            print(
                f"Matched    : "
                f"{decision.matched_skills}"
            )

            print(
                f"Missing    : "
                f"{decision.missing_skills}"
            )

            print(
                f"Reason     : "
                f"{decision.reason}"
            )

            print(
                f"AI Model   : "
                f"{decision.model}"
            )

        except Exception as exc:
            print(
                f"ANALYZER ERROR: {exc}"
            )

    print(
        "\n" + "=" * 70
    )
    print(
        "AI JOB ANALYZER TEST COMPLETE"
    )
    print(
        "=" * 70
    )


if __name__ == "__main__":
    main()
