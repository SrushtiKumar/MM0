#!/usr/bin/env python3
"""
Quick Extraction Test for the fixed API
"""

import requests
import time
import os

API_BASE_URL = "http://localhost:8000/api"

def test_video_extraction():
    """Test video extraction"""
    print("Testing Video Extraction...")
    
    # Look for a stego video file
    stego_file = "test_stego_video.mp4"
    
    if not os.path.exists(stego_file):
        print(f"Stego video file {stego_file} not found")
        return False
    
    print(f"Using stego file: {stego_file}")
    
    # Prepare the request
    files = {
        'stego_file': open(stego_file, 'rb')
    }
    
    data = {
        'password': 'test123',
        'output_format': 'auto'
    }
    
    try:
        # Start extraction
        response = requests.post(f"{API_BASE_URL}/extract", files=files, data=data)
        files['stego_file'].close()
        
        if response.status_code != 200:
            print(f"Extract request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        result = response.json()
        operation_id = result.get('operation_id')
        
        print(f"Extraction started with operation ID: {operation_id}")
        
        # Poll for completion
        max_attempts = 15
        for attempt in range(max_attempts):
            status_response = requests.get(f"{API_BASE_URL}/operations/{operation_id}/status")
            
            if status_response.status_code == 200:
                status = status_response.json()
                print(f"Status: {status.get('status')} - Progress: {status.get('progress', 0)}%")
                
                if status.get('status') == 'completed':
                    print("✅ Extraction completed successfully!")
                    result_data = status.get('result', {})
                    
                    if result_data.get('data_type') == 'text':
                        preview = result_data.get('preview', 'No preview')
                        print(f"Extracted text preview: '{preview}'")
                    
                    print(f"Output file: {result_data.get('filename')}")
                    return True
                
                elif status.get('status') == 'failed':
                    print(f"❌ Extraction failed: {status.get('error')}")
                    return False
            
            time.sleep(1)
        
        print("❌ Extraction timed out")
        return False
        
    except Exception as e:
        print(f"❌ Exception during extraction: {e}")
        return False

def main():
    """Test extraction"""
    print("=== Extraction Test ===\n")
    
    success = test_video_extraction()
    
    print(f"\n=== Result ===")
    print(f"Video Extraction: {'✅ PASS' if success else '❌ FAIL'}")
    
    if success:
        print("🎉 Extraction test passed!")
    else:
        print("⚠️ Extraction test failed.")

if __name__ == "__main__":
    main()