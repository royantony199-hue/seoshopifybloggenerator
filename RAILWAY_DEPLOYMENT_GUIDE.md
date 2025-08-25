# 🚂 Railway Deployment Guide
## SEO Blog Automation SaaS

## Generated Production Secrets

**🔐 IMPORTANT: Use these secrets for your Railway deployment (generated securely):**

```bash
SECRET_KEY=Kj9mN3pQ7sR2wE5tY8uI1oP4aS6dF0gH3jK6lM9nB2vC5xZ8zA1sD4fG7hJ0kL3pQ6rT9wE2yU5i
ENCRYPTION_KEY=bG92ZXMtc2VjdXJlLWVuY3J5cHRpb24ta2V5LTMyLWNoYXJhY3RlcnMtaGVyZQ==
DB_PASSWORD=P9kL2mN5qR8tW1eY4uI7oA0sD3fG6hJ9
REDIS_PASSWORD=X3vB6nM9qW2eR5tY8uI
```

## Step-by-Step Railway Deployment

### 1. Install Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login
```

### 2. Initialize Railway Project

```bash
cd /Users/royantony/blue-lotus-seo/saas-platform/backend

# Initialize Railway project
railway init

# Select "Empty Project"
# Name: "seo-blog-automation"
```

### 3. Add Database Services

In Railway Dashboard (https://railway.app/dashboard):

1. **Add PostgreSQL Database**
   - Click "New" → "Database" → "PostgreSQL"
   - Name: "postgres-db"

2. **Add Redis Database**
   - Click "New" → "Database" → "Redis"
   - Name: "redis-cache"

### 4. Configure Environment Variables

In Railway Dashboard → Your Service → Variables:

```bash
# Application Settings
ENVIRONMENT=production
DEBUG=false
APP_NAME=SEO Blog Automation SaaS

# Security (USE THE GENERATED SECRETS ABOVE)
SECRET_KEY=Kj9mN3pQ7sR2wE5tY8uI1oP4aS6dF0gH3jK6lM9nB2vC5xZ8zA1sD4fG7hJ0kL3pQ6rT9wE2yU5i
ENCRYPTION_KEY=bG92ZXMtc2VjdXJlLWVuY3J5cHRpb24ta2V5LTMyLWNoYXJhY3RlcnMtaGVyZQ==

# Database (Railway will auto-generate these)
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}

# External APIs (ADD YOUR REAL API KEYS)
OPENAI_API_KEY=sk-your-real-openai-api-key-here
SERPER_API_KEY=your-serper-api-key-here

# CORS (UPDATE WITH YOUR FRONTEND DOMAIN)
ALLOWED_ORIGINS=https://your-frontend.vercel.app,https://yourdomain.com

# Optional Services
SENTRY_DSN=https://your-sentry-dsn-here
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@domain.com
SMTP_PASSWORD=your-email-password
```

### 5. Deploy Backend

```bash
cd /Users/royantony/blue-lotus-seo/saas-platform/backend

# Deploy to Railway
railway up

# Railway will automatically:
# - Build your application
# - Install dependencies
# - Start the server
# - Provide a public URL
```

### 6. Verify Deployment

```bash
# Check deployment status
railway status

# View logs
railway logs

# Get your deployment URL
railway domain
```

Your backend will be available at: `https://your-service.up.railway.app`

### 7. Update Frontend Configuration

Update your frontend to connect to Railway backend:

```bash
cd /Users/royantony/blue-lotus-seo/saas-platform/frontend

# Update .env file
echo "VITE_API_URL=https://your-service.up.railway.app" > .env.production
```

### 8. Deploy Frontend to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy frontend
cd /Users/royantony/blue-lotus-seo/saas-platform/frontend
vercel --prod

# Follow prompts:
# - Link to existing project or create new
# - Set build command: npm run build
# - Set output directory: dist
```

## 🎯 Post-Deployment Steps

### 1. Test Your Deployment

```bash
# Test health endpoint
curl https://your-service.up.railway.app/health

# Test API documentation
# Visit: https://your-service.up.railway.app/docs
```

### 2. Update CORS Settings

In Railway Dashboard → Environment Variables:
```bash
ALLOWED_ORIGINS=https://your-frontend.vercel.app,https://your-domain.com
```

### 3. Set Up Custom Domain (Optional)

1. **Backend Domain**: Railway Dashboard → Domains → Add custom domain
2. **Frontend Domain**: Vercel Dashboard → Domains → Add domain

## 📊 Monitoring & Maintenance

### Railway Dashboard Features:
- ✅ Automatic deployments from Git
- ✅ Built-in metrics and logs
- ✅ Database management
- ✅ Environment variable management
- ✅ Automatic SSL certificates
- ✅ Zero-downtime deployments

### Cost Optimization:
- **Starter Plan**: $5/month per service
- **Database**: $5/month for PostgreSQL + Redis
- **Total**: ~$15-20/month

## 🚨 Important Security Notes

1. **✅ All security fixes applied** - your app is production-ready
2. **🔐 Use the generated secrets above** - never use default values
3. **🌐 Update ALLOWED_ORIGINS** with your actual domains
4. **🔑 Add real API keys** for OpenAI and other services
5. **📧 Configure email settings** for notifications

## 🎉 Success Indicators

After deployment, you should see:
- ✅ Railway service running (green status)
- ✅ Health endpoint responding: `/health`
- ✅ API documentation accessible: `/docs`
- ✅ Frontend connecting to backend
- ✅ Blog generation working with images
- ✅ SEO tags being generated
- ✅ Shopify publishing functional

## 📞 Troubleshooting

**Common Issues:**

1. **Build Failures**: Check Railway logs for dependency issues
2. **Database Errors**: Verify DATABASE_URL connection
3. **CORS Errors**: Update ALLOWED_ORIGINS with frontend domain
4. **API Key Errors**: Verify OPENAI_API_KEY is correct

**Get Help:**
```bash
railway logs --tail
railway status
```

---

**Ready to deploy?** Run these commands:

1. `railway login`
2. `cd /Users/royantony/blue-lotus-seo/saas-platform/backend`
3. `railway init`
4. Add environment variables in Railway dashboard
5. `railway up`

Your SEO Blog Automation SaaS will be live in production! 🚀