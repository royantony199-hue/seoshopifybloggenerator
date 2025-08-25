#!/usr/bin/env python3
"""
User Data Protection System
Automatically backs up data before any risky operations
"""

import os
import atexit
from functools import wraps
from backup_restore_system import DataBackupRestore

# Global backup system
backup_system = None

def init_protection():
    """Initialize data protection"""
    global backup_system
    if not backup_system:
        backup_system = DataBackupRestore()
        # Create backup on startup
        backup_system.auto_backup()
        # Register cleanup
        atexit.register(cleanup_protection)

def cleanup_protection():
    """Cleanup on exit"""
    global backup_system
    if backup_system:
        backup_system.close()

def protect_user_data(func):
    """Decorator to protect user data before database operations"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        init_protection()
        # Create backup before risky operations
        if backup_system:
            backup_system.auto_backup()
        return func(*args, **kwargs)
    return wrapper

def emergency_restore():
    """Emergency restore function"""
    init_protection()
    if backup_system:
        return backup_system.restore_from_backup()
    return False

if __name__ == "__main__":
    print("🛡️  Data Protection System")
    print("=" * 40)
    
    init_protection()
    
    print("✅ Protection system initialized")
    print("✅ Automatic backup created")
    print("\nTo manually restore data:")
    print("  python3 backup_restore_system.py restore")
    print("\nTo manually backup data:")
    print("  python3 backup_restore_system.py backup")