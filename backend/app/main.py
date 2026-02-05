#!/usr/bin/env python3
"""
SEO Blog Automation SaaS Platform - Main FastAPI Application
"""

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from datetime import datetime, date
from pydantic import BaseModel
from typing import Optional
import logging

try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

from app.core.config import settings
from app.core.database import create_tables, get_db, Keyword, GeneratedBlog, Tenant
from app.routers import auth, users, stores, keywords, blogs, analytics, billing, products
from app.routers import settings as settings_router
from app.routers.demo_auth import get_demo_current_user
from app.middleware.tenant import TenantMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.csrf import CSRFMiddleware, get_csrf_token

logger = logging.getLogger(__name__)

# Multi-Store Configuration (tokens loaded from environment variables)
import os

SHOPIFY_STORES = {
    "perfectseed": {
        "id": "perfectseed",
        "name": "Perfect Seed",
        "shop_url": "perfectseed",
        "access_token": os.environ.get("SHOPIFY_ACCESS_TOKEN_PERFECTSEED", os.environ.get("SHOPIFY_ACCESS_TOKEN", "")),
        "blog_handle": "imaginal-tech",
        "custom_domain": "www.imaginal.tech",
        "api_version": "2024-01"
    },
    "trusttheplant": {
        "id": "trusttheplant",
        "name": "Trust The Plant",
        "shop_url": "bluelotusimaginal",
        "access_token": os.environ.get("SHOPIFY_ACCESS_TOKEN_TRUSTTHEPLANT", ""),
        "blog_handle": "news",
        "custom_domain": None,
        "api_version": "2024-01"
    }
}

