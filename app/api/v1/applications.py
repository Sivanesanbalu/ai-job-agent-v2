from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.auth_middleware import get_current_user
from app.db.session import get_db
from app.db.models import User, Application, ApplicationEvent, JobListing
from app.schemas import ApplicationOut, ApplicationEventOut

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.get("", response_model=List[ApplicationOut])
def list_applications(
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = (
        db.query(Application)
        .join(JobListing, Application.job_id == JobListing.id)
        .filter(Application.user_id == current_user.id)
    )

    if status_filter:
        query = query.filter(Application.status == status_filter.lower())

    if search:
        s = f"%{search.lower()}%"
        query = query.filter((JobListing.title.ilike(s)) | (JobListing.company.ilike(s)))

    apps = query.order_by(Application.created_at.desc()).offset(offset).limit(limit).all()
    return apps


@router.get("/{application_id}", response_model=ApplicationOut)
def get_application_detail(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    app = (
        db.query(Application)
        .filter(Application.id == application_id, Application.user_id == current_user.id)
        .first()
    )
    if not app:
        raise HTTPException(status_code=404, detail="Application not found.")
    return app


@router.post("/{application_id}/approve")
def approve_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    app = (
        db.query(Application)
        .filter(Application.id == application_id, Application.user_id == current_user.id)
        .first()
    )
    if not app:
        raise HTTPException(status_code=404, detail="Application not found.")

    app.status = "approved_for_application"
    db.add(ApplicationEvent(
        application_id=app.id,
        user_id=current_user.id,
        status="approved_for_application",
        stage="human_gate",
        message="Application approved by candidate for automatic submission.",
    ))
    db.commit()
    db.refresh(app)
    return {"status": "approved", "application_id": app.id}


@router.post("/{application_id}/reject")
def reject_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    app = (
        db.query(Application)
        .filter(Application.id == application_id, Application.user_id == current_user.id)
        .first()
    )
    if not app:
        raise HTTPException(status_code=404, detail="Application not found.")

    app.status = "rejected_by_user"
    db.add(ApplicationEvent(
        application_id=app.id,
        user_id=current_user.id,
        status="rejected_by_user",
        stage="human_gate",
        message="Application rejected by candidate.",
    ))
    db.commit()
    db.refresh(app)
    return {"status": "rejected", "application_id": app.id}


@router.post("/submit-all-ready")
def submit_all_ready(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from datetime import datetime
    from app.db.models import Notification

    ready_apps = (
        db.query(Application)
        .filter(
            Application.user_id == current_user.id,
            Application.status.in_(["ready_to_submit", "needs_human_review", "approved_for_application"])
        )
        .all()
    )
    now = datetime.utcnow()
    submitted_ids = []
    for app in ready_apps:
        app.status = "submitted"
        app.stage = "completed"
        app.submitted_at = now
        sub_data = dict(app.submission_data or {})
        sub_data["submitted_at"] = now.isoformat()
        sub_data["submission_status"] = "submitted"
        app.submission_data = sub_data

        db.add(ApplicationEvent(
            application_id=app.id,
            user_id=current_user.id,
            status="submitted",
            stage="completed",
            message="Application submitted to company.",
        ))
        submitted_ids.append(app.id)

    if submitted_ids:
        db.add(Notification(
            user_id=current_user.id,
            type="bulk_submission",
            title="Applications Submitted",
            message=f"Successfully submitted {len(submitted_ids)} applications.",
            metadata_json={"submitted_count": len(submitted_ids)},
        ))
        db.commit()

    return {"status": "success", "submitted_count": len(submitted_ids), "application_ids": submitted_ids}


@router.post("/{application_id}/submit")
def submit_single_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from datetime import datetime
    from app.db.models import Notification

    app = (
        db.query(Application)
        .filter(Application.id == application_id, Application.user_id == current_user.id)
        .first()
    )
    if not app:
        raise HTTPException(status_code=404, detail="Application not found.")

    now = datetime.utcnow()
    app.status = "submitted"
    app.stage = "completed"
    app.submitted_at = now

    sub_data = dict(app.submission_data or {})
    sub_data["submitted_at"] = now.isoformat()
    sub_data["submission_status"] = "submitted"
    app.submission_data = sub_data

    job_title = app.job.title if app.job else "job"
    company_name = app.job.company if app.job else "company"

    db.add(ApplicationEvent(
        application_id=app.id,
        user_id=current_user.id,
        status="submitted",
        stage="completed",
        message=f"Application submitted to {company_name} for {job_title}.",
    ))
    db.add(Notification(
        user_id=current_user.id,
        type="application_submitted",
        title="Application Submitted",
        message=f"Successfully submitted application to {company_name} for {job_title}.",
        metadata_json={"application_id": app.id},
    ))
    db.commit()
    db.refresh(app)
    return {"status": "submitted", "application_id": app.id}
