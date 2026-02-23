from googleapiclient.discovery import build
import json

def check_v4():
    try:
        print("Building mybusiness v4...")
        service = build('mybusiness', 'v4', developerKey='DUMMY')
        print("Success building mybusiness v4")
        if hasattr(service, 'accounts'):
            print("Has accounts resource")
            if hasattr(service.accounts(), 'locations'):
                print("Has locations resource")
                if hasattr(service.accounts().locations(), 'reviews'):
                    print("Has reviews resource")
                else:
                    print("No reviews resource")
    except Exception as e:
        print(f"Error building mybusiness v4: {e}")

if __name__ == "__main__":
    check_v4()
