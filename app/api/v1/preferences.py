from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.auth_middleware import get_current_user
from app.db.session import get_db
from app.db.models import User, Preferences
from app.schemas import PreferencesOut, PreferencesUpdate

router = APIRouter(prefix="/preferences", tags=["Preferences"])


@router.get("", response_model=PreferencesOut)
def get_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pref = db.query(Preferences).filter(Preferences.user_id == current_user.id).first()
    if not pref:
        pref = Preferences(user_id=current_user.id)
        db.add(pref)
        db.commit()
        db.refresh(pref)
    return pref


@router.patch("", response_model=PreferencesOut)
def update_preferences(
    data: PreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pref = db.query(Preferences).filter(Preferences.user_id == current_user.id).first()
    if not pref:
        pref = Preferences(user_id=current_user.id)
        db.add(pref)

    update_dict = data.model_dump(exclude_unset=True)
    for field, val in update_dict.items():
        setattr(pref, field, val)

    db.commit()
    db.refresh(pref)
    return pref
