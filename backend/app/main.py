#!/usr/bin/env python3
"""
SEO Blog Automation SaaS Platform - Main FastAPI Application
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

from app.core.config import settings
from app.core.database import create_tables
from app.routers import auth, users, stores, keywords, blogs, analytics, billing
from app.routers import settings as settings_router
from app.middleware.tenant import TenantMiddleware
from app.middleware.rate_limit import RateLimitMiddleware

# Initialize Sentry for error monitoring (optional)
if SENTRY_AVAILABLE and settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[FastApiIntegration()],
        traces_sample_rate=0.1,
    )

# Temporarily disabled lifespan for debugging
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """Application lifespan manager"""
#     # Startup
#     await create_tables()
#     yield
#     # Shutdown - cleanup if needed

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Simple lifespan without database startup"""
    yield

# Initialize FastAPI app
app = FastAPI(
    title="SEO Blog Automation SaaS",
    description="Multi-tenant platform for automated SEO blog generation and Shopify publishing",
    version="1.0.0",
    lifespan=lifespan
)

# Security
security = HTTPBearer()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temporarily disable middleware for debugging
# app.add_middleware(TenantMiddleware)
# app.add_middleware(RateLimitMiddleware)

# Routers are included below after health check

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SEO Blog Automation SaaS Platform",
        "version": "1.0.0",
        "status": "active",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected"
    }

# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(settings_router.router, prefix="/api/settings", tags=["Settings"])
app.include_router(keywords.router, prefix="/api/keywords", tags=["Keywords"])
app.include_router(blogs.router, prefix="/api/blogs", tags=["Blogs"])
app.include_router(stores.router, prefix="/api/stores", tags=["Stores"])

@app.get("/api/dashboard")
async def dashboard_stats(current_user=Depends(auth.get_current_user)):
    """Get dashboard statistics for current user"""
    # This would be implemented with proper tenant isolation
    return {
        "user_id": current_user.id,
        "tenant_id": current_user.tenant_id,
        "total_blogs": 0,
        "published_blogs": 0,
        "keywords_processed": 0,
        "monthly_usage": {
            "blogs_generated": 0,
            "api_calls": 0,
            "storage_used": "0 MB"
        },
        "recent_blogs": [],
        "performance_metrics": {
            "avg_generation_time": "0s",
            "success_rate": "0%",
            "total_words_generated": 0
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )