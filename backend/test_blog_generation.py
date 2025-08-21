#!/usr/bin/env python3
"""
Test blog generation process
"""

import requests
import sqlite3
import json
import time

def test_blog_generation():
    # Get a pending keyword and store
    conn = sqlite3.connect('seo_saas.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, keyword FROM keywords WHERE status = "pending" LIMIT 1')
    keyword_row = cursor.fetchone()
    
    cursor.execute('SELECT id FROM shopify_stores LIMIT 1')
    store_row = cursor.fetchone()
    
    conn.close()
    
    if not keyword_row or not store_row:
        print("❌ No pending keywords or stores found")
        return
        
    keyword_id, keyword_text = keyword_row
    store_id = store_row[0]
    
    print(f"🧪 Testing blog generation:")
    print(f"  Keyword ID: {keyword_id} ('{keyword_text}')")
    print(f"  Store ID: {store_id}")
    
    # Test the generate API endpoint
    url = "http://localhost:8000/api/blogs/generate"
    
    payload = {
        "keyword_ids": [keyword_id],
        "store_id": store_id,
        "template_type": "ecommerce_general",
        "auto_publish": False
    }
    
    try:
        print(f"\n📡 Making API request to {url}")
        response = requests.post(url, json=payload)
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success Response:")
            print(f"  Message: {result.get('message')}")
            print(f"  Job ID: {result.get('job_id')}")
            print(f"  Blogs Queued: {result.get('blogs_queued')}")
            print(f"  Estimated Completion: {result.get('estimated_completion')}")
            
            # Wait a moment and check keyword status
            print(f"\n⏳ Waiting 5 seconds to check status...")
            time.sleep(5)
            
            conn = sqlite3.connect('seo_saas.db')
            cursor = conn.cursor()
            cursor.execute('SELECT status, blog_generated FROM keywords WHERE id = ?', (keyword_id,))
            updated_status = cursor.fetchone()
            conn.close()
            
            if updated_status:
                print(f"  Updated Status: {updated_status[0]}")
                print(f"  Blog Generated: {updated_status[1]}")
            
        else:
            print(f"❌ API Error Response:")
            print(f"  Status: {response.status_code}")
            print(f"  Text: {response.text}")
            
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Error: {e}")
        print("  Is the backend server running on port 8000?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_blog_generation()