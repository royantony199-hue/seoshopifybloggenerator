#!/usr/bin/env python3
"""
Railway startup script with proper timeout configuration for article generation
"""
import os
import subprocess
import sys

if __name__ == "__main__":
    # Get port from environment variable, default to 8000
    port = int(os.environ.get("PORT", 8000))

    print(f"Starting SEO Blog Automation SaaS on port {port}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python version: {sys.version}")

    # Build gunicorn command with proper timeout for article generation
    # Article generation with OpenAI can take 60-120+ seconds
    cmd = [
        "gunicorn",
        "app.main:app",
        "--bind", f"0.0.0.0:{port}",
        "--workers", "1",
        "--worker-class", "uvicorn.workers.UvicornWorker",
        "--timeout", "300",  # 5 minute timeout
        "--graceful-timeout", "120",
        "--keep-alive", "5",
        "--log-level", "info",
        "--access-logfile", "-",
        "--error-logfile", "-",
    ]

    print(f"Running: {' '.join(cmd)}")

    # Use subprocess.run instead of os.system for better error handling
    result = subprocess.run(cmd)
    sys.exit(result.returncode)
