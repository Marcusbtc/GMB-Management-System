import requests

def check_discovery_url():
    url = "https://mybusinessreviews.googleapis.com/$discovery/rest?version=v1"
    print(f"Checking URL: {url}")
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Success! Discovery document found.")
        # print(response.text[:200])
    else:
        print("Failed to retrieve discovery document.")

if __name__ == "__main__":
    check_discovery_url()
