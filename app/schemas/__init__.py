from __future__ import annotations
from typing import Optional, List, Dict, Any
import datetime
from pydantic import BaseModel, EmailStr, Field


# ==========================================
# AUTH SCHEMAS
# ==========================================
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


class UserOut(BaseModel):
    id: int
    email: str
    is_active: bool
    is_verified: bool
    is_admin: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=6)


# ==========================================
# PROFILE SCHEMAS
# ==========================================
class ProfileBase(BaseModel):
    first_name: str = ""
    middle_name: str = ""
    last_name: str = ""
    preferred_name: str = ""
    email: str = ""
    phone: str = ""
    dob: str = ""
    country: str = "India"
    state: str = ""
    city: str = ""
    address: str = ""
    pincode: str = ""
    headline: str = ""
    summary: str = ""
    linkedin_url: str = ""
    github_url: str = ""
    portfolio_url: str = ""
    education: str = ""
    experience_years: float = 0.0
    skills: List[str] = Field(default_factory=list)
    projects: List[Dict[str, Any]] = Field(default_factory=list)


class ProfileUpdate(ProfileBase):
    pass


class ProfileOut(ProfileBase):
    id: int
    user_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


# ==========================================
# RESUME SCHEMAS
# ==========================================
class ResumeOut(BaseModel):
    id: int
    user_id: int
    filename: str
    file_size: int
    mime_type: str
    is_active: bool
    version: int
    parsed_data: Dict[str, Any]
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


class ResumeUpdate(BaseModel):
    is_active: Optional[bool] = None
    filename: Optional[str] = None
    parsed_data: Optional[Dict[str, Any]] = None


# ==========================================
# PREFERENCES SCHEMAS
# ==========================================
class PreferencesBase(BaseModel):
    preferred_roles: List[str] = Field(default_factory=list)
    preferred_locations: List[str] = Field(default_factory=list)
    remote_friendly: bool = True
    min_salary_lpa: float = 5.0
    max_experience_years: float = 2.0
    min_match_score: int = 70
    max_applications_per_day: Optional[int] = 25
    auto_submit: bool = True
    require_human_review: bool = False
    employment_types: List[str] = Field(default_factory=lambda: ["Full-time", "Contract"])
    keywords: List[str] = Field(default_factory=list)
    excluded_keywords: List[str] = Field(default_factory=list)
    sponsorship_required: bool = False
    relocation: bool = True


class PreferencesUpdate(PreferencesBase):
    pass


class PreferencesOut(PreferencesBase):
    id: int
    user_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


# ==========================================
# APPLICATION PROFILE SCHEMAS
# ==========================================
class ApplicationProfileBase(BaseModel):
    notice_period_days: int = 15
    work_authorization: str = "Authorized to work in India"
    expected_salary_lpa: float = 6.0
    current_salary_lpa: Optional[float] = 0.0
    years_of_experience: float = 0.5
    willing_to_relocate: bool = True
    disability_status: str = "No"
    veteran_status: str = "No"
    gender: str = "Prefer not to say"
    ethnicity: str = "Asian"
    custom_answers: Dict[str, Any] = Field(default_factory=dict)


class ApplicationProfileUpdate(ApplicationProfileBase):
    pass


class ApplicationProfileOut(ApplicationProfileBase):
    id: int
    user_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


# ==========================================
# JOB LISTING & MATCH SCHEMAS
# ==========================================
class JobListingOut(BaseModel):
    id: int
    external_id: Optional[str] = None
    source: str
    url: str
    title: str
    company: str
    location: str
    description: str
    experience_years: Optional[float] = None
    salary: Optional[str] = None
    match_score: Optional[int] = None
    match_details: Optional[Dict[str, Any]] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class JobSearchRequest(BaseModel):
    keyword: Optional[str] = ""
    location: Optional[str] = ""
    sources: List[str] = Field(default_factory=lambda: ["linkedin", "naukri", "indeed"])
    limit: int = 20


# ==========================================
# APPLICATION SCHEMAS
# ==========================================
class ApplicationEventOut(BaseModel):
    id: int
    status: str
    stage: str
    message: str
    data: Dict[str, Any]
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class ApplicationOut(BaseModel):
    id: int
    user_id: int
    job_id: int
    resume_id: Optional[int] = None
    status: str
    stage: str
    match_score: int = 0
    error_message: Optional[str] = None
    verification_reason: Optional[str] = None
    submitted_at: Optional[datetime.datetime] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    job: Optional[JobListingOut] = None
    events: List[ApplicationEventOut] = Field(default_factory=list)

    class Config:
        from_attributes = True


# ==========================================
# AUTOMATION SCHEMAS
# ==========================================
class AutomationStatusResponse(BaseModel):
    is_running: bool
    status: str
    current_action: str
    jobs_discovered: int
    jobs_analyzed: int
    jobs_matched: int
    eligible_applications: int
    applications_submitted: int
    verification_required: int
    login_required: int
    failed: int
    credits_remaining: int
    active_tasks: int


class AutomationControlRequest(BaseModel):
    action: str = Field(..., pattern="^(start|pause|resume|stop)$")


# ==========================================
# CONNECTED ACCOUNT SCHEMAS
# ==========================================
class ConnectedAccountOut(BaseModel):
    id: int
    platform: str
    account_identifier: str
    auth_status: str
    last_verified_at: Optional[datetime.datetime] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class ConnectedAccountCreate(BaseModel):
    platform: str
    account_identifier: str
    credentials: Optional[Dict[str, Any]] = Field(default_factory=dict)


# ==========================================
# CREDIT & BILLING SCHEMAS
# ==========================================
class CreditBalanceOut(BaseModel):
    balance: int
    total_included: int
    total_purchased: int
    total_used: int
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


class CreditTransactionOut(BaseModel):
    id: int
    type: str
    amount: int
    balance_before: int
    balance_after: int
    description: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class PlanOut(BaseModel):
    id: int
    name: str
    slug: str
    price_inr: int
    included_applications: int
    features: List[str]
    is_active: bool
    billing_type: Optional[str] = "one_time"
    tag: Optional[str] = None

    class Config:
        from_attributes = True


class CheckoutRequest(BaseModel):
    plan_slug: str


class RazorpayOrderCreateRequest(BaseModel):
    plan_slug: str


class RazorpayOrderResponse(BaseModel):
    order_id: str
    amount: int
    amount_inr: int
    currency: str
    key_id: str
    plan_name: str
    plan_slug: str
    credits: int
    user_email: str
    user_name: str
    user_phone: str


class RazorpayVerifyRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


# ==========================================
# NOTIFICATION SCHEMAS
# ==========================================
class NotificationOut(BaseModel):
    id: int
    type: str
    title: str
    message: str
    is_read: bool
    metadata_json: Dict[str, Any]
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# ==========================================
# ANALYTICS SCHEMAS
# ==========================================
class AnalyticsSummaryOut(BaseModel):
    total_jobs_found: int
    total_jobs_matched: int
    total_applications: int
    applications_submitted: int
    applications_pending: int
    applications_failed: int
    verification_required: int
    credits_remaining: int
    credits_used: int
