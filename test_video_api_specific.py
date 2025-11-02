#!/usr/bin/env python3
"""
Test API with the video that works directly
"""

import requests
import time
import os

# Server configuration
SERVER_URL = "http://localhost:8000"

def test_video_api_with_working_file():
    """Test video steganography API with file that works directly"""
    
    # Use the file that works in direct test
    video_path = "comprehensive_test_video.mp4"
    if not os.path.exists(video_path):
        print(f"❌ Video not found: {video_path}")
        return False
    
    print(f"Testing video API with: {video_path}")
    
    # Test embedding
    print("\n1. Testing embedding via API...")
    
    with open(video_path, 'rb') as f:
        files = {'carrier_file': (video_path, f, 'video/mp4')}
        data = {
            'text_content': 'Z',  # Simple test message
            'password': 'test123',
            'content_type': 'text'
        }
        
        response = requests.post(f"{SERVER_URL}/api/embed", files=files, data=data)
        print(f"Embed response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Embed failed: {response.text}")
            return False
        
        result = response.json()
        print(f"Embed result: {result}")
        
        if not result.get('success'):
            print(f"❌ Embed not successful")
            return False
        
        operation_id = result['operation_id']
        
        # Wait for completion
        while True:
            status_response = requests.get(f"{SERVER_URL}/api/operations/{operation_id}/status")
            if status_response.status_code == 200:
                status = status_response.json()
                if status['status'] == 'completed':
                    print(f"✅ Embedding completed")
                    break
                elif status['status'] == 'failed':
                    print(f"❌ Embedding failed: {status.get('error')}")
                    return False
            time.sleep(0.5)
        
        # Download result
        download_response = requests.get(f"{SERVER_URL}/api/operations/{operation_id}/download")
        if download_response.status_code == 200:
            output_path = "api_test_video_embed.mp4"
            with open(output_path, 'wb') as f:
                f.write(download_response.content)
            print(f"✅ Downloaded embedded video: {output_path}")
        else:
            print(f"❌ Download failed")
            return False
    
    # Test extraction
    print("\n2. Testing extraction via API...")
    
    with open(output_path, 'rb') as f:
        files = {'stego_file': (output_path, f, 'video/mp4')}
        data = {'password': 'test123'}
        
        response = requests.post(f"{SERVER_URL}/api/extract", files=files, data=data)
        print(f"Extract response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Extract failed: {response.text}")
            return False
        
        result = response.json()
        
        if not result.get('success'):
            print(f"❌ Extract not successful")
            return False
        
        operation_id = result['operation_id']
        
        # Wait for completion
        while True:
            status_response = requests.get(f"{SERVER_URL}/api/operations/{operation_id}/status")
            if status_response.status_code == 200:
                status = status_response.json()
                if status['status'] == 'completed':
                    print(f"✅ Extraction completed")
                    break
                elif status['status'] == 'failed':
                    print(f"❌ Extraction failed: {status.get('error')}")
                    return False
            time.sleep(0.5)
        
        # Download result
        download_response = requests.get(f"{SERVER_URL}/api/operations/{operation_id}/download")
        if download_response.status_code == 200:
            extracted_content = download_response.text
            print(f"✅ Extracted content: '{extracted_content}'")
            
            if extracted_content == 'Z':
                print(f"✅ SUCCESS: Content matches!")
                return True
            else:
                print(f"❌ Content mismatch: expected 'Z', got '{extracted_content}'")
                return False
        else:
            print(f"❌ Download failed")
            return False

if __name__ == "__main__":
    success = test_video_api_with_working_file()
    print(f"\n" + "="*50)
    print(f"VIDEO API TEST RESULT: {'✅ PASS' if success else '❌ FAIL'}")
    print(f"="*50)