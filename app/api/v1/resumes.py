from __future__ import annotations

import os
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.auth_middleware import get_current_user
from app.db.session import get_db
from app.db.models import User, Resume, ResumeVersion, Profile
from app.schemas import ResumeOut, ResumeUpdate
from app.services.resume_storage import validate_resume_file, save_user_resume_file, delete_resume_file
from app.services.resume_parser import parse_resume

router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.post("", response_model=ResumeOut)
async def upload_resume(
    file: UploadFile = File(...),
    set_active: bool = Form(default=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    content = await file.read()
    filename, mime_type = validate_resume_file(file, content)

    # Save to user-isolated storage
    dest_path = save_user_resume_file(current_user.id, filename, content)

    # Parse resume
    try:
        parsed_data = parse_resume(dest_path, filename)
    except Exception as e:
        delete_resume_file(str(dest_path))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not parse resume contents: {e}",
        )

    # If set_active is True or this is user's first resume, deactivate others
    count = db.query(Resume).filter(Resume.user_id == current_user.id).count()
    if set_active or count == 0:
        db.query(Resume).filter(Resume.user_id == current_user.id).update({"is_active": False})
        is_active = True
    else:
        is_active = False

    resume = Resume(
        user_id=current_user.id,
        filename=filename,
        file_path=str(dest_path),
        file_size=len(content),
        mime_type=mime_type,
        parsed_data=parsed_data,
        is_active=is_active,
        version=1,
    )
    db.add(resume)
    db.flush()

    # Create initial version
    version_rec = ResumeVersion(
        resume_id=resume.id,
        user_id=current_user.id,
        version_num=1,
        file_path=str(dest_path),
        parsed_data=parsed_data,
    )
    db.add(version_rec)

    # Sync parsed data to user profile if profile is sparse
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if profile:
        if not profile.first_name and parsed_data.get("first_name"):
            profile.first_name = parsed_data["first_name"]
        if not profile.last_name and parsed_data.get("last_name"):
            profile.last_name = parsed_data["last_name"]
        if not profile.phone and parsed_data.get("phone"):
            profile.phone = parsed_data["phone"]
        if not profile.skills and parsed_data.get("skills"):
            profile.skills = parsed_data["skills"]
        if not profile.education and parsed_data.get("education"):
            profile.education = parsed_data["education"]
        if not profile.headline and parsed_data.get("headline"):
            profile.headline = parsed_data["headline"]
        if not profile.summary and parsed_data.get("summary"):
            profile.summary = parsed_data["summary"]
        if not profile.linkedin_url and parsed_data.get("linkedin_url"):
            profile.linkedin_url = parsed_data["linkedin_url"]
        if not profile.github_url and parsed_data.get("github_url"):
            profile.github_url = parsed_data["github_url"]
        if profile.experience_years == 0.0 and parsed_data.get("experience_years"):
            profile.experience_years = float(parsed_data["experience_years"])

    db.commit()
    db.refresh(resume)
    return resume


@router.get("", response_model=List[ResumeOut])
def get_user_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.created_at.desc())
        .all()
    )


@router.get("/{resume_id}", response_model=ResumeOut)
def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = (
        db.query(Resume)
        .filter(Resume.id == resume_id, Resume.user_id == current_user.id)
        .first()
    )
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")
    return resume


@router.patch("/{resume_id}", response_model=ResumeOut)
def update_resume(
    resume_id: int,
    data: ResumeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = (
        db.query(Resume)
        .filter(Resume.id == resume_id, Resume.user_id == current_user.id)
        .first()
    )
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    if data.is_active is True:
        db.query(Resume).filter(Resume.user_id == current_user.id).update({"is_active": False})
        resume.is_active = True

    if data.filename is not None:
        resume.filename = data.filename

    if data.parsed_data is not None:
        resume.parsed_data = data.parsed_data
        # Create version
        resume.version += 1
        new_version = ResumeVersion(
            resume_id=resume.id,
            user_id=current_user.id,
            version_num=resume.version,
            file_path=resume.file_path,
            parsed_data=data.parsed_data,
        )
        db.add(new_version)

    db.commit()
    db.refresh(resume)
    return resume


@router.delete("/{resume_id}")
def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = (
        db.query(Resume)
        .filter(Resume.id == resume_id, Resume.user_id == current_user.id)
        .first()
    )
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    delete_resume_file(resume.file_path)
    db.delete(resume)
    db.commit()

    # If the active resume was deleted, make the newest remaining resume active
    remaining = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.created_at.desc())
        .first()
    )
    if remaining:
        remaining.is_active = True
        db.commit()

    return {"status": "ok", "message": "Resume deleted successfully."}


@router.get("/{resume_id}/download")
def download_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = (
        db.query(Resume)
        .filter(Resume.id == resume_id, Resume.user_id == current_user.id)
        .first()
    )
    if not resume or not Path(resume.file_path).exists():
        raise HTTPException(status_code=404, detail="Resume file not found.")

    return FileResponse(
        path=resume.file_path,
        filename=resume.filename,
        media_type=resume.mime_type,
    )
