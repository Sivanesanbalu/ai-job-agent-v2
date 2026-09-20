from __future__ import annotations

import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.db.models import CreditBalance, CreditTransaction, Application

logger = logging.getLogger(__name__)


def initialize_user_credits(db: Session, user_id: int, initial_credits: int = 100) -> CreditBalance:
    existing = db.query(CreditBalance).filter(CreditBalance.user_id == user_id).first()
    if existing:
        return existing

    credit_bal = CreditBalance(
        user_id=user_id,
        balance=initial_credits,
        total_included=initial_credits,
        total_purchased=0,
        total_used=0,
    )
    db.add(credit_bal)
    db.flush()

    tx = CreditTransaction(
        user_id=user_id,
        application_id=None,
        type="grant",
        amount=initial_credits,
        balance_before=0,
        balance_after=initial_credits,
        description="Welcome bonus: 100 free job applications",
    )
    db.add(tx)
    db.commit()
    db.refresh(credit_bal)
    return credit_bal


def check_has_sufficient_credits(db: Session, user_id: int) -> bool:
    bal = db.query(CreditBalance).filter(CreditBalance.user_id == user_id).first()
    return bal is not None and bal.balance > 0


def deduct_credit_for_application(db: Session, user_id: int, application_id: int) -> CreditTransaction:
    """
    Atomically deduct 1 application credit with row-level locking.
    Prevents double charging for the same application.
    """
    # Check for existing deduction for this application
    existing_tx = (
        db.query(CreditTransaction)
        .filter(
            CreditTransaction.user_id == user_id,
            CreditTransaction.application_id == application_id,
            CreditTransaction.type == "deduction",
        )
        .first()
    )
    if existing_tx:
        # Already deducted for this application (idempotent)
        return existing_tx

    # Lock credit balance record
    credit_record = (
        db.query(CreditBalance)
        .filter(CreditBalance.user_id == user_id)
        .with_for_update()
        .first()
    )

    if not credit_record or credit_record.balance < 1:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Insufficient application credits. Please purchase additional credits to continue automated applications.",
        )

    before = credit_record.balance
    after = before - 1

    credit_record.balance = after
    credit_record.total_used += 1

    tx = CreditTransaction(
        user_id=user_id,
        application_id=application_id,
        type="deduction",
        amount=-1,
        balance_before=before,
        balance_after=after,
        description=f"Automated submission credit for application #{application_id}",
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


def refund_credit_for_application(db: Session, user_id: int, application_id: int, reason: str = "Application failed") -> CreditTransaction:
    # Check if a deduction actually occurred
    deduction_tx = (
        db.query(CreditTransaction)
        .filter(
            CreditTransaction.user_id == user_id,
            CreditTransaction.application_id == application_id,
            CreditTransaction.type == "deduction",
        )
        .first()
    )
    if not deduction_tx:
        return None

    # Check if already refunded
    refund_tx = (
        db.query(CreditTransaction)
        .filter(
            CreditTransaction.user_id == user_id,
            CreditTransaction.application_id == application_id,
            CreditTransaction.type == "refund",
        )
        .first()
    )
    if refund_tx:
        return refund_tx

    credit_record = (
        db.query(CreditBalance)
        .filter(CreditBalance.user_id == user_id)
        .with_for_update()
        .first()
    )
    before = credit_record.balance
    after = before + 1

    credit_record.balance = after
    credit_record.total_used = max(0, credit_record.total_used - 1)

    tx = CreditTransaction(
        user_id=user_id,
        application_id=application_id,
        type="refund",
        amount=1,
        balance_before=before,
        balance_after=after,
        description=f"Refund for application #{application_id}: {reason}",
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


def purchase_credits(db: Session, user_id: int, amount: int, description: str) -> CreditTransaction:
    credit_record = (
        db.query(CreditBalance)
        .filter(CreditBalance.user_id == user_id)
        .with_for_update()
        .first()
    )
    before = credit_record.balance
    after = before + amount

    credit_record.balance = after
    credit_record.total_purchased += amount

    tx = CreditTransaction(
        user_id=user_id,
        application_id=None,
        type="purchase",
        amount=amount,
        balance_before=before,
        balance_after=after,
        description=description,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx
