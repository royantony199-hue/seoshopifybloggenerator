#!/usr/bin/env python3
"""
Demo authentication for testing without JWT tokens
"""

import os
import logging
from sqlalchemy.orm import Session
from app.core.database import get_db, User, Tenant, Keyword, KeywordCampaign
from app.core.config import settings

logger = logging.getLogger(__name__)

# Seed keywords for Blue Lotus SEO - embedded for deployment (177 keywords)
SEED_KEYWORDS = [
    {"keyword": "blue lotus", "search_volume": 18000, "category": "Blue Lotus", "keyword_difficulty": 35.0},
    {"keyword": "blue lotus flower", "search_volume": 12000, "category": "Blue Lotus", "keyword_difficulty": 32.0},
    {"keyword": "blue lotus gummies", "search_volume": 8500, "category": "Blue Lotus Products", "keyword_difficulty": 28.0},
    {"keyword": "blue lotus extract", "search_volume": 6200, "category": "Blue Lotus Products", "keyword_difficulty": 30.0},
    {"keyword": "blue lotus tea", "search_volume": 5500, "category": "Blue Lotus Products", "keyword_difficulty": 25.0},
    {"keyword": "blue lotus effects", "search_volume": 4800, "category": "Blue Lotus", "keyword_difficulty": 33.0},
    {"keyword": "blue lotus benefits", "search_volume": 4200, "category": "Blue Lotus", "keyword_difficulty": 30.0},
    {"keyword": "what is blue lotus", "search_volume": 3800, "category": "Blue Lotus", "keyword_difficulty": 22.0},
    {"keyword": "blue lotus supplement", "search_volume": 3500, "category": "Blue Lotus Products", "keyword_difficulty": 35.0},
    {"keyword": "blue lotus tincture", "search_volume": 3200, "category": "Blue Lotus Products", "keyword_difficulty": 28.0},
    {"keyword": "blue lotus for sleep", "search_volume": 3000, "category": "Sleep", "keyword_difficulty": 35.0},
    {"keyword": "blue lotus vape", "search_volume": 2800, "category": "Blue Lotus Products", "keyword_difficulty": 40.0},
    {"keyword": "blue lotus smoking", "search_volume": 2500, "category": "Blue Lotus Products", "keyword_difficulty": 38.0},
    {"keyword": "buy blue lotus", "search_volume": 2400, "category": "Blue Lotus Products", "keyword_difficulty": 32.0},
    {"keyword": "blue lotus near me", "search_volume": 2200, "category": "Blue Lotus Products", "keyword_difficulty": 25.0},
    {"keyword": "blue lotus dosage", "search_volume": 2000, "category": "Blue Lotus", "keyword_difficulty": 28.0},
    {"keyword": "is blue lotus safe", "search_volume": 1900, "category": "Blue Lotus", "keyword_difficulty": 30.0},
    {"keyword": "blue lotus relaxation", "search_volume": 1700, "category": "Blue Lotus", "keyword_difficulty": 25.0},
    {"keyword": "blue lotus anxiety", "search_volume": 1600, "category": "Blue Lotus", "keyword_difficulty": 33.0},
    {"keyword": "blue lotus sleep aid", "search_volume": 1500, "category": "Sleep", "keyword_difficulty": 30.0},
    {"keyword": "blue lotus capsules", "search_volume": 1400, "category": "Blue Lotus Products", "keyword_difficulty": 28.0},
    {"keyword": "blue lotus powder", "search_volume": 1300, "category": "Blue Lotus Products", "keyword_difficulty": 26.0},
    {"keyword": "blue lotus oil", "search_volume": 1200, "category": "Blue Lotus Products", "keyword_difficulty": 28.0},
    {"keyword": "organic blue lotus", "search_volume": 1100, "category": "Blue Lotus Products", "keyword_difficulty": 24.0},
    {"keyword": "blue lotus flower tea", "search_volume": 1000, "category": "Blue Lotus Products", "keyword_difficulty": 22.0},
    {"keyword": "best blue lotus gummies", "search_volume": 950, "category": "Blue Lotus Products", "keyword_difficulty": 35.0},
    {"keyword": "blue lotus edibles", "search_volume": 900, "category": "Blue Lotus Products", "keyword_difficulty": 32.0},
    {"keyword": "blue lotus stress relief", "search_volume": 850, "category": "Blue Lotus", "keyword_difficulty": 28.0},
    {"keyword": "blue lotus meditation", "search_volume": 800, "category": "Blue Lotus", "keyword_difficulty": 24.0},
    {"keyword": "blue lotus lucid dreaming", "search_volume": 750, "category": "Blue Lotus", "keyword_difficulty": 36.0},
    {"keyword": "blue lotus dream enhancement", "search_volume": 700, "category": "Blue Lotus", "keyword_difficulty": 34.0},
    {"keyword": "blue lotus spiritual", "search_volume": 680, "category": "Blue Lotus", "keyword_difficulty": 28.0},
    {"keyword": "blue lotus ancient egypt", "search_volume": 650, "category": "Blue Lotus", "keyword_difficulty": 20.0},
    {"keyword": "blue lotus history", "search_volume": 600, "category": "Blue Lotus", "keyword_difficulty": 18.0},
    {"keyword": "blue lotus vs cbd", "search_volume": 580, "category": "Blue Lotus", "keyword_difficulty": 35.0},
    {"keyword": "blue lotus and cbd", "search_volume": 550, "category": "Blue Lotus Products", "keyword_difficulty": 30.0},
    {"keyword": "blue lotus calming", "search_volume": 520, "category": "Blue Lotus", "keyword_difficulty": 25.0},
    {"keyword": "blue lotus mood", "search_volume": 500, "category": "Blue Lotus", "keyword_difficulty": 28.0},
    {"keyword": "blue lotus wellness", "search_volume": 480, "category": "Blue Lotus", "keyword_difficulty": 22.0},
    {"keyword": "blue lotus natural remedy", "search_volume": 460, "category": "Blue Lotus", "keyword_difficulty": 26.0},
    {"keyword": "blue lotus herbal", "search_volume": 450, "category": "Blue Lotus", "keyword_difficulty": 24.0},
    {"keyword": "blue lotus relaxant", "search_volume": 440, "category": "Blue Lotus", "keyword_difficulty": 26.0},
    {"keyword": "blue lotus flower benefits", "search_volume": 430, "category": "Blue Lotus", "keyword_difficulty": 28.0},
    {"keyword": "blue lotus for anxiety relief", "search_volume": 420, "category": "Blue Lotus", "keyword_difficulty": 32.0},
    {"keyword": "blue lotus sleep support", "search_volume": 410, "category": "Blue Lotus", "keyword_difficulty": 30.0},
    {"keyword": "how to use blue lotus", "search_volume": 400, "category": "Blue Lotus", "keyword_difficulty": 22.0},
    {"keyword": "blue lotus side effects", "search_volume": 390, "category": "Blue Lotus", "keyword_difficulty": 35.0},
    {"keyword": "blue lotus legal", "search_volume": 380, "category": "Blue Lotus", "keyword_difficulty": 28.0},
    {"keyword": "where to buy blue lotus", "search_volume": 370, "category": "Blue Lotus Products", "keyword_difficulty": 26.0},
    {"keyword": "blue lotus online", "search_volume": 360, "category": "Blue Lotus Products", "keyword_difficulty": 24.0},
    {"keyword": "blue lotus shop", "search_volume": 350, "category": "Blue Lotus Products", "keyword_difficulty": 22.0},
    {"keyword": "blue lotus store", "search_volume": 340, "category": "Blue Lotus Products", "keyword_difficulty": 22.0},
    {"keyword": "premium blue lotus", "search_volume": 330, "category": "Blue Lotus Products", "keyword_difficulty": 28.0},
    {"keyword": "blue lotus quality", "search_volume": 320, "category": "Blue Lotus Products", "keyword_difficulty": 25.0},
    {"keyword": "pure blue lotus", "search_volume": 310, "category": "Blue Lotus Products", "keyword_difficulty": 26.0},
    {"keyword": "natural blue lotus", "search_volume": 300, "category": "Blue Lotus Products", "keyword_difficulty": 24.0},
    {"keyword": "blue lotus flower extract", "search_volume": 290, "category": "Blue Lotus Products", "keyword_difficulty": 28.0},
    {"keyword": "blue lotus supplement benefits", "search_volume": 280, "category": "Blue Lotus Products", "keyword_difficulty": 30.0},
    {"keyword": "blue lotus gummies for sleep", "search_volume": 270, "category": "Sleep", "keyword_difficulty": 32.0},
    {"keyword": "blue lotus gummies effects", "search_volume": 260, "category": "Blue Lotus Products", "keyword_difficulty": 30.0},
    {"keyword": "best blue lotus supplement", "search_volume": 250, "category": "Blue Lotus Products", "keyword_difficulty": 35.0},
    {"keyword": "blue lotus wellness products", "search_volume": 240, "category": "Blue Lotus Products", "keyword_difficulty": 26.0},
    {"keyword": "blue lotus health benefits", "search_volume": 230, "category": "Blue Lotus", "keyword_difficulty": 28.0},
    {"keyword": "blue lotus therapeutic", "search_volume": 220, "category": "Blue Lotus", "keyword_difficulty": 30.0},
    {"keyword": "blue lotus traditional use", "search_volume": 210, "category": "Blue Lotus", "keyword_difficulty": 22.0},
    {"keyword": "blue lotus ceremonial", "search_volume": 200, "category": "Blue Lotus", "keyword_difficulty": 26.0},
    {"keyword": "blue lotus ritual", "search_volume": 190, "category": "Blue Lotus", "keyword_difficulty": 28.0},
    {"keyword": "blue lotus sacred", "search_volume": 180, "category": "Blue Lotus", "keyword_difficulty": 24.0},
    {"keyword": "blue lotus flower meaning", "search_volume": 170, "category": "Blue Lotus", "keyword_difficulty": 18.0},
    {"keyword": "blue lotus symbolism", "search_volume": 160, "category": "Blue Lotus", "keyword_difficulty": 16.0},
    {"keyword": "blue lotus nymphaea caerulea", "search_volume": 150, "category": "Blue Lotus", "keyword_difficulty": 20.0},
    {"keyword": "egyptian blue lotus", "search_volume": 140, "category": "Blue Lotus", "keyword_difficulty": 22.0},
    {"keyword": "blue lotus aphrodisiac", "search_volume": 130, "category": "Blue Lotus", "keyword_difficulty": 35.0},
    {"keyword": "blue lotus euphoria", "search_volume": 120, "category": "Blue Lotus", "keyword_difficulty": 38.0},
    {"keyword": "blue lotus experience", "search_volume": 110, "category": "Blue Lotus", "keyword_difficulty": 30.0},
    {"keyword": "blue lotus review", "search_volume": 100, "category": "Blue Lotus Products", "keyword_difficulty": 28.0},
    {"keyword": "blue lotus testimonials", "search_volume": 95, "category": "Blue Lotus Products", "keyword_difficulty": 25.0},
    {"keyword": "CBD gummies", "search_volume": 201000, "category": "CBD Products", "keyword_difficulty": 65.0},
    {"keyword": "CBD oil", "search_volume": 165000, "category": "CBD Products", "keyword_difficulty": 68.0},
    {"keyword": "CBD tincture", "search_volume": 22000, "category": "CBD Products", "keyword_difficulty": 45.0},
    {"keyword": "CBD capsules", "search_volume": 18000, "category": "CBD Products", "keyword_difficulty": 42.0},
    {"keyword": "CBD vape", "search_volume": 33000, "category": "CBD Products", "keyword_difficulty": 55.0},
    {"keyword": "CBD cream", "search_volume": 14800, "category": "CBD Products", "keyword_difficulty": 40.0},
    {"keyword": "CBD lotion", "search_volume": 9500, "category": "CBD Products", "keyword_difficulty": 38.0},
    {"keyword": "CBD balm", "search_volume": 7200, "category": "CBD Products", "keyword_difficulty": 35.0},
    {"keyword": "CBD isolate", "search_volume": 12000, "category": "CBD Products", "keyword_difficulty": 48.0},
    {"keyword": "full spectrum CBD", "search_volume": 27000, "category": "CBD Products", "keyword_difficulty": 52.0},
    {"keyword": "broad spectrum CBD", "search_volume": 14500, "category": "CBD Products", "keyword_difficulty": 48.0},
    {"keyword": "CBD for pain", "search_volume": 18100, "category": "CBD Products", "keyword_difficulty": 58.0},
    {"keyword": "CBD for anxiety", "search_volume": 22000, "category": "CBD Products", "keyword_difficulty": 55.0},
    {"keyword": "CBD for sleep", "search_volume": 14800, "category": "CBD Products", "keyword_difficulty": 52.0},
    {"keyword": "CBD for pets", "search_volume": 11000, "category": "CBD Products", "keyword_difficulty": 45.0},
    {"keyword": "hemp gummies", "search_volume": 33000, "category": "Hemp Products", "keyword_difficulty": 50.0},
    {"keyword": "delta 8 gummies", "search_volume": 74000, "category": "Delta Products", "keyword_difficulty": 62.0},
    {"keyword": "delta 9 gummies", "search_volume": 49500, "category": "Delta Products", "keyword_difficulty": 58.0},
    {"keyword": "delta 10 gummies", "search_volume": 18000, "category": "Delta Products", "keyword_difficulty": 52.0},
    {"keyword": "THC gummies", "search_volume": 90500, "category": "THC Products", "keyword_difficulty": 70.0},
    {"keyword": "CBD edibles", "search_volume": 12000, "category": "CBD Products", "keyword_difficulty": 48.0},
    {"keyword": "CBD chocolate", "search_volume": 5400, "category": "CBD Products", "keyword_difficulty": 35.0},
    {"keyword": "CBD coffee", "search_volume": 4400, "category": "CBD Products", "keyword_difficulty": 32.0},
    {"keyword": "CBD bath bombs", "search_volume": 6600, "category": "CBD Products", "keyword_difficulty": 38.0},
    {"keyword": "CBD topicals", "search_volume": 8100, "category": "CBD Products", "keyword_difficulty": 42.0},
    {"keyword": "ashwagandha", "search_volume": 301000, "category": "Medicinal Herbs", "keyword_difficulty": 72.0},
    {"keyword": "turmeric supplements", "search_volume": 40500, "category": "Medicinal Herbs", "keyword_difficulty": 55.0},
    {"keyword": "ginger root", "search_volume": 49500, "category": "Medicinal Herbs", "keyword_difficulty": 48.0},
    {"keyword": "echinacea", "search_volume": 74000, "category": "Medicinal Herbs", "keyword_difficulty": 52.0},
    {"keyword": "ginseng", "search_volume": 110000, "category": "Medicinal Herbs", "keyword_difficulty": 58.0},
    {"keyword": "milk thistle", "search_volume": 60500, "category": "Medicinal Herbs", "keyword_difficulty": 50.0},
    {"keyword": "St Johns Wort", "search_volume": 49500, "category": "Medicinal Herbs", "keyword_difficulty": 48.0},
    {"keyword": "valerian root", "search_volume": 40500, "category": "Medicinal Herbs", "keyword_difficulty": 45.0},
    {"keyword": "chamomile", "search_volume": 135000, "category": "Medicinal Herbs", "keyword_difficulty": 52.0},
    {"keyword": "lavender", "search_volume": 201000, "category": "Medicinal Herbs", "keyword_difficulty": 55.0},
    {"keyword": "peppermint oil", "search_volume": 40500, "category": "Medicinal Herbs", "keyword_difficulty": 45.0},
    {"keyword": "tea tree oil", "search_volume": 74000, "category": "Medicinal Herbs", "keyword_difficulty": 50.0},
    {"keyword": "frankincense", "search_volume": 49500, "category": "Medicinal Herbs", "keyword_difficulty": 42.0},
    {"keyword": "myrrh", "search_volume": 33000, "category": "Medicinal Herbs", "keyword_difficulty": 38.0},
    {"keyword": "elderberry", "search_volume": 90500, "category": "Medicinal Herbs", "keyword_difficulty": 55.0},
    {"keyword": "rhodiola", "search_volume": 27000, "category": "Medicinal Herbs", "keyword_difficulty": 45.0},
    {"keyword": "maca root", "search_volume": 40500, "category": "Medicinal Herbs", "keyword_difficulty": 48.0},
    {"keyword": "spirulina", "search_volume": 74000, "category": "Medicinal Herbs", "keyword_difficulty": 52.0},
    {"keyword": "chlorella", "search_volume": 33000, "category": "Medicinal Herbs", "keyword_difficulty": 45.0},
    {"keyword": "moringa", "search_volume": 49500, "category": "Medicinal Herbs", "keyword_difficulty": 48.0},
    {"keyword": "reishi mushroom", "search_volume": 33000, "category": "Mushroom Supplements", "keyword_difficulty": 50.0},
    {"keyword": "lions mane mushroom", "search_volume": 49500, "category": "Mushroom Supplements", "keyword_difficulty": 52.0},
    {"keyword": "cordyceps", "search_volume": 40500, "category": "Mushroom Supplements", "keyword_difficulty": 48.0},
    {"keyword": "chaga mushroom", "search_volume": 27000, "category": "Mushroom Supplements", "keyword_difficulty": 45.0},
    {"keyword": "turkey tail mushroom", "search_volume": 22000, "category": "Mushroom Supplements", "keyword_difficulty": 42.0},
    {"keyword": "melatonin gummies", "search_volume": 74000, "category": "Vitamin Gummies", "keyword_difficulty": 58.0},
    {"keyword": "vitamin D gummies", "search_volume": 33000, "category": "Vitamin Gummies", "keyword_difficulty": 52.0},
    {"keyword": "vitamin C gummies", "search_volume": 27000, "category": "Vitamin Gummies", "keyword_difficulty": 50.0},
    {"keyword": "multivitamin gummies", "search_volume": 40500, "category": "Vitamin Gummies", "keyword_difficulty": 55.0},
    {"keyword": "probiotic gummies", "search_volume": 22000, "category": "Vitamin Gummies", "keyword_difficulty": 48.0},
    {"keyword": "collagen gummies", "search_volume": 27000, "category": "Vitamin Gummies", "keyword_difficulty": 50.0},
    {"keyword": "biotin gummies", "search_volume": 33000, "category": "Vitamin Gummies", "keyword_difficulty": 52.0},
    {"keyword": "iron gummies", "search_volume": 14800, "category": "Vitamin Gummies", "keyword_difficulty": 42.0},
    {"keyword": "zinc gummies", "search_volume": 18000, "category": "Vitamin Gummies", "keyword_difficulty": 45.0},
    {"keyword": "elderberry gummies", "search_volume": 40500, "category": "Vitamin Gummies", "keyword_difficulty": 52.0},
    {"keyword": "turmeric gummies", "search_volume": 22000, "category": "Vitamin Gummies", "keyword_difficulty": 48.0},
    {"keyword": "ashwagandha gummies", "search_volume": 49500, "category": "Vitamin Gummies", "keyword_difficulty": 55.0},
    {"keyword": "sleep gummies", "search_volume": 60500, "category": "Wellness Gummies", "keyword_difficulty": 58.0},
    {"keyword": "energy gummies", "search_volume": 18000, "category": "Wellness Gummies", "keyword_difficulty": 45.0},
    {"keyword": "immune support gummies", "search_volume": 14800, "category": "Wellness Gummies", "keyword_difficulty": 48.0},
    {"keyword": "hair growth gummies", "search_volume": 27000, "category": "Wellness Gummies", "keyword_difficulty": 52.0},
    {"keyword": "skin health gummies", "search_volume": 9500, "category": "Wellness Gummies", "keyword_difficulty": 42.0},
    {"keyword": "joint support gummies", "search_volume": 12000, "category": "Wellness Gummies", "keyword_difficulty": 45.0},
    {"keyword": "stress relief gummies", "search_volume": 22000, "category": "Wellness Gummies", "keyword_difficulty": 50.0},
    {"keyword": "focus gummies", "search_volume": 14800, "category": "Wellness Gummies", "keyword_difficulty": 48.0},
    {"keyword": "herbal supplements", "search_volume": 33000, "category": "General Wellness", "keyword_difficulty": 55.0},
    {"keyword": "natural remedies", "search_volume": 49500, "category": "General Wellness", "keyword_difficulty": 52.0},
    {"keyword": "plant based medicine", "search_volume": 12000, "category": "General Wellness", "keyword_difficulty": 45.0},
    {"keyword": "holistic health products", "search_volume": 8100, "category": "General Wellness", "keyword_difficulty": 42.0},
    {"keyword": "organic supplements", "search_volume": 22000, "category": "General Wellness", "keyword_difficulty": 48.0},
    {"keyword": "vegan gummies", "search_volume": 14800, "category": "General Wellness", "keyword_difficulty": 45.0},
    {"keyword": "non GMO supplements", "search_volume": 6600, "category": "General Wellness", "keyword_difficulty": 38.0},
    {"keyword": "keto gummies", "search_volume": 40500, "category": "General Wellness", "keyword_difficulty": 55.0},
    {"keyword": "sugar free gummies", "search_volume": 22000, "category": "General Wellness", "keyword_difficulty": 48.0},
    {"keyword": "organic CBD", "search_volume": 18000, "category": "CBD Products", "keyword_difficulty": 50.0},
    {"keyword": "lab tested CBD", "search_volume": 5400, "category": "CBD Products", "keyword_difficulty": 35.0},
    {"keyword": "third party tested CBD", "search_volume": 4400, "category": "CBD Products", "keyword_difficulty": 32.0},
    {"keyword": "CBD isolate products", "search_volume": 6600, "category": "CBD Products", "keyword_difficulty": 40.0},
    {"keyword": "hemp extract", "search_volume": 14800, "category": "Hemp Products", "keyword_difficulty": 45.0},
    {"keyword": "cannabis products", "search_volume": 33000, "category": "Cannabis", "keyword_difficulty": 62.0},
    {"keyword": "medical marijuana", "search_volume": 60500, "category": "Cannabis", "keyword_difficulty": 68.0},
    {"keyword": "cannabis edibles", "search_volume": 27000, "category": "Cannabis", "keyword_difficulty": 58.0},
    {"keyword": "THC products", "search_volume": 22000, "category": "THC Products", "keyword_difficulty": 62.0},
    {"keyword": "cannabinoids", "search_volume": 18000, "category": "Cannabis", "keyword_difficulty": 52.0},
    {"keyword": "terpenes", "search_volume": 27000, "category": "Cannabis", "keyword_difficulty": 48.0},
    {"keyword": "adaptogens", "search_volume": 33000, "category": "General Wellness", "keyword_difficulty": 50.0},
    {"keyword": "nootropics", "search_volume": 49500, "category": "General Wellness", "keyword_difficulty": 55.0},
    {"keyword": "superfoods", "search_volume": 74000, "category": "General Wellness", "keyword_difficulty": 52.0},
    {"keyword": "herbal teas", "search_volume": 40500, "category": "General Wellness", "keyword_difficulty": 48.0},
    {"keyword": "tinctures", "search_volume": 22000, "category": "General Wellness", "keyword_difficulty": 45.0},
    {"keyword": "extracts", "search_volume": 18000, "category": "General Wellness", "keyword_difficulty": 42.0},
    {"keyword": "essential oils", "search_volume": 165000, "category": "General Wellness", "keyword_difficulty": 58.0},
    {"keyword": "aromatherapy products", "search_volume": 14800, "category": "General Wellness", "keyword_difficulty": 45.0},
    {"keyword": "natural pain relief", "search_volume": 27000, "category": "General Wellness", "keyword_difficulty": 52.0},
    {"keyword": "alternative medicine", "search_volume": 40500, "category": "General Wellness", "keyword_difficulty": 55.0},
    {"keyword": "natural sleep aid", "search_volume": 18000, "category": "Sleep", "keyword_difficulty": 45.0},
]


