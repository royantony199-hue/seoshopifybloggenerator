#!/usr/bin/env python3
"""
User Data Management Tool
Easy backup, restore, and protection for your data
"""

import sys
import os
from backup_restore_system import DataBackupRestore

def show_menu():
    print("\n🛡️  DATA MANAGEMENT TOOL")
    print("=" * 40)
    print("1. 📁 Create Backup")
    print("2. 🔄 Restore from Backup")
    print("3. 📋 List All Backups")
    print("4. ✅ Check Data Status")
    print("5. 🚨 Emergency Restore (Latest)")
    print("6. 🗑️  Clean Old Backups")
    print("0. Exit")
    print()

def list_backups():
    backup_dir = "/Users/royantony/blue-lotus-seo/saas-platform/backend/backups"
    if not os.path.exists(backup_dir):
        print("❌ No backup directory found")
        return []
    
    backups = [f for f in os.listdir(backup_dir) if f.startswith('backup_') and f.endswith('.json')]
    backups.sort(reverse=True)  # Most recent first
    
    if not backups:
        print("❌ No backups found")
        return []
    
    print(f"\n📁 Found {len(backups)} backups:")
    for i, backup in enumerate(backups, 1):
        # Extract timestamp from filename
        timestamp = backup.replace('backup_', '').replace('.json', '')
        formatted_time = f"{timestamp[:8]} {timestamp[9:11]}:{timestamp[11:13]}:{timestamp[13:15]}"
        print(f"  {i}. {backup} ({formatted_time})")
    
    return backups

def check_data_status():
    backup_system = DataBackupRestore()
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.core.database import User, Product, GeneratedBlog
        from app.core.config import settings
        
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        user = db.query(User).filter(User.email == "demo@example.com").first()
        if not user:
            print("❌ Demo user not found")
            return
        
        products = db.query(Product).filter(Product.tenant_id == user.tenant_id).all()
        blogs = db.query(GeneratedBlog).filter(GeneratedBlog.tenant_id == user.tenant_id).count()
        
        print("\n📊 CURRENT DATA STATUS:")
        print("=" * 30)
        print(f"✅ User: {user.email}")
        print(f"✅ OpenAI Key: {'SET (' + user.openai_api_key[:10] + '...)' if user.openai_api_key else 'NOT SET'}")
        print(f"✅ Products: {len(products)}")
        for product in products:
            print(f"   - {product.name}: {product.url}")
        print(f"✅ Generated Blogs: {blogs}")
        
        db.close()
    finally:
        backup_system.close()

def main():
    if len(sys.argv) > 1:
        # Command line mode
        command = sys.argv[1].lower()
        backup_system = DataBackupRestore()
        try:
            if command == "backup":
                backup_system.backup_all_data()
            elif command == "restore":
                backup_system.restore_from_backup()
            elif command == "status":
                check_data_status()
            elif command == "emergency":
                backup_system.restore_from_backup()
        finally:
            backup_system.close()
        return
    
    # Interactive mode
    while True:
        show_menu()
        try:
            choice = input("Enter your choice (0-6): ").strip()
            
            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                backup_system = DataBackupRestore()
                try:
                    backup_system.backup_all_data()
                finally:
                    backup_system.close()
            elif choice == "2":
                backups = list_backups()
                if backups:
                    try:
                        backup_num = int(input(f"\nEnter backup number (1-{len(backups)}): "))
                        if 1 <= backup_num <= len(backups):
                            backup_file = os.path.join(
                                "/Users/royantony/blue-lotus-seo/saas-platform/backend/backups",
                                backups[backup_num - 1]
                            )
                            backup_system = DataBackupRestore()
                            try:
                                backup_system.restore_from_backup(backup_file)
                            finally:
                                backup_system.close()
                        else:
                            print("❌ Invalid backup number")
                    except ValueError:
                        print("❌ Please enter a valid number")
            elif choice == "3":
                list_backups()
            elif choice == "4":
                check_data_status()
            elif choice == "5":
                backup_system = DataBackupRestore()
                try:
                    backup_system.restore_from_backup()
                finally:
                    backup_system.close()
            elif choice == "6":
                backup_dir = "/Users/royantony/blue-lotus-seo/saas-platform/backend/backups"
                backups = list_backups()
                if len(backups) > 5:
                    print(f"\n🗑️  Keeping 5 most recent backups, removing {len(backups) - 5} old ones")
                    for backup in backups[5:]:
                        os.remove(os.path.join(backup_dir, backup))
                    print("✅ Cleanup complete")
                else:
                    print("✅ No cleanup needed (5 or fewer backups)")
            else:
                print("❌ Invalid choice")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

if __name__ == "__main__":
    main()