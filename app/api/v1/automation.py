from __future__ import annotations

from fastapi import APIRouter, Depends
from app.core.auth_middleware import get_current_user
from app.db.models import User
from app.schemas import AutomationStatusResponse
from app.worker.automation_manager import AutomationManager

router = APIRouter(prefix="/automation", tags=["Automation"])


@router.get("/status", response_model=AutomationStatusResponse)
def get_status(current_user: User = Depends(get_current_user)):
    mgr = AutomationManager.get_instance()
    status_dict = mgr.get_user_status(current_user.id)
    return status_dict


@router.post("/start", response_model=AutomationStatusResponse)
def start_automation(current_user: User = Depends(get_current_user)):
    mgr = AutomationManager.get_instance()
    status_dict = mgr.start_user_automation(current_user.id)
    return status_dict


@router.post("/pause", response_model=AutomationStatusResponse)
def pause_automation(current_user: User = Depends(get_current_user)):
    mgr = AutomationManager.get_instance()
    status_dict = mgr.pause_user_automation(current_user.id)
    return status_dict


@router.post("/resume", response_model=AutomationStatusResponse)
def resume_automation(current_user: User = Depends(get_current_user)):
    mgr = AutomationManager.get_instance()
    status_dict = mgr.resume_user_automation(current_user.id)
    return status_dict


@router.post("/stop", response_model=AutomationStatusResponse)
def stop_automation(current_user: User = Depends(get_current_user)):
    mgr = AutomationManager.get_instance()
    status_dict = mgr.stop_user_automation(current_user.id)
    return status_dict
