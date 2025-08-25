#!/bin/bash
# Railway production startup script

echo "🚂 Starting SEO Blog Automation SaaS on Railway..."

# Install dependencies if needed
pip install -r requirements.txt

# Run database migrations
echo "📊 Running database migrations..."
python -m alembic upgrade head || echo "Migration failed, continuing..."

# Start the application with production settings
echo "🚀 Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2