from googleapiclient.discovery import build
import requests

def try_manual_discovery():
    # Try to fetch the discovery document from a known location if possible, 
    # or use the 'mybusiness' v4 if it's still the only way, but maybe with a specific URL.
    
    # Some users report v4 is gone.
    # The new APIs are split.
    # Reviews should be in 'mybusinessreviews' v1?
    
    # Let's try to find the discovery URL from the Google API Discovery Service list again,
    # but maybe we missed it because of the name?
    
    url = "https://www.googleapis.com/discovery/v1/apis"
    resp = requests.get(url)
    data = resp.json()
    for item in data['items']:
        if 'review' in item['id'] or 'business' in item['id']:
            print(f"ID: {item['id']}, Title: {item.get('title')}, Discovery: {item['discoveryRestUrl']}")

try_manual_discovery()
