#!/usr/bin/env python3
"""
Settings management router - API keys, user preferences
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db, User
from app.routers.auth import get_current_user
from app.routers.demo_auth import get_demo_current_user

router = APIRouter()

# Pydantic models
class APIKeysRequest(BaseModel):
    openai_api_key: Optional[str] = None
    serper_api_key: Optional[str] = None
    unsplash_api_key: Optional[str] = None
    google_sheets_credentials: Optional[str] = None
    google_sheets_id: Optional[str] = None

class APIKeysResponse(BaseModel):
    openai_api_key: Optional[str] = None
    serper_api_key: Optional[str] = None
    unsplash_api_key: Optional[str] = None
    google_sheets_credentials: Optional[str] = None
    google_sheets_id: Optional[str] = None

def mask_api_key(api_key: Optional[str]) -> Optional[str]:
    """Mask API key for security"""
    if not api_key:
        return None
    if len(api_key) <= 8:
        return api_key
    return api_key[:4] + "..." + api_key[-4:]

@router.get("/api-keys", response_model=APIKeysResponse)
async def get_api_keys(db: Session = Depends(get_db)):
    """Get current user's API keys (masked for security)"""
    
    # Get demo user for testing
    current_user = await get_demo_current_user(db)
    
    return APIKeysResponse(
        openai_api_key=mask_api_key(current_user.openai_api_key),
        serper_api_key=mask_api_key(current_user.serper_api_key),
        unsplash_api_key=mask_api_key(current_user.unsplash_api_key),
        google_sheets_credentials=mask_api_key(current_user.google_sheets_credentials),
        google_sheets_id=current_user.google_sheets_id
    )

@router.post("/api-keys")
async def save_api_keys(
    request: APIKeysRequest,
    db: Session = Depends(get_db)
):
    """Save API keys for current user"""
    
    # Get demo user for testing
    current_user = await get_demo_current_user(db)
    
    # Update only provided keys (don't clear existing ones)
    if request.openai_api_key is not None:
        current_user.openai_api_key = request.openai_api_key
    
    if request.serper_api_key is not None:
        current_user.serper_api_key = request.serper_api_key
    
    if request.unsplash_api_key is not None:
        current_user.unsplash_api_key = request.unsplash_api_key
    
    if request.google_sheets_credentials is not None:
        current_user.google_sheets_credentials = request.google_sheets_credentials
    
    if request.google_sheets_id is not None:
        current_user.google_sheets_id = request.google_sheets_id
    
    db.commit()
    
    return {
        "success": True,
        "message": "API keys saved successfully"
    }

@router.get("/profile")
async def get_user_profile(db: Session = Depends(get_db)):
    """Get current user profile"""
    
    # Get demo user for testing
    current_user = await get_demo_current_user(db)
    
    return {
        "id": current_user.id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "role": current_user.role,
        "tenant_id": current_user.tenant_id,
        "has_openai_key": bool(current_user.openai_api_key),
        "has_serper_key": bool(current_user.serper_api_key),
        "has_unsplash_key": bool(current_user.unsplash_api_key),
        "has_google_sheets": bool(current_user.google_sheets_credentials),
    }