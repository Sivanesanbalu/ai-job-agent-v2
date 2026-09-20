from app.services.database import get_connection


def _row_to_job(row):
    if row is None:
        return None

    from app.models.job import Job
    from app.models.job_source import JobSourceName

    return Job(
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


def get_all_jobs():
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM jobs
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return [_row_to_job(row) for row in rows]


def get_job_by_url(url: str):
    connection = get_connection()

    row = connection.execute(
        """
        SELECT *
        FROM jobs
        WHERE url = ?
        """,
        (url,),
    ).fetchone()

    connection.close()

    return _row_to_job(row)


def get_application_candidates():
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM jobs
        WHERE application_status = ?
        ORDER BY match_score DESC
        """,
        ("application_candidate",),
    ).fetchall()

    connection.close()

    return [_row_to_job(row) for row in rows]


def get_human_review_jobs():
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM jobs
        WHERE application_status = ?
        ORDER BY match_score DESC
        """,
        ("needs_human_review",),
    ).fetchall()

    connection.close()

    return [_row_to_job(row) for row in rows]


def get_approved_jobs():
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM jobs
        WHERE application_status = ?
        ORDER BY match_score DESC
        """,
        ("approved_for_application",),
    ).fetchall()

    connection.close()

    return [_row_to_job(row) for row in rows]


def get_human_action_queue():
    """
    Return applications that currently require
    human interaction.

    These states intentionally exclude failed jobs.
    """

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM jobs
        WHERE application_status IN (
            'application_started'
        )
        ORDER BY match_score DESC, id DESC
        """
    ).fetchall()

    connection.close()

    return [_row_to_job(row) for row in rows]


def get_application_dashboard_stats():
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT application_status, COUNT(*) AS count
        FROM jobs
        GROUP BY application_status
        """
    ).fetchall()

    connection.close()

    stats = {
        "total_jobs": 0,
        "discovered": 0,
        "application_candidate": 0,
        "needs_human_review": 0,
        "approved_for_application": 0,
        "application_started": 0,
        "ready_for_submission": 0,
        "submitted": 0,
        "rejected_by_user": 0,
        "failed": 0,
    }

    for row in rows:
        status = row["application_status"]
        count = row["count"]

        stats["total_jobs"] += count

        if status in stats:
            stats[status] = count

    return stats
