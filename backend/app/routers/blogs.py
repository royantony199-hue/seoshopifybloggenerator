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
import base64
import io
from PIL import Image

from app.core.database import get_db, GeneratedBlog, Keyword, ShopifyStore, KeywordCampaign, Tenant, Product
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
    featured_image_url: Optional[str]
    image_generated: bool

class BlogContent(BaseModel):
    id: int
    title: str
    content_html: str
    meta_description: Optional[str]
    word_count: int
    live_url: Optional[str]
    featured_image_url: Optional[str]
    image_generated: bool

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
        
        # Use new products system if available, fallback to old system
        if store_info.get("products") and len(store_info["products"]) > 0:
            products = store_info["products"]
            product_links = []
            for product in products:
                link_text = product.get("integration_text", f"For premium {product['name'].lower()}")
                if product.get("price"):
                    link_text += f" (Starting at {product['price']})"
                # Create proper HTML link
                html_link = f'<a href="{product["url"]}" target="_blank" rel="noopener">{link_text}</a>'
                product_links.append(html_link)
            
            product_integration = f"""
            - MUST naturally integrate these specific product recommendations as CLICKABLE LINKS throughout the content:
              {chr(10).join([f"  * {link}" for link in product_links])}
            - Place product recommendations contextually within relevant sections
            - Use varied language like "Check out our", "Consider our", "For best results try our", "Recommended", etc.
            - IMPORTANT: Include the full HTML <a> tags exactly as shown above for clickable links
            """
        elif store_info.get("default_product_url"):
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
    
    def generate_featured_image(self, keyword: str, store_info: dict) -> dict:
        """Generate a featured image using OpenAI DALL-E"""
        try:
            # Create a professional, SEO-optimized image prompt
            image_prompt = self._build_image_prompt(keyword, store_info)
            
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=image_prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )
            
            image_url = response.data[0].url
            
            # Download the image
            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                return {
                    "success": True,
                    "image_data": image_response.content,
                    "image_url": image_url,
                    "prompt_used": image_prompt
                }
            else:
                return {"success": False, "error": "Failed to download generated image"}
                
        except Exception as e:
            # Return a fallback - no image generated
            return {"success": False, "error": f"Image generation failed: {str(e)}"}
    
    def _build_image_prompt(self, keyword: str, store_info: dict) -> str:
        """Build image generation prompt based on keyword"""
        
        keyword_lower = keyword.lower()
        
        # Base professional style
        base_style = "Professional, clean, modern design with soft lighting and calming colors"
        
        # Customize based on keyword category
        if any(term in keyword_lower for term in ['sleep', 'insomnia', 'bedtime', 'rest']):
            scene = "peaceful bedroom scene with soft pillows, warm lighting, and serene atmosphere"
        elif any(term in keyword_lower for term in ['cbd', 'hemp', 'cannabis']):
            scene = "natural hemp leaves and CBD oil bottles on white background with green accents"
        elif any(term in keyword_lower for term in ['anxiety', 'stress', 'calm', 'relax']):
            scene = "zen-like meditation space with plants, soft textures, and peaceful ambiance"
        elif any(term in keyword_lower for term in ['pain', 'headache', 'inflammation']):
            scene = "wellness concept with natural remedies, herbs, and healing elements"
        else:
            scene = "health and wellness theme with natural elements, soft colors, and modern design"
        
        prompt = f"""Create a {base_style} image featuring {scene}. 
        The image should be suitable for a health and wellness blog post about '{keyword}'.
        Style: Professional photography, high quality, suitable for web publication.
        Colors: Soft, calming palette with blues, greens, and warm neutrals.
        No text or logos in the image. Clean, minimalist composition."""
        
        return prompt

