#!/usr/bin/env python3
"""
Test Blog Generation with Product Integration
"""

import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Keyword, User
from app.core.config import settings
from app.routers.blogs import generate_single_blog

async def test_blog_generation():
    """Test generating a blog with product integration"""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Get demo user
        user = db.query(User).filter(User.email == "demo@example.com").first()
        
        # Get a CBD-related keyword
        keyword = db.query(Keyword).filter(
            Keyword.tenant_id == user.tenant_id,
            Keyword.status == "pending",
            Keyword.keyword.ilike("%cbd%")
        ).first()
        
        if not keyword:
            print("❌ No CBD keywords found")
            return
        
        print("🚀 TESTING BLOG GENERATION WITH PRODUCT INTEGRATION")
        print("=" * 60)
        print(f"Keyword: {keyword.keyword}")
        print(f"Keyword ID: {keyword.id}")
        print(f"User: {user.email}")
        print(f"OpenAI Key: {user.openai_api_key[:10]}...{user.openai_api_key[-4:]}")
        print()
        
        # Generate blog
        print("🔄 Starting blog generation...")
        generate_single_blog(
            keyword_id=keyword.id,
            store_id=1,  # imaginal.tech store
            template_type="ecommerce_general",
            auto_publish=False,
            tenant_id=user.tenant_id,
            openai_api_key=user.openai_api_key,
            db=db
        )
        
        print("✅ Blog generation completed!")
        print("\n📋 Check the database for the new blog with product integration.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_blog_generation())