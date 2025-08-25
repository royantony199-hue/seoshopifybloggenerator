import sqlite3
import requests

# Get the Shopify store credentials
conn = sqlite3.connect('seo_saas.db')
cursor = conn.cursor()
cursor.execute('SELECT shop_url, access_token FROM shopify_stores LIMIT 1')
result = cursor.fetchone()
conn.close()

if result:
    shop_url, access_token = result
    print(f'Testing Shopify connection to: {shop_url}')
    
    headers = {
        'X-Shopify-Access-Token': access_token,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(f'https://{shop_url}.myshopify.com/admin/api/2025-07/shop.json', headers=headers, timeout=10)
        print(f'Shopify API Status: {response.status_code}')
        if response.status_code != 200:
            print(f'Error Response: {response.text}')
        else:
            print('Shopify API is accessible')
    except requests.exceptions.RequestException as e:
        print(f'Connection Error: {e}')
else:
    print('No Shopify store found')