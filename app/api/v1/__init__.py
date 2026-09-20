from __future__ import annotations

from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.profile import router as profile_router
from app.api.v1.resumes import router as resumes_router
from app.api.v1.preferences import router as preferences_router
from app.api.v1.application_profile import router as app_profile_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.applications import router as applications_router
from app.api.v1.automation import router as automation_router
from app.api.v1.connected_accounts import router as connected_accounts_router
from app.api.v1.credits import router as credits_router
from app.api.v1.billing import router as billing_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.analytics import router as analytics_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(auth_router)
api_v1_router.include_router(profile_router)
api_v1_router.include_router(resumes_router)
api_v1_router.include_router(preferences_router)
api_v1_router.include_router(app_profile_router)
api_v1_router.include_router(jobs_router)
api_v1_router.include_router(applications_router)
api_v1_router.include_router(automation_router)
api_v1_router.include_router(connected_accounts_router)
api_v1_router.include_router(credits_router)
api_v1_router.include_router(billing_router)
api_v1_router.include_router(notifications_router)
api_v1_router.include_router(analytics_router)
