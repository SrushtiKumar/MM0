#!/usr/bin/env python3
"""
Simple test for extract fix verification
"""

import requests
import time

def test_extract_simple():
    BASE_URL = "http://localhost:8001"
    
    # Test server connection
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Server running: {response.status_code}")
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        return False
    
    # Create simple test files
    with open("test.png", "wb") as f:
        f.write(b"PNG_TEST_DATA" * 500)
    
    with open("secret.txt", "w") as f:
        f.write("Secret message for testing!")
    
    # Test hide operation
    print("\n📁 Testing hide...")
    with open("test.png", "rb") as img, open("secret.txt", "rb") as secret:
        files = {
            "container_file": ("test.png", img, "image/png"),
            "secret_file": ("secret.txt", secret, "text/plain")
        }
        data = {"password": "test123"}
        
        response = requests.post(f"{BASE_URL}/hide", files=files, data=data)
        if response.status_code != 200:
            print(f"❌ Hide failed: {response.text}")
            return False
        
        job_id = response.json()["job_id"]
        print(f"Hide job: {job_id}")
        
        # Wait for completion
        for _ in range(20):
            status = requests.get(f"{BASE_URL}/status/{job_id}").json()
            if status["status"] == "completed":
                print("✅ Hide completed")
                break
            elif status["status"] == "failed":
                print(f"❌ Hide failed: {status.get('message')}")
                return False
            time.sleep(1)
        
        # Download result
        download = requests.get(f"{BASE_URL}/download/{job_id}")
        if download.status_code != 200:
            print("❌ Download failed")
            return False
        
        with open("stego.png", "wb") as f:
            f.write(download.content)
        print("✅ Downloaded stego image")
    
    # Test extract operation
    print("\n🔍 Testing extract...")
    with open("stego.png", "rb") as stego:
        files = {"container_file": ("stego.png", stego, "image/png")}
        data = {"password": "test123"}
        
        response = requests.post(f"{BASE_URL}/extract", files=files, data=data)
        if response.status_code != 200:
            print(f"❌ Extract failed: {response.text}")
            return False
        
        extract_job_id = response.json()["job_id"]
        print(f"Extract job: {extract_job_id}")
        
        # Wait for completion
        for _ in range(20):
            status = requests.get(f"{BASE_URL}/status/{extract_job_id}").json()
            if status["status"] == "completed":
                print("✅ Extract completed!")
                print(f"Result: {status.get('result', {})}")
                break
            elif status["status"] == "failed":
                print(f"❌ Extract failed: {status.get('message')}")
                print(f"Error: {status.get('error')}")
                return False
            time.sleep(1)
        
        # Download extracted content
        extract_download = requests.get(f"{BASE_URL}/download/{extract_job_id}")
        if extract_download.status_code != 200:
            print("❌ Extract download failed")
            return False
        
        content_disposition = extract_download.headers.get('Content-Disposition', '')
        print(f"📁 Filename: {content_disposition}")
        
        extracted = extract_download.content.decode()
        print(f"📄 Content: {extracted}")
        
        if "Secret message for testing!" in extracted:
            print("🎉 SUCCESS! Extract operation is working correctly!")
            return True
        else:
            print("❌ Content mismatch")
            return False

if __name__ == "__main__":
    test_extract_simple()