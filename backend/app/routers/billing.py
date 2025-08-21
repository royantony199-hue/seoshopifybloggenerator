#!/usr/bin/env python3
"""
Billing and subscription management router
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db, Tenant
from app.routers.auth import get_current_user, User
from app.core.config import SUBSCRIPTION_PLANS

router = APIRouter()

@router.get("/subscription")
async def get_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current subscription details"""
    
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    
    plan_details = SUBSCRIPTION_PLANS.get(tenant.subscription_plan, SUBSCRIPTION_PLANS["starter"])
    
    return {
        "plan": tenant.subscription_plan,
        "status": tenant.subscription_status,
        "trial_ends_at": tenant.trial_ends_at.isoformat() if tenant.trial_ends_at else None,
        "monthly_blog_limit": tenant.monthly_blog_limit,
        "monthly_blogs_used": tenant.monthly_blogs_used,
        "plan_details": plan_details,
        "usage_percentage": (tenant.monthly_blogs_used / tenant.monthly_blog_limit * 100) if tenant.monthly_blog_limit > 0 else 0
    }

@router.get("/plans")
async def get_available_plans():
    """Get all available subscription plans"""
    return {"plans": SUBSCRIPTION_PLANS}