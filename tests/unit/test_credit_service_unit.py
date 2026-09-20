import time
import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.models import User, CreditBalance, CreditTransaction, Application, JobListing
from app.core.security import get_password_hash
from app.services.credit_service import (
    initialize_user_credits,
    check_has_sufficient_credits,
    deduct_credit_for_application,
    refund_credit_for_application,
    purchase_credits,
)

def test_initialize_user_credits(db: Session):
    user = User(email=f"credits_user_1_{time.time_ns()}@test.com", hashed_password=get_password_hash("pass"), is_active=True)
    db.add(user)
    db.commit()

    bal = initialize_user_credits(db, user.id, 100)
    assert bal.balance == 100
    assert bal.total_included == 100

    # Test idempotency - calling again does not grant another 100
    bal_second = initialize_user_credits(db, user.id, 100)
    assert bal_second.balance == 100

    tx = db.query(CreditTransaction).filter(CreditTransaction.user_id == user.id).first()
    assert tx is not None
    assert tx.type == "grant"
    assert tx.amount == 100

def test_deduct_and_refund_flow(db: Session):
    user = User(email=f"credits_user_2_{time.time_ns()}@test.com", hashed_password=get_password_hash("pass"), is_active=True)
    db.add(user)
    db.commit()
    initialize_user_credits(db, user.id, 5)

    job = JobListing(title="Test Job", company="Test Corp", url=f"https://example.com/job2_{time.time_ns()}", source="test")
    db.add(job)
    db.commit()

    app_rec = Application(user_id=user.id, job_id=job.id, status="queued")
    db.add(app_rec)
    db.commit()

    # Deduct 1 credit
    deduct_tx = deduct_credit_for_application(db, user.id, app_rec.id)
    assert deduct_tx.amount == -1
    assert deduct_tx.balance_after == 4

    # Idempotent deduction check - deduplication
    deduct_tx_dup = deduct_credit_for_application(db, user.id, app_rec.id)
    assert deduct_tx_dup.id == deduct_tx.id
    bal_after = db.query(CreditBalance).filter(CreditBalance.user_id == user.id).first()
    assert bal_after.balance == 4

    # Refund credit
    refund_tx = refund_credit_for_application(db, user.id, app_rec.id, reason="Portal error")
    assert refund_tx is not None
    assert refund_tx.amount == 1
    assert refund_tx.balance_after == 5

    # Idempotent refund check
    refund_tx_dup = refund_credit_for_application(db, user.id, app_rec.id, reason="Portal error")
    assert refund_tx_dup.id == refund_tx.id

def test_insufficient_credits_raises_402(db: Session):
    user = User(email=f"credits_user_empty_{time.time_ns()}@test.com", hashed_password=get_password_hash("pass"), is_active=True)
    db.add(user)
    db.commit()
    initialize_user_credits(db, user.id, 0)

    job = JobListing(title="Job 3", company="Co", url=f"https://example.com/job3_{time.time_ns()}", source="test")
    db.add(job)
    db.commit()

    app_rec = Application(user_id=user.id, job_id=job.id, status="queued")
    db.add(app_rec)
    db.commit()

    with pytest.raises(HTTPException) as exc_info:
        deduct_credit_for_application(db, user.id, app_rec.id)
    assert exc_info.value.status_code == 402

def test_grant_purchased_credits(db: Session):
    user = User(email=f"credits_user_purchase_{time.time_ns()}@test.com", hashed_password=get_password_hash("pass"), is_active=True)
    db.add(user)
    db.commit()
    initialize_user_credits(db, user.id, 10)

    purchase_credits(db, user.id, 250, "Pro Plan Upgrade")
    bal = db.query(CreditBalance).filter(CreditBalance.user_id == user.id).first()
    assert bal.balance == 260
    assert bal.total_purchased == 250
