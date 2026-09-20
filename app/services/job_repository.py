from app.models.job import Job
from app.services.database import get_connection


def save_job(job: Job) -> None:
    connection = get_connection()

    connection.execute(
        """
        INSERT INTO jobs (
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
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(url) DO UPDATE SET
            title = excluded.title,
            company = excluded.company,
            location = excluded.location,
            description = excluded.description,
            experience_years = excluded.experience_years,
            salary = excluded.salary,
            source = excluded.source,
            match_score = excluded.match_score,
            application_status = excluded.application_status
        """,
        (
            job.title,
            job.company,
            job.location,
            job.url,
            job.description,
            job.experience_years,
            job.salary,
            job.source.value,
            job.match_score,
            job.application_status,
        ),
    )

    connection.commit()
    connection.close()


def update_application_status(url: str, status: str) -> None:
    connection = get_connection()

    connection.execute(
        """
        UPDATE jobs
        SET application_status = ?
        WHERE url = ?
        """,
        (status, url),
    )

    connection.commit()
    connection.close()


def approve_job(url: str) -> None:
    update_application_status(
        url,
        "approved_for_application",
    )


def reject_job(url: str) -> None:
    update_application_status(
        url,
        "rejected_by_user",
    )


def save_jobs(jobs: list[Job]) -> None:
    """Bulk upsert jobs using a single connection and transaction."""

    if not jobs:
        return

    connection = get_connection()

    try:
        connection.executemany(
            """
            INSERT INTO jobs (
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
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(url) DO UPDATE SET
                title = excluded.title,
                company = excluded.company,
                location = excluded.location,
                description = excluded.description,
                experience_years = excluded.experience_years,
                salary = excluded.salary,
                source = excluded.source,
                match_score = excluded.match_score,
                application_status = excluded.application_status
            """,
            [
                (
                    job.title,
                    job.company,
                    job.location,
                    job.url,
                    job.description,
                    job.experience_years,
                    job.salary,
                    job.source.value,
                    job.match_score,
                    job.application_status,
                )
                for job in jobs
            ],
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