# Initialize Sentry for error monitoring (optional)
if SENTRY_AVAILABLE and settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[FastApiIntegration()],
        traces_sample_rate=0.1,
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager with proper database initialization"""
    # Log database configuration at startup
    db_url = settings.DATABASE_URL
    db_type = "PostgreSQL" if "postgresql" in db_url else "SQLite"
    print(f"🔧 Database: {db_type}")
    print(f"🔧 DATABASE_URL starts with: {db_url[:50]}...")

    # Startup - ensure database tables exist
    try:
        await create_tables()
        print("✅ Database tables created/verified")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        # Don't fail startup, but log the error
    yield
    # Shutdown - cleanup if needed

# Initialize FastAPI app
app = FastAPI(
    title="SEO Blog Automation SaaS",
    description="Multi-tenant platform for automated SEO blog generation and Shopify publishing",
    version="1.0.0",
    lifespan=lifespan
)

# Security
security = HTTPBearer()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for simple frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security middleware (disabled for simple mode)
# if settings.ENVIRONMENT == "production":
#     app.add_middleware(CSRFMiddleware, secret_key=settings.SECRET_KEY)
#     app.add_middleware(TenantMiddleware)
#     app.add_middleware(RateLimitMiddleware)

# HTML Frontend Template
FRONTEND_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blue Lotus SEO Tool</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .hero-section { background: linear-gradient(135deg, #2E7D32, #4CAF50); color: white; }
        .stat-card { border-radius: 15px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
        .btn-gradient { background: linear-gradient(45deg, #4CAF50, #2E7D32); border: none; color: white; }
        .btn-gradient:hover { background: linear-gradient(45deg, #2E7D32, #1B5E20); color: white; }
        .store-selector { background: rgba(255,255,255,0.15); border-radius: 10px; padding: 10px 15px; }
        .store-selector select { background: white; border: none; padding: 8px 15px; border-radius: 5px; font-weight: 500; }
        .store-badge { font-size: 0.8rem; padding: 4px 10px; border-radius: 20px; }
    </style>
</head>
<body>
    <div class="hero-section py-4">
        <div class="container">
            <div class="d-flex justify-content-between align-items-center flex-wrap">
                <div>
                    <h1><i class="fas fa-leaf me-2"></i>Blue Lotus SEO Tool</h1>
                    <p class="mb-0">AI-Powered Content Generation & Publishing</p>
                </div>
                <div class="store-selector mt-2 mt-md-0">
                    <label class="me-2"><i class="fas fa-store me-1"></i>Store:</label>
                    <select id="storeSelector" class="form-select-sm" onchange="switchStore()">
                        <option value="perfectseed">Perfect Seed</option>
                        <option value="trusttheplant">Trust The Plant</option>
                    </select>
                </div>
            </div>
        </div>
    </div>

    <div class="container my-4">
        <div class="alert alert-info d-flex align-items-center" id="storeInfo">
            <i class="fas fa-info-circle me-2"></i>
            <span>Publishing to: <strong id="currentStoreName">Perfect Seed</strong> (<span id="currentStoreUrl">perfectseed.myshopify.com</span>)</span>
        </div>

        <div class="row g-3 mb-4">
            <div class="col-md-3">
                <div class="card stat-card text-center">
                    <div class="card-body">
                        <h3 class="text-warning" id="pending-articles">0</h3>
                        <small>Pending Articles</small>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card text-center">
                    <div class="card-body">
                        <h3 class="text-success" id="published-articles">0</h3>
                        <small>Published Articles</small>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card text-center">
                    <div class="card-body">
                        <h3 class="text-primary" id="keywords-remaining">0</h3>
                        <small>Keywords Remaining</small>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card text-center">
                    <div class="card-body">
                        <h3 class="text-info" id="published-today">0</h3>
                        <small>Published Today</small>
                    </div>
                </div>
            </div>
        </div>

        <div class="card mt-4">
            <div class="card-body text-center">
                <h4>Generate New Content</h4>
                <div class="row g-2 align-items-end justify-content-center">
                    <div class="col-auto">
                        <label class="form-label">Articles:</label>
                        <select id="articleCount" class="form-select">
                            <option value="1">1 article</option>
                            <option value="2">2 articles</option>
                            <option value="5">5 articles</option>
                            <option value="10">10 articles</option>
                        </select>
                    </div>
                    <div class="col-auto">
                        <button id="generateBtn" class="btn btn-gradient btn-lg">
                            <i class="fas fa-magic me-2"></i>Generate with OpenAI
                        </button>
                    </div>
                </div>
                <div id="generateStatus" class="mt-3"></div>
            </div>
        </div>

        <div class="card mt-4">
            <div class="card-header"><h5><i class="fas fa-list me-2"></i>Pending Articles</h5></div>
            <div class="card-body"><div id="pendingArticles">Loading...</div></div>
        </div>

        <div class="card mt-4">
            <div class="card-header"><h5><i class="fas fa-check-circle me-2"></i>Published Articles</h5></div>
            <div class="card-body"><div id="publishedArticles">Loading...</div></div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.getElementById('generateBtn').addEventListener('click', generateContent);

        function generateContent() {
            const count = document.getElementById('articleCount').value;
            const btn = document.getElementById('generateBtn');
            const status = document.getElementById('generateStatus');

            btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generating...';
            btn.disabled = true;
            status.innerHTML = '<div class="alert alert-info">Generating ' + count + ' articles...</div>';

            fetch('/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ count: parseInt(count) })
            })
            .then(r => r.json())
            .then(data => {
                if (data.status === 'success') {
                    status.innerHTML = '<div class="alert alert-success">' + data.message + '</div>';
                } else if (data.status === 'warning') {
                    status.innerHTML = '<div class="alert alert-warning">' + data.message + '</div>';
                } else {
                    status.innerHTML = '<div class="alert alert-danger">Error: ' + (data.error || 'Failed') + '</div>';
                }
                loadPendingArticles();
                loadStats();
            })
            .catch(e => status.innerHTML = '<div class="alert alert-danger">Error: ' + e + '</div>')
            .finally(() => { btn.innerHTML = '<i class="fas fa-magic me-2"></i>Generate with OpenAI'; btn.disabled = false; });
        }

        // Store data
        const storeData = {
            perfectseed: { name: 'Perfect Seed', url: 'perfectseed.myshopify.com', domain: 'www.imaginal.tech' },
            trusttheplant: { name: 'Trust The Plant', url: 'bluelotusimaginal.myshopify.com', domain: null }
        };
        let currentStore = 'perfectseed';

        function switchStore() {
            currentStore = document.getElementById('storeSelector').value;
            const store = storeData[currentStore];
            document.getElementById('currentStoreName').textContent = store.name;
            document.getElementById('currentStoreUrl').textContent = store.domain || store.url;
            loadPendingArticles();
            loadPublishedArticles();
        }

        function loadPendingArticles() {
            fetch('/api/content').then(r => r.json()).then(data => {
                const pending = data.content ? data.content.filter(a => a.status === 'pending' || a.status === 'draft') : [];
                const container = document.getElementById('pendingArticles');
                if (pending.length > 0) {
                    container.innerHTML = pending.map(a => `
                        <div class="card mb-2">
                            <div class="card-body d-flex justify-content-between align-items-center">
                                <div><h6 class="mb-1">${a.title}</h6><small class="text-muted">Keyword: ${a.keyword}</small></div>
                                <div class="d-flex gap-2">
                                    <button class="btn btn-sm btn-success" onclick="approveArticle(${a.id})">
                                        <i class="fas fa-upload me-1"></i>Publish to ${storeData[currentStore].name}
                                    </button>
                                </div>
                            </div>
                        </div>
                    `).join('');
                } else {
                    container.innerHTML = '<div class="alert alert-info">No pending articles. Generate some content first!</div>';
                }
            });
        }

        function approveArticle(id) {
            const store = storeData[currentStore];
            if (!confirm('Publish this article to ' + store.name + '?')) return;

            fetch('/api/publish/' + id + '?store_id=' + currentStore, { method: 'POST' })
            .then(r => r.json())
            .then(data => {
                if (data.status === 'success') {
                    alert('Published to ' + store.name + '!\\n\\nLive URL: ' + (data.url || 'Pending'));
                } else {
                    alert('Error: ' + data.error);
                }
                loadPendingArticles();
                loadPublishedArticles();
                loadStats();
            });
        }

        function loadStats() {
            fetch('/api/stats').then(r => r.json()).then(data => {
                document.getElementById('pending-articles').textContent = data.pending_content || 0;
                document.getElementById('published-articles').textContent = data.published_content || 0;
                document.getElementById('keywords-remaining').textContent = data.remaining_keywords || 0;
                document.getElementById('published-today').textContent = data.published_today || 0;
            });
        }

        function loadPublishedArticles() {
            fetch('/api/content').then(r => r.json()).then(data => {
                const published = data.content ? data.content.filter(a => a.status === 'published') : [];
                const container = document.getElementById('publishedArticles');
                if (published.length > 0) {
                    container.innerHTML = '<div class="table-responsive"><table class="table table-striped"><thead><tr><th>Title</th><th>Keyword</th><th>Store</th><th>Live Link</th></tr></thead><tbody>' +
                        published.map(a => `
                            <tr>
                                <td>${a.title}</td>
                                <td><span class="badge bg-secondary">${a.keyword}</span></td>
                                <td><span class="badge ${a.store_id === 'trusttheplant' ? 'bg-info' : 'bg-primary'}">${a.store_name || 'Perfect Seed'}</span></td>
                                <td>${a.live_url ? '<a href="' + a.live_url + '" target="_blank" class="btn btn-sm btn-success"><i class="fas fa-external-link-alt me-1"></i>View Live</a>' : '<span class="text-muted">Pending sync</span>'}</td>
                            </tr>
                        `).join('') + '</tbody></table></div>';
                } else {
                    container.innerHTML = '<div class="alert alert-info">No published articles yet.</div>';
                }
            });
        }

        loadPendingArticles();
        loadPublishedArticles();
        loadStats();
    </script>
</body>
</html>
"""

