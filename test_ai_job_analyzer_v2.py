from app.intelligence.ai_job_analyzer import AIJobAnalyzer
from app.models.job import Job
from app.models.job_source import JobSourceName


analyzer = AIJobAnalyzer()

print("=" * 70)
print("RESUME-DRIVEN AI MATCHER TEST")
print("=" * 70)

print("Model:", analyzer.model)
print("Ollama available:", analyzer.is_available())


jobs = [

    Job(
        title="Junior AI Engineer",
        company="Test AI Company",
        location="Coimbatore, Tamil Nadu, India",
        url="https://example.com/junior-ai",
        description="""
        We are looking for a Junior AI Engineer / Generative AI
        Engineer to build LLM-powered applications.

        Responsibilities:
        - Build RAG pipelines.
        - Develop AI agents.
        - Work with Python and LangChain.
        - Build APIs using FastAPI.
        - Work with embeddings and vector databases.
        - Integrate Hugging Face models.
        - Collaborate with the engineering team.

        Requirements:
        - Bachelor's degree in AI, Computer Science or related field.
        - 0-1 years experience.
        - Strong Python skills.
        - Knowledge of Generative AI and LLMs.
        """,
        experience_years=0,
        salary="₹6 LPA",
        source=JobSourceName.LINKEDIN,
    ),

    Job(
        title="Senior Generative AI Engineer",
        company="Test Enterprise",
        location="Coimbatore, Tamil Nadu, India",
        url="https://example.com/senior-ai",
        description="""
        We are hiring a Senior Generative AI Engineer.

        Requirements:
        - 5+ years of professional AI/ML experience.
        - 5+ years building production LLM systems.
        - Experience leading engineering teams.
        - Strong cloud architecture experience.
        - Kubernetes and distributed systems expertise.
        """,
        experience_years=5,
        salary="₹20 LPA",
        source=JobSourceName.LINKEDIN,
    ),

    Job(
        title="Administrative Operations Specialist",
        company="Test Company",
        location="Coimbatore, Tamil Nadu, India",
        url="https://example.com/admin",
        description="""
        We are looking for an administrative operations specialist.

        Responsibilities:
        - Manage office documentation.
        - Coordinate meetings.
        - Maintain records.
        - Handle administrative communication.
        - Manage spreadsheets and office operations.

        Requirements:
        - Strong organizational skills.
        - Microsoft Office.
        - Administrative experience.
        """,
        experience_years=0,
        salary="₹6 LPA",
        source=JobSourceName.LINKEDIN,
    ),

    Job(
        title="AI Automation Developer",
        company="Test Automation Company",
        location="Chennai, Tamil Nadu, India",
        url="https://example.com/automation",
        description="""
        Build intelligent automation systems using Python and AI.

        Responsibilities:
        - Develop AI-powered automation workflows.
        - Build LLM agents.
        - Integrate APIs.
        - Use Python and FastAPI.
        - Implement RAG and embeddings.
        - Build internal AI tools.

        Requirements:
        - Bachelor's degree in AI, CS or related field.
        - 0-2 years experience.
        - Python.
        - LLMs.
        - AI agents.
        """,
        experience_years=0,
        salary=None,
        source=JobSourceName.LINKEDIN,
    ),
]


for index, job in enumerate(
    jobs,
    start=1,
):

    print("")
    print("-" * 70)
    print(f"[{index}] {job.title}")
    print("-" * 70)

    decision = analyzer.analyze(
        job
    )

    print("Apply          :", decision.apply)
    print("Score          :", decision.score)
    print("Relevance      :", decision.relevance)
    print(
        "Matched skills :",
        decision.matched_skills,
    )
    print(
        "Missing skills :",
        decision.missing_skills,
    )
    print(
        "Experience     :",
        decision.experience_match,
    )
    print(
        "Location       :",
        decision.location_match,
    )
    print(
        "Salary         :",
        decision.salary_match,
    )
    print(
        "Reason         :",
        decision.reason,
    )
    print(
        "Model          :",
        decision.model,
    )

print("")
print("=" * 70)
print("TEST COMPLETE")
print("=" * 70)
