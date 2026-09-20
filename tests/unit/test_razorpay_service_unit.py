import hmac
import hashlib
import json
import time
import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.models import User, Plan, Payment, CreditBalance
from app.services.credit_service import ensure_user_credits
from app.services.razorpay_service import RazorpayService


def get_or_create_test_user(db: Session, email_prefix: str = "rzp_user") -> User:
    email = f"{email_prefix}_{time.time_ns()}@example.com"
    user = User(
        email=email,
        hashed_password=get_password_hash("secret123"),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    ensure_user_credits(db, user.id)
    return user


def test_create_order_starter_pack(db: Session):
    user = get_or_create_test_user(db, "order_starter")
    order = RazorpayService.create_order(db, user.id, "starter_pack")

    assert order["amount"] == 14900  # ₹149 in paise
    assert order["amount_inr"] == 149
    assert order["credits"] == 10
    assert order["plan_slug"] == "starter_pack"
    assert order["currency"] == "INR"
    assert order["order_id"].startswith("order_")

    # Payment record created in DB with status pending
    payment = db.query(Payment).filter(Payment.razorpay_order_id == order["order_id"]).first()
    assert payment is not None
    assert payment.status == "pending"
    assert payment.amount_inr == 149
    assert payment.credits_granted == 0


def test_create_order_job_seeker_pack(db: Session):
    user = get_or_create_test_user(db, "order_seeker")
    order = RazorpayService.create_order(db, user.id, "job_seeker_pack")

    assert order["amount"] == 29900  # ₹299 in paise
    assert order["credits"] == 25
    assert order["plan_slug"] == "job_seeker_pack"


def test_create_order_power_pack(db: Session):
    user = get_or_create_test_user(db, "order_power")
    order = RazorpayService.create_order(db, user.id, "power_pack")

    assert order["amount"] == 49900  # ₹499 in paise
    assert order["credits"] == 50
    assert order["plan_slug"] == "power_pack"


def test_free_plan_order_rejected(db: Session):
    user = get_or_create_test_user(db, "order_free")
    with pytest.raises(HTTPException) as exc:
        RazorpayService.create_order(db, user.id, "free")
    assert exc.value.status_code == 400
    assert "Free plan cannot be purchased" in exc.value.detail


def test_invalid_plan_slug_raises_404(db: Session):
    user = get_or_create_test_user(db, "order_invalid")
    with pytest.raises(HTTPException) as exc:
        RazorpayService.create_order(db, user.id, "non_existent_plan_xyz")
    assert exc.value.status_code == 404


def test_verify_payment_signature_success_and_credits_fulfilled(db: Session):
    user = get_or_create_test_user(db, "verify_success")
    order = RazorpayService.create_order(db, user.id, "starter_pack")
    order_id = order["order_id"]
    payment_id = f"pay_{time.time_ns()}"

    # Compute valid HMAC-SHA256 signature
    msg = f"{order_id}|{payment_id}".encode("utf-8")
    valid_sig = hmac.new(settings.RAZORPAY_KEY_SECRET.encode("utf-8"), msg, hashlib.sha256).hexdigest()

    # Initial balance should be 5 free credits
    bal_before = db.query(CreditBalance).filter(CreditBalance.user_id == user.id).first().balance
    assert bal_before == 5

    # Verify payment
    payment = RazorpayService.verify_payment_signature(
        db=db,
        user_id=user.id,
        razorpay_order_id=order_id,
        razorpay_payment_id=payment_id,
        razorpay_signature=valid_sig,
    )

    assert payment.status == "completed"
    assert payment.razorpay_payment_id == payment_id
    assert payment.credits_granted == 10

    # User balance should now be 5 + 10 = 15
    bal_after = db.query(CreditBalance).filter(CreditBalance.user_id == user.id).first().balance
    assert bal_after == 15

    # Idempotent re-verification - does not grant extra credits
    payment_again = RazorpayService.verify_payment_signature(
        db=db,
        user_id=user.id,
        razorpay_order_id=order_id,
        razorpay_payment_id=payment_id,
        razorpay_signature=valid_sig,
    )
    assert payment_again.id == payment.id
    bal_final = db.query(CreditBalance).filter(CreditBalance.user_id == user.id).first().balance
    assert bal_final == 15


def test_verify_payment_signature_invalid_fails(db: Session):
    user = get_or_create_test_user(db, "verify_fake")
    order = RazorpayService.create_order(db, user.id, "starter_pack")
    order_id = order["order_id"]
    payment_id = f"pay_{time.time_ns()}"
    fake_sig = "forged_signature_attack_string_123456"

    with pytest.raises(HTTPException) as exc:
        RazorpayService.verify_payment_signature(
            db=db,
            user_id=user.id,
            razorpay_order_id=order_id,
            razorpay_payment_id=payment_id,
            razorpay_signature=fake_sig,
        )
    assert exc.value.status_code == 400
    assert "Cryptographic signature verification failed" in exc.value.detail

    # Verify payment status was marked failed and 0 credits granted
    pmt = db.query(Payment).filter(Payment.razorpay_order_id == order_id).first()
    assert pmt.status == "failed"
    bal = db.query(CreditBalance).filter(CreditBalance.user_id == user.id).first().balance
    assert bal == 5


def test_webhook_order_paid_fulfillment(db: Session):
    user = get_or_create_test_user(db, "webhook_user")
    order = RazorpayService.create_order(db, user.id, "job_seeker_pack")  # 25 credits
    order_id = order["order_id"]
    payment_id = f"pay_hook_{time.time_ns()}"

    webhook_payload = {
        "entity": "event",
        "account_id": "acc_test",
        "event": "order.paid",
        "contains": ["payment", "order"],
        "payload": {
            "payment": {
                "entity": {
                    "id": payment_id,
                    "order_id": order_id,
                    "amount": 29900,
                    "status": "captured",
                }
            },
            "order": {
                "entity": {
                    "id": order_id,
                    "amount_paid": 29900,
                    "status": "paid",
                }
            }
        }
    }
    raw_body = json.dumps(webhook_payload).encode("utf-8")
    sig = hmac.new(settings.RAZORPAY_WEBHOOK_SECRET.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()

    result = RazorpayService.process_webhook(db, raw_body=raw_body, signature=sig)
    assert result["status"] == "fulfilled"
    assert result["credits_granted"] == 25

    # Credits granted in DB: 5 + 25 = 30
    bal = db.query(CreditBalance).filter(CreditBalance.user_id == user.id).first().balance
    assert bal == 30

    # Repeating webhook (duplicate webhook delivery) does not grant extra credits
    result_dup = RazorpayService.process_webhook(db, raw_body=raw_body, signature=sig)
    assert result_dup["status"] == "received"
    bal_after = db.query(CreditBalance).filter(CreditBalance.user_id == user.id).first().balance
    assert bal_after == 30
