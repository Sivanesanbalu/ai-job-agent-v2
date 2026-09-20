from app.models.job import Job
from app.services.base_discovery import JobSource


class DemoJobSource(JobSource):

    def search(self) -> list[Job]:
        return [
            Job(
                title="Generative AI Engineer",
                company="Demo AI Company",
                location="Coimbatore",
                url="https://example.com/job/1",
                description=(
                    "Build LLM, RAG and AI agent applications "
                    "using Python and LangChain."
                ),
                experience_years=0.0,
                salary="₹4-6 LPA",
                source="demo",
            ),
            Job(
                title="AI Automation Engineer",
                company="Demo Automation Company",
                location="Chennai",
                url="https://example.com/job/2",
                description=(
                    "Build AI automation workflows using Python, "
                    "LLMs, APIs and AI agents."
                ),
                experience_years=1.0,
                salary="₹5-7 LPA",
                source="demo",
            ),
        ]
