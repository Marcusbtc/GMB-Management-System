from googleapiclient.discovery import build
import requests

def check_v4_discovery():
    url = "https://developers.google.com/my-business/samples/mybusiness_google_rest_v4p9.json"
    print(f"Checking URL: {url}")
    
    try:
        # Fetch the discovery doc content first to verify it exists
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch discovery doc: {response.status_code}")
            return

        print("Discovery doc found. Building service...")
        service = build('mybusiness', 'v4', discoveryServiceUrl=url, developerKey='DUMMY')
        print("Success building mybusiness v4 with discovery URL")
        
        # Check for reviews
        if hasattr(service, 'accounts'):
            if hasattr(service.accounts(), 'locations'):
                if hasattr(service.accounts().locations(), 'reviews'):
                    print("Has reviews resource!")
                else:
                    print("No reviews resource")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_v4_discovery()
