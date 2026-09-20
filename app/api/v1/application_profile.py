from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.auth_middleware import get_current_user
from app.db.session import get_db
from app.db.models import User, ApplicationProfile
from app.schemas import ApplicationProfileOut, ApplicationProfileUpdate

router = APIRouter(prefix="/application-profile", tags=["Application Profile"])


@router.get("", response_model=ApplicationProfileOut)
def get_application_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    app_prof = db.query(ApplicationProfile).filter(ApplicationProfile.user_id == current_user.id).first()
    if not app_prof:
        app_prof = ApplicationProfile(user_id=current_user.id)
        db.add(app_prof)
        db.commit()
        db.refresh(app_prof)
    return app_prof


@router.patch("", response_model=ApplicationProfileOut)
def update_application_profile(
    data: ApplicationProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    app_prof = db.query(ApplicationProfile).filter(ApplicationProfile.user_id == current_user.id).first()
    if not app_prof:
        app_prof = ApplicationProfile(user_id=current_user.id)
        db.add(app_prof)

    update_dict = data.model_dump(exclude_unset=True)
    for field, val in update_dict.items():
        setattr(app_prof, field, val)

    db.commit()
    db.refresh(app_prof)
    return app_prof
