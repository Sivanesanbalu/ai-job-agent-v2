from app.config import MAX_APPLICATIONS_PER_DAY
from app.services.database import get_connection


def get_today_application_count() -> int:
    connection = get_connection()

    row = connection.execute(
        """
        SELECT COUNT(DISTINCT job_url) AS count
        FROM application_attempts
        WHERE DATE(created_at) = DATE('now', 'localtime')
        AND status IN (
            'application_started',
            'submitted'
        )
        """
    ).fetchone()

    connection.close()

    return row["count"]


def can_apply_today() -> bool:
    return (
        get_today_application_count()
        < MAX_APPLICATIONS_PER_DAY
    )


def get_remaining_applications_today() -> int:
    used = get_today_application_count()

    return max(
        MAX_APPLICATIONS_PER_DAY - used,
        0,
    )
