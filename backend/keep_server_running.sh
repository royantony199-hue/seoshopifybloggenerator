#!/bin/bash

# Script to keep the SEO Blog Automation server running
# This prevents the server from shutting down and losing background tasks

cd "$(dirname "$0")"

echo "Starting SEO Blog Automation server monitor..."

while true; do
    # Check if the correct server is running
    SERVER_CHECK=$(curl -s http://localhost:8000/ 2>/dev/null | grep "SEO Blog Automation SaaS Platform")
    
    if [ -z "$SERVER_CHECK" ]; then
        echo "$(date): SEO server not running or wrong server detected. Starting correct server..."
        
        # Kill any existing process on port 8000
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
        
        # Wait a moment for port to be released
        sleep 2
        
        # Start the correct server
        nohup python3 -m uvicorn app.main:app --reload --port 8000 > /tmp/seo_server.log 2>&1 &
        
        # Wait for server to start
        sleep 5
        
        # Verify it started correctly
        SERVER_VERIFY=$(curl -s http://localhost:8000/ 2>/dev/null | grep "SEO Blog Automation SaaS Platform")
        if [ -n "$SERVER_VERIFY" ]; then
            echo "$(date): ✅ SEO Blog Automation server started successfully"
        else
            echo "$(date): ❌ Failed to start SEO server"
        fi
    else
        echo "$(date): ✅ SEO server running correctly"
    fi
    
    # Check every 30 seconds
    sleep 30
done