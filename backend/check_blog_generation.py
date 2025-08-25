#!/usr/bin/env python3
"""
Blog Generation Health Check Script
This script checks all components required for blog generation
"""

import sys
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import User, Keyword, ShopifyStore, Product, Tenant, KeywordCampaign
from app.core.config import settings
import openai

def check_database_connection():
    """Check if database is accessible"""
    try:
        engine = create_engine(settings.DATABASE_URL)
        connection = engine.connect()
        connection.close()
        print("✅ Database connection: OK")
        return True
    except Exception as e:
        print(f"❌ Database connection: FAILED - {str(e)}")
        return False

def check_demo_user(db):
    """Check if demo user exists and has necessary data"""
    user = db.query(User).filter(User.email == "demo@example.com").first()
    if not user:
        print("❌ Demo user: NOT FOUND")
        return None
    
    print("✅ Demo user: EXISTS")
    print(f"   - Email: {user.email}")
    print(f"   - Tenant ID: {user.tenant_id}")
    print(f"   - OpenAI API Key: {'SET' if user.openai_api_key else 'NOT SET'}")
    
    if user.openai_api_key:
        print(f"   - API Key Preview: {user.openai_api_key[:10]}...{user.openai_api_key[-4:]}")
    
    return user

def check_tenant(db, tenant_id):
    """Check tenant settings"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        print("❌ Tenant: NOT FOUND")
        return None
    
    print("✅ Tenant: EXISTS")
    print(f"   - Name: {tenant.name}")
    print(f"   - Monthly Blog Limit: {tenant.monthly_blog_limit}")
    print(f"   - Blogs Used: {tenant.monthly_blogs_used}")
    print(f"   - Remaining: {tenant.monthly_blog_limit - tenant.monthly_blogs_used}")
    
    return tenant

def check_shopify_stores(db, tenant_id):
    """Check if Shopify stores exist"""
    stores = db.query(ShopifyStore).filter(ShopifyStore.tenant_id == tenant_id).all()
    
    if not stores:
        print("❌ Shopify Stores: NONE FOUND")
        return None
    
    print(f"✅ Shopify Stores: {len(stores)} FOUND")
    for store in stores:
        print(f"   - Store: {store.store_name} ({store.shop_url})")
        print(f"     Active: {store.is_active}")
    
    return stores[0] if stores else None

def check_keywords(db, tenant_id):
    """Check available keywords"""
    pending_keywords = db.query(Keyword).filter(
        Keyword.tenant_id == tenant_id,
        Keyword.status == "pending"
    ).limit(5).all()
    
    total_keywords = db.query(Keyword).filter(Keyword.tenant_id == tenant_id).count()
    
    print(f"✅ Keywords: {total_keywords} TOTAL")
    print(f"   - Pending: {len(pending_keywords)}")
    
    if pending_keywords:
        print("   - Sample pending keywords:")
        for kw in pending_keywords[:3]:
            print(f"     • {kw.keyword} (ID: {kw.id})")
    
    return pending_keywords

def check_products(db, tenant_id, store_id):
    """Check products for blog integration"""
    products = db.query(Product).filter(
        Product.tenant_id == tenant_id,
        Product.store_id == store_id,
        Product.is_active == True
    ).all()
    
    print(f"✅ Products: {len(products)} ACTIVE")
    if products:
        for product in products[:3]:
            print(f"   - {product.name}")
            print(f"     URL: {product.url}")
            print(f"     Keywords: {product.keywords}")

def test_openai_api_key(api_key):
    """Test if OpenAI API key is valid"""
    if not api_key:
        print("❌ OpenAI API Key: NOT SET")
        return False
    
    try:
        client = openai.OpenAI(api_key=api_key)
        # Test with a simple completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'test'"}],
            max_tokens=5
        )
        print("✅ OpenAI API Key: VALID AND WORKING")
        return True
    except openai.AuthenticationError:
        print("❌ OpenAI API Key: INVALID (Authentication Failed)")
        return False
    except Exception as e:
        print(f"❌ OpenAI API Key: ERROR - {str(e)}")
        return False

def main():
    print("=" * 60)
    print("BLOG GENERATION HEALTH CHECK")
    print("=" * 60)
    
    # Check database
    if not check_database_connection():
        sys.exit(1)
    
    # Create session
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Check demo user
        user = check_demo_user(db)
        if not user:
            print("\n⚠️  CREATING DEMO USER...")
            from app.routers.demo_auth import get_demo_user
            user = get_demo_user(db)
            print("✅ Demo user created")
        
        print()
        
        # Check tenant
        tenant = check_tenant(db, user.tenant_id)
        print()
        
        # Check Shopify stores
        store = check_shopify_stores(db, user.tenant_id)
        print()
        
        # Check keywords
        keywords = check_keywords(db, user.tenant_id)
        print()
        
        # Check products
        if store:
            check_products(db, user.tenant_id, store.id)
            print()
        
        # Test OpenAI API
        test_openai_api_key(user.openai_api_key)
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        
        issues = []
        
        if not user.openai_api_key or not test_openai_api_key(user.openai_api_key):
            issues.append("❌ OpenAI API key is missing or invalid")
        
        if not store:
            issues.append("❌ No Shopify store configured")
        
        if not keywords:
            issues.append("❌ No pending keywords to generate blogs for")
        
        if tenant and tenant.monthly_blogs_used >= tenant.monthly_blog_limit:
            issues.append("❌ Monthly blog limit reached")
        
        if issues:
            print("ISSUES FOUND:")
            for issue in issues:
                print(f"  {issue}")
            print("\nTO FIX:")
            if "OpenAI API key" in str(issues):
                print("  1. Go to Settings → API Keys")
                print("  2. Add a valid OpenAI API key")
                print("  3. Save the settings")
            if "Shopify store" in str(issues):
                print("  1. Go to Settings → Shopify Stores")
                print("  2. Add at least one store")
            if "No pending keywords" in str(issues):
                print("  1. Go to Keywords page")
                print("  2. Upload keywords CSV file")
        else:
            print("✅ ALL SYSTEMS GO! Blog generation should work correctly.")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()