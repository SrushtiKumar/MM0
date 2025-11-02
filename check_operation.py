"""
Check the status of the completed operation to see what happened
"""
import requests
import json

def check_operation_status():
    operation_id = "0bcd0e22-41f5-4b78-855b-1ccc1848f1a4"  # From the previous test
    status_url = f"http://localhost:8000/api/operations/{operation_id}/status"
    
    print(f"Checking operation: {operation_id}")
    
    response = requests.get(status_url)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Full status response:")
        print(json.dumps(result, indent=2))
        
        # Also check download URL
        download_url = f"http://localhost:8000/api/operations/{operation_id}/download"
        print(f"\\nTrying download URL: {download_url}")
        
        download_response = requests.get(download_url)
        print(f"Download status: {download_response.status_code}")
        
        if download_response.status_code == 200:
            print("✅ File download works!")
            # Save the file for testing
            with open("downloaded_stego_audio.wav", "wb") as f:
                f.write(download_response.content)
            print("Saved as downloaded_stego_audio.wav")
        else:
            print(f"❌ Download failed: {download_response.text}")
    else:
        print(f"Status check failed: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    check_operation_status()