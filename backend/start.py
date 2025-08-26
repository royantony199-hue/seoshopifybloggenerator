#!/usr/bin/env python3
"""
Railway startup script that handles PORT environment variable correctly
"""
import os
import sys
import uvicorn

if __name__ == "__main__":
    # Get port from environment variable, default to 8000
    port = int(os.environ.get("PORT", 8000))
    
    print(f"🚀 Starting SEO Blog Automation SaaS on port {port}")
    print(f"📁 Current working directory: {os.getcwd()}")
    print(f"🐍 Python path: {sys.path}")
    
    # Start uvicorn server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        workers=1,  # Single worker for Railway
        log_level="info"
    )