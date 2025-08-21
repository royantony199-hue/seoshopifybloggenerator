#!/usr/bin/env python3
"""
Shopify stores management router
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db, ShopifyStore
from app.routers.auth import get_current_user, User
from app.routers.demo_auth import get_demo_current_user

router = APIRouter()

class StoreCreate(BaseModel):
    store_name: str
    shop_url: str
    access_token: str
    blog_handle: str = "news"
    auto_publish: bool = False
    default_product_url: Optional[str] = None

class StoreUpdate(BaseModel):
    store_name: Optional[str] = None
    shop_url: Optional[str] = None
    access_token: Optional[str] = None
    blog_handle: Optional[str] = None
    auto_publish: Optional[bool] = None
    default_product_url: Optional[str] = None
    is_active: Optional[bool] = None

class StoreResponse(BaseModel):
    id: int
    store_name: str
    shop_url: str
    blog_handle: str
    is_active: bool
    auto_publish: bool
    default_product_url: Optional[str]
    created_at: datetime
    last_sync: Optional[datetime]

@router.get("/", response_model=List[StoreResponse])
async def get_stores(db: Session = Depends(get_db)):
    """Get all stores for current tenant"""
    
    # Get demo user for testing
    current_user = await get_demo_current_user(db)
    
    stores = db.query(ShopifyStore).filter(
        ShopifyStore.tenant_id == current_user.tenant_id
    ).all()
    
    return [StoreResponse(
        id=store.id,
        store_name=store.store_name,
        shop_url=store.shop_url,
        blog_handle=store.blog_handle,
        is_active=store.is_active,
        auto_publish=store.auto_publish,
        default_product_url=store.default_product_url,
        created_at=store.created_at,
        last_sync=store.last_sync
    ) for store in stores]

@router.post("/", response_model=StoreResponse)
async def create_store(
    store_data: StoreCreate,
    db: Session = Depends(get_db)
):
    """Create a new Shopify store"""
    
    # Get demo user for testing
    current_user = await get_demo_current_user(db)
    
    # Check if store with same shop_url already exists
    existing = db.query(ShopifyStore).filter(
        ShopifyStore.tenant_id == current_user.tenant_id,
        ShopifyStore.shop_url == store_data.shop_url
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Store with this shop URL already exists"
        )
    
    store = ShopifyStore(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        store_name=store_data.store_name,
        shop_url=store_data.shop_url,
        access_token=store_data.access_token,
        blog_handle=store_data.blog_handle,
        auto_publish=store_data.auto_publish,
        default_product_url=store_data.default_product_url,
        is_active=True
    )
    
    db.add(store)
    db.commit()
    db.refresh(store)
    
    return StoreResponse(
        id=store.id,
        store_name=store.store_name,
        shop_url=store.shop_url,
        blog_handle=store.blog_handle,
        is_active=store.is_active,
        auto_publish=store.auto_publish,
        default_product_url=store.default_product_url,
        created_at=store.created_at,
        last_sync=store.last_sync
    )

@router.put("/{store_id}", response_model=StoreResponse)
async def update_store(
    store_id: int,
    store_data: StoreUpdate,
    db: Session = Depends(get_db)
):
    """Update a Shopify store"""
    
    # Get demo user for testing
    current_user = await get_demo_current_user(db)
    
    store = db.query(ShopifyStore).filter(
        ShopifyStore.id == store_id,
        ShopifyStore.tenant_id == current_user.tenant_id
    ).first()
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )
    
    # Update only provided fields
    update_data = store_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(store, field, value)
    
    db.commit()
    db.refresh(store)
    
    return StoreResponse(
        id=store.id,
        store_name=store.store_name,
        shop_url=store.shop_url,
        blog_handle=store.blog_handle,
        is_active=store.is_active,
        auto_publish=store.auto_publish,
        default_product_url=store.default_product_url,
        created_at=store.created_at,
        last_sync=store.last_sync
    )

@router.delete("/{store_id}")
async def delete_store(
    store_id: int,
    db: Session = Depends(get_db)
):
    """Delete a Shopify store"""
    
    # Get demo user for testing
    current_user = await get_demo_current_user(db)
    
    store = db.query(ShopifyStore).filter(
        ShopifyStore.id == store_id,
        ShopifyStore.tenant_id == current_user.tenant_id
    ).first()
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )
    
    db.delete(store)
    db.commit()
    
    return {"message": "Store deleted successfully"}

@router.get("/stats")
async def get_stores_stats(db: Session = Depends(get_db)):
    """Get stores statistics"""
    
    # Get demo user for testing
    current_user = await get_demo_current_user(db)
    
    total = db.query(ShopifyStore).filter(
        ShopifyStore.tenant_id == current_user.tenant_id
    ).count()
    
    active = db.query(ShopifyStore).filter(
        ShopifyStore.tenant_id == current_user.tenant_id,
        ShopifyStore.is_active == True
    ).count()
    
    return {
        "total_stores": total,
        "active_stores": active,
        "inactive_stores": total - active
    }