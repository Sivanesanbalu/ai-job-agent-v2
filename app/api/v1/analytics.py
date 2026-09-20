from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.auth_middleware import get_current_user
from app.db.session import get_db
from app.db.models import User, JobListing, JobMatch, Application, CreditBalance
from app.schemas import AnalyticsSummaryOut

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("", response_model=AnalyticsSummaryOut)
def get_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    total_jobs = db.query(JobListing).count()

    total_matched = (
        db.query(JobMatch)
        .filter(JobMatch.user_id == current_user.id, JobMatch.apply_decision == True)
        .count()
    )

    total_apps = db.query(Application).filter(Application.user_id == current_user.id).count()

    apps_submitted = (
        db.query(Application)
        .filter(Application.user_id == current_user.id, Application.status == "submitted")
        .count()
    )

    apps_pending = (
        db.query(Application)
        .filter(
            Application.user_id == current_user.id,
            Application.status.in_(["application_started", "form_filling", "needs_human_review"]),
        )
        .count()
    )

    apps_failed = (
        db.query(Application)
        .filter(Application.user_id == current_user.id, Application.status == "failed")
        .count()
    )

    verification_req = (
        db.query(Application)
        .filter(Application.user_id == current_user.id, Application.status == "verification_required")
        .count()
    )

    cb = db.query(CreditBalance).filter(CreditBalance.user_id == current_user.id).first()
    credits_remaining = cb.balance if cb else 0
    credits_used = cb.total_used if cb else 0

    return AnalyticsSummaryOut(
        total_jobs_found=total_jobs,
        total_jobs_matched=total_matched,
        total_applications=total_apps,
        applications_submitted=apps_submitted,
        applications_pending=apps_pending,
        applications_failed=apps_failed,
        verification_required=verification_req,
        credits_remaining=credits_remaining,
        credits_used=credits_used,
    )
