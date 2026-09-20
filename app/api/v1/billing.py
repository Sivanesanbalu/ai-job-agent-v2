from __future__ import annotations

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request, Header, status
from sqlalchemy.orm import Session
from app.core.auth_middleware import get_current_user
from app.db.session import get_db
from app.db.models import User, Plan, Payment
from app.schemas import (
    PlanOut,
    CheckoutRequest,
    RazorpayOrderCreateRequest,
    RazorpayOrderResponse,
    RazorpayVerifyRequest,
)
from app.services.billing_service import BillingService
from app.services.razorpay_service import RazorpayService

router = APIRouter(prefix="/billing", tags=["Billing"])


@router.get("/plans", response_model=List[PlanOut])
def list_plans(db: Session = Depends(get_db)):
    """List all available pricing tiers and credit packs."""
    return db.query(Plan).filter(Plan.is_active == True).order_by(Plan.price_inr.asc()).all()


@router.post("/create-order", response_model=RazorpayOrderResponse)
def create_razorpay_order(
    data: RazorpayOrderCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Creates a Razorpay order for the selected credit pack.
    Returns order details and merchant key ID needed by the frontend Razorpay Checkout modal.
    """
    return RazorpayService.create_order(db, user_id=current_user.id, plan_slug=data.plan_slug)


@router.post("/verify-payment")
def verify_razorpay_payment(
    data: RazorpayVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Verifies Razorpay HMAC SHA256 payment signature.
    Credits are fulfilled to the user's account ONLY upon successful verification.
    """
    payment = RazorpayService.verify_payment_signature(
        db=db,
        user_id=current_user.id,
        razorpay_order_id=data.razorpay_order_id,
        razorpay_payment_id=data.razorpay_payment_id,
        razorpay_signature=data.razorpay_signature,
    )
    return {
        "status": "success",
        "message": f"Payment of ₹{payment.amount_inr} verified successfully. {payment.credits_granted} credits added to your account.",
        "payment_id": payment.id,
        "razorpay_order_id": payment.razorpay_order_id,
        "razorpay_payment_id": payment.razorpay_payment_id,
        "credits_granted": payment.credits_granted,
        "amount_inr": payment.amount_inr,
    }


@router.post("/webhook")
async def razorpay_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_razorpay_signature: str = Header(None, alias="X-Razorpay-Signature"),
):
    """
    Razorpay Webhook listener (source of truth).
    Handles events like order.paid and payment.captured with cryptographic verification
    and idempotent credit fulfillment.
    """
    if not x_razorpay_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing X-Razorpay-Signature header",
        )
    raw_body = await request.body()
    result = RazorpayService.process_webhook(db=db, raw_body=raw_body, signature=x_razorpay_signature)
    return result


@router.post("/checkout")
def create_checkout(
    data: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Legacy/Simulated checkout endpoint."""
    session_data = BillingService.create_checkout_session(db, current_user.id, data.plan_slug)
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
    """Retrieves all payment and purchase transactions for the current user."""
    payments = (
        db.query(Payment)
        .filter(Payment.user_id == current_user.id)
        .order_by(Payment.created_at.desc())
        .all()
    )
    result = []
    for p in payments:
        result.append({
            "id": p.id,
            "amount_inr": p.amount_inr,
            "currency": p.currency,
            "status": p.status,
            "provider": p.provider,
            "provider_tx_id": p.provider_tx_id,
            "razorpay_order_id": p.razorpay_order_id,
            "razorpay_payment_id": p.razorpay_payment_id,
            "pack_slug": p.pack_slug or (p.plan.slug if p.plan else "pack"),
            "plan_name": p.plan.name if p.plan else (p.pack_slug or "Credit Top-Up"),
            "credits_granted": p.credits_granted,
            "created_at": p.created_at,
        })
    return result
