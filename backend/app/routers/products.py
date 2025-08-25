#!/usr/bin/env python3
"""
Products management router for blog integration
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db, Product, ShopifyStore
from app.routers.demo_auth import get_demo_current_user

router = APIRouter()

# Pydantic models
class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    url: str
    price: Optional[str] = None
    keywords: Optional[str] = None
    integration_text: Optional[str] = None
    store_id: int
    priority: int = 0

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    price: Optional[str] = None
    keywords: Optional[str] = None
    integration_text: Optional[str] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    url: str
    price: Optional[str]
    keywords: Optional[str]
    integration_text: Optional[str]
    store_id: int
    is_active: bool
    priority: int
    created_at: datetime

# Routes
@router.get("/", response_model=List[ProductResponse])
async def get_products(
    store_id: Optional[int] = None,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get products for current tenant"""
    
    # Get demo user for testing
    current_user = await get_demo_current_user(db)
    
    query = db.query(Product).filter(Product.tenant_id == current_user.tenant_id)
    
    if store_id:
        query = query.filter(Product.store_id == store_id)
    
    if active_only:
        query = query.filter(Product.is_active == True)
    
    products = query.order_by(Product.priority.desc(), Product.created_at.desc()).all()
    
    return products

@router.post("/", response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db)
):
    """Create a new product"""
    
    # Get demo user for testing
    current_user = await get_demo_current_user(db)
    
    # Verify store belongs to user's tenant
    store = db.query(ShopifyStore).filter(
        ShopifyStore.id == product_data.store_id,
        ShopifyStore.tenant_id == current_user.tenant_id
    ).first()
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )
    
    # Create product
    product = Product(
        tenant_id=current_user.tenant_id,
        store_id=product_data.store_id,
        name=product_data.name,
        description=product_data.description,
        url=product_data.url,
        price=product_data.price,
        keywords=product_data.keywords,
        integration_text=product_data.integration_text,
        priority=product_data.priority
    )
    
    db.add(product)
    db.commit()
    db.refresh(product)
    
    return product

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db)
):
    """Update a product"""
    
    # Get demo user for testing
    current_user = await get_demo_current_user(db)
    
    # Get product
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.tenant_id == current_user.tenant_id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Update fields
    update_data = product_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    
    return product

@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Delete a product"""
    
    # Get demo user for testing
    current_user = await get_demo_current_user(db)
    
    # Get product
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.tenant_id == current_user.tenant_id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    db.delete(product)
    db.commit()
    
    return {"message": "Product deleted successfully"}

@router.get("/by-keywords/{keyword}")
async def get_products_by_keyword(
    keyword: str,
    store_id: int,
    db: Session = Depends(get_db)
):
    """Get products that match a specific keyword for blog integration"""
    
    # Get demo user for testing
    current_user = await get_demo_current_user(db)
    
    # Search for products that have this keyword in their keywords field
    products = db.query(Product).filter(
        Product.tenant_id == current_user.tenant_id,
        Product.store_id == store_id,
        Product.is_active == True,
        Product.keywords.ilike(f"%{keyword}%")
    ).order_by(Product.priority.desc()).limit(3).all()
    
    return [
        {
            "id": p.id,
            "name": p.name,
            "url": p.url,
            "price": p.price,
            "integration_text": p.integration_text or f"Check out our {p.name} - the perfect solution for your needs!"
        }
        for p in products
    ]