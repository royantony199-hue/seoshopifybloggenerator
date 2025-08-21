#!/usr/bin/env python3
"""
Analytics and reporting router
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.core.database import get_db, GeneratedBlog, Keyword, UsageTracking
from app.routers.auth import get_current_user, User

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard analytics data"""
    
    # Basic counts
    total_blogs = db.query(GeneratedBlog).filter(
        GeneratedBlog.tenant_id == current_user.tenant_id
    ).count()
    
    published_blogs = db.query(GeneratedBlog).filter(
        GeneratedBlog.tenant_id == current_user.tenant_id,
        GeneratedBlog.published == True
    ).count()
    
    total_keywords = db.query(Keyword).filter(
        Keyword.tenant_id == current_user.tenant_id
    ).count()
    
    # Recent blogs
    recent_blogs = db.query(GeneratedBlog).filter(
        GeneratedBlog.tenant_id == current_user.tenant_id
    ).order_by(GeneratedBlog.created_at.desc()).limit(5).all()
    
    recent_blogs_data = []
    for blog in recent_blogs:
        keyword_text = None
        if blog.keyword_record:
            keyword_text = blog.keyword_record.keyword
            
        recent_blogs_data.append({
            "id": blog.id,
            "title": blog.title,
            "keyword": keyword_text,
            "status": blog.status,
            "live_url": blog.live_url,
            "created_at": blog.created_at.isoformat()
        })
    
    # Performance metrics
    avg_generation_time = db.query(func.avg(GeneratedBlog.generation_time)).filter(
        GeneratedBlog.tenant_id == current_user.tenant_id,
        GeneratedBlog.generation_time.isnot(None)
    ).scalar() or 0
    
    success_rate = (published_blogs / total_blogs * 100) if total_blogs > 0 else 0
    
    total_words = db.query(func.sum(GeneratedBlog.word_count)).filter(
        GeneratedBlog.tenant_id == current_user.tenant_id,
        GeneratedBlog.word_count.isnot(None)
    ).scalar() or 0
    
    return {
        "user_id": current_user.id,
        "tenant_id": current_user.tenant_id,
        "total_blogs": total_blogs,
        "published_blogs": published_blogs,
        "keywords_processed": total_keywords,
        "monthly_usage": {
            "blogs_generated": total_blogs,
            "api_calls": 0,
            "storage_used": f"{total_words // 1000}KB"
        },
        "recent_blogs": recent_blogs_data,
        "performance_metrics": {
            "avg_generation_time": f"{avg_generation_time:.1f}s" if avg_generation_time else "0s",
            "success_rate": f"{success_rate:.1f}%",
            "total_words_generated": int(total_words)
        }
    }