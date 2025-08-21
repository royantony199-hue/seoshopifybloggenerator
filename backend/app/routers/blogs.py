#!/usr/bin/env python3
"""
Blog generation and management router
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import time
import openai
import requests

from app.core.database import get_db, GeneratedBlog, Keyword, ShopifyStore, KeywordCampaign, Tenant
from app.routers.auth import get_current_user, User
from app.routers.demo_auth import get_demo_current_user
from app.core.config import settings, BLOG_TEMPLATES

router = APIRouter()

# Pydantic models
class BlogGenerateRequest(BaseModel):
    keyword_ids: List[int]
    store_id: int
    template_type: Optional[str] = "ecommerce_general"
    auto_publish: bool = False

class BlogResponse(BaseModel):
    id: int
    title: str
    keyword: Optional[str]
    word_count: Optional[int]
    status: str
    live_url: Optional[str]
    published: bool
    created_at: datetime
    published_at: Optional[datetime]

class BlogContent(BaseModel):
    id: int
    title: str
    content_html: str
    meta_description: Optional[str]
    word_count: int
    live_url: Optional[str]

class BatchGenerateResponse(BaseModel):
    success: bool
    message: str
    job_id: str
    blogs_queued: int
    estimated_completion: str

# Blog generation engine
class BlogGenerator:
    """Core blog generation engine"""
    
    def __init__(self, openai_api_key: str):
        self.client = openai.OpenAI(api_key=openai_api_key)
    
    def generate_blog_content(self, keyword: str, template_config: dict, store_info: dict) -> dict:
        """Generate blog content using OpenAI"""
        
        template = BLOG_TEMPLATES[template_config.get("template_type", "ecommerce_general")]
        
        # Build comprehensive prompt
        prompt = self._build_prompt(keyword, template, store_info)
        
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert SEO content writer and digital marketing specialist who creates high-converting, comprehensive blog posts that rank #1 on Google. Your content is thoroughly researched, engaging, and optimized for both search engines and user experience."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=4000,
                temperature=0.7
            )
            
            generation_time = time.time() - start_time
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else 0
            
            # Extract metadata
            word_count = len(content.split())
            
            # Generate meta description
            meta_description = self._generate_meta_description(keyword, content)
            
            return {
                "content_html": content,
                "word_count": word_count,
                "meta_description": meta_description,
                "generation_time": generation_time,
                "tokens_used": tokens_used
            }
            
        except Exception as e:
            raise Exception(f"Blog generation failed: {str(e)}")
    
    def _build_prompt(self, keyword: str, template: dict, store_info: dict) -> str:
        """Build comprehensive blog generation prompt"""
        
        product_integration = ""
        if store_info.get("default_product_url"):
            product_integration = f"""
            - Naturally integrate this product recommendation: "{store_info.get('product_integration_text', f'For premium quality products, check out: {store_info["default_product_url"]}')}"
            """
        
        prompt = f'''Create a comprehensive, SEO-optimized blog post about "{keyword}" using the {template["name"]} template.

STRICT REQUIREMENTS:
- MINIMUM {template["min_words"]} words (aim for {template["min_words"] + 500}+ words)
- Use "{keyword}" naturally {12 if template["min_words"] >= 2500 else 10}-15 times throughout
- Include {template["faq_count"]}+ comprehensive FAQ questions with detailed answers
- Professional HTML structure with proper DOCTYPE, head, and body tags
- Target long-tail keywords related to "{keyword}"
{product_integration}

EXACT HTML STRUCTURE:
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{keyword.title()}: Complete Professional Guide 2025</title>
    <meta name="description" content="Comprehensive guide to {keyword} with expert insights, practical advice, and detailed recommendations for optimal results.">
</head>
<body>
    <h1>{keyword.title()}: Complete Professional Guide 2025</h1>
    
    <p>Opening paragraph with {keyword} mentioned in first sentence and compelling hook... (300+ words)</p>
    
    <h2>Table of Contents</h2>
    <ul>
        {"".join([f"<li><a href=\"#{section.lower().replace(' ', '-').replace('&', '')}\">{section}</a></li>" for section in template["sections"]])}
    </ul>
    
    <!-- Generate comprehensive sections based on template sections -->
    {self._generate_section_structure(template["sections"], keyword)}
    
    <h2 id="faq">Comprehensive FAQ Section</h2>
    <!-- Generate {template["faq_count"]}+ detailed FAQ questions -->
    
    <h2 id="conclusion">Conclusion</h2>
    <p>Comprehensive conclusion summarizing key insights about {keyword}... (400+ words)</p>
    
</body>
</html>

CONTENT GUIDELINES:
- Write in an authoritative, professional tone
- Include scientific backing and evidence where relevant
- Use subheadings, bullet points, and proper formatting
- Optimize for featured snippets
- Include internal linking opportunities
- Add proper medical/legal disclaimers if applicable
- Focus on user intent and providing genuine value

Target minimum {template["min_words"]} words with exceptional quality and depth.'''

        return prompt
    
    def _generate_section_structure(self, sections: List[str], keyword: str) -> str:
        """Generate HTML structure for template sections"""
        html_sections = []
        
        for section in sections:
            section_id = section.lower().replace(' ', '-').replace('&', '')
            html_sections.append(f'''
    <h2 id="{section_id}">{section.replace('[KEYWORD]', keyword.title())}</h2>
    <p>Comprehensive content for {section.lower()} related to {keyword}... (400+ words)</p>''')
        
        return "".join(html_sections)
    
    def _generate_meta_description(self, keyword: str, content: str) -> str:
        """Generate meta description from content"""
        # Extract first 150-160 characters of meaningful content
        # This is a simplified version - could be enhanced with AI
        clean_content = content.replace('<', ' ').replace('>', ' ')
        words = clean_content.split()[:25]  # First 25 words
        meta_desc = ' '.join(words)
        
        if len(meta_desc) > 155:
            meta_desc = meta_desc[:155] + "..."
        
        return f"Complete guide to {keyword}. {meta_desc}"

class ShopifyPublisher:
    """Shopify blog publishing engine"""
    
    def __init__(self, store_info: dict):
        self.store_info = store_info
        self.api_base = f"https://{store_info['shop_url']}.myshopify.com/admin/api/2025-07"
        self.headers = {
            'X-Shopify-Access-Token': store_info['access_token'],
            'Content-Type': 'application/json'
        }
    
    def publish_blog(self, title: str, content: str, handle: str) -> dict:
        """Publish blog to Shopify"""
        
        try:
            # Check if we have real credentials
            if self.store_info.get('access_token', '').startswith('demo_') or not self.store_info.get('access_token'):
                # Demo Mode - Skip actual Shopify API calls
                demo_article_id = f"demo_article_{int(time.time())}"
                demo_url = f"https://{self.store_info['shop_url']}.myshopify.com/blogs/{self.store_info['blog_handle']}/{handle}"
                
                return {
                    "success": True,
                    "article_id": demo_article_id,
                    "live_url": demo_url,
                    "demo_mode": True
                }
            
            # Real Shopify API call
            blog_id_response = requests.get(f"{self.api_base}/blogs.json", headers=self.headers)
            
            if blog_id_response.status_code != 200:
                raise Exception(f"Failed to get blogs: {blog_id_response.text}")
            
            blogs = blog_id_response.json().get('blogs', [])
            target_blog = None
            
            # Find the target blog by handle
            for blog in blogs:
                if blog.get('handle') == self.store_info['blog_handle']:
                    target_blog = blog
                    break
            
            if not target_blog:
                raise Exception(f"Blog with handle '{self.store_info['blog_handle']}' not found")
            
            # Create the article
            article_data = {
                "article": {
                    "title": title,
                    "body_html": content,
                    "handle": handle,
                    "published": True,
                    "tags": "SEO, Automated Content"
                }
            }
            
            response = requests.post(
                f"{self.api_base}/blogs/{target_blog['id']}/articles.json",
                headers=self.headers,
                json=article_data
            )
            
            if response.status_code == 201:
                article = response.json()['article']
                # Use the actual domain instead of .myshopify.com
                live_url = f"https://www.imaginal.tech/blogs/{self.store_info['blog_handle']}/{handle}"
                
                return {
                    "success": True,
                    "article_id": str(article['id']),
                    "live_url": live_url,
                    "demo_mode": False
                }
            else:
                raise Exception(f"Shopify API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

def generate_single_blog(
    keyword_id: int,
    store_id: int,
    template_type: str,
    auto_publish: bool,
    tenant_id: int,
    openai_api_key: str,
    db: Session
):
    """Background task to generate a single blog"""
    
    try:
        # Get keyword and store info
        keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()
        store = db.query(ShopifyStore).filter(ShopifyStore.id == store_id).first()
        
        if not keyword or not store:
            return
        
        # Update keyword status
        keyword.status = "processing"
        db.commit()
        
        # Generate blog content
        generator = BlogGenerator(openai_api_key)
        
        store_info = {
            "shop_url": store.shop_url,
            "blog_handle": store.blog_handle,
            "default_product_url": store.default_product_url,
            "product_integration_text": store.product_integration_text,
            "template_type": template_type
        }
        
        result = generator.generate_blog_content(keyword.keyword, {"template_type": template_type}, store_info)
        
        # Create blog record
        blog = GeneratedBlog(
            tenant_id=tenant_id,
            store_id=store_id,
            keyword_id=keyword_id,
            title=f"{keyword.keyword.title()}: Complete Professional Guide 2025",
            content_html=result["content_html"],
            meta_description=result["meta_description"],
            word_count=result["word_count"],
            template_used=template_type,
            generation_time=result["generation_time"],
            tokens_used=result["tokens_used"],
            status="draft"
        )
        
        db.add(blog)
        db.commit()
        db.refresh(blog)
        
        # Auto-publish if requested
        if auto_publish:
            publisher = ShopifyPublisher({
                "shop_url": store.shop_url,
                "access_token": store.access_token,
                "blog_handle": store.blog_handle
            })
            
            handle = keyword.keyword.lower().replace(" ", "-").replace("'", "")
            publish_result = publisher.publish_blog(blog.title, blog.content_html, handle)
            
            if publish_result["success"]:
                blog.published = True
                blog.status = "published"
                blog.shopify_article_id = publish_result["article_id"]
                blog.shopify_handle = handle
                blog.live_url = publish_result["live_url"]
                blog.published_at = datetime.utcnow()
            else:
                blog.status = "failed"
                blog.error_message = publish_result["error"]
        
        # Update keyword status
        keyword.status = "completed"
        keyword.blog_generated = True
        keyword.processed_at = datetime.utcnow()
        
        db.commit()
        
    except Exception as e:
        # Update keyword status to failed
        keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()
        if keyword:
            keyword.status = "failed"
            db.commit()
        
        print(f"Blog generation failed for keyword {keyword_id}: {str(e)}")

# Routes
@router.post("/generate", response_model=BatchGenerateResponse)
async def generate_blogs(
    request: BlogGenerateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate blogs for selected keywords"""
    
    # Get demo user for testing
    current_user = await get_demo_current_user(db)
    
    # Validate user has OpenAI API key
    if not current_user.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OpenAI API key required. Please add it in your profile settings."
        )
    
    # Validate keywords belong to user's tenant
    keywords = db.query(Keyword).filter(
        Keyword.id.in_(request.keyword_ids),
        Keyword.tenant_id == current_user.tenant_id,
        Keyword.status == "pending"
    ).all()
    
    if len(keywords) != len(request.keyword_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Some keywords not found or already processed"
        )
    
    # Validate store
    store = db.query(ShopifyStore).filter(
        ShopifyStore.id == request.store_id,
        ShopifyStore.tenant_id == current_user.tenant_id
    ).first()
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )
    
    # Check subscription limits
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if tenant.monthly_blogs_used + len(keywords) > tenant.monthly_blog_limit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Would exceed monthly blog limit. Used: {tenant.monthly_blogs_used}, Limit: {tenant.monthly_blog_limit}"
        )
    
    # Generate job ID
    import uuid
    job_id = str(uuid.uuid4())
    
    # Queue background tasks
    for keyword in keywords:
        background_tasks.add_task(
            generate_single_blog,
            keyword.id,
            request.store_id,
            request.template_type,
            request.auto_publish,
            current_user.tenant_id,
            current_user.openai_api_key,
            db
        )
    
    # Update tenant usage
    tenant.monthly_blogs_used += len(keywords)
    db.commit()
    
    return BatchGenerateResponse(
        success=True,
        message=f"Queued {len(keywords)} blogs for generation",
        job_id=job_id,
        blogs_queued=len(keywords),
        estimated_completion=f"{len(keywords) * 3} minutes"
    )

