from __future__ import annotations

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.auth_middleware import get_current_user
from app.db.session import get_db
from app.db.models import User, CreditBalance, CreditTransaction
from app.schemas import CreditBalanceOut, CreditTransactionOut

router = APIRouter(prefix="/credits", tags=["Credits"])


@router.get("", response_model=CreditBalanceOut)
def get_credits(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cb = db.query(CreditBalance).filter(CreditBalance.user_id == current_user.id).first()
    if not cb:
        cb = CreditBalance(
            user_id=current_user.id,
            balance=100,
            total_included=100,
            total_purchased=0,
            total_used=0,
        )
        db.add(cb)
        db.commit()
        db.refresh(cb)
    return cb


@router.get("/transactions", response_model=List[CreditTransactionOut])
def get_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(CreditTransaction)
        .filter(CreditTransaction.user_id == current_user.id)
        .order_by(CreditTransaction.created_at.desc())
        .limit(100)
        .all()
    )
