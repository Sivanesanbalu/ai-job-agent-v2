from app.intelligence.job_intelligence import JobIntelligence
from app.intelligence.resume_intelligence import ResumeIntelligence
from app.config import RESUME_PATH
from app.models.job import Job


def main():
    print("=" * 70)
    print("JOB INTELLIGENCE TEST")
    print("=" * 70)

    resume_engine = ResumeIntelligence(RESUME_PATH)
    profile = resume_engine.build_profile()

    engine = JobIntelligence(profile)

    jobs = [
        Job(
            title="Generative AI Engineer",
            company="Real AI Company",
            location="Coimbatore",
            url="https://example.com/real-test-1",
            description=(
                "Build LLM and RAG applications using Python, "
                "LangChain, AI agents, FastAPI and embeddings. "
                "0-1 years experience."
            ),
            experience_years=0,
            salary="₹6-8 LPA",
            source="test",
        ),
        Job(
            title="Senior Java Developer",
            company="Unrelated Company",
            location="Mumbai",
            url="https://example.com/real-test-2",
            description=(
                "Java Spring Boot backend development. "
                "5-8 years experience."
            ),
            experience_years=5,
            salary="₹12-18 LPA",
            source="test",
        ),
    ]

    results = engine.analyze_many(jobs)

    for result in results:
        print()
        print(f"Job       : {result.title}")
        print(f"Company   : {result.company}")
        print(f"Location  : {result.location}")
        print(f"Score     : {result.final_score}")
        print(f"Decision  : {result.recommendation}")
        print(f"Roles     : {result.detected_roles}")
        print(f"Skills    : {result.detected_skills}")
        print(f"Salary    : {result.minimum_salary_lpa}")
        print(f"Experience: {result.minimum_experience_years}")
        print("Reasons:")
        for reason in result.reasons:
            print(f"  ✓ {reason}")

    assert results[0].recommendation == "APPLY"
    assert results[-1].recommendation == "SKIP"

    print("\n" + "=" * 70)
    print("JOB INTELLIGENCE: PASS")
    print("=" * 70)


if __name__ == "__main__":
    main()
