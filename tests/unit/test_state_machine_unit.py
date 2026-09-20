import time
import pytest
from sqlalchemy.orm import Session
from app.db.models import User, JobListing, Application, ApplicationEvent
from app.core.security import get_password_hash

VALID_STAGES = [
    "discovered",
    "analyzed",
    "queued",
    "preparing",
    "filling",
    "review_required",
    "submitting",
    "submitted",
    "failed",
    "verification_required",
]

def log_transition(db: Session, app_rec: Application, new_status: str, stage: str, message: str, data: dict = None):
    app_rec.status = new_status
    app_rec.stage = stage
    event = ApplicationEvent(
        application_id=app_rec.id,
        user_id=app_rec.user_id,
        status=new_status,
        stage=stage,
        message=message,
        data=data or {},
    )
    db.add(event)
    db.commit()
    db.refresh(app_rec)
    return event

def test_application_lifecycle_progression(db: Session):
    user = User(email=f"statemachine_user_{time.time_ns()}@test.com", hashed_password=get_password_hash("pass"), is_active=True)
    db.add(user)
    db.commit()

    job = JobListing(title="ML Engineer", company="AI Labs", url=f"https://example.com/ml1_{time.time_ns()}", source="test")
    db.add(job)
    db.commit()

    # Initial state
    app_rec = Application(user_id=user.id, job_id=job.id, status="discovered", stage="initial")
    db.add(app_rec)
    db.commit()
    db.refresh(app_rec)
    assert app_rec.status == "discovered"

    # Step 1: Analyzed
    log_transition(db, app_rec, "analyzed", "intelligence", "AI match score calculated: 88%", {"score": 88})
    assert app_rec.status == "analyzed"

    # Step 2: Queued
    log_transition(db, app_rec, "queued", "scheduler", "Application queued for browser execution")
    assert app_rec.status == "queued"

    # Step 3: Preparing & Filling
    log_transition(db, app_rec, "filling", "browser", "Playwright opened job portal, pre-filling form inputs")
    assert app_rec.status == "filling"

    # Step 4: Review Required (Human-in-the-loop)
    log_transition(db, app_rec, "review_required", "human_gate", "Application prepared. Waiting for candidate approval.")
    assert app_rec.status == "review_required"

    # Step 5: Candidate Approved -> Submitting -> Submitted
    log_transition(db, app_rec, "submitting", "browser", "Candidate approved. Submitting final form.")
    log_transition(db, app_rec, "submitted", "completed", "Application submitted successfully!")
    assert app_rec.status == "submitted"

    # Verify event audit trail
    events = db.query(ApplicationEvent).filter(ApplicationEvent.application_id == app_rec.id).order_by(ApplicationEvent.created_at.asc()).all()
    assert len(events) == 6
    statuses = [e.status for e in events]
    assert statuses == ["analyzed", "queued", "filling", "review_required", "submitting", "submitted"]

def test_application_verification_required_halts(db: Session):
    user = User(email=f"verify_halt_user_{time.time_ns()}@test.com", hashed_password=get_password_hash("pass"), is_active=True)
    db.add(user)
    db.commit()

    job = JobListing(title="Staff Engineer", company="SecureNet", url=f"https://example.com/sec1_{time.time_ns()}", source="test")
    db.add(job)
    db.commit()

    app_rec = Application(user_id=user.id, job_id=job.id, status="filling", stage="browser")
    db.add(app_rec)
    db.commit()

    # Challenge encountered (CAPTCHA / 2FA)
    app_rec.verification_reason = "Cloudflare Turnstile CAPTCHA detected"
    log_transition(
        db,
        app_rec,
        "verification_required",
        "safety_guard",
        "Security challenge detected. Automated bypass prohibited by safety policy.",
        {"challenge_type": "captcha"}
    )

    assert app_rec.status == "verification_required"
    assert "CAPTCHA" in app_rec.verification_reason
