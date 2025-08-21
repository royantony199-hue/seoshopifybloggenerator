#!/usr/bin/env python3
"""
Test script to debug Shopify publishing
"""

import requests
import sqlite3
from datetime import datetime

def test_shopify_publish():
    # Get store credentials from database
    conn = sqlite3.connect('seo_saas.db')
    cursor = conn.cursor()
    cursor.execute('SELECT shop_url, access_token, blog_handle FROM shopify_stores WHERE id = 1')
    store = cursor.fetchone()
    conn.close()
    
    if not store:
        print("❌ No store found in database")
        return
        
    shop_url, access_token, blog_handle = store
    print(f"🔧 Testing with store: {shop_url}")
    print(f"🔧 Blog handle: {blog_handle}")
    print(f"🔧 Token: {access_token[:10]}...{access_token[-4:]}")
    
    # Shopify API setup
    api_base = f"https://{shop_url}.myshopify.com/admin/api/2025-07"
    headers = {
        'X-Shopify-Access-Token': access_token,
        'Content-Type': 'application/json'
    }
    
    print(f"🔧 API Base URL: {api_base}")
    
    try:
        # Step 1: Test API connection
        print("\n📡 Testing API connection...")
        shop_response = requests.get(f"{api_base}/shop.json", headers=headers)
        print(f"Shop API Status: {shop_response.status_code}")
        
        if shop_response.status_code == 200:
            shop_info = shop_response.json()['shop']
            print(f"✅ Connected to shop: {shop_info['name']} ({shop_info['domain']})")
        else:
            print(f"❌ Shop API failed: {shop_response.text}")
            return
            
        # Step 2: Get blogs
        print("\n📋 Getting blogs...")
        blogs_response = requests.get(f"{api_base}/blogs.json", headers=headers)
        print(f"Blogs API Status: {blogs_response.status_code}")
        
        if blogs_response.status_code == 200:
            blogs = blogs_response.json().get('blogs', [])
            print(f"✅ Found {len(blogs)} blogs:")
            for blog in blogs:
                print(f"  - {blog['title']} (handle: {blog['handle']}, id: {blog['id']})")
                
            # Find target blog
            target_blog = None
            for blog in blogs:
                if blog['handle'] == blog_handle:
                    target_blog = blog
                    break
                    
            if not target_blog:
                print(f"❌ Blog with handle '{blog_handle}' not found")
                print("Available blog handles:", [b['handle'] for b in blogs])
                return
            else:
                print(f"✅ Found target blog: {target_blog['title']} (ID: {target_blog['id']})")
        else:
            print(f"❌ Blogs API failed: {blogs_response.text}")
            return
            
        # Step 3: Create test article
        print("\n📝 Creating test article...")
        test_article = {
            "article": {
                "title": f"API Test Article {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "body_html": "<h1>Test Article</h1><p>This is a test article created via API to verify publishing works.</p>",
                "handle": f"api-test-{int(datetime.now().timestamp())}",
                "published": True,
                "tags": "API Test, Automated"
            }
        }
        
        create_response = requests.post(
            f"{api_base}/blogs/{target_blog['id']}/articles.json",
            headers=headers,
            json=test_article
        )
        
        print(f"Create Article Status: {create_response.status_code}")
        
        if create_response.status_code == 201:
            article = create_response.json()['article']
            print(f"✅ Article created successfully!")
            print(f"  Article ID: {article['id']}")
            print(f"  Handle: {article['handle']}")
            
            # Construct the live URL
            # Note: The live URL should use the actual domain, not .myshopify.com
            live_url = f"https://www.imaginal.tech/blogs/{blog_handle}/{article['handle']}"
            print(f"  🔗 Live URL: {live_url}")
            
            return {
                "success": True,
                "article_id": article['id'],
                "live_url": live_url,
                "handle": article['handle']
            }
        else:
            print(f"❌ Article creation failed: {create_response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

if __name__ == "__main__":
    result = test_shopify_publish()
    if result:
        print(f"\n🎉 SUCCESS! Test article published:")
        print(f"🔗 {result['live_url']}")
    else:
        print("\n💥 Publishing test failed")