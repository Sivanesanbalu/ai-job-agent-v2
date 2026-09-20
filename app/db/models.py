from __future__ import annotations

import datetime
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    JSON,
    Index,
)
from sqlalchemy.orm import relationship
from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )

    # Relationships
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("Preferences", back_populates="user", uselist=False, cascade="all, delete-orphan")
    application_profile = relationship("ApplicationProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    connected_accounts = relationship("ConnectedAccount", back_populates="user", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    credit_balance = relationship("CreditBalance", back_populates="user", uselist=False, cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    token = Column(String(512), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    first_name = Column(String(100), default="", nullable=False)
    middle_name = Column(String(100), default="", nullable=False)
    last_name = Column(String(100), default="", nullable=False)
    preferred_name = Column(String(100), default="", nullable=False)
    email = Column(String(255), default="", nullable=False)
    phone = Column(String(50), default="", nullable=False)
    dob = Column(String(50), default="", nullable=False)
    country = Column(String(100), default="India", nullable=False)
    state = Column(String(100), default="", nullable=False)
    city = Column(String(100), default="", nullable=False)
    address = Column(Text, default="", nullable=False)
    pincode = Column(String(20), default="", nullable=False)
    headline = Column(String(255), default="", nullable=False)
    summary = Column(Text, default="", nullable=False)
    linkedin_url = Column(String(512), default="", nullable=False)
    github_url = Column(String(512), default="", nullable=False)
    portfolio_url = Column(String(512), default="", nullable=False)
    education = Column(String(255), default="", nullable=False)
    experience_years = Column(Float, default=0.0, nullable=False)
    skills = Column(JSON, default=list, nullable=False)
    projects = Column(JSON, default=list, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )

    user = relationship("User", back_populates="profile")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer, default=0, nullable=False)
    mime_type = Column(String(100), default="application/pdf", nullable=False)
    parsed_data = Column(JSON, default=dict, nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )

    user = relationship("User", back_populates="resumes")
    versions = relationship("ResumeVersion", back_populates="resume", cascade="all, delete-orphan")


class ResumeVersion(Base):
    __tablename__ = "resume_versions"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    version_num = Column(Integer, nullable=False)
    file_path = Column(String(512), nullable=False)
    parsed_data = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    resume = relationship("Resume", back_populates="versions")


class Preferences(Base):
    __tablename__ = "preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    preferred_roles = Column(JSON, default=list, nullable=False)
    preferred_locations = Column(JSON, default=list, nullable=False)
    remote_friendly = Column(Boolean, default=True, nullable=False)
    min_salary_lpa = Column(Float, default=5.0, nullable=False)
    max_experience_years = Column(Float, default=2.0, nullable=False)
    min_match_score = Column(Integer, default=70, nullable=False)
    max_applications_per_day = Column(Integer, default=25, nullable=True)
    auto_submit = Column(Boolean, default=True, nullable=False)
    require_human_review = Column(Boolean, default=False, nullable=False)
    employment_types = Column(JSON, default=lambda: ["Full-time", "Contract"], nullable=False)
    keywords = Column(JSON, default=list, nullable=False)
    excluded_keywords = Column(JSON, default=list, nullable=False)
    sponsorship_required = Column(Boolean, default=False, nullable=False)
    relocation = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )

    user = relationship("User", back_populates="preferences")


class ApplicationProfile(Base):
    __tablename__ = "application_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    notice_period_days = Column(Integer, default=15, nullable=False)
    work_authorization = Column(String(100), default="Authorized to work in India", nullable=False)
    expected_salary_lpa = Column(Float, default=6.0, nullable=False)
    current_salary_lpa = Column(Float, default=0.0, nullable=True)
    years_of_experience = Column(Float, default=0.5, nullable=False)
    willing_to_relocate = Column(Boolean, default=True, nullable=False)
    disability_status = Column(String(50), default="No", nullable=False)
    veteran_status = Column(String(50), default="No", nullable=False)
    gender = Column(String(50), default="Prefer not to say", nullable=False)
    ethnicity = Column(String(50), default="Asian", nullable=False)
    custom_answers = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )

    user = relationship("User", back_populates="application_profile")


class ApplicationAnswer(Base):
    __tablename__ = "application_answers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    question_key = Column(String(100), index=True, nullable=False)
    question_text = Column(Text, nullable=False)
    answer_value = Column(Text, nullable=False)
    category = Column(String(50), default="general", nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )


class ConnectedAccount(Base):
    __tablename__ = "connected_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    platform = Column(String(50), index=True, nullable=False)  # linkedin, naukri, indeed
    account_identifier = Column(String(255), default="", nullable=False)
    auth_status = Column(String(50), default="not_connected", nullable=False)  # connected, login_required, reauth_required
    credentials_encrypted = Column(JSON, default=dict, nullable=False)
    last_verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )

    user = relationship("User", back_populates="connected_accounts")


class JobListing(Base):
    __tablename__ = "job_listings"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(255), index=True, nullable=True)
    source = Column(String(50), index=True, nullable=False)  # linkedin, naukri, indeed, generic
    url = Column(Text, unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255), default="", nullable=False)
    description = Column(Text, default="", nullable=False)
    experience_years = Column(Float, nullable=True)
    salary = Column(String(100), nullable=True)
    raw_data = Column(JSON, default=dict, nullable=False)
    posted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True, nullable=False)


