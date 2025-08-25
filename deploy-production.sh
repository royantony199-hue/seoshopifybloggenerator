#!/bin/bash
# Production Deployment Script for SEO Blog Automation SaaS

set -e  # Exit on any error

echo "🚀 Starting production deployment..."

# Check if environment file exists
if [ ! -f .env.production ]; then
    echo "❌ Error: .env.production file not found!"
    echo "Please copy .env.production.example to .env.production and configure all values"
    exit 1
fi

# Load environment variables
export $(cat .env.production | grep -v '^#' | xargs)

# Validate critical environment variables
required_vars=("SECRET_KEY" "ENCRYPTION_KEY" "DATABASE_URL" "OPENAI_API_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Error: Required environment variable $var is not set"
        exit 1
    fi
done

# Validate secret key length
if [ ${#SECRET_KEY} -lt 32 ]; then
    echo "❌ Error: SECRET_KEY must be at least 32 characters long"
    exit 1
fi

echo "✅ Environment validation passed"

# Build and start services
echo "🔨 Building production images..."
docker-compose -f docker-compose.production.yml build --no-cache

echo "🔄 Starting production services..."
docker-compose -f docker-compose.production.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
timeout=120
elapsed=0
while [ $elapsed -lt $timeout ]; do
    if curl -f -s http://localhost:8000/health > /dev/null; then
        echo "✅ Backend service is healthy"
        break
    fi
    sleep 5
    elapsed=$((elapsed + 5))
    echo "Waiting... ($elapsed/${timeout}s)"
done

if [ $elapsed -ge $timeout ]; then
    echo "❌ Error: Backend service failed to become healthy within ${timeout} seconds"
    docker-compose -f docker-compose.production.yml logs backend
    exit 1
fi

# Run database migrations
echo "📊 Running database migrations..."
docker-compose -f docker-compose.production.yml exec -T backend alembic upgrade head

# Verify deployment
echo "🔍 Verifying deployment..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ "$response" = "200" ]; then
    echo "✅ Deployment successful!"
    echo ""
    echo "🎉 SEO Blog Automation SaaS is now running in production mode"
    echo "📊 Health check: http://localhost:8000/health"
    echo "📚 API Documentation: http://localhost:8000/docs"
    echo ""
    echo "📋 Next steps:"
    echo "1. Configure your domain and SSL certificates"
    echo "2. Set up monitoring and alerting"
    echo "3. Configure backup schedules"
    echo "4. Test all critical functionality"
else
    echo "❌ Deployment verification failed (HTTP $response)"
    exit 1
fi