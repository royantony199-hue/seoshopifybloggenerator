#!/usr/bin/env python3
"""
Safe Database Initialization
ALWAYS preserves existing user data
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, User, Tenant, ShopifyStore, Product
from app.core.config import settings
from backup_restore_system import DataBackupRestore

def safe_database_init():
    """Initialize database while preserving existing data"""
    print("🛡️  SAFE DATABASE INITIALIZATION")
    print("=" * 50)
    
    # Step 1: Create backup of existing data
    backup_system = DataBackupRestore()
    backup_file = backup_system.auto_backup()
    
    if backup_file:
        print(f"✅ Created safety backup: {backup_file}")
    
    # Step 2: Create tables (won't affect existing data)
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables ensured")
    
    # Step 3: Check and restore user data if needed
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        user = db.query(User).filter(User.email == "demo@example.com").first()
        
        # If user exists, check data integrity
        if user:
            api_key_exists = bool(user.openai_api_key and not user.openai_api_key.startswith("sk-test"))
            products_exist = db.query(Product).filter(Product.tenant_id == user.tenant_id).count() > 0
            
            print(f"✅ User exists: {user.email}")
            print(f"   - Valid API Key: {'✅' if api_key_exists else '❌'}")
            print(f"   - Products: {db.query(Product).filter(Product.tenant_id == user.tenant_id).count()}")
            
            # If data is missing and we have a backup, offer to restore
            if not api_key_exists and backup_file:
                print("\n⚠️  API key missing - restoring from backup...")
                backup_system.restore_from_backup(backup_file)
        
        else:
            # Create new user but try to restore from backup first
            print("⚠️  Creating new user...")
            if backup_file:
                print("   Attempting to restore from backup first...")
                backup_system.restore_from_backup(backup_file)
            else:
                # Create minimal user
                from app.routers.demo_auth import get_demo_user
                get_demo_user(db)
                print("✅ Demo user created")
    
    finally:
        db.close()
        backup_system.close()
    
    print("\n🎯 INITIALIZATION COMPLETE - Data Protected!")

if __name__ == "__main__":
    safe_database_init()