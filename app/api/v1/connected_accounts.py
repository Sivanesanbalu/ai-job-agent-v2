from __future__ import annotations

import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.auth_middleware import get_current_user
from app.db.session import get_db
from app.db.models import User, ConnectedAccount
from app.schemas import ConnectedAccountOut, ConnectedAccountCreate

router = APIRouter(prefix="/connected-accounts", tags=["Connected Accounts"])


@router.get("", response_model=List[ConnectedAccountOut])
def list_connected_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    accounts = (
        db.query(ConnectedAccount)
        .filter(ConnectedAccount.user_id == current_user.id)
        .all()
    )
    # Ensure standard platforms are returned
    platforms = {"linkedin", "naukri", "indeed"}
    found_platforms = {a.platform for a in accounts}

    for p in platforms - found_platforms:
        dummy = ConnectedAccount(
            user_id=current_user.id,
            platform=p,
            account_identifier="",
            auth_status="not_connected",
            credentials_encrypted={},
        )
        db.add(dummy)
    if platforms - found_platforms:
        db.commit()
        accounts = (
            db.query(ConnectedAccount)
            .filter(ConnectedAccount.user_id == current_user.id)
            .all()
        )

    return accounts


@router.post("", response_model=ConnectedAccountOut)
def connect_account(
    data: ConnectedAccountCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    acc = (
        db.query(ConnectedAccount)
        .filter(
            ConnectedAccount.user_id == current_user.id,
            ConnectedAccount.platform == data.platform.lower(),
        )
        .first()
    )
    if not acc:
        acc = ConnectedAccount(
            user_id=current_user.id,
            platform=data.platform.lower(),
            account_identifier=data.account_identifier,
            auth_status="connected",
            credentials_encrypted=data.credentials or {},
            last_verified_at=datetime.datetime.utcnow(),
        )
        db.add(acc)
    else:
        acc.account_identifier = data.account_identifier
        acc.auth_status = "connected"
        acc.credentials_encrypted = data.credentials or {}
        acc.last_verified_at = datetime.datetime.utcnow()

    db.commit()
    db.refresh(acc)
    return acc


@router.delete("/{account_id}")
def disconnect_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    acc = (
        db.query(ConnectedAccount)
        .filter(
            ConnectedAccount.id == account_id,
            ConnectedAccount.user_id == current_user.id,
        )
        .first()
    )
    if not acc:
        raise HTTPException(status_code=404, detail="Connected account not found.")

    acc.account_identifier = ""
    acc.auth_status = "not_connected"
    acc.credentials_encrypted = {}
    acc.last_verified_at = None
    db.commit()

    return {"status": "ok", "message": "Account disconnected successfully."}
