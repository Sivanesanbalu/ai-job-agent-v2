from app.agents.application_preparer import prepare_application
from app.services.database import get_connection
from app.models.job import Job
from app.models.job_source import JobSourceName


connection = get_connection()

connection.execute(
    """
    INSERT OR IGNORE INTO jobs (title, company, location, url, description, experience_years, salary, source, match_score, application_status)
    VALUES ('AI Engineer', 'DeepTech', 'Bangalore', 'https://example.com/job/1', 'AI Engineer needed', 1.0, '₹10 LPA', 'demo', 85, 'discovered')
    """
)
connection.commit()

row = connection.execute(
    """
    SELECT
        title,
        company,
        location,
        url,
        description,
        experience_years,
        salary,
        source,
        match_score,
        application_status
    FROM jobs
    WHERE url = ?
    """,
    ("https://example.com/job/1",),
).fetchone()

connection.close()


job = Job(
    title=row["title"],
    company=row["company"],
    location=row["location"],
    url=row["url"],
    description=row["description"] or "",
    experience_years=row["experience_years"],
    salary=row["salary"],
    source=JobSourceName(row["source"]),
    match_score=row["match_score"],
    application_status=row["application_status"],
)

application = prepare_application(job)

print("APPLICATION PACKAGE")
print("===================")

for key, value in application.items():
    print(f"{key}: {value}")
