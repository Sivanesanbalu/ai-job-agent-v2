from __future__ import annotations

import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.auth_middleware import get_current_user
from app.db.session import get_db
from app.db.models import (
    User, Profile, Preferences, ApplicationProfile, CreditBalance, CreditTransaction
)
from app.schemas import (
    UserRegister, UserLogin, TokenResponse, UserOut,
    ForgotPasswordRequest, ResetPasswordRequest
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse)
def register(data: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email.lower().strip()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    # 1. Create User
    user = User(
        email=data.email.lower().strip(),
        hashed_password=get_password_hash(data.password),
        is_active=True,
        is_verified=True,
        is_admin=False,
    )
    db.add(user)
    db.flush()

    # 2. Initialize default Profile
    profile = Profile(
        user_id=user.id,
        first_name=data.first_name or "",
        last_name=data.last_name or "",
        email=user.email,
        headline="Software Professional",
        country="India",
    )
    db.add(profile)

    # 3. Initialize default Preferences
    preferences = Preferences(
        user_id=user.id,
        preferred_roles=[
            "AI Engineer",
            "Generative AI Engineer",
            "Python Engineer",
            "Machine Learning Engineer",
        ],
        preferred_locations=["Bangalore", "Chennai", "Coimbatore", "Hyderabad", "Pune", "Remote"],
        remote_friendly=True,
        min_salary_lpa=5.0,
        max_experience_years=2.0,
        min_match_score=70,
        max_applications_per_day=25,
        auto_submit=True,
        require_human_review=False,
    )
    db.add(preferences)

    # 4. Initialize default Application Profile
    app_profile = ApplicationProfile(
        user_id=user.id,
        notice_period_days=15,
        work_authorization="Authorized to work in India",
        expected_salary_lpa=6.0,
        years_of_experience=1.0,
    )
    db.add(app_profile)

    # 5. Initialize Credit Balance (5 free monthly applications)
    from app.services.credit_service import ensure_user_credits
    ensure_user_credits(db, user.id)

    db.commit()
    db.refresh(user)

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "is_admin": user.is_admin,
            "first_name": profile.first_name,
            "last_name": profile.last_name,
        },
    }


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower().strip()).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated.",
        )

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    profile = user.profile
    first_name = profile.first_name if profile else ""
    last_name = profile.last_name if profile else ""

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "is_admin": user.is_admin,
            "first_name": first_name,
            "last_name": last_name,
        },
    }


@router.post("/refresh")
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = int(payload["sub"])
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid refresh token: {e}")

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not active or not found")

    new_access_token = create_access_token(user.id)
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    return {"status": "success", "message": "Logged out successfully."}


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from app.services.credit_service import ensure_user_credits
    cb = ensure_user_credits(db, current_user.id)
    credits_rem = cb.balance if cb else 0

    return {
        "id": current_user.id,
        "email": current_user.email,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "is_admin": current_user.is_admin,
        "created_at": current_user.created_at,
        "profile": current_user.profile,
        "preferences": current_user.preferences,
        "application_profile": current_user.application_profile,
        "credits_remaining": credits_rem,
    }


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower().strip()).first()
    if not user:
        # Avoid user enumeration by returning ok
        return {"status": "ok", "message": "If an account exists, a reset link was generated."}

    # Generate a password reset token valid for 1 hour
    token = create_access_token(user.id, expires_delta=datetime.timedelta(hours=1), extra_claims={"purpose": "reset_password"})
    return {
        "status": "ok",
        "message": "Reset token generated successfully.",
        "reset_token": token,  # Provided for seamless API/UI consumption
    }


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        payload = decode_token(data.token)
        user_id = int(payload["sub"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid or expired reset token: {e}")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user.hashed_password = get_password_hash(data.new_password)
    db.commit()

    return {"status": "ok", "message": "Password reset successfully. You can now login with your new password."}
