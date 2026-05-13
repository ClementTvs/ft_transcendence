"""
API key management — requires JWT authentication (normal user login).

POST   /api/apikeys          Generate a new key
GET    /api/apikeys          List your keys (key value masked)
DELETE /api/apikeys/{key_id} Revoke a key
"""

import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models import APIKey, User
from app.auth import get_current_active_user

router = APIRouter(prefix="/api/apikeys", tags=["API Keys"])


class APIKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)


class APIKeyOut(BaseModel):
    id: int
    name: str
    key: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("", response_model=APIKeyOut, status_code=status.HTTP_201_CREATED,
             summary="Generate a new API key")
def create_api_key(
    body: APIKeyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Creates a new API key. The full key is only shown once — save it immediately."""
    active_count = (
        db.query(APIKey)
        .filter(APIKey.user_id == current_user.id, APIKey.is_active == True)
        .count()
    )
    if active_count >= 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum of 10 active API keys reached. Revoke one first.",
        )
    raw_key = "sk_" + secrets.token_urlsafe(32)
    record = APIKey(key=raw_key, name=body.name, user_id=current_user.id)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("", response_model=List[APIKeyOut], summary="List your API keys")
def list_api_keys(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Returns all API keys for the authenticated user. Key values are masked."""
    keys = (
        db.query(APIKey)
        .filter(APIKey.user_id == current_user.id)
        .order_by(APIKey.created_at.desc())
        .all()
    )
    # Mask key in list view — show prefix + last 4 chars only
    for k in keys:
        k.key = k.key[:6] + "••••••••" + k.key[-4:]
    return keys


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Revoke an API key")
def revoke_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Permanently deactivates the API key."""
    record = (
        db.query(APIKey)
        .filter(APIKey.id == key_id, APIKey.user_id == current_user.id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="API key not found")
    record.is_active = False
    db.commit()
