#!/usr/bin/env python3
"""
Protected Server Startup
Always preserves user data and creates backups
"""

import subprocess
import sys
from safe_init import safe_database_init

def start_protected_server():
    """Start server with data protection"""
    print("🚀 STARTING PROTECTED SERVER")
    print("=" * 40)
    
    # Step 1: Safe database initialization
    safe_database_init()
    
    print("\n🔄 Starting FastAPI server...")
    print("   Your data is protected with automatic backups")
    print("   Backups are stored in: ./backups/")
    print()
    
    # Step 2: Start the server
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "127.0.0.1", 
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\n\n🛡️  Server stopped - Data remains protected!")

if __name__ == "__main__":
    start_protected_server()