class JobMatch(Base):
    __tablename__ = "job_matches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    job_id = Column(Integer, ForeignKey("job_listings.id", ondelete="CASCADE"), index=True, nullable=False)
    match_score = Column(Integer, default=0, nullable=False)
    relevance = Column(String(50), default="unknown", nullable=False)
    matched_skills = Column(JSON, default=list, nullable=False)
    missing_skills = Column(JSON, default=list, nullable=False)
    reason = Column(Text, default="", nullable=False)
    apply_decision = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_user_job_match"),
        Index("ix_job_matches_user_score", "user_id", "match_score"),
    )

    job = relationship("JobListing")


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    job_id = Column(Integer, ForeignKey("job_listings.id", ondelete="CASCADE"), index=True, nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(50), default="discovered", index=True, nullable=False)
    stage = Column(String(50), default="initial", nullable=False)
    error_message = Column(Text, default="", nullable=True)
    verification_reason = Column(Text, default="", nullable=True)
    match_score = Column(Integer, default=0, nullable=False)
    submission_data = Column(JSON, default=dict, nullable=False)
    submitted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_user_job_application"),
        Index("ix_applications_user_status", "user_id", "status"),
        Index("ix_applications_user_created", "user_id", "created_at"),
    )

    user = relationship("User", back_populates="applications")
    job = relationship("JobListing")
    resume = relationship("Resume")
    events = relationship("ApplicationEvent", back_populates="application", cascade="all, delete-orphan")


class ApplicationEvent(Base):
    __tablename__ = "application_events"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    status = Column(String(50), nullable=False)
    stage = Column(String(50), default="", nullable=False)
    message = Column(Text, default="", nullable=False)
    data = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True, nullable=False)

    application = relationship("Application", back_populates="events")


class AutomationTask(Base):
    __tablename__ = "automation_tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    task_type = Column(String(50), index=True, nullable=False)  # discovery, reader, matching, application
    status = Column(String(50), default="pending", index=True, nullable=False)  # pending, running, completed, failed, cancelled
    priority = Column(Integer, default=10, nullable=False)
    attempt_count = Column(Integer, default=0, nullable=False)
    max_attempts = Column(Integer, default=3, nullable=False)
    job_id = Column(Integer, ForeignKey("job_listings.id", ondelete="SET NULL"), nullable=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="SET NULL"), nullable=True)
    payload = Column(JSON, default=dict, nullable=False)
    result = Column(JSON, default=dict, nullable=False)
    error_message = Column(Text, default="", nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True, nullable=False)


class BrowserSession(Base):
    __tablename__ = "browser_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    session_token = Column(String(255), unique=True, index=True, nullable=False)
    context_dir = Column(String(512), nullable=False)
    status = Column(String(50), default="idle", nullable=False)  # idle, running, closed
    last_active_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    price_inr = Column(Integer, default=0, nullable=False)
    included_applications = Column(Integer, default=5, nullable=False)
    extra_application_cost_inr = Column(Integer, default=1, nullable=False)
    features = Column(JSON, default=list, nullable=False)
    billing_type = Column(String(50), default="pay_as_you_go", nullable=False)  # free, pay_as_you_go
    tag = Column(String(50), default="", nullable=True)  # Popular, Best Value
    is_active = Column(Boolean, default=True, nullable=False)


class CreditBalance(Base):
    __tablename__ = "credit_balances"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    balance = Column(Integer, default=5, nullable=False)
    total_included = Column(Integer, default=5, nullable=False)
    total_purchased = Column(Integer, default=0, nullable=False)
    total_used = Column(Integer, default=0, nullable=False)
    last_monthly_grant_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )

    user = relationship("User", back_populates="credit_balance")


class CreditTransaction(Base):
    __tablename__ = "credit_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="SET NULL"), nullable=True)
    type = Column(String(50), nullable=False)  # grant, deduction, refund, purchase
    amount = Column(Integer, nullable=False)
    balance_before = Column(Integer, nullable=False)
    balance_after = Column(Integer, nullable=False)
    description = Column(String(255), default="", nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True, nullable=False)

    __table_args__ = (
        Index("ix_credit_transactions_user_date", "user_id", "created_at"),
    )


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id", ondelete="SET NULL"), nullable=True)
    amount_inr = Column(Integer, nullable=False)
    currency = Column(String(10), default="INR", nullable=False)
    status = Column(String(50), default="pending", index=True, nullable=False)  # pending, completed, failed
    provider = Column(String(50), default="razorpay", nullable=False)
    provider_tx_id = Column(String(255), default="", nullable=False)
    razorpay_order_id = Column(String(255), unique=True, index=True, nullable=True)
    razorpay_payment_id = Column(String(255), unique=True, index=True, nullable=True)
    razorpay_signature = Column(String(255), nullable=True)
    pack_slug = Column(String(100), nullable=True)
    credits_granted = Column(Integer, default=0, nullable=False)
    webhook_payload = Column(JSON, default=dict, nullable=True)
    error_reason = Column(String(255), nullable=True)
    receipt_url = Column(String(512), default="", nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True, nullable=False)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    type = Column(String(50), default="info", nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, index=True, nullable=False)
    metadata_json = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True, nullable=False)

    __table_args__ = (
        Index("ix_notifications_user_read", "user_id", "is_read"),
    )

    user = relationship("User", back_populates="notifications")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), index=True, nullable=False)
    ip_address = Column(String(50), default="", nullable=True)
    user_agent = Column(String(255), default="", nullable=True)
    details = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True, nullable=False)
