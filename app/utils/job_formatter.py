from app.models.job import Job


def format_job(job: Job) -> dict:
    return {
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "source": job.source.value,
        "match_score": job.match_score,
        "application_status": job.application_status,
        "url": job.url,
    }
