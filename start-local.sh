#!/bin/bash

# SEO Blog Automation SaaS - Local Development Setup

echo "🚀 Starting SEO Blog Automation SaaS Platform..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start only database and Redis
echo "📦 Starting database and Redis..."
docker-compose up -d db redis

echo "⏳ Waiting for database to be ready..."
sleep 10

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is required but not found."
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not found."
    exit 1
fi

# Backend setup
echo "🐍 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://seo_user:seo_password_123@localhost:5432/seo_saas_db"
export REDIS_URL="redis://localhost:6379/0"
export SECRET_KEY="seo-blog-automation-secret-key-change-in-production-minimum-32-chars"
export DEBUG="true"
export ALLOWED_ORIGINS='["http://localhost:3000","http://localhost:3001","http://127.0.0.1:3000"]'

# Start backend
echo "🌐 Starting backend server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

cd ../frontend

# Frontend setup
echo "⚛️ Setting up frontend..."

# Install dependencies
echo "Installing Node.js dependencies..."
npm install

# Set environment variables
export VITE_API_URL="http://localhost:8000"

# Start frontend
echo "🎨 Starting frontend server..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "🎉 SEO Blog Automation SaaS Platform is starting!"
echo ""
echo "📍 Services:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📊 Database:"
echo "   PostgreSQL: localhost:5432"
echo "   Redis:      localhost:6379"
echo ""
echo "🛑 To stop all services:"
echo "   Press Ctrl+C or run: ./stop-local.sh"
echo ""

# Wait for interrupt
trap "echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; docker-compose stop db redis; exit" INT
wait