# Pydantic models for simple API
class GenerateRequest(BaseModel):
    count: int = 1

# Simple API Routes (for HTML frontend compatibility)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve HTML frontend"""
    return FRONTEND_HTML

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "features": "cbd_content_generator",
        "version": "v2.0",
        "timestamp": str(date.today())
    }

@app.get("/api/stats")
async def get_simple_stats(db: Session = Depends(get_db)):
    """Get simple stats for dashboard"""
    try:
        user = await get_demo_current_user(db)
        tenant_id = user.tenant_id

        # Count keywords
        total_keywords = db.query(Keyword).filter(Keyword.tenant_id == tenant_id).count()
        used_keywords = db.query(Keyword).filter(
            Keyword.tenant_id == tenant_id,
            Keyword.blog_generated == True
        ).count()
        remaining_keywords = total_keywords - used_keywords

        # Count blogs
        pending_blogs = db.query(GeneratedBlog).filter(
            GeneratedBlog.tenant_id == tenant_id,
            GeneratedBlog.status == "draft"
        ).count()

        published_blogs = db.query(GeneratedBlog).filter(
            GeneratedBlog.tenant_id == tenant_id,
            GeneratedBlog.published == True
        ).count()

        # Count today's published
        today = date.today()
        published_today = db.query(GeneratedBlog).filter(
            GeneratedBlog.tenant_id == tenant_id,
            GeneratedBlog.published == True,
            GeneratedBlog.published_at >= datetime.combine(today, datetime.min.time())
        ).count()

        return {
            "remaining_keywords": remaining_keywords,
            "pending_content": pending_blogs,
            "published_content": published_blogs,
            "published_today": published_today
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return {
            "remaining_keywords": 0,
            "pending_content": 0,
            "published_content": 0,
            "published_today": 0,
            "error": str(e)
        }

@app.get("/api/content")
async def get_simple_content(db: Session = Depends(get_db)):
    """Get all content for dashboard"""
    try:
        user = await get_demo_current_user(db)
        tenant_id = user.tenant_id

        blogs = db.query(GeneratedBlog).filter(
            GeneratedBlog.tenant_id == tenant_id
        ).order_by(GeneratedBlog.created_at.desc()).limit(100).all()

        content = []
        for blog in blogs:
            # Get keyword info
            keyword_text = ""
            search_volume = 0
            if blog.keyword_id:
                kw = db.query(Keyword).filter(Keyword.id == blog.keyword_id).first()
                if kw:
                    keyword_text = kw.keyword
                    search_volume = kw.search_volume or 0

            # Get store info from template_used field (stores which store it was published to)
            store_id = blog.template_used if blog.template_used in SHOPIFY_STORES else "perfectseed"
            store_name = SHOPIFY_STORES.get(store_id, {}).get("name", "Perfect Seed")

            content.append({
                "id": blog.id,
                "title": blog.title,
                "keyword": keyword_text,
                "search_volume": search_volume,
                "status": "published" if blog.published else blog.status,
                "live_url": blog.live_url,
                "store_id": store_id if blog.published else None,
                "store_name": store_name if blog.published else None,
                "created_at": str(blog.created_at)
            })

        return {"content": content}
    except Exception as e:
        logger.error(f"Error getting content: {e}")
        return {"content": [], "error": str(e)}

@app.post("/api/generate")
async def generate_simple_content(request: GenerateRequest, db: Session = Depends(get_db)):
    """Generate content using OpenAI"""
    try:
        from app.routers.blogs import BlogGenerator
        from app.core.config import BLOG_TEMPLATES

        user = await get_demo_current_user(db)
        tenant_id = user.tenant_id

        # Check for OpenAI API key
        if not user.openai_api_key:
            return {
                "status": "error",
                "error": "OpenAI API key not configured. Please set the OPENAI_API_KEY environment variable."
            }

        # Get pending keywords
        pending_keywords = db.query(Keyword).filter(
            Keyword.tenant_id == tenant_id,
            Keyword.blog_generated == False,
            Keyword.status == "pending"
        ).limit(request.count).all()

        if not pending_keywords:
            return {
                "status": "warning",
                "message": "All available keywords have been used! No new content can be generated to avoid duplicates. You have successfully covered all topics in your keyword database."
            }

        generated = 0
        failed = 0
        generator = BlogGenerator(user.openai_api_key)

        for keyword in pending_keywords:
            try:
                # Mark as processing
                keyword.status = "processing"
                db.commit()

                # Generate blog content
                template_config = {"template_type": "cbd_wellness"}
                store_info = {
                    "shop_url": "",
                    "blog_handle": "",
                    "default_product_url": "",
                    "product_integration_text": "",
                    "template_type": "cbd_wellness",
                    "products": []
                }

                blog_content = generator.generate_blog_content(
                    keyword=keyword.keyword,
                    template_config=template_config,
                    store_info=store_info
                )

                if blog_content and blog_content.get("content_html"):
                    # Save to database
                    new_blog = GeneratedBlog(
                        tenant_id=tenant_id,
                        keyword_id=keyword.id,
                        title=blog_content.get("title", f"Complete Guide to {keyword.keyword.title()}"),
                        content_html=blog_content.get("content_html", ""),
                        meta_description=blog_content.get("meta_description", ""),
                        word_count=blog_content.get("word_count", 0),
                        status="draft",
                        published=False
                    )
                    db.add(new_blog)

                    # Mark keyword as completed
                    keyword.status = "completed"
                    keyword.blog_generated = True
                    keyword.processed_at = datetime.utcnow()
                    db.commit()
                    generated += 1
                else:
                    keyword.status = "failed"
                    db.commit()
                    failed += 1
            except Exception as e:
                logger.error(f"Error generating blog for keyword {keyword.keyword}: {e}")
                keyword.status = "failed"
                db.commit()
                failed += 1

        if generated > 0:
            return {
                "status": "success",
                "message": f"Successfully generated {generated} articles!",
                "generated": generated,
                "failed": failed
            }
        else:
            return {
                "status": "error",
                "error": f"Failed to generate articles. {failed} attempts failed.",
                "generated": 0,
                "failed": failed
            }
    except Exception as e:
        logger.error(f"Error generating content: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

@app.get("/api/store-options")
async def get_store_options():
    """Get available Shopify stores for dropdown selector"""
    stores = []
    for store_id, store in SHOPIFY_STORES.items():
        stores.append({
            "id": store_id,
            "name": store["name"],
            "shop_url": f"{store['shop_url']}.myshopify.com",
            "blog_handle": store["blog_handle"],
            "custom_domain": store.get("custom_domain")
        })
    return {"stores": stores}


@app.post("/api/publish/{blog_id}")
async def publish_simple_content(blog_id: int, store_id: str = "perfectseed", db: Session = Depends(get_db)):
    """Publish a single article to selected Shopify store"""
    import requests

    try:
        user = await get_demo_current_user(db)
        tenant_id = user.tenant_id

        blog = db.query(GeneratedBlog).filter(
            GeneratedBlog.id == blog_id,
            GeneratedBlog.tenant_id == tenant_id
        ).first()

        if not blog:
            return {"status": "error", "error": "Article not found"}

        # Get store configuration
        if store_id not in SHOPIFY_STORES:
            return {"status": "error", "error": f"Store '{store_id}' not found"}

        store = SHOPIFY_STORES[store_id]
        shop_url = store["shop_url"]
        access_token = store["access_token"]
        blog_handle = store["blog_handle"]
        api_version = store.get("api_version", "2024-01")
        custom_domain = store.get("custom_domain")

        # First, get the blog ID from the blog handle
        blog_list_url = f"https://{shop_url}.myshopify.com/admin/api/{api_version}/blogs.json"
        headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json"
        }

        blogs_response = requests.get(blog_list_url, headers=headers)
        if blogs_response.status_code != 200:
            logger.error(f"Failed to get blogs: {blogs_response.text}")
            return {"status": "error", "error": f"Failed to connect to Shopify: {blogs_response.status_code}"}

        blogs_data = blogs_response.json()
        shopify_blog_id = None

        for shopify_blog in blogs_data.get("blogs", []):
            if shopify_blog.get("handle") == blog_handle or shopify_blog.get("title").lower() == blog_handle.lower():
                shopify_blog_id = shopify_blog["id"]
                break

        if not shopify_blog_id:
            return {"status": "error", "error": f"Blog '{blog_handle}' not found in Shopify store"}

        # Create the article in Shopify
        article_url = f"https://{shop_url}.myshopify.com/admin/api/{api_version}/blogs/{shopify_blog_id}/articles.json"

        article_data = {
            "article": {
                "title": blog.title,
                "body_html": blog.content_html,
                "published": True,
                "tags": "seo, blue lotus, wellness"
            }
        }

        if blog.meta_description:
            article_data["article"]["summary_html"] = f"<p>{blog.meta_description}</p>"

        response = requests.post(article_url, headers=headers, json=article_data)

        if response.status_code in [200, 201]:
            article_result = response.json()
            shopify_article = article_result.get("article", {})
            article_id = shopify_article.get("id")
            article_handle = shopify_article.get("handle")

            # Build live URL
            if custom_domain:
                live_url = f"https://{custom_domain}/blogs/{blog_handle}/{article_handle}"
            else:
                live_url = f"https://{shop_url}.myshopify.com/blogs/{blog_handle}/{article_handle}"

            # Update blog record
            blog.published = True
            blog.status = "published"
            blog.published_at = datetime.utcnow()
            blog.shopify_article_id = str(article_id)
            blog.shopify_handle = article_handle
            blog.live_url = live_url
            blog.template_used = store_id  # Store which store it was published to
            db.commit()

            return {
                "status": "success",
                "message": f"Article published to {store['name']}!",
                "url": live_url,
                "store": store["name"],
                "article_id": article_id
            }
        else:
            error_msg = response.json().get("errors", response.text)
            logger.error(f"Shopify publish error: {error_msg}")
            return {"status": "error", "error": f"Shopify error: {error_msg}"}

    except Exception as e:
        logger.error(f"Error publishing content: {e}")
        return {"status": "error", "error": str(e)}

@app.post("/api/publish/all")
async def publish_all_content(db: Session = Depends(get_db)):
    """Publish all pending articles"""
    try:
        user = await get_demo_current_user(db)
        tenant_id = user.tenant_id

        pending_blogs = db.query(GeneratedBlog).filter(
            GeneratedBlog.tenant_id == tenant_id,
            GeneratedBlog.published == False,
            GeneratedBlog.status == "draft"
        ).all()

        if not pending_blogs:
            return {"status": "warning", "message": "No pending articles to publish"}

        published = 0
        failed = 0

        for blog in pending_blogs:
            try:
                blog.published = True
                blog.status = "published"
                blog.published_at = datetime.utcnow()
                published += 1
            except Exception:
                failed += 1

        db.commit()

        return {
            "status": "success",
            "message": f"Published {published} articles",
            "published": published,
            "failed": failed,
            "total": len(pending_blogs)
        }
    except Exception as e:
        logger.error(f"Error publishing all content: {e}")
        return {"status": "error", "error": str(e)}

@app.get("/content/{blog_id}", response_class=HTMLResponse)
async def view_content(blog_id: int, db: Session = Depends(get_db)):
    """View a single article"""
    try:
        blog = db.query(GeneratedBlog).filter(GeneratedBlog.id == blog_id).first()
        if not blog:
            return "<h1>Article not found</h1>"

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{blog.title}</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container my-4">
                <a href="/" class="btn btn-secondary mb-3">Back to Dashboard</a>
                <h1>{blog.title}</h1>
                <div class="content">{blog.content_html}</div>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        return f"<h1>Error: {e}</h1>"

@app.get("/api/csrf-token")
async def get_csrf_token_endpoint():
    """Get CSRF token for form submissions"""
    token = get_csrf_token(settings.SECRET_KEY)
    return {"csrf_token": token}

# Include API routers (for advanced usage)
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(settings_router.router, prefix="/api/settings", tags=["Settings"])
app.include_router(keywords.router, prefix="/api/keywords", tags=["Keywords"])
app.include_router(blogs.router, prefix="/api/blogs", tags=["Blogs"])
app.include_router(stores.router, prefix="/api/stores", tags=["Stores"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )