from app.services.database import get_connection


def record_application_attempt(
    job_url: str,
    status: str,
    message: str = "",
) -> None:
    connection = get_connection()

    connection.execute(
        """
        INSERT INTO application_attempts (
            job_url,
            status,
            message
        )
        VALUES (?, ?, ?)
        """,
        (
            job_url,
            status,
            message,
        ),
    )

    connection.commit()
    connection.close()


def get_application_attempts(job_url: str) -> list[dict]:
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            id,
            job_url,
            status,
            message,
            created_at
        FROM application_attempts
        WHERE job_url = ?
        ORDER BY created_at DESC
        """,
        (job_url,),
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]
