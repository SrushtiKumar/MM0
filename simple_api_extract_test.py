#!/usr/bin/env python3
"""
Simple script to test extraction via API and see debug logs
"""

import requests
import json
import time

def test_api_extraction():
    """Test extraction directly via API"""
    
    print("🧪 Testing API Extraction...")
    
    # Extract from our stego video
    with open("debug_stego_video.mp4", "rb") as f:
        response = requests.post(
            "http://localhost:8000/api/extract",
            files={"stego_file": ("debug_stego_video.mp4", f, "video/mp4")},
            data={
                "password": "testpass123",
                "output_format": "auto"
            }
        )
    
    if response.status_code != 200:
        print(f"❌ Extract failed: {response.text}")
        return
        
    result = response.json()
    if not result.get('success'):
        print(f"❌ Extract failed: {result}")
        return
        
    operation_id = result['operation_id']
    print(f"✅ Extract started: {operation_id}")
    
    # Wait for completion
    while True:
        status_response = requests.get(f"http://localhost:8000/api/operations/{operation_id}/status")
        status_data = status_response.json()
        print(f"📊 Status: {status_data['status']}")
        
        if status_data['status'] == 'completed':
            break
        elif status_data['status'] == 'failed':
            print(f"❌ Failed: {status_data.get('error')}")
            return
            
        time.sleep(1)
    
    # Download result
    download_response = requests.get(f"http://localhost:8000/api/operations/{operation_id}/download")
    if download_response.status_code != 200:
        print(f"❌ Download failed: {download_response.status_code}")
        return
        
    # Check headers for filename
    content_disposition = download_response.headers.get('Content-Disposition', '')
    print(f"📋 Content-Disposition: {content_disposition}")
    
    # Save file
    with open("api_extracted_file.bin", "wb") as f:
        f.write(download_response.content)
        
    print(f"✅ Saved {len(download_response.content)} bytes")
    
    # Check if it's a valid PNG
    try:
        from PIL import Image
        with Image.open("api_extracted_file.bin") as img:
            print(f"✅ Valid image: {img.format} {img.size}")
    except Exception as e:
        print(f"❌ Not a valid image: {e}")

if __name__ == "__main__":
    test_api_extraction()