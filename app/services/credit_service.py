import datetime
import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.core.config import settings
from app.db.models import CreditBalance, CreditTransaction, Application

logger = logging.getLogger(__name__)


def ensure_user_credits(db: Session, user_id: int) -> CreditBalance:
    """
    Ensures user has an active CreditBalance.
    Grants the free monthly credits (5 per month) if user is new or if 30 days have elapsed.
    """
    now = datetime.datetime.utcnow()
    bal = db.query(CreditBalance).filter(CreditBalance.user_id == user_id).first()
    monthly_credits = getattr(settings, "FREE_MONTHLY_CREDITS", 5)

    if not bal:
        bal = CreditBalance(
            user_id=user_id,
            balance=monthly_credits,
            total_included=monthly_credits,
            total_purchased=0,
            total_used=0,
            last_monthly_grant_at=now,
        )
        db.add(bal)
        db.flush()

        tx = CreditTransaction(
            user_id=user_id,
            application_id=None,
            type="grant",
            amount=monthly_credits,
            balance_before=0,
            balance_after=monthly_credits,
            description=f"Free monthly allowance: {monthly_credits} application credits",
        )
        db.add(tx)
        db.commit()
        db.refresh(bal)
        return bal

    # Monthly renewal check (every 30 days)
    last_grant = bal.last_monthly_grant_at
    if last_grant is None or (now - last_grant).days >= 30:
        before = bal.balance
        after = before + monthly_credits
        bal.balance = after
        bal.total_included += monthly_credits
        bal.last_monthly_grant_at = now

        tx = CreditTransaction(
            user_id=user_id,
            application_id=None,
            type="grant",
            amount=monthly_credits,
            balance_before=before,
            balance_after=after,
            description=f"Monthly free renewal: +{monthly_credits} application credits",
        )
        db.add(tx)
        db.commit()
        db.refresh(bal)

    return bal


def initialize_user_credits(db: Session, user_id: int, initial_credits: int = 5) -> CreditBalance:
    return ensure_user_credits(db, user_id)


def check_has_sufficient_credits(db: Session, user_id: int) -> bool:
    bal = ensure_user_credits(db, user_id)
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
