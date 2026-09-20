from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.auth_middleware import get_current_user
from app.db.session import get_db
from app.db.models import User, JobListing, JobMatch, Resume
from app.schemas import JobListingOut, JobSearchRequest
from app.services.matching_engine import match_job_for_user

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("", response_model=List[JobListingOut])
def list_jobs(
    keyword: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    min_score: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(JobListing)

    if keyword:
        kw = f"%{keyword.lower()}%"
        query = query.filter((JobListing.title.ilike(kw)) | (JobListing.description.ilike(kw)))

    if location:
        query = query.filter(JobListing.location.ilike(f"%{location}%"))

    if source:
        query = query.filter(JobListing.source == source.lower())

    jobs = query.order_by(JobListing.created_at.desc()).offset(offset).limit(limit).all()

    # Enrich with user's match score and match details
    results = []
    for job in jobs:
        match = (
            db.query(JobMatch)
            .filter(JobMatch.user_id == current_user.id, JobMatch.job_id == job.id)
            .first()
        )
        match_score = match.match_score if match else None
        match_details = (
            {
                "relevance": match.relevance,
                "matched_skills": match.matched_skills,
                "missing_skills": match.missing_skills,
                "reason": match.reason,
                "apply_decision": match.apply_decision,
            }
            if match
            else None
        )

        if min_score is not None:
            if match_score is None or match_score < min_score:
                continue

        results.append(
            JobListingOut(
                id=job.id,
                external_id=job.external_id,
                source=job.source,
                url=job.url,
                title=job.title,
                company=job.company,
                location=job.location,
                description=job.description,
                experience_years=job.experience_years,
                salary=job.salary,
                match_score=match_score,
                match_details=match_details,
                created_at=job.created_at,
            )
        )

    return results


@router.get("/{job_id}", response_model=JobListingOut)
def get_job_detail(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.query(JobListing).filter(JobListing.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    match = (
        db.query(JobMatch)
        .filter(JobMatch.user_id == current_user.id, JobMatch.job_id == job.id)
        .first()
    )
    if not match:
        # Calculate dynamic match
        pref = current_user.preferences
        active_resume = (
            db.query(Resume)
            .filter(Resume.user_id == current_user.id, Resume.is_active == True)
            .first()
        )
        if pref:
            res = match_job_for_user(job, pref, current_user.profile, active_resume)
            match = JobMatch(
                user_id=current_user.id,
                job_id=job.id,
                match_score=res.match_score,
                relevance=res.relevance,
                matched_skills=res.matched_skills,
                missing_skills=res.missing_skills,
                reason=res.reason,
                apply_decision=res.apply_decision,
            )
            db.add(match)
            db.commit()
            db.refresh(match)

    return JobListingOut(
        id=job.id,
        external_id=job.external_id,
        source=job.source,
        url=job.url,
        title=job.title,
        company=job.company,
        location=job.location,
        description=job.description,
        experience_years=job.experience_years,
        salary=job.salary,
        match_score=match.match_score if match else None,
        match_details={
            "relevance": match.relevance,
            "matched_skills": match.matched_skills,
            "missing_skills": match.missing_skills,
            "reason": match.reason,
            "apply_decision": match.apply_decision,
        } if match else None,
        created_at=job.created_at,
    )


@router.post("/search")
def search_jobs(
    data: JobSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Triggers discovery for the user's criteria
    pref = current_user.preferences
    keyword = data.keyword or (pref.preferred_roles[0] if pref and pref.preferred_roles else "Engineer")
    location = data.location or (pref.preferred_locations[0] if pref and pref.preferred_locations else "Bangalore")

    # In production/dev mode, verify or discover real jobs
    found_jobs = db.query(JobListing).filter(JobListing.title.ilike(f"%{keyword}%")).limit(data.limit).all()
    return {
        "status": "ok",
        "message": f"Discovery completed for '{keyword}' in '{location}'",
        "count": len(found_jobs),
    }


@router.post("/{job_id}/match")
def match_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.query(JobListing).filter(JobListing.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    pref = current_user.preferences
    if not pref:
        raise HTTPException(status_code=400, detail="User preferences must be configured before matching.")

    active_resume = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id, Resume.is_active == True)
        .first()
    )

    result = match_job_for_user(job, pref, current_user.profile, active_resume)

    existing_match = (
        db.query(JobMatch)
        .filter(JobMatch.user_id == current_user.id, JobMatch.job_id == job.id)
        .first()
    )
    if not existing_match:
        existing_match = JobMatch(
            user_id=current_user.id,
            job_id=job.id,
            match_score=result.match_score,
            relevance=result.relevance,
            matched_skills=result.matched_skills,
            missing_skills=result.missing_skills,
            reason=result.reason,
            apply_decision=result.apply_decision,
        )
        db.add(existing_match)
    else:
        existing_match.match_score = result.match_score
        existing_match.relevance = result.relevance
        existing_match.matched_skills = result.matched_skills
        existing_match.missing_skills = result.missing_skills
        existing_match.reason = result.reason
        existing_match.apply_decision = result.apply_decision

    db.commit()
    db.refresh(existing_match)

    return {
        "job_id": job.id,
        "match_score": existing_match.match_score,
        "relevance": existing_match.relevance,
        "matched_skills": existing_match.matched_skills,
        "missing_skills": existing_match.missing_skills,
        "reason": existing_match.reason,
        "apply_decision": existing_match.apply_decision,
    }
