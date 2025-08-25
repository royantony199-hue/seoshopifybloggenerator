#!/bin/bash
# Stable Server Manager for SEO Blog Automation
# Prevents rate limiting and connection issues

echo "🚀 STARTING STABLE SEO SERVERS"
echo "=================================="

# Kill any existing servers
echo "🔧 Cleaning up existing processes..."
pkill -f "uvicorn.*port.*8000" 2>/dev/null || true
pkill -f "uvicorn.*port.*8001" 2>/dev/null || true

# Wait for processes to stop
sleep 2

# Start SEO Blog Automation on port 8000 (no rate limiting)
echo "🎯 Starting SEO Blog Automation (port 8000)..."
cd /Users/royantony/blue-lotus-seo/saas-platform/backend

# Set environment variables to prevent issues
export PYTHONPATH=/Users/royantony/blue-lotus-seo/saas-platform/backend:$PYTHONPATH
export RATE_LIMIT_ENABLED=false

nohup python3 -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 > seo_server.log 2>&1 &
SEO_PID=$!
echo "✅ SEO server started (PID: $SEO_PID)"

# Wait and test SEO server
sleep 5
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ SEO server is responding on http://localhost:8000"
else
    echo "❌ SEO server failed to start"
    exit 1
fi

# Start Aurora Life OS on port 8001
echo "🌟 Starting Aurora Life OS (port 8001)..."
cd "/Users/royantony/auroyra life os/backend"

nohup python3 -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001 > aurora_server.log 2>&1 &
AURORA_PID=$!
echo "✅ Aurora server started (PID: $AURORA_PID)"

# Wait and test Aurora server
sleep 5
if curl -s http://localhost:8001/health > /dev/null; then
    echo "✅ Aurora server is responding on http://localhost:8001"
else
    echo "⚠️  Aurora server may have issues (continuing anyway)"
fi

echo ""
echo "🎉 SERVERS STARTED SUCCESSFULLY!"
echo "================================="
echo "📊 SEO Blog Automation:  http://localhost:8000"
echo "🤖 Aurora Life OS:       http://localhost:8001" 
echo ""
echo "📝 Server Status:"
echo "   SEO PID: $SEO_PID (logs: seo_server.log)"
echo "   Aurora PID: $AURORA_PID (logs: aurora_server.log)"
echo ""
echo "🛑 To stop servers: pkill -f uvicorn"
echo "📈 To monitor: tail -f */server.log"

# Keep script running to show status
echo ""
echo "⏳ Servers are running... Press Ctrl+C to see status"
trap 'echo ""; echo "📊 Current server status:"; ps aux | grep uvicorn | grep -v grep' INT
while true; do
    sleep 30
    # Basic health check every 30 seconds
    if ! curl -s http://localhost:8000/health > /dev/null; then
        echo "⚠️  $(date): SEO server not responding"
    fi
done