def seed_keywords_for_tenant(db: Session, tenant_id: int):
    """Seed keywords for a tenant if none exist"""
    existing_count = db.query(Keyword).filter(Keyword.tenant_id == tenant_id).count()

    if existing_count > 0:
        logger.info(f"Tenant {tenant_id} already has {existing_count} keywords, skipping seed")
        return 0

    # Create default campaign
    campaign = KeywordCampaign(
        tenant_id=tenant_id,
        name="Blue Lotus SEO Keywords",
        description="Pre-loaded keywords for Blue Lotus and wellness products",
        template_type="cbd_wellness"
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)

    # Add seed keywords
    keywords_added = 0
    for kw_data in SEED_KEYWORDS:
        keyword = Keyword(
            tenant_id=tenant_id,
            campaign_id=campaign.id,
            keyword=kw_data["keyword"].lower().strip(),
            search_volume=kw_data.get("search_volume"),
            keyword_difficulty=kw_data.get("keyword_difficulty"),
            category=kw_data.get("category", "General"),
            status="pending"
        )
        db.add(keyword)
        keywords_added += 1

    db.commit()
    logger.info(f"Seeded {keywords_added} keywords for tenant {tenant_id}")
    return keywords_added


def get_demo_user(db: Session):
    """Get or create demo user for testing"""
    user = db.query(User).filter(User.email == "demo@example.com").first()
    if not user:
        # First check if tenant already exists
        tenant = db.query(Tenant).filter(Tenant.slug == "demo-company").first()

        if not tenant:
            # Create demo tenant only if it doesn't exist
            tenant = Tenant(
                name='Demo Company',
                slug='demo-company',
                subscription_plan='professional',
                subscription_status='trial',
                monthly_blog_limit=500,
                monthly_blogs_used=0
            )
            db.add(tenant)
            db.commit()
            db.refresh(tenant)

        # Create demo user with OpenAI API key from environment
        from app.routers.auth import get_password_hash
        openai_key = os.environ.get('OPENAI_API_KEY') or getattr(settings, 'OPENAI_API_KEY', None)

        user = User(
            tenant_id=tenant.id,
            email='demo@example.com',
            hashed_password=get_password_hash('demo123'),
            first_name='Demo',
            last_name='User',
            role='admin',
            openai_api_key=openai_key  # Set OpenAI key from environment
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Seed keywords for the new tenant
        seed_keywords_for_tenant(db, tenant.id)
    else:
        # Update existing user's OpenAI key if not set but available in environment
        if not user.openai_api_key:
            openai_key = os.environ.get('OPENAI_API_KEY') or getattr(settings, 'OPENAI_API_KEY', None)
            if openai_key:
                user.openai_api_key = openai_key
                db.commit()
                db.refresh(user)

        # Ensure keywords exist for the tenant
        seed_keywords_for_tenant(db, user.tenant_id)

    return user

async def get_demo_current_user(db: Session):
    """Demo version that always returns the demo user"""
    return get_demo_user(db)