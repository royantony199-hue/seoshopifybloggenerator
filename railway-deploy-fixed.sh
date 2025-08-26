#!/bin/bash
# Fixed Railway Deployment for SEO Blog Automation SaaS

echo "🚂 Deploying SEO Blog Automation SaaS to Railway..."
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Navigate to backend directory
cd /Users/royantony/blue-lotus-seo/saas-platform/backend

echo "🔗 Linking to your Railway project..."
echo "Please follow these steps:"
echo ""
echo "1. Run: railway login (if not already logged in)"
echo "2. Run: railway link"
echo "3. Select your existing project: 'SEO Blog Automation'"
echo "4. Then run: railway up"
echo ""
echo "Or run these commands manually:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "railway login"
echo "railway link"
echo "railway up"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔗 Railway Dashboard: https://railway.com/project/5e6d8ada-3de2-48cc-b496-86582baca4eb"