from __future__ import annotations

import logging
import uuid
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.db.models import Plan, Payment, User
from app.services.credit_service import purchase_credits

logger = logging.getLogger(__name__)


class BillingService:
    @staticmethod
    def create_checkout_session(db: Session, user_id: int, plan_slug: str) -> Dict[str, Any]:
        plan = db.query(Plan).filter(Plan.slug == plan_slug, Plan.is_active == True).first()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plan '{plan_slug}' not found or inactive.",
            )

        tx_id = f"tx_{uuid.uuid4().hex[:16]}"

        payment = Payment(
            user_id=user_id,
            plan_id=plan.id,
            amount_inr=plan.price_inr,
            currency="INR",
            status="pending",
            provider="mock_payment_gateway",
            provider_tx_id=tx_id,
            receipt_url=f"/api/v1/billing/receipts/{tx_id}",
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)

        return {
            "checkout_id": payment.id,
            "provider_tx_id": tx_id,
            "plan_name": plan.name,
            "amount_inr": plan.price_inr,
            "currency": "INR",
            "included_applications": plan.included_applications,
            "status": "pending",
        }

    @staticmethod
    def process_payment_success(db: Session, checkout_id: int, user_id: int) -> Payment:
        payment = (
            db.query(Payment)
            .filter(Payment.id == checkout_id, Payment.user_id == user_id)
            .first()
        )
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment checkout session not found",
            )

        if payment.status == "completed":
            return payment

        plan = db.query(Plan).filter(Plan.id == payment.plan_id).first()
        apps_to_add = plan.included_applications if plan else 100

        # Fulfill credits
        purchase_credits(
            db,
            user_id=user_id,
            amount=apps_to_add,
            description=f"Purchased {plan.name if plan else 'Credits'}: +{apps_to_add} Applications",
        )

        payment.status = "completed"
        db.commit()
        db.refresh(payment)
        return payment