@router.get("/", response_model=List[BlogResponse])
async def get_blogs(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get blogs for current tenant"""
    
    # Get demo user for testing
    current_user = await get_demo_current_user(db)
    
    query = db.query(GeneratedBlog).filter(
        GeneratedBlog.tenant_id == current_user.tenant_id
    ).order_by(GeneratedBlog.created_at.desc())
    
    if status:
        query = query.filter(GeneratedBlog.status == status)
    
    blogs = query.offset(offset).limit(limit).all()
    
    results = []
    for blog in blogs:
        keyword_text = None
        if blog.keyword_record:
            keyword_text = blog.keyword_record.keyword
        
        results.append(BlogResponse(
            id=blog.id,
            title=blog.title,
            keyword=keyword_text,
            word_count=blog.word_count,
            status=blog.status,
            live_url=blog.live_url,
            published=blog.published,
            created_at=blog.created_at,
            published_at=blog.published_at
        ))
    
    return results

@router.get("/{blog_id}", response_model=BlogContent)
async def get_blog_content(
    blog_id: int,
    db: Session = Depends(get_db)
):
    """Get full blog content"""
    
    # Get demo user for testing
    current_user = await get_demo_current_user(db)
    
    blog = db.query(GeneratedBlog).filter(
        GeneratedBlog.id == blog_id,
        GeneratedBlog.tenant_id == current_user.tenant_id
    ).first()
    
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found"
        )
    
    return BlogContent(
        id=blog.id,
        title=blog.title,
        content_html=blog.content_html,
        meta_description=blog.meta_description,
        word_count=blog.word_count,
        live_url=blog.live_url
    )

@router.post("/{blog_id}/publish")
async def publish_blog(
    blog_id: int,
    db: Session = Depends(get_db)
):
    """Manually publish a blog"""
    
    # Get demo user for testing
    current_user = await get_demo_current_user(db)
    
    blog = db.query(GeneratedBlog).filter(
        GeneratedBlog.id == blog_id,
        GeneratedBlog.tenant_id == current_user.tenant_id
    ).first()
    
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found"
        )
    
    # Check if it's really published (not just demo published)
    if blog.published and blog.shopify_article_id and not blog.shopify_article_id.startswith('demo_'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Blog already published to Shopify"
        )
    
    # Get store info
    store = db.query(ShopifyStore).filter(ShopifyStore.id == blog.store_id).first()
    if not store:
        # If no store found, use first available store
        store = db.query(ShopifyStore).first()
        if not store:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No Shopify store configured"
            )
    
    # Publish to Shopify (using demo mode)
    publisher = ShopifyPublisher({
        "shop_url": store.shop_url,
        "access_token": store.access_token,
        "blog_handle": store.blog_handle
    })
    
    # Generate SEO-friendly handle from keyword
    keyword = db.query(Keyword).filter(Keyword.id == blog.keyword_id).first()
    if keyword:
        # Create handle from keyword: "cbd for headaches" -> "cbd-for-headaches-guide"
        keyword_handle = keyword.keyword.lower().replace(' ', '-').replace("'", "").replace('"', '')
        # Remove special characters and limit length
        import re
        keyword_handle = re.sub(r'[^a-z0-9\-]', '', keyword_handle)
        keyword_handle = keyword_handle[:40]  # Shopify handle limit
        handle = f"{keyword_handle}-guide"
    else:
        handle = f"blog-{blog.id}-{int(time.time())}"
    result = publisher.publish_blog(blog.title, blog.content_html, handle)
    
    if result["success"]:
        blog.published = True
        blog.status = "published"
        blog.shopify_article_id = result["article_id"]
        blog.shopify_handle = handle
        blog.live_url = result["live_url"]
        blog.published_at = datetime.utcnow()
        db.commit()
        
        return {
            "message": f"Blog published successfully{' (Demo Mode)' if result.get('demo_mode') else '!'}", 
            "live_url": blog.live_url,
            "demo_mode": result.get("demo_mode", False),
            "note": "This is a demo URL. To publish to your real Shopify store, add valid API credentials in Settings → Shopify Stores." if result.get('demo_mode') else None
        }
    else:
        blog.status = "failed"
        blog.error_message = result["error"]
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Publishing failed: {result['error']}"
        )

@router.get("/stats/overview")
async def get_blog_stats(
    db: Session = Depends(get_db)
):
    """Get blog generation statistics"""
    
    # Get demo user for testing
    current_user = await get_demo_current_user(db)
    
    total = db.query(GeneratedBlog).filter(
        GeneratedBlog.tenant_id == current_user.tenant_id
    ).count()
    
    published = db.query(GeneratedBlog).filter(
        GeneratedBlog.tenant_id == current_user.tenant_id,
        GeneratedBlog.published == True
    ).count()
    
    draft = db.query(GeneratedBlog).filter(
        GeneratedBlog.tenant_id == current_user.tenant_id,
        GeneratedBlog.status == "draft"
    ).count()
    
    failed = db.query(GeneratedBlog).filter(
        GeneratedBlog.tenant_id == current_user.tenant_id,
        GeneratedBlog.status == "failed"
    ).count()
    
    # Get tenant usage
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    
    return {
        "total_blogs": total,
        "published_blogs": published,
        "draft_blogs": draft,
        "failed_blogs": failed,
        "monthly_usage": {
            "blogs_used": tenant.monthly_blogs_used,
            "blogs_limit": tenant.monthly_blog_limit,
            "usage_percentage": round((tenant.monthly_blogs_used / tenant.monthly_blog_limit * 100), 2) if tenant.monthly_blog_limit > 0 else 0
        },
        "success_rate": round((published / total * 100), 2) if total > 0 else 0
    }