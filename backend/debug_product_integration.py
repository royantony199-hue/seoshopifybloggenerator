#!/usr/bin/env python3
"""
Debug Product Integration in Blog Generation
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Product, Keyword, ShopifyStore, User
from app.core.config import settings

def test_product_matching():
    """Test the product matching logic"""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Get demo user and store
        user = db.query(User).filter(User.email == "demo@example.com").first()
        store = db.query(ShopifyStore).filter(
            ShopifyStore.tenant_id == user.tenant_id,
            ShopifyStore.is_active == True
        ).first()
        
        # Get a CBD-related keyword
        keyword = db.query(Keyword).filter(
            Keyword.tenant_id == user.tenant_id,
            Keyword.status == "pending",
            Keyword.keyword.ilike("%cbd%")
        ).first()
        
        if not keyword:
            print("❌ No CBD keywords found")
            return
        
        print("DEBUGGING PRODUCT INTEGRATION")
        print("=" * 60)
        print(f"Testing with keyword: '{keyword.keyword}'")
        print(f"Store: {store.store_name} (ID: {store.id})")
        print(f"Tenant ID: {user.tenant_id}")
        print()
        
        # Test exact keyword matching
        print("1. EXACT KEYWORD MATCHING:")
        exact_matches = db.query(Product).filter(
            Product.tenant_id == user.tenant_id,
            Product.store_id == store.id,
            Product.is_active == True,
            Product.keywords.ilike(f"%{keyword.keyword}%")
        ).order_by(Product.priority.desc()).limit(3).all()
        
        print(f"   Found {len(exact_matches)} exact matches")
        for product in exact_matches:
            print(f"   - {product.name}: '{product.keywords}'")
        print()
        
        # Test word-by-word matching (the fallback logic)
        print("2. WORD-BY-WORD MATCHING:")
        matching_products = []
        if not exact_matches:
            keyword_words = keyword.keyword.lower().split()
            print(f"   Testing words: {keyword_words}")
            
            for word in keyword_words[:3]:  # Try first 3 words
                if len(word) >= 3:  # Only meaningful words
                    print(f"   Testing word: '{word}'")
                    word_matches = db.query(Product).filter(
                        Product.tenant_id == user.tenant_id,
                        Product.store_id == store.id,
                        Product.is_active == True,
                        Product.keywords.ilike(f"%{word}%")
                    ).order_by(Product.priority.desc()).limit(2).all()
                    
                    print(f"     Found {len(word_matches)} matches")
                    for product in word_matches:
                        print(f"     - {product.name}: '{product.keywords}'")
                    
                    if word_matches:
                        matching_products = word_matches
                        break
        else:
            matching_products = exact_matches
        
        print()
        print("3. FINAL MATCHING PRODUCTS:")
        print(f"   Total products to integrate: {len(matching_products)}")
        
        if matching_products:
            print("   Products that SHOULD be integrated:")
            for product in matching_products:
                print(f"   - Name: {product.name}")
                print(f"     URL: {product.url}")
                print(f"     Keywords: {product.keywords}")
                print(f"     Integration Text: {product.integration_text}")
                print(f"     Priority: {product.priority}")
                print()
        
        # Simulate the store_info data structure
        print("4. STORE_INFO DATA STRUCTURE:")
        store_info = {
            "shop_url": store.shop_url,
            "blog_handle": store.blog_handle,
            "default_product_url": store.default_product_url,
            "product_integration_text": store.product_integration_text,
            "template_type": "ecommerce_general",
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
        
        print(f"   Products in store_info: {len(store_info['products'])}")
        for i, product in enumerate(store_info['products']):
            print(f"   Product {i+1}:")
            print(f"     Name: {product['name']}")
            print(f"     URL: {product['url']}")
            print(f"     Price: {product['price']}")
            print(f"     Integration Text: {product['integration_text']}")
        
        print()
        print("5. PROMPT GENERATION TEST:")
        
        # Test the product integration prompt generation
        if store_info.get("products") and len(store_info["products"]) > 0:
            products = store_info["products"]
            product_links = []
            for product in products:
                link_text = product.get("integration_text", f"For premium {product['name'].lower()}, visit: {product['url']}")
                if product.get("price"):
                    link_text += f" (Starting at {product['price']})"
                product_links.append(link_text)
            
            product_integration = f"""
            - MUST naturally integrate these specific product recommendations throughout the content:
              {chr(10).join([f"  * {link}" for link in product_links])}
            - Place product recommendations contextually within relevant sections
            - Use varied language like "Check out", "Consider", "For best results", "Recommended", etc.
            """
            
            print("   Product integration instructions to be added to prompt:")
            print(product_integration)
        else:
            print("   ❌ NO PRODUCT INTEGRATION INSTRUCTIONS - This is the problem!")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_product_matching()