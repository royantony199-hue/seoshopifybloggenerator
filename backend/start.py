#!/usr/bin/env python3
"""
Railway startup script with proper timeout configuration for article generation
"""
import os
import sys

if __name__ == "__main__":
    # Get port from environment variable, default to 8000
    port = int(os.environ.get("PORT", 8000))

    print(f"Starting SEO Blog Automation SaaS on port {port}")
    print(f"Current working directory: {os.getcwd()}")

    # Use gunicorn for production with longer timeout for article generation
    # Article generation with OpenAI can take 30-60+ seconds
    os.system(
        f"gunicorn app.main:app "
        f"--bind 0.0.0.0:{port} "
        f"--workers 1 "
        f"--worker-class uvicorn.workers.UvicornWorker "
        f"--timeout 300 "  # 5 minute timeout for long article generation
        f"--graceful-timeout 120 "
        f"--keep-alive 5 "
        f"--log-level info "
        f"--access-logfile - "
        f"--error-logfile -"
    )
