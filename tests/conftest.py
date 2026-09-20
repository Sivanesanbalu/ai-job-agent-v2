import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.session import SessionLocal, engine, Base, init_db
from app.db.models import User, CreditBalance, Profile, Preferences, ApplicationProfile
from app.core.security import create_access_token, get_password_hash

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    init_db()
    yield

@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def test_user(db: Session):
    email = f"test_user_{id(db)}@example.com"
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            email=email,
            hashed_password=get_password_hash("Password123!"),
            is_active=True,
            is_verified=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Give 100 free credits
        credit = CreditBalance(
            user_id=user.id,
            balance=100,
            total_included=100,
            total_purchased=0,
            total_used=0,
        )
        db.add(credit)

        profile = Profile(
            user_id=user.id,
            first_name="Test",
            last_name="Engineer",
            email=user.email,
            skills=["Python", "FastAPI", "React"],
            experience_years=5.0,
        )
        db.add(profile)

        pref = Preferences(
            user_id=user.id,
            preferred_roles=["Senior Python Developer"],
            preferred_locations=["Remote"],
            min_salary_lpa=20.0,
            max_experience_years=8,
            min_match_score=70,
            auto_submit=False,
        )
        db.add(pref)

        app_prof = ApplicationProfile(
            user_id=user.id,
            notice_period_days=30,
            work_authorization="Citizen",
            expected_salary_lpa=25.0,
            years_of_experience=5.0,
        )
        db.add(app_prof)
        db.commit()
        db.refresh(user)

    return user

@pytest.fixture
def auth_headers(test_user: User):
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}
