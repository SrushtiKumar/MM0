#!/usr/bin/env python3
"""
Quick test to verify extract operation with fixed file naming
"""

import requests
import time
import tempfile
import os
from pathlib import Path

def test_extract_fix():
    """Test that extract operation works with fixed file naming"""
    print("🧪 Testing Extract Operation Fix...")
    
    BASE_URL = "http://localhost:8000"
    
    # Check server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Server is running (status: {response.status_code})")
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        return
    
    # Create test files
    test_image = "test_extract_fix.png"
    test_secret = "secret_file.txt"
    
    # Create a simple test image file
    with open(test_image, "wb") as f:
        f.write(b"PNG_FAKE_DATA" * 1000)  # Make it large enough for steganography
    
    # Create test secret file
    with open(test_secret, "w") as f:
        f.write("This is a secret file for testing the extract fix!\nThe file naming should work correctly now.")
    
    password = "testfix123"
    
    try:
        print("\n📁 Testing Hide Operation...")
        # Hide the secret file in the image
        with open(test_image, "rb") as img_file, open(test_secret, "rb") as secret_file:
            files = {
                "container_file": (test_image, img_file, "image/png"),
                "secret_file": (test_secret, secret_file, "text/plain")
            }
            data = {"password": password}
            
            hide_response = requests.post(f"{BASE_URL}/hide", files=files, data=data)
            if hide_response.status_code != 200:
                print(f"❌ Hide failed: {hide_response.text}")
                return
            
            hide_job = hide_response.json()
            hide_job_id = hide_job["job_id"]
            print(f"Hide job started: {hide_job_id}")
            
            # Wait for hide completion
            for i in range(30):
                status_response = requests.get(f"{BASE_URL}/status/{hide_job_id}")
                status = status_response.json()
                
                if status["status"] == "completed":
                    print("✅ Hide operation completed")
                    break
                elif status["status"] == "failed":
                    print(f"❌ Hide failed: {status.get('message', 'Unknown error')}")
                    return
                
                time.sleep(1)
            else:
                print("❌ Hide operation timed out")
                return
            
            # Download the steganographic image
            download_response = requests.get(f"{BASE_URL}/download/{hide_job_id}")
            if download_response.status_code != 200:
                print(f"❌ Download failed: {download_response.status_code}")
                return
            
            stego_filename = "stego_image.png"
            with open(stego_filename, "wb") as f:
                f.write(download_response.content)
            
            print(f"✅ Downloaded steganographic image: {stego_filename}")
        
        print("\n🔍 Testing Extract Operation...")
        # Extract the secret file from the steganographic image
        with open(stego_filename, "rb") as stego_file:
            files = {"container_file": (stego_filename, stego_file, "image/png")}
            data = {"password": password}
            
            extract_response = requests.post(f"{BASE_URL}/extract", files=files, data=data)
            if extract_response.status_code != 200:
                print(f"❌ Extract request failed: {extract_response.text}")
                return
            
            extract_job = extract_response.json()
            extract_job_id = extract_job["job_id"]
            print(f"Extract job started: {extract_job_id}")
            
            # Wait for extract completion
            for i in range(30):
                extract_status_response = requests.get(f"{BASE_URL}/status/{extract_job_id}")
                extract_status = extract_status_response.json()
                
                if extract_status["status"] == "completed":
                    print("✅ Extract operation completed successfully!")
                    print(f"Result: {extract_status.get('result', {})}")
                    break
                elif extract_status["status"] == "failed":
                    print(f"❌ Extract failed: {extract_status.get('message', 'Unknown error')}")
                    print(f"Error: {extract_status.get('error', 'No error details')}")
                    return
                
                time.sleep(1)
            else:
                print("❌ Extract operation timed out")
                return
            
            # Download the extracted file
            extract_download_response = requests.get(f"{BASE_URL}/download/{extract_job_id}")
            if extract_download_response.status_code != 200:
                print(f"❌ Extract download failed: {extract_download_response.status_code}")
                return
            
            # Check the filename from header
            content_disposition = extract_download_response.headers.get('Content-Disposition', '')
            print(f"📁 Extract filename header: {content_disposition}")
            
            extracted_content = extract_download_response.content.decode()
            print(f"📄 Extracted content: {extracted_content}")
            
            # Verify content matches
            with open(test_secret, "r") as f:
                original_content = f.read()
            
            if original_content.strip() == extracted_content.strip():
                print("✅ Extracted content matches original!")
                print("🎉 Extract operation fix verified successfully!")
            else:
                print("❌ Extracted content doesn't match original")
                print(f"Original: {original_content[:100]}...")
                print(f"Extracted: {extracted_content[:100]}...")
    
    finally:
        # Cleanup
        for file in [test_image, test_secret, "stego_image.png"]:
            if Path(file).exists():
                os.remove(file)
                print(f"🧹 Cleaned up: {file}")

if __name__ == "__main__":
    test_extract_fix()