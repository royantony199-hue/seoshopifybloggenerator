#!/usr/bin/env python3
"""
Database configuration and models for multi-tenant SaaS
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional

from app.core.config import settings

# Database connection
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Database Models with Multi-tenant Architecture

class Tenant(Base):
    """Tenant/Organization model for multi-tenancy"""
    __tablename__ = "tenants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False, index=True)
    domain = Column(String, unique=True, nullable=True)  # Custom domain
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Subscription info
    subscription_plan = Column(String, default="starter")
    subscription_status = Column(String, default="trial")  # trial, active, suspended, cancelled
    trial_ends_at = Column(DateTime(timezone=True), nullable=True)
    
    # Usage tracking
    monthly_blog_limit = Column(Integer, default=100)
    monthly_blogs_used = Column(Integer, default=0)
    
    # Relationships
    users = relationship("User", back_populates="tenant")
    stores = relationship("ShopifyStore", back_populates="tenant")
    keywords = relationship("Keyword", back_populates="tenant")
    blogs = relationship("GeneratedBlog", back_populates="tenant")

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    role = Column(String, default="user")  # admin, user
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # API Keys for external services
    openai_api_key = Column(String, nullable=True)
    serper_api_key = Column(String, nullable=True)
    unsplash_api_key = Column(String, nullable=True)
    google_sheets_credentials = Column(Text, nullable=True)
    google_sheets_id = Column(String, nullable=True)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    stores = relationship("ShopifyStore", back_populates="user")

class ShopifyStore(Base):
    """Shopify store integration"""
    __tablename__ = "shopify_stores"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    store_name = Column(String, nullable=False)
    shop_url = Column(String, nullable=False)  # e.g., "mystore"
    access_token = Column(String, nullable=False)
    blog_handle = Column(String, default="news")
    
    # Store settings
    is_active = Column(Boolean, default=True)
    auto_publish = Column(Boolean, default=False)
    
    # Product integration
    default_product_url = Column(String, nullable=True)
    product_integration_text = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_sync = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="stores")
    user = relationship("User", back_populates="stores")
    blogs = relationship("GeneratedBlog", back_populates="store")
    products = relationship("Product", back_populates="store")

class Product(Base):
    """Product catalog for blog integration"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    store_id = Column(Integer, ForeignKey("shopify_stores.id"), nullable=False)
    
    # Product details
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String, nullable=False)  # Product URL
    price = Column(String, nullable=True)  # e.g., "$29.99"
    
    # SEO and marketing
    keywords = Column(Text, nullable=True)  # Comma-separated keywords this product relates to
    integration_text = Column(Text, nullable=True)  # Custom text for blog integration
    
    # Status
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)  # Higher priority products shown first
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant")
    store = relationship("ShopifyStore", back_populates="products")

class KeywordCampaign(Base):
    """Keyword campaign for organizing keyword sets"""
    __tablename__ = "keyword_campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    template_type = Column(String, default="ecommerce_general")
    
    # Campaign settings
    min_words = Column(Integer, default=2000)
    faq_count = Column(Integer, default=15)
    auto_generate = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    keywords = relationship("Keyword", back_populates="campaign")

class Keyword(Base):
    """Keyword tracking"""
    __tablename__ = "keywords"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    campaign_id = Column(Integer, ForeignKey("keyword_campaigns.id"), nullable=True)
    
    keyword = Column(String, nullable=False, index=True)
    search_volume = Column(Integer, nullable=True)
    keyword_difficulty = Column(Float, nullable=True)
    category = Column(String, nullable=True)
    
    # Processing status
    status = Column(String, default="pending")  # pending, processing, completed, failed
    blog_generated = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="keywords")
    campaign = relationship("KeywordCampaign", back_populates="keywords")
    blogs = relationship("GeneratedBlog", back_populates="keyword_record")

class GeneratedBlog(Base):
    """Generated blog content tracking"""
    __tablename__ = "generated_blogs"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    store_id = Column(Integer, ForeignKey("shopify_stores.id"), nullable=True)
    keyword_id = Column(Integer, ForeignKey("keywords.id"), nullable=True)
    
    # Blog content
    title = Column(String, nullable=False)
    content_html = Column(Text, nullable=False)
    meta_description = Column(String, nullable=True)
    word_count = Column(Integer, nullable=True)
    
    # Shopify integration
    shopify_article_id = Column(String, nullable=True)
    shopify_handle = Column(String, nullable=True)
    live_url = Column(String, nullable=True)
    published = Column(Boolean, default=False)
    
    # Featured image
    featured_image_url = Column(String, nullable=True)
    image_prompt_used = Column(Text, nullable=True)
    image_generated = Column(Boolean, default=False)
    
    # Generation metadata
    template_used = Column(String, nullable=True)
    generation_time = Column(Float, nullable=True)  # seconds
    tokens_used = Column(Integer, nullable=True)
    
    # Status tracking
    status = Column(String, default="draft")  # draft, published, failed
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="blogs")
    store = relationship("ShopifyStore", back_populates="blogs")
    keyword_record = relationship("Keyword", back_populates="blogs")

class UsageTracking(Base):
    """Track API usage and billing metrics"""
    __tablename__ = "usage_tracking"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    
    # Usage metrics
    date = Column(DateTime(timezone=True), server_default=func.now())
    blogs_generated = Column(Integer, default=0)
    openai_tokens_used = Column(Integer, default=0)
    api_calls_made = Column(Integer, default=0)
    
    # Cost tracking
    estimated_cost = Column(Float, default=0.0)

class BillingRecord(Base):
    """Billing and subscription records"""
    __tablename__ = "billing_records"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    
    # Stripe integration
    stripe_subscription_id = Column(String, nullable=True)
    stripe_customer_id = Column(String, nullable=True)
    
    # Billing details
    plan = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    interval = Column(String, default="month")
    
    # Status
    status = Column(String, nullable=False)  # active, cancelled, past_due
    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Database utility functions

async def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Export all models for easy importing
__all__ = ["User", "Tenant", "ShopifyStore", "Product", "KeywordCampaign", "Keyword", "GeneratedBlog", "BillingRecord"]