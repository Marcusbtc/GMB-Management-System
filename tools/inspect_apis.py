from googleapiclient.discovery import build
import json

def inspect_service(service_name, version):
    print(f"--- Inspecting {service_name} {version} ---")
    try:
        # We don't need credentials just to build the service object for inspection if we don't make calls
        # But build() might require them or at least an API key if we were making calls. 
        # For discovery, build() fetches the doc.
        # We can use developerKey=None and it should work for building.
        service = build(service_name, version, developerKey='DUMMY') 
        
        # Inspect resources
        if hasattr(service, 'accounts'):
            accounts = service.accounts()
            print("Has 'accounts' resource")
            if hasattr(accounts, 'locations'):
                locations = accounts.locations()
                print("  Has 'locations' resource")
                # Check for reviews
                if hasattr(locations, 'reviews'):
                    print("    Has 'reviews' resource!")
                else:
                    print(f"    No 'reviews' resource in {service_name}")
                    # List available methods/resources
                    # print(dir(locations))
            else:
                print(f"  No 'locations' resource in {service_name}")
        else:
            print(f"No 'accounts' resource in {service_name}")
            
    except Exception as e:
        print(f"Error building {service_name}: {e}")

if __name__ == "__main__":
    inspect_service('mybusinessbusinessinformation', 'v1')
    inspect_service('mybusinessaccountmanagement', 'v1')
    # inspect_service('mybusiness', 'v4') # Deprecated but let's check if it was there
