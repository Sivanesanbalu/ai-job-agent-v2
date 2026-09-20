from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.auth_middleware import get_current_user
from app.db.session import get_db
from app.db.models import User, Profile
from app.schemas import ProfileOut, ProfileUpdate

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("", response_model=ProfileOut)
def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        profile = Profile(user_id=current_user.id, email=current_user.email)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


@router.patch("", response_model=ProfileOut)
def update_user_profile(
    data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        profile = Profile(user_id=current_user.id, email=current_user.email)
        db.add(profile)

    update_dict = data.model_dump(exclude_unset=True)
    for field, val in update_dict.items():
        setattr(profile, field, val)

    db.commit()
    db.refresh(profile)
    return profile
