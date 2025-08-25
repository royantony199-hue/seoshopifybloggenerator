#!/usr/bin/env python3
"""
Monitor Blog Generation Status
"""

import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Keyword, GeneratedBlog
from app.core.config import settings
from datetime import datetime, timedelta

def monitor_blog_generation():
    """Monitor blog generation status in real-time"""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    print("Blog Generation Monitor")
    print("=" * 60)
    print("Press Ctrl+C to stop")
    print()
    
    try:
        while True:
            # Get recent keywords
            recent_keywords = db.query(Keyword).filter(
                Keyword.created_at >= datetime.utcnow() - timedelta(hours=1)
            ).order_by(Keyword.created_at.desc()).limit(10).all()
            
            # Get recent blogs
            recent_blogs = db.query(GeneratedBlog).filter(
                GeneratedBlog.created_at >= datetime.utcnow() - timedelta(hours=1)
            ).order_by(GeneratedBlog.created_at.desc()).limit(10).all()
            
            # Clear screen
            print("\033[2J\033[H")  # Clear screen and move cursor to top
            
            print(f"Blog Generation Status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 60)
            
            print("\nRecent Keywords (Last Hour):")
            print("-" * 40)
            if recent_keywords:
                for kw in recent_keywords:
                    status_icon = {
                        'pending': '⏳',
                        'processing': '🔄',
                        'completed': '✅',
                        'failed': '❌'
                    }.get(kw.status, '❓')
                    
                    print(f"{status_icon} [{kw.id}] {kw.keyword[:50]}")
                    print(f"   Status: {kw.status} | Created: {kw.created_at.strftime('%H:%M:%S')}")
            else:
                print("   No recent keywords")
            
            print("\nRecent Blog Generation (Last Hour):")
            print("-" * 40)
            if recent_blogs:
                for blog in recent_blogs:
                    status_icon = {
                        'draft': '📝',
                        'published': '🌐',
                        'failed': '❌'
                    }.get(blog.status, '❓')
                    
                    print(f"{status_icon} [{blog.id}] {blog.title[:50]}...")
                    print(f"   Status: {blog.status} | Words: {blog.word_count} | Time: {blog.generation_time:.1f}s")
                    if blog.error_message:
                        print(f"   ❌ Error: {blog.error_message}")
            else:
                print("   No recent blog generations")
            
            # Refresh database session
            db.close()
            db = SessionLocal()
            
            # Wait 5 seconds before next update
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")
    finally:
        db.close()

if __name__ == "__main__":
    monitor_blog_generation()