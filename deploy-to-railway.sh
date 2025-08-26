#!/bin/bash
# Deploy SEO Blog Automation SaaS to Railway

echo "🚂 Deploying SEO Blog Automation SaaS to Railway..."
echo "Project ID: 5e6d8ada-3de2-48cc-b496-86582baca4eb"
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Navigate to backend directory
cd /Users/royantony/blue-lotus-seo/saas-platform/backend

# Link to your existing Railway project
echo "🔗 Linking to your Railway project..."
railway link 5e6d8ada-3de2-48cc-b496-86582baca4eb

# Deploy to Railway
echo "🚀 Deploying to Railway..."
railway up

echo ""
echo "✅ Deployment initiated!"
echo ""
echo "📋 Next steps:"
echo "1. Check your Railway dashboard to monitor deployment progress"
echo "2. Once deployed, Railway will provide your live URL"
echo "3. Update your frontend .env with the Railway URL"
echo "4. Test your deployment with the /health endpoint"
echo ""
echo "🔗 Railway Dashboard: https://railway.com/project/5e6d8ada-3de2-48cc-b496-86582baca4eb"