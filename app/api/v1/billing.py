from __future__ import annotations

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.auth_middleware import get_current_user
from app.db.session import get_db
from app.db.models import User, Plan, Payment
from app.schemas import PlanOut, CheckoutRequest
from app.services.billing_service import BillingService

router = APIRouter(prefix="/billing", tags=["Billing"])


@router.get("/plans", response_model=List[PlanOut])
def list_plans(db: Session = Depends(get_db)):
    return db.query(Plan).filter(Plan.is_active == True).all()


@router.post("/checkout")
def create_checkout(
    data: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session_data = BillingService.create_checkout_session(db, current_user.id, data.plan_slug)
    # Auto-fulfill in simulated payment environment
    payment = BillingService.process_payment_success(db, session_data["checkout_id"], current_user.id)
    return {
        "status": "success",
        "message": f"Payment of ₹{payment.amount_inr} processed successfully. Credits added to your account.",
        "payment_id": payment.id,
        "transaction_id": payment.provider_tx_id,
        "amount_inr": payment.amount_inr,
    }


@router.get("/history")
def payment_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    payments = (
        db.query(Payment)
        .filter(Payment.user_id == current_user.id)
        .order_by(Payment.created_at.desc())
        .all()
    )
    return payments
