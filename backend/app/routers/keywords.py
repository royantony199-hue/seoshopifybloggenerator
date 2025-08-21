#!/usr/bin/env python3
"""
Keywords management router - upload, process, and manage keywords
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import io
from datetime import datetime

from app.core.database import get_db, Keyword, KeywordCampaign, Tenant, GeneratedBlog
from app.routers.auth import get_current_user, User
from app.routers.demo_auth import get_demo_current_user
from app.core.config import settings, BLOG_TEMPLATES

router = APIRouter()

# Pydantic models
class KeywordCreate(BaseModel):
    keyword: str
    search_volume: Optional[int] = None
    keyword_difficulty: Optional[float] = None
    category: Optional[str] = None

class KeywordResponse(BaseModel):
    id: int
    keyword: str
    search_volume: Optional[int]
    keyword_difficulty: Optional[float]
    category: Optional[str]
    status: str
    blog_generated: bool
    created_at: datetime

class CampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    template_type: str = "ecommerce_general"
    min_words: int = 2000
    faq_count: int = 15
    auto_generate: bool = False

class CampaignResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    template_type: str
    min_words: int
    faq_count: int
    auto_generate: bool
    keyword_count: int
    created_at: datetime

class BulkUploadResponse(BaseModel):
    success: bool
    message: str
    keywords_processed: int
    keywords_added: int
    keywords_skipped: int
    campaign_id: Optional[int] = None

# Routes
@router.post("/campaigns", response_model=CampaignResponse)
async def create_campaign(
    campaign_data: CampaignCreate,
    db: Session = Depends(get_db)
):
    """Create a new keyword campaign"""
    
    # Get demo user for testing
    current_user = await get_demo_current_user(db)
    
    # Validate template type
    if campaign_data.template_type not in BLOG_TEMPLATES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid template type. Available: {list(BLOG_TEMPLATES.keys())}"
        )
    
    campaign = KeywordCampaign(
        tenant_id=current_user.tenant_id,
        name=campaign_data.name,
        description=campaign_data.description,
        template_type=campaign_data.template_type,
        min_words=campaign_data.min_words,
        faq_count=campaign_data.faq_count,
        auto_generate=campaign_data.auto_generate
    )
    
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    
    return CampaignResponse(
        id=campaign.id,
        name=campaign.name,
        description=campaign.description,
        template_type=campaign.template_type,
        min_words=campaign.min_words,
        faq_count=campaign.faq_count,
        auto_generate=campaign.auto_generate,
        keyword_count=0,
        created_at=campaign.created_at
    )

@router.get("/campaigns", response_model=List[CampaignResponse])
async def get_campaigns(
    db: Session = Depends(get_db)
):
    """Get all campaigns for current tenant"""
    
    # Get demo user for testing
    current_user = await get_demo_current_user(db)
    
    campaigns = db.query(KeywordCampaign).filter(
        KeywordCampaign.tenant_id == current_user.tenant_id
    ).all()
    
    results = []
    for campaign in campaigns:
        keyword_count = db.query(Keyword).filter(
            Keyword.campaign_id == campaign.id
        ).count()
        
        results.append(CampaignResponse(
            id=campaign.id,
            name=campaign.name,
            description=campaign.description,
            template_type=campaign.template_type,
            min_words=campaign.min_words,
            faq_count=campaign.faq_count,
            auto_generate=campaign.auto_generate,
            keyword_count=keyword_count,
            created_at=campaign.created_at
        ))
    
    return results

@router.post("/upload", response_model=BulkUploadResponse)
async def upload_keywords(
    file: UploadFile = File(...),
    campaign_id: Optional[int] = Form(None),
    campaign_name: Optional[str] = Form("Uploaded Keywords"),
    template_type: str = Form("ecommerce_general"),
    db: Session = Depends(get_db)
):
    """Upload keywords from CSV or Excel file"""
    
    # Get demo user for testing
    current_user = await get_demo_current_user(db)
    
    # Check file type
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be CSV or Excel format"
        )
    
    # Check tenant limits
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    existing_keywords = db.query(Keyword).filter(
        Keyword.tenant_id == current_user.tenant_id
    ).count()
    
    if existing_keywords >= settings.MAX_KEYWORDS_PER_UPLOAD:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {settings.MAX_KEYWORDS_PER_UPLOAD} keywords allowed per account"
        )
    
    try:
        # Read file content
        contents = await file.read()
        
        # Parse file based on type
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        else:
            df = pd.read_excel(io.BytesIO(contents))
        
        # Validate required columns
        required_columns = ['keyword']
        if not all(col in df.columns for col in required_columns):
            # Try common variations
            column_mapping = {
                'keywords': 'keyword',
                'search_term': 'keyword',
                'query': 'keyword',
                'volume': 'search_volume',
                'monthly_searches': 'search_volume',
                'difficulty': 'keyword_difficulty',
                'kd': 'keyword_difficulty',
                'category': 'category',
                'topic': 'category'
            }
            
            df = df.rename(columns=column_mapping)
            
            if 'keyword' not in df.columns:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File must contain a 'keyword' column"
                )
        
        # Create or get campaign
        # Handle campaign_id properly (it might come as None or empty)
        campaign_id_value = None
        if campaign_id is not None:
            try:
                campaign_id_value = int(campaign_id)
            except (ValueError, TypeError):
                campaign_id_value = None
        
        if campaign_id_value:
            campaign = db.query(KeywordCampaign).filter(
                KeywordCampaign.id == campaign_id_value,
                KeywordCampaign.tenant_id == current_user.tenant_id
            ).first()
            if not campaign:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Campaign not found"
                )
        else:
            # Create new campaign
            campaign = KeywordCampaign(
                tenant_id=current_user.tenant_id,
                name=campaign_name,
                template_type=template_type
            )
            db.add(campaign)
            db.commit()
            db.refresh(campaign)
        
        # Process keywords
        keywords_processed = 0
        keywords_added = 0
        keywords_skipped = 0
        
        for _, row in df.iterrows():
            keyword_text = str(row['keyword']).strip().lower()
            
            if not keyword_text or keyword_text == 'nan':
                keywords_skipped += 1
                continue
            
            keywords_processed += 1
            
            # Check if keyword already exists for this tenant
            existing = db.query(Keyword).filter(
                Keyword.tenant_id == current_user.tenant_id,
                Keyword.keyword == keyword_text
            ).first()
            
            if existing:
                keywords_skipped += 1
                continue
            
            # Extract additional data
            search_volume = None
            if 'search_volume' in row and pd.notna(row['search_volume']):
                try:
                    search_volume = int(str(row['search_volume']).replace(',', ''))
                except (ValueError, TypeError):
                    search_volume = None
            
            keyword_difficulty = None
            if 'keyword_difficulty' in row and pd.notna(row['keyword_difficulty']):
                try:
                    keyword_difficulty = float(row['keyword_difficulty'])
                except (ValueError, TypeError):
                    keyword_difficulty = None
            
            category = None
            if 'category' in row and pd.notna(row['category']):
                category = str(row['category']).strip()
            
            # Create keyword
            keyword = Keyword(
                tenant_id=current_user.tenant_id,
                campaign_id=campaign.id,
                keyword=keyword_text,
                search_volume=search_volume,
                keyword_difficulty=keyword_difficulty,
                category=category,
                status="pending"
            )
            
            db.add(keyword)
            keywords_added += 1
            
            # Check limits
            if keywords_added >= (settings.MAX_KEYWORDS_PER_UPLOAD - existing_keywords):
                break
        
        db.commit()
        
        return BulkUploadResponse(
            success=True,
            message=f"Successfully processed {keywords_processed} keywords",
            keywords_processed=keywords_processed,
            keywords_added=keywords_added,
            keywords_skipped=keywords_skipped,
            campaign_id=campaign.id
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )

@router.get("/", response_model=List[KeywordResponse])
async def get_keywords(
    campaign_id: Optional[int] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get keywords for current tenant"""
    
    # Get demo user for testing
    current_user = await get_demo_current_user(db)
    
    query = db.query(Keyword).filter(Keyword.tenant_id == current_user.tenant_id)
    
    if campaign_id:
        query = query.filter(Keyword.campaign_id == campaign_id)
    
    if status:
        query = query.filter(Keyword.status == status)
    
    keywords = query.offset(offset).limit(limit).all()
    
    return [KeywordResponse(
        id=k.id,
        keyword=k.keyword,
        search_volume=k.search_volume,
        keyword_difficulty=k.keyword_difficulty,
        category=k.category,
        status=k.status,
        blog_generated=k.blog_generated,
        created_at=k.created_at
    ) for k in keywords]

