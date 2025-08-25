#!/usr/bin/env python3
"""
Generate secure secrets for production deployment
"""

import secrets
import string
from cryptography.fernet import Fernet
import base64

def generate_secret_key(length=64):
    """Generate a secure secret key"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_encryption_key():
    """Generate a secure encryption key"""
    key = Fernet.generate_key()
    return base64.urlsafe_b64encode(key).decode()

def generate_password(length=32):
    """Generate a secure password"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def main():
    print("🔐 Generating production secrets for SEO Blog Automation SaaS")
    print("=" * 60)
    
    # Generate secrets
    secret_key = generate_secret_key(64)
    encryption_key = generate_encryption_key()
    db_password = generate_password(32)
    redis_password = generate_password(24)
    
    print("✅ Secrets generated successfully!")
    print("\n📋 Add these to your .env.production file:")
    print("=" * 60)
    print(f"SECRET_KEY={secret_key}")
    print(f"ENCRYPTION_KEY={encryption_key}")
    print(f"DB_PASSWORD={db_password}")
    print(f"REDIS_PASSWORD={redis_password}")
    print("=" * 60)
    
    print("\n⚠️  IMPORTANT SECURITY NOTES:")
    print("1. Store these secrets securely - never commit to version control")
    print("2. Use different secrets for development, staging, and production")
    print("3. Rotate secrets regularly (every 90 days recommended)")
    print("4. Use a password manager or secrets management service")
    print("5. Backup these secrets in a secure location")
    
    print("\n🔒 For additional security:")
    print("- Enable database SSL connections")
    print("- Use Redis AUTH and SSL")
    print("- Configure firewall rules")
    print("- Enable monitoring and alerting")
    print("- Regular security audits")

if __name__ == "__main__":
    main()