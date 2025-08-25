#!/usr/bin/env python3
"""
Data Backup and Restore System
Prevents data loss during development
"""

import json
import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import User, Product, ShopifyStore, Keyword, GeneratedBlog
from app.core.config import settings

BACKUP_DIR = "/Users/royantony/blue-lotus-seo/saas-platform/backend/backups"

class DataBackupRestore:
    def __init__(self):
        self.engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(bind=self.engine)
        self.db = SessionLocal()
        
        # Ensure backup directory exists
        os.makedirs(BACKUP_DIR, exist_ok=True)
    
    def backup_all_data(self):
        """Create a complete backup of all user data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{BACKUP_DIR}/backup_{timestamp}.json"
        
        try:
            user = self.db.query(User).filter(User.email == "demo@example.com").first()
            if not user:
                print("❌ Demo user not found")
                return None
            
            backup_data = {
                "timestamp": timestamp,
                "user": {
                    "email": user.email,
                    "openai_api_key": user.openai_api_key,
                    "serper_api_key": user.serper_api_key,
                    "unsplash_api_key": user.unsplash_api_key,
                    "google_sheets_credentials": user.google_sheets_credentials,
                    "google_sheets_id": user.google_sheets_id,
                },
                "stores": [],
                "products": [],
                "keywords_count": 0,
                "blogs_count": 0
            }
            
            # Backup stores
            stores = self.db.query(ShopifyStore).filter(ShopifyStore.tenant_id == user.tenant_id).all()
            for store in stores:
                backup_data["stores"].append({
                    "store_name": store.store_name,
                    "shop_url": store.shop_url,
                    "access_token": store.access_token,
                    "blog_handle": store.blog_handle,
                    "is_active": store.is_active,
                    "auto_publish": store.auto_publish,
                    "default_product_url": store.default_product_url,
                    "product_integration_text": store.product_integration_text
                })
            
            # Backup products
            products = self.db.query(Product).filter(Product.tenant_id == user.tenant_id).all()
            for product in products:
                backup_data["products"].append({
                    "name": product.name,
                    "description": product.description,
                    "url": product.url,
                    "price": product.price,
                    "keywords": product.keywords,
                    "integration_text": product.integration_text,
                    "is_active": product.is_active,
                    "priority": product.priority,
                    "store_name": self.db.query(ShopifyStore).filter(ShopifyStore.id == product.store_id).first().store_name if product.store_id else None
                })
            
            # Count other data
            backup_data["keywords_count"] = self.db.query(Keyword).filter(Keyword.tenant_id == user.tenant_id).count()
            backup_data["blogs_count"] = self.db.query(GeneratedBlog).filter(GeneratedBlog.tenant_id == user.tenant_id).count()
            
            # Save backup
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            print(f"✅ Backup created: {backup_file}")
            print(f"   - API Keys: {'✅' if user.openai_api_key else '❌'}")
            print(f"   - Stores: {len(backup_data['stores'])}")
            print(f"   - Products: {len(backup_data['products'])}")
            print(f"   - Keywords: {backup_data['keywords_count']}")
            print(f"   - Blogs: {backup_data['blogs_count']}")
            
            return backup_file
            
        except Exception as e:
            print(f"❌ Backup failed: {str(e)}")
            return None
    
    def restore_from_backup(self, backup_file=None):
        """Restore data from most recent backup"""
        if not backup_file:
            # Find most recent backup
            backups = [f for f in os.listdir(BACKUP_DIR) if f.startswith('backup_') and f.endswith('.json')]
            if not backups:
                print("❌ No backups found")
                return False
            backup_file = os.path.join(BACKUP_DIR, sorted(backups)[-1])
        
        try:
            with open(backup_file, 'r') as f:
                backup_data = json.load(f)
            
            print(f"🔄 Restoring from: {backup_file}")
            
            # Get or create user
            user = self.db.query(User).filter(User.email == "demo@example.com").first()
            if not user:
                print("❌ User not found for restore")
                return False
            
            # Restore API keys
            user_data = backup_data["user"]
            if user_data.get("openai_api_key"):
                user.openai_api_key = user_data["openai_api_key"]
            if user_data.get("serper_api_key"):
                user.serper_api_key = user_data["serper_api_key"]
            if user_data.get("unsplash_api_key"):
                user.unsplash_api_key = user_data["unsplash_api_key"]
            if user_data.get("google_sheets_credentials"):
                user.google_sheets_credentials = user_data["google_sheets_credentials"]
            if user_data.get("google_sheets_id"):
                user.google_sheets_id = user_data["google_sheets_id"]
            
            # Restore products (merge, don't duplicate)
            for product_data in backup_data["products"]:
                existing = self.db.query(Product).filter(
                    Product.tenant_id == user.tenant_id,
                    Product.name == product_data["name"]
                ).first()
                
                if not existing:
                    # Find store
                    store = self.db.query(ShopifyStore).filter(
                        ShopifyStore.tenant_id == user.tenant_id,
                        ShopifyStore.store_name == product_data.get("store_name", "imaginal.tech")
                    ).first()
                    
                    if not store:
                        store = self.db.query(ShopifyStore).filter(ShopifyStore.tenant_id == user.tenant_id).first()
                    
                    if store:
                        product = Product(
                            tenant_id=user.tenant_id,
                            store_id=store.id,
                            name=product_data["name"],
                            description=product_data.get("description"),
                            url=product_data["url"],
                            price=product_data.get("price"),
                            keywords=product_data.get("keywords"),
                            integration_text=product_data.get("integration_text"),
                            is_active=product_data.get("is_active", True),
                            priority=product_data.get("priority", 0)
                        )
                        self.db.add(product)
            
            self.db.commit()
            
            print("✅ Data restored successfully!")
            print(f"   - API Keys: {'✅' if user.openai_api_key else '❌'}")
            print(f"   - Products restored: {len(backup_data['products'])}")
            
            return True
            
        except Exception as e:
            print(f"❌ Restore failed: {str(e)}")
            self.db.rollback()
            return False
    
    def auto_backup(self):
        """Create automatic backup if data exists"""
        user = self.db.query(User).filter(User.email == "demo@example.com").first()
        if user and (user.openai_api_key or self.db.query(Product).filter(Product.tenant_id == user.tenant_id).count() > 0):
            return self.backup_all_data()
        return None
    
    def close(self):
        self.db.close()

def main():
    import sys
    backup_system = DataBackupRestore()
    
    try:
        if len(sys.argv) > 1:
            command = sys.argv[1]
            if command == "backup":
                backup_system.backup_all_data()
            elif command == "restore":
                backup_file = sys.argv[2] if len(sys.argv) > 2 else None
                backup_system.restore_from_backup(backup_file)
            elif command == "auto":
                backup_system.auto_backup()
        else:
            print("Usage:")
            print("  python3 backup_restore_system.py backup")
            print("  python3 backup_restore_system.py restore [backup_file]")
            print("  python3 backup_restore_system.py auto")
    finally:
        backup_system.close()

if __name__ == "__main__":
    main()