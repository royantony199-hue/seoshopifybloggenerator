# 🚀 SEO Blog Automation SaaS - Deployment Guide

## Quick Setup (5 Minutes)

### 1. Clone & Configure
```bash
git clone <repository-url>
cd seo-blog-automation-saas

# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

### 2. Required Environment Variables
```env
# Database
DATABASE_URL=postgresql://seo_user:seo_password_123@localhost:5432/seo_saas_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-super-secret-key-minimum-32-characters
JWT_SECRET_KEY=your-jwt-secret-key-minimum-32-characters

# CORS
ALLOWED_ORIGINS=["http://localhost:3000","https://yourdomain.com"]

# External APIs (Users will add their own)
OPENAI_API_KEY=optional-default-key

# Email (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Stripe (Optional for billing)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Monitoring (Optional)
SENTRY_DSN=https://...
```

### 3. Development Setup
```bash
# Start all services
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Check services
docker-compose ps

# View logs
docker-compose logs -f backend
```

### 4. Production Deployment

#### Option A: Docker Compose (Recommended for small-medium scale)
```bash
# Set production environment variables
export SECRET_KEY="your-production-secret-key"
export DATABASE_URL="postgresql://user:pass@prod-db:5432/seo_saas_db"

# Deploy
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Setup SSL (Let's Encrypt)
docker run -it --rm \
  -v /docker-volumes/etc/letsencrypt:/etc/letsencrypt \
  -v /docker-volumes/var/lib/letsencrypt:/var/lib/letsencrypt \
  -p 80:80 \
  certbot/certbot certonly --standalone -d yourdomain.com
```

#### Option B: AWS ECS (Scalable production)
```bash
# Build and push images
docker build -t your-registry/seo-backend:latest ./backend
docker build -t your-registry/seo-frontend:latest ./frontend

docker push your-registry/seo-backend:latest
docker push your-registry/seo-frontend:latest

# Deploy using provided ECS task definitions
aws ecs update-service --cluster seo-cluster --service seo-backend --force-new-deployment
```

#### Option C: Kubernetes
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/database.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml
kubectl apply -f k8s/ingress.yaml
```

## 🛠️ Configuration Options

### Subscription Plans
Edit `backend/app/core/config.py`:
```python
SUBSCRIPTION_PLANS = {
    "starter": {
        "name": "Starter",
        "price": 99.00,  # Your pricing
        "monthly_blogs": 100,
        "max_stores": 1,
    },
    "professional": {
        "name": "Professional", 
        "price": 299.00,
        "monthly_blogs": 500,
        "max_stores": 3,
    }
}
```

### Blog Templates
Add custom templates in `backend/app/core/config.py`:
```python
BLOG_TEMPLATES = {
    "your_industry": {
        "name": "Your Industry",
        "description": "Optimized for your specific industry",
        "sections": [
            "Industry Overview",
            "Key Benefits",
            "Implementation Guide",
            "Case Studies",
            "FAQ Section"
        ],
        "min_words": 2000,
        "faq_count": 15
    }
}
```

### Branding
Edit `frontend/src/config/branding.ts`:
```typescript
export const BRANDING = {
  appName: "Your SaaS Name",
  tagline: "Your tagline here",
  logo: "/path/to/your/logo.png",
  colors: {
    primary: "#1976d2",
    secondary: "#dc004e"
  }
};
```

## 🔧 Database Setup

### Initial Migration
```bash
# Access backend container
docker-compose exec backend bash

# Create initial migration
alembic revision --autogenerate -m "Initial tables"

# Apply migrations
alembic upgrade head

# Create admin user (optional)
python scripts/create_admin.py
```

### Database Backup
```bash
# Backup
docker-compose exec db pg_dump -U seo_user seo_saas_db > backup.sql

# Restore
docker-compose exec -T db psql -U seo_user seo_saas_db < backup.sql
```

## 📊 Monitoring & Analytics

### Health Checks
- Backend: `http://localhost:8000/health`
- Frontend: `http://localhost:3000`
- Database: Check via backend health endpoint
- Redis: Check via backend health endpoint

### Logs
```bash
# Application logs
docker-compose logs -f backend frontend

# Worker logs  
docker-compose logs -f worker

# Database logs
docker-compose logs -f db
```

### Metrics (Production)
- **Sentry**: Error tracking
- **CloudWatch**: AWS metrics
- **Flower**: Celery task monitoring (`http://localhost:5555`)

## 🔐 Security Checklist

- [ ] Change all default passwords
- [ ] Set strong JWT secrets (32+ characters)
- [ ] Enable HTTPS with SSL certificates
- [ ] Configure CORS properly
- [ ] Set up rate limiting
- [ ] Enable database backups
- [ ] Configure firewall rules
- [ ] Set up monitoring alerts

## 💰 Billing Setup (Optional)

### Stripe Integration
1. Create Stripe account
2. Add webhook endpoint: `https://yourdomain.com/api/webhooks/stripe`
3. Configure webhook events:
   - `invoice.payment_succeeded`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`

### Webhook Configuration
```bash
# Test webhook locally
stripe listen --forward-to localhost:8000/api/webhooks/stripe
```

## 📱 API Documentation

Access interactive API docs at:
- **Development**: `http://localhost:8000/docs`
- **Production**: `https://yourdomain.com/docs`

## 🚀 Scaling Considerations

### Traffic Growth
- **Horizontal scaling**: Add more backend containers
- **Database**: Use managed PostgreSQL (AWS RDS, Google Cloud SQL)
- **Redis**: Use managed Redis (AWS ElastiCache, Redis Cloud)
- **CDN**: CloudFront for static assets

### Cost Optimization
- **OpenAI costs**: Monitor token usage, implement caching
- **Database**: Optimize queries, add indexes
- **Storage**: Use S3 for file storage
- **Monitoring**: Set up cost alerts

## 🆘 Troubleshooting

### Common Issues

#### Backend won't start
```bash
# Check logs
docker-compose logs backend

# Common fixes
docker-compose down
docker-compose build --no-cache backend
docker-compose up -d
```

#### Database connection errors
```bash
# Check database is running
docker-compose ps db

# Reset database
docker-compose down -v
docker-compose up -d db
# Wait 30 seconds
docker-compose up -d backend
```

#### Frontend build errors
```bash
# Clear node_modules
docker-compose down
docker-compose build --no-cache frontend
docker-compose up -d
```

### Support
For technical support:
1. Check logs first
2. Review environment variables
3. Verify all services are running
4. Check GitHub issues
5. Contact support team

## 🔄 Updates & Maintenance

### Regular Updates
```bash
# Pull latest changes
git pull origin main

# Rebuild containers
docker-compose build

# Apply database migrations
docker-compose exec backend alembic upgrade head

# Restart services
docker-compose restart
```

### Backup Schedule
- **Daily**: Database backup
- **Weekly**: Full system backup
- **Monthly**: Archive old backups

---

**🎉 Your SEO Blog Automation SaaS is ready!**

Access your platform at: `http://localhost:3000`

Default admin login will be created during first setup.