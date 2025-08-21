#!/usr/bin/env python3
"""
Demo authentication for testing without JWT tokens
"""

from sqlalchemy.orm import Session
from app.core.database import get_db, User, Tenant

def get_demo_user(db: Session):
    """Get or create demo user for testing"""
    user = db.query(User).filter(User.email == "demo@example.com").first()
    if not user:
        # Create demo tenant
        tenant = Tenant(
            name='Demo Company',
            slug='demo-company',
            subscription_plan='professional',
            subscription_status='trial',
            monthly_blog_limit=500,
            monthly_blogs_used=0
        )
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        
        # Create demo user  
        from app.routers.auth import get_password_hash
        user = User(
            tenant_id=tenant.id,
            email='demo@example.com',
            hashed_password=get_password_hash('demo123'),
            first_name='Demo',
            last_name='User',
            role='admin'
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user

async def get_demo_current_user(db: Session):
    """Demo version that always returns the demo user"""
    return get_demo_user(db)