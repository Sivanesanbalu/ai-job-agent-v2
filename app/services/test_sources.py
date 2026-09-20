from app.models.job import Job
from app.services.base_discovery import JobSource


class DuplicateDemoSource(JobSource):

    def search(self) -> list[Job]:
        return [
            Job(
                title="Generative AI Engineer",
                company="Demo AI Company",
                location="Coimbatore",
                url="https://example.com/job/1",
                description="Build LLM and RAG applications.",
                experience_years=0,
                source="duplicate-demo",
            )
        ]
