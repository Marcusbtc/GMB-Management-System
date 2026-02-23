import requests
import json

def check_api_direct():
    # Try to find the discovery doc in the main list again, but print ALL names to be sure
    url = "https://www.googleapis.com/discovery/v1/apis"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        items = data.get('items', [])
        print(f"Total APIs found: {len(items)}")
        found = False
        for item in items:
            if 'mybusiness' in item['name']:
                print(f"Found: {item['name']} {item['version']}")
                if item['name'] == 'mybusinessreviews':
                    found = True
                    print(f"Discovery URL: {item.get('discoveryRestUrl')}")
        
        if not found:
            print("mybusinessreviews NOT found in public directory.")
            
check_api_direct()