@router.get("/stats")
async def get_keyword_stats(
    db: Session = Depends(get_db)
):
    """Get keyword statistics for current tenant"""
    
    # Get demo user for testing
    current_user = await get_demo_current_user(db)
    
    total = db.query(Keyword).filter(Keyword.tenant_id == current_user.tenant_id).count()
    
    pending = db.query(Keyword).filter(
        Keyword.tenant_id == current_user.tenant_id,
        Keyword.status == "pending"
    ).count()
    
    processing = db.query(Keyword).filter(
        Keyword.tenant_id == current_user.tenant_id,
        Keyword.status == "processing"
    ).count()
    
    completed = db.query(Keyword).filter(
        Keyword.tenant_id == current_user.tenant_id,
        Keyword.status == "completed"
    ).count()
    
    blogs_generated = db.query(Keyword).filter(
        Keyword.tenant_id == current_user.tenant_id,
        Keyword.blog_generated == True
    ).count()
    
    return {
        "total_keywords": total,
        "pending": pending,
        "processing": processing,
        "completed": completed,
        "blogs_generated": blogs_generated,
        "completion_rate": round((completed / total * 100) if total > 0 else 0, 2)
    }

@router.delete("/{keyword_id}")
async def delete_keyword(
    keyword_id: int,
    db: Session = Depends(get_db)
):
    """Delete a keyword"""
    
    # Get demo user for testing
    current_user = await get_demo_current_user(db)
    
    keyword = db.query(Keyword).filter(
        Keyword.id == keyword_id,
        Keyword.tenant_id == current_user.tenant_id
    ).first()
    
    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keyword not found"
        )
    
    db.delete(keyword)
    db.commit()
    
    return {"message": "Keyword deleted successfully"}

@router.post("/{keyword_id}/reset")
async def reset_keyword(
    keyword_id: int,
    db: Session = Depends(get_db)
):
    """Reset a failed keyword back to pending status for retry"""
    
    # Get demo user for testing
    current_user = await get_demo_current_user(db)
    
    keyword = db.query(Keyword).filter(
        Keyword.id == keyword_id,
        Keyword.tenant_id == current_user.tenant_id
    ).first()
    
    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keyword not found"
        )
    
    # Reset keyword to pending status
    keyword.status = "pending"
    keyword.blog_generated = False
    keyword.processed_at = None
    
    # Also delete any failed blog attempts for this keyword
    failed_blogs = db.query(GeneratedBlog).filter(
        GeneratedBlog.keyword_id == keyword_id,
        GeneratedBlog.status == "failed"
    ).all()
    
    for blog in failed_blogs:
        db.delete(blog)
    
    db.commit()
    
    return {
        "message": "Keyword reset to pending status", 
        "keyword": keyword.keyword,
        "new_status": keyword.status
    }