class ShopifyPublisher:
    """Shopify blog publishing engine"""
    
    def __init__(self, store_info: dict):
        self.store_info = store_info
        self.api_base = f"https://{store_info['shop_url']}.myshopify.com/admin/api/2025-07"
        self.headers = {
            'X-Shopify-Access-Token': store_info['access_token'],
            'Content-Type': 'application/json'
        }
    
    def publish_blog(self, title: str, content: str, handle: str, keyword: str = None, image_data: bytes = None, image_url: str = None) -> dict:
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
            
            # Generate dynamic SEO tags based on keyword
            seo_tags = self._generate_seo_tags(keyword)
            
            # Embed featured image directly in content if available
            if image_url:
                print(f"DEBUG: Embedding image URL: {image_url}")
                # Create featured image HTML tag
                featured_image_html = f'''<div style="text-align: center; margin: 20px 0;">
    <img src="{image_url}" alt="Featured image for {title}" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);" />
</div>'''
                
                # Insert the image after the first paragraph
                if '<p>' in content:
                    # Find the end of the first paragraph and insert image
                    first_p_end = content.find('</p>') + 4
                    content = content[:first_p_end] + featured_image_html + content[first_p_end:]
                    print(f"DEBUG: Image inserted after first paragraph at position {first_p_end}")
                else:
                    # Fallback: add at the beginning of body
                    body_start = content.find('<body>') + 6
                    if body_start > 5:
                        content = content[:body_start] + featured_image_html + content[body_start:]
                        print(f"DEBUG: Image inserted at body start position {body_start}")
                    else:
                        print("DEBUG: Could not find insertion point for image")
            
            # Create the article
            article_data = {
                "article": {
                    "title": title,
                    "body_html": content,
                    "handle": handle,
                    "published": True,
                    "tags": seo_tags
                }
            }
            
            try:
                response = requests.post(
                    f"{self.api_base}/blogs/{target_blog['id']}/articles.json",
                    headers=self.headers,
                    json=article_data,
                    timeout=30
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
                    error_msg = f"Shopify API error: {response.status_code} - {response.text}"
                    print(f"Shopify publish error: {error_msg}")
                    raise Exception(error_msg)
                    
            except requests.exceptions.RequestException as e:
                error_msg = f"Request failed: {str(e)}"
                print(f"Network error during publish: {error_msg}")
                raise Exception(error_msg)
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_seo_tags(self, keyword: str = None) -> str:
        """Generate relevant SEO tags based on keyword"""
        if not keyword:
            return "SEO, Blog Content, Health & Wellness"
        
        # Base tags that always apply
        base_tags = ["SEO", "Health & Wellness", "Blog Content"]
        
        # Extract relevant terms from keyword for additional tags
        keyword_lower = keyword.lower()
        additional_tags = []
        
        # Sleep-related keywords
        if any(term in keyword_lower for term in ['sleep', 'insomnia', 'bedtime', 'rest', 'dream']):
            additional_tags.extend(['Sleep Health', 'Better Sleep', 'Sleep Tips'])
        
        # CBD/Cannabis related
        if any(term in keyword_lower for term in ['cbd', 'hemp', 'cannabis', 'cannabinoid']):
            additional_tags.extend(['CBD', 'Natural Wellness', 'Hemp Products'])
        
        # Anxiety/Stress related
        if any(term in keyword_lower for term in ['anxiety', 'stress', 'calm', 'relax']):
            additional_tags.extend(['Mental Health', 'Stress Relief', 'Natural Remedies'])
        
        # Pain/Inflammation related  
        if any(term in keyword_lower for term in ['pain', 'inflammation', 'headache', 'migraine']):
            additional_tags.extend(['Pain Relief', 'Natural Healing', 'Wellness Solutions'])
        
        # Wellness/Health general
        if any(term in keyword_lower for term in ['health', 'wellness', 'natural', 'organic']):
            additional_tags.extend(['Natural Health', 'Wellness', 'Holistic Health'])
        
        # Combine base tags with additional relevant tags (limit to 8 total)
        all_tags = base_tags + additional_tags
        final_tags = list(dict.fromkeys(all_tags))[:8]  # Remove duplicates and limit
        
        return ", ".join(final_tags)
    
    def _upload_image(self, image_data: bytes, filename: str) -> dict:
        """Upload image to Shopify and return image ID"""
        try:
            # For blog articles in Shopify, we need to use a different approach
            # We'll upload the image as a file asset first
            
            # Convert image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Upload as file asset to Shopify files
            files_payload = {
                "asset": {
                    "key": f"assets/{filename}.jpg",
                    "value": image_base64
                }
            }
            
            # Get current theme ID first
            themes_response = requests.get(
                f"{self.api_base}/themes.json",
                headers=self.headers
            )
            
            if themes_response.status_code != 200:
                return {"success": False, "error": f"Failed to get themes: {themes_response.text}"}
            
            themes = themes_response.json().get('themes', [])
            current_theme = None
            for theme in themes:
                if theme.get('role') == 'main':
                    current_theme = theme
                    break
            
            if not current_theme:
                return {"success": False, "error": "No main theme found"}
            
            # Upload to theme assets
            upload_response = requests.put(
                f"{self.api_base}/themes/{current_theme['id']}/assets.json",
                headers=self.headers,
                json=files_payload
            )
            
            if upload_response.status_code == 200:
                # Create the public URL for the uploaded image
                public_url = f"https://{self.store_info['shop_url']}.myshopify.com/cdn/shop/files/{filename}.jpg"
                
                return {
                    "success": True,
                    "image_id": None,  # Shopify articles use URLs, not IDs for external images
                    "image_url": public_url
                }
            else:
                return {"success": False, "error": f"Image upload failed: {upload_response.text}"}
                
        except Exception as e:
            return {"success": False, "error": f"Image upload error: {str(e)}"}

def generate_single_blog(
    keyword_id: int,
    store_id: int,
    template_type: str,
    auto_publish: bool,
    tenant_id: int,
    openai_api_key: str
):
    """Background task to generate a single blog"""
    
    # Create new database session for this background task
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.core.config import settings
    
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Get keyword and store info
        keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()
        store = db.query(ShopifyStore).filter(ShopifyStore.id == store_id).first()
        
        if not keyword or not store:
            return
        
        # Update keyword status
        keyword.status = "processing"
        db.commit()
        
        # Find matching products for this keyword
        matching_products = db.query(Product).filter(
            Product.tenant_id == tenant_id,
            Product.store_id == store_id,
            Product.is_active == True,
            Product.keywords.ilike(f"%{keyword.keyword}%")
        ).order_by(Product.priority.desc()).limit(3).all()
        
        # If no keyword match, try partial matches
        if not matching_products:
            keyword_words = keyword.keyword.lower().split()
            for word in keyword_words:  # Try ALL words, not just first 3
                if len(word) >= 3:  # Only meaningful words
                    matching_products = db.query(Product).filter(
                        Product.tenant_id == tenant_id,
                        Product.store_id == store_id,
                        Product.is_active == True,
                        Product.keywords.ilike(f"%{word}%")
                    ).order_by(Product.priority.desc()).limit(2).all()
                    if matching_products:
                        break
        
        # Generate blog content
        generator = BlogGenerator(openai_api_key)
        
        store_info = {
            "shop_url": store.shop_url,
            "blog_handle": store.blog_handle,
            "default_product_url": store.default_product_url,
            "product_integration_text": store.product_integration_text,
            "template_type": template_type,
            "products": [
                {
                    "name": p.name,
                    "url": p.url,
                    "price": p.price,
                    "integration_text": p.integration_text or f"For premium {p.name.lower()}, visit: {p.url}"
                }
                for p in matching_products
            ]
        }
        
        result = generator.generate_blog_content(keyword.keyword, {"template_type": template_type}, store_info)
        
        # Generate featured image
        image_result = generator.generate_featured_image(keyword.keyword, store_info)
        image_data = image_result.get("image_data") if image_result.get("success") else None
        
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
            status="draft",
            # Image information
            featured_image_url=image_result.get("image_url") if image_result.get("success") else None,
            image_prompt_used=image_result.get("prompt_used") if image_result.get("success") else None,
            image_generated=image_result.get("success", False)
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
            
            # Generate SEO-friendly handle from keyword
            import re
            handle = keyword.keyword.lower().replace(" ", "-").replace("'", "").replace('"', '')
            handle = re.sub(r'[^a-z0-9\-]', '', handle)
            # Collapse multiple consecutive hyphens into a single hyphen
            handle = re.sub(r'-+', '-', handle)
            # Remove leading/trailing hyphens
            handle = handle.strip('-')
            handle = handle[:40]  # Shopify handle limit
            # Strip hyphens again after length limit (in case we cut off in the middle)
            handle = handle.rstrip('-')
            # Get image URL from the generated image result
            image_url = image_result.get("image_url") if image_result.get("success") else None
            publish_result = publisher.publish_blog(blog.title, blog.content_html, handle, keyword.keyword, image_data, image_url)
            
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
        try:
            keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()
            if keyword:
                keyword.status = "failed"
                db.commit()
        except Exception as db_error:
            print(f"Database error while updating failed status: {str(db_error)}")
        
        print(f"Blog generation failed for keyword {keyword_id}: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Always close the database session
        db.close()

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
            current_user.openai_api_key
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
            published_at=blog.published_at,
            featured_image_url=blog.featured_image_url,
            image_generated=blog.image_generated
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
        live_url=blog.live_url,
        featured_image_url=blog.featured_image_url,
        image_generated=blog.image_generated or False
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
        # Collapse multiple consecutive hyphens into a single hyphen
        keyword_handle = re.sub(r'-+', '-', keyword_handle)
        # Remove leading/trailing hyphens
        keyword_handle = keyword_handle.strip('-')
        keyword_handle = keyword_handle[:40]  # Shopify handle limit
        # Strip hyphens again after length limit (in case we cut off in the middle)
        keyword_handle = keyword_handle.rstrip('-')
        handle = f"{keyword_handle}-guide"
    else:
        handle = f"blog-{blog.id}-{int(time.time())}"
    
    # Generate featured image for manual publish
    image_data = None
    if keyword:
        try:
            # Get current user for OpenAI key
            current_user = await get_demo_current_user(db)
            if current_user.openai_api_key:
                from app.routers.blogs import BlogGenerator
                generator = BlogGenerator(current_user.openai_api_key)
                image_result = generator.generate_featured_image(keyword.keyword, {})
                image_data = image_result.get("image_data") if image_result.get("success") else None
        except Exception as e:
            print(f"Image generation failed: {e}")
    
    # Try publishing with original handle first
    keyword_text = keyword.keyword if keyword else None
    # Use existing image URL from database if available
    blog_image_url = blog.featured_image_url
    print(f"DEBUG: Publishing with image URL: {blog_image_url}")
    result = publisher.publish_blog(blog.title, blog.content_html, handle, keyword_text, image_data, blog_image_url)
    
    # If handle already exists, add unique suffix
    if not result["success"] and "handle" in result.get("error", "") and "already been taken" in result.get("error", ""):
        unique_suffix = int(time.time()) % 10000  # Last 4 digits of timestamp
        handle = f"{keyword_handle[:35]}-{unique_suffix}-guide"  # Leave room for suffix
        result = publisher.publish_blog(blog.title, blog.content_html, handle, keyword_text, image_data, blog_image_url)
    
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