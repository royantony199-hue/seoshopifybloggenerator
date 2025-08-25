#!/usr/bin/env python3
"""
Complete Blog Generation Setup Script
Ensures all components are properly configured
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, User, Tenant, ShopifyStore, Product, Keyword, KeywordCampaign
from app.core.config import settings
from app.routers.auth import get_password_hash

def setup_database():
    """Create all database tables"""
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    return engine

def setup_demo_data(db):
    """Setup demo tenant, user, and store"""
    # Check if demo tenant exists
    tenant = db.query(Tenant).filter(Tenant.slug == "demo-company").first()
    if not tenant:
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
        print("✅ Demo tenant created")
    else:
        print("✅ Demo tenant exists")
    
    # Check if demo user exists
    user = db.query(User).filter(User.email == "demo@example.com").first()
    if not user:
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
        print("✅ Demo user created")
    else:
        print("✅ Demo user exists")
    
    # Check if demo store exists
    store = db.query(ShopifyStore).filter(
        ShopifyStore.tenant_id == tenant.id,
        ShopifyStore.store_name == "Demo Store"
    ).first()
    
    if not store:
        store = ShopifyStore(
            tenant_id=tenant.id,
            user_id=user.id,
            store_name="Demo Store",
            shop_url="demo-store",
            access_token="demo_access_token",
            blog_handle="news",
            is_active=True,
            auto_publish=False,
            default_product_url="https://example.com/products/demo-product"
        )
        db.add(store)
        db.commit()
        db.refresh(store)
        print("✅ Demo store created")
    else:
        print("✅ Demo store exists")
    
    # Check if demo product exists
    product = db.query(Product).filter(
        Product.tenant_id == tenant.id,
        Product.store_id == store.id,
        Product.name == "Demo Product"
    ).first()
    
    if not product:
        product = Product(
            tenant_id=tenant.id,
            store_id=store.id,
            name="Demo Product",
            description="High-quality CBD oil for pain relief",
            url="https://example.com/products/cbd-oil",
            price="$49.99",
            keywords="cbd oil, pain relief, fibromyalgia, arthritis, chronic pain",
            integration_text="For premium CBD products that provide natural pain relief, check out our",
            is_active=True,
            priority=10
        )
        db.add(product)
        db.commit()
        print("✅ Demo product created")
    else:
        print("✅ Demo product exists")
    
    # Add sample keywords if none exist
    keyword_count = db.query(Keyword).filter(Keyword.tenant_id == tenant.id).count()
    if keyword_count == 0:
        sample_keywords = [
            "cbd oil for chronic pain",
            "best cbd gummies for sleep",
            "cbd cream for arthritis",
            "hemp oil vs cbd oil",
            "cbd dosage for anxiety"
        ]
        
        campaign = KeywordCampaign(
            tenant_id=tenant.id,
            name="Demo Campaign",
            description="Sample keywords for testing",
            template_type="ecommerce_general"
        )
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        
        for kw_text in sample_keywords:
            kw = Keyword(
                tenant_id=tenant.id,
                campaign_id=campaign.id,
                keyword=kw_text,
                status="pending"
            )
            db.add(kw)
        
        db.commit()
        print(f"✅ Added {len(sample_keywords)} sample keywords")
    else:
        print(f"✅ Keywords exist ({keyword_count} found)")
    
    return user, store

def main():
    print("=" * 60)
    print("BLOG GENERATION SETUP")
    print("=" * 60)
    
    # Setup database
    engine = setup_database()
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Setup demo data
        user, store = setup_demo_data(db)
        
        print("\n" + "=" * 60)
        print("SETUP COMPLETE!")
        print("=" * 60)
        
        print("\n📋 NEXT STEPS:")
        print("\n1. UPDATE OPENAI API KEY:")
        print("   Option A: Use the web interface")
        print("   - Go to http://localhost:3000/settings")
        print("   - Click on 'API Keys' tab")
        print("   - Enter your OpenAI API key")
        print("   - Click 'Save API Keys'")
        
        print("\n   Option B: Use the command line")
        print("   python3 update_api_key.py sk-proj-YOUR_ACTUAL_KEY")
        
        print("\n2. GENERATE BLOGS:")
        print("   - Go to http://localhost:3000/keywords")
        print("   - Select keywords to generate")
        print("   - Click 'Generate Blogs'")
        
        print("\n3. MONITOR GENERATION:")
        print("   python3 monitor_blog_generation.py")
        
        print("\n📊 CURRENT STATUS:")
        print(f"   - Demo User: {user.email}")
        print(f"   - OpenAI Key: {'SET' if user.openai_api_key else 'NOT SET'}")
        print(f"   - Store: {store.store_name}")
        print(f"   - Keywords: {db.query(Keyword).filter(Keyword.tenant_id == user.tenant_id).count()}")
        
        if not user.openai_api_key or user.openai_api_key.startswith("sk-test"):
            print("\n⚠️  WARNING: OpenAI API key is not set or is invalid!")
            print("   Blog generation will fail until you add a valid key.")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()