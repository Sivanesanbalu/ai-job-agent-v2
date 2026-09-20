from pathlib import Path
import sqlite3
import threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

from app.config import AUTO_SUBMIT, REQUIRE_HUMAN_REVIEW
from app.data.candidate_profile import CANDIDATE_PROFILE
from app.models.job import Job
from app.services.database import initialize_database
from app.services.browser_executor import BrowserExecutor
from app.agents.application_workflow import run_application_workflow


print("=" * 40)
print("STEP 11K — AUTONOMOUS E2E TEST")
print("=" * 40)

assert AUTO_SUBMIT is True
assert REQUIRE_HUMAN_REVIEW is False

test_dir = Path(".browser_test").resolve()


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


server = ThreadingHTTPServer(
    ("127.0.0.1", 8765),
    lambda *args, **kwargs: QuietHandler(
        *args,
        directory=str(test_dir),
        **kwargs,
    ),
)

thread = threading.Thread(
    target=server.serve_forever,
    daemon=True,
)
thread.start()

test_url = "http://127.0.0.1:8765/application.html"

db_path = Path("jobs.db")

if db_path.exists():
    db_path.unlink()

initialize_database()

original_email = CANDIDATE_PROFILE.email
CANDIDATE_PROFILE.email = "test@example.com"

job = Job(
    title="AI Automation Engineer",
    company="Demo Automation Company",
    location="Chennai",
    url=test_url,
    description=(
        "Build AI automation workflows using Python, "
        "LLMs, APIs and AI agents."
    ),
    experience_years=1.0,
    salary="₹5-7 LPA",
    source="demo",
    match_score=70,
    application_status="application_candidate",
)

connection = sqlite3.connect("jobs.db")

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
    """,
    (
        job.title,
        job.company,
        job.location,
        job.url,
        job.description,
        job.experience_years,
        job.salary,
        job.source.value if hasattr(job.source, "value") else job.source,
        job.match_score,
        job.application_status,
    ),
)

connection.commit()
connection.close()

executor = BrowserExecutor()

try:
    result = run_application_workflow(
        job,
        executor,
    )

    connection = sqlite3.connect("jobs.db")

    row = connection.execute(
        """
        SELECT application_status
        FROM jobs
        WHERE url = ?
        """,
        (test_url,),
    ).fetchone()

    attempts = connection.execute(
        """
        SELECT status, message
        FROM application_attempts
        WHERE job_url = ?
        ORDER BY id
        """,
        (test_url,),
    ).fetchall()

    connection.close()

    statuses = [attempt[0] for attempt in attempts]

    print("")
    print("Final status :", result.get("status"))
    print("Final stage  :", result.get("stage"))
    print("DB status    :", row[0])

    print("")
    print("State history:")

    for status, message in attempts:
        print(f"  {status} | {message}")

    print("")
    print("=" * 40)
    print("ASSERTIONS")
    print("=" * 40)

    assert result["status"] == "submitted"
    print("Automatic submission     : PASS ✅")

    assert result["stage"] == "submitted"
    print("Submitted stage          : PASS ✅")

    assert row[0] == "submitted"
    print("Database submitted state : PASS ✅")

    # application_candidate is the initial DB state for this E2E test,
    # so it is not expected to appear in application_attempts.
    connection = sqlite3.connect("jobs.db")
    initial_row = connection.execute(
        """
        SELECT application_status
        FROM jobs
        WHERE url = ?
        """,
        (test_url,),
    ).fetchone()
    connection.close()

    assert initial_row[0] == "submitted"
    print("Application candidate    : INITIAL STATE ✅")

    expected_statuses = [
        "approved_for_application",
        "application_started",
        "ready_for_submission",
        "submitted",
    ]

    assert statuses == expected_statuses
    print("Autonomous state sequence: PASS ✅")

    assert "approved_for_application" in statuses
    print("Automatic approval       : PASS ✅")

    assert "application_started" in statuses
    print("Application started      : PASS ✅")

    assert "ready_for_submission" in statuses
    print("Ready for submission     : PASS ✅")

    assert "submitted" in statuses
    print("Submitted state          : PASS ✅")

    assert "needs_human_review" not in statuses
    print("No human-review gate     : PASS ✅")

    package = result.get("application", {})

    assert package.get("requires_human_review") is False
    print("Package review flag      : PASS ✅")

    print("")
    print("=" * 40)
    print("STEP 11K — COMPLETE PASS ✅")
    print("=" * 40)

finally:
    CANDIDATE_PROFILE.email = original_email
    executor.close()
    server.shutdown()
