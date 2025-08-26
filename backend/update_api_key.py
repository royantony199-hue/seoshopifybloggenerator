#!/usr/bin/env python3
"""
Update OpenAI API Key for demo user
"""

import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import User
from app.core.config import settings

def update_openai_key(new_key):
    """Update the OpenAI API key for demo user"""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Get demo user
        user = db.query(User).filter(User.email == "demo@example.com").first()
        
        if not user:
            print("❌ Demo user not found!")
            return False
        
        # Update the key
        user.openai_api_key = new_key
        db.commit()
        
        print(f"✅ OpenAI API key updated successfully!")
        print(f"   New key: {new_key[:10]}...{new_key[-4:]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating key: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("OpenAI API Key Updater")
    print("=" * 40)
    print("\nTo update the OpenAI API key, you can:")
    print("1. Use the web interface: Go to Settings → API Keys")
    print("2. Or run this command:")
    print("\n   python3 update_api_key.py YOUR_API_KEY")
    print("\nGet your API key from: https://platform.openai.com/api-keys")
    
    if len(sys.argv) > 1:
        new_key = sys.argv[1]
        if len(new_key) > 20:
            update_openai_key(new_key)
        else:
            print("\n❌ Invalid key format. Key too short.")
    else:
        print("\n⚠️  No key provided. Use the command above to update.")