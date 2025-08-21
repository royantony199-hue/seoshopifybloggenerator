#!/usr/bin/env python3
"""
Test publishing the specific blog that was just created
"""

import requests
import sqlite3

def test_publish_blog():
    # Test publishing blog ID 10
    blog_id = 10
    url = f"http://localhost:8000/api/blogs/{blog_id}/publish"
    
    try:
        print(f"🧪 Testing publish for blog ID {blog_id}")
        response = requests.post(url)
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success Response:")
            print(f"  Message: {result.get('message')}")
            print(f"  Live URL: {result.get('live_url')}")
            print(f"  Demo Mode: {result.get('demo_mode')}")
            
            # Check database after publishing
            conn = sqlite3.connect('seo_saas.db')
            cursor = conn.cursor()
            cursor.execute('SELECT live_url, shopify_article_id, published FROM generated_blogs WHERE id = ?', (blog_id,))
            updated_blog = cursor.fetchone()
            conn.close()
            
            if updated_blog:
                print(f"\n📊 Updated blog in database:")
                print(f"  Live URL: {updated_blog[0]}")
                print(f"  Shopify Article ID: {updated_blog[1]}")
                print(f"  Published: {updated_blog[2]}")
        else:
            print(f"❌ API Error Response:")
            print(f"  Status: {response.status_code}")
            print(f"  Text: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_publish_blog()