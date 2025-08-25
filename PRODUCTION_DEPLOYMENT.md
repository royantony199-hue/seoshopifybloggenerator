# Production Deployment Guide
## SEO Blog Automation SaaS

This guide covers secure production deployment of the SEO Blog Automation SaaS platform.

## 🛡️ Security First

**CRITICAL**: The security vulnerabilities have been fixed, but you MUST complete these steps before deployment:

### 1. Generate Production Secrets

```bash
# Generate secure secrets
python3 generate-production-secrets.py

# Install production dependencies
pip install cryptography==41.0.7
```

### 2. Configure Environment

```bash
# Copy and configure production environment
cp .env.production.example .env.production

# Edit .env.production with the generated secrets
# NEVER commit this file to version control!
```

## 🚀 Deployment Options

### Option 1: Railway (Recommended for Simplicity)

1. **Setup Railway Account**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   railway login
   ```

2. **Deploy Backend**
   ```bash
   cd backend/
   railway up
   
   # Add environment variables in Railway dashboard:
   # - SECRET_KEY (from generate-production-secrets.py)
   # - ENCRYPTION_KEY (from generate-production-secrets.py)
   # - OPENAI_API_KEY (your OpenAI key)
   # - ALLOWED_ORIGINS (your frontend domain)
   ```

3. **Deploy Frontend**
   ```bash
   cd frontend/
   # Update vercel.json with your Railway backend URL
   # Deploy to Vercel
   vercel --prod
   ```

**Cost**: ~$20-50/month (scales with usage)

### Option 2: Vercel + Supabase (Recommended for Scale)

1. **Setup Database (Supabase)**
   - Create Supabase project
   - Note the PostgreSQL connection string
   - Enable Redis addon

2. **Deploy Backend**
   ```bash
   # Configure Vercel for backend
   cd backend/
   vercel --prod
   ```

3. **Deploy Frontend**
   ```bash
   cd frontend/
   vercel --prod
   ```

**Cost**: ~$10-25/month (very scalable)

### Option 3: Docker + VPS (Full Control)

1. **Server Setup**
   ```bash
   # On your VPS (Ubuntu 22.04 recommended)
   sudo apt update
   sudo apt install docker.io docker-compose-plugin
   
   # Clone repository
   git clone <your-repo>
   cd seo-blog-automation
   ```

2. **Configure Production**
   ```bash
   # Generate secrets
   python3 generate-production-secrets.py
   
   # Configure environment
   cp .env.production.example .env.production
   # Edit .env.production with generated secrets
   ```

3. **Deploy**
   ```bash
   # Run deployment script
   ./deploy-production.sh
   ```

**Cost**: ~$5-20/month (fixed cost)

## 🔧 Post-Deployment Configuration

### 1. Database Setup
```bash
# Run migrations (Railway/Vercel will do this automatically)
python -m alembic upgrade head

# Create initial admin user
python create_admin_user.py
```

### 2. SSL/HTTPS
- **Railway/Vercel**: Automatic
- **VPS**: Configure nginx with Let's Encrypt

### 3. Domain Configuration
- Point your domain to the deployment
- Update ALLOWED_ORIGINS in environment variables
- Update frontend API URL

## 📊 Monitoring & Maintenance

### 1. Health Monitoring
```bash
# Check application health
curl https://your-api-domain.com/health
```

### 2. Error Tracking
- Configure Sentry DSN in environment variables
- Monitor error rates and performance

### 3. Database Backups
```bash
# Automated backups (configure cron job)
python backup_restore_system.py backup
```

## 🔐 Security Checklist

- [ ] ✅ Security middleware enabled
- [ ] ✅ Secure secrets generated (64+ chars)
- [ ] ✅ API keys encrypted in database
- [ ] ✅ Environment variables configured
- [ ] ✅ CORS properly configured
- [ ] ✅ Database connection secured
- [ ] ✅ Redis password protected
- [ ] ✅ SSL/HTTPS enabled
- [ ] ✅ Error monitoring configured
- [ ] ✅ Backup system implemented

## 🚨 Security Fixes Applied

The following critical vulnerabilities have been **FIXED**:

1. **✅ Security Middleware**: Enabled CSRF, rate limiting, and tenant middleware
2. **✅ Secret Key Management**: Proper validation and environment-based configuration
3. **✅ API Key Encryption**: Sensitive API keys now encrypted at rest
4. **✅ Environment Security**: Production-ready environment configuration
5. **✅ Database Initialization**: Proper lifespan management with error handling

## 📞 Support

For deployment assistance:
1. Check logs: `docker-compose logs backend` (Docker) or platform logs
2. Verify health endpoint: `/health`
3. Review environment variables
4. Check database connectivity

## 🎯 Performance Optimization

### Production Settings Applied:
- Multi-worker Uvicorn deployment
- Connection pooling for database
- Redis caching enabled
- Rate limiting configured
- Static file serving optimized

### Scaling Considerations:
- **Railway**: Automatic scaling based on traffic
- **Vercel**: Serverless scaling (unlimited)
- **VPS**: Manual scaling (add more workers/instances)

---

**IMPORTANT**: Test all functionality in a staging environment before production deployment. Monitor performance and error rates closely during the first 48 hours.