#!/usr/bin/env python3
"""
Configuration management for SEO Blog Automation SaaS
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # App Info
    APP_NAME: str = "SEO Blog Automation SaaS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "sqlite:///./seo_saas.db"
    
    # Redis (for caching and background tasks)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "https://yourdomain.com"
    ]
    
    # External APIs  
    OPENAI_API_KEY: Optional[str] = None
    
    # Default for missing env var
    SENTRY_DSN: Optional[str] = None
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # Stripe
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600  # 1 hour
    
    # File Storage
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_S3_BUCKET: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    
    # Business Logic
    MAX_KEYWORDS_PER_UPLOAD: int = 10000
    MAX_BLOGS_PER_BATCH: int = 50
    DEFAULT_BLOG_MIN_WORDS: int = 2000
    DEFAULT_FAQ_COUNT: int = 15
    
    # Subscription Limits
    STARTER_MONTHLY_BLOGS: int = 100
    PROFESSIONAL_MONTHLY_BLOGS: int = 500
    ENTERPRISE_MONTHLY_BLOGS: int = 2000
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings instance
settings = Settings()

# Plan configurations
SUBSCRIPTION_PLANS = {
    "starter": {
        "name": "Starter",
        "price": 99.00,
        "currency": "USD",
        "interval": "month",
        "max_stores": 1,
        "monthly_blogs": settings.STARTER_MONTHLY_BLOGS,
        "features": [
            "1 Shopify store",
            "100 blogs/month",
            "Basic templates",
            "Email support"
        ]
    },
    "professional": {
        "name": "Professional", 
        "price": 299.00,
        "currency": "USD",
        "interval": "month",
        "max_stores": 3,
        "monthly_blogs": settings.PROFESSIONAL_MONTHLY_BLOGS,
        "features": [
            "3 Shopify stores",
            "500 blogs/month", 
            "Custom templates",
            "Priority support",
            "Analytics dashboard"
        ]
    },
    "enterprise": {
        "name": "Enterprise",
        "price": 799.00, 
        "currency": "USD",
        "interval": "month",
        "max_stores": -1,  # Unlimited
        "monthly_blogs": settings.ENTERPRISE_MONTHLY_BLOGS,
        "features": [
            "Unlimited stores",
            "2000 blogs/month",
            "White-label option", 
            "API access",
            "Dedicated support"
        ]
    }
}

# Blog generation templates
BLOG_TEMPLATES = {
    "cbd_wellness": {
        "name": "CBD & Wellness",
        "description": "Optimized for CBD and wellness products",
        "sections": [
            "Introduction",
            "Benefits & Science", 
            "Usage Guidelines",
            "Safety Information",
            "Product Recommendations",
            "Comprehensive FAQ",
            "Conclusion"
        ],
        "min_words": 2500,
        "faq_count": 18
    },
    "ecommerce_general": {
        "name": "E-commerce General",
        "description": "General product-focused content",
        "sections": [
            "Product Overview",
            "Key Features",
            "Benefits",
            "How to Choose", 
            "Product Comparisons",
            "FAQ Section",
            "Conclusion"
        ],
        "min_words": 2000,
        "faq_count": 15
    },
    "service_business": {
        "name": "Service Business",
        "description": "Service-oriented content",
        "sections": [
            "Service Overview",
            "Why Choose Us",
            "Process & Methodology",
            "Case Studies",
            "Pricing Guide",
            "FAQ Section", 
            "Get Started"
        ],
        "min_words": 1800,
        "faq_count": 12
    }
}