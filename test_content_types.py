#!/usr/bin/env python3
"""
Test All Content Types
Tests the new content type functionality (text, file, image, video, audio, document)
"""

import requests
import time
import os

API_BASE_URL = "http://localhost:8000/api"

def test_all_content_types():
    """Test all content types with video carrier"""
    
    # Check if test video exists
    video_path = "simple_test_video.mp4"
    if not os.path.exists(video_path):
        print(f"Error: Test video {video_path} not found")
        return False
    
    # Test different content types
    test_cases = [
        {
            "name": "Text Content",
            "content_type": "text",
            "text_content": "This is a secret text message!",
            "file": None
        },
        {
            "name": "Binary File",
            "content_type": "file", 
            "text_content": None,
            "file_content": b"Binary data for testing: \x00\x01\x02\x03\xFF"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases):
        print(f"\n{'='*50}")
        print(f"Testing: {test_case['name']}")
        print(f"{'='*50}")
        
        # Prepare files
        files = {'carrier_file': open(video_path, 'rb')}
        
        # Prepare form data
        data = {
            'carrier_type': 'video',
            'content_type': test_case['content_type'],
            'password': f'test{i}123',
            'encryption_type': 'aes-256-gcm',
            'project_name': f'Test Project {i+1}',
            'project_description': f'Testing {test_case["name"]} embedding'
        }
        
        # Add content based on type
        if test_case['content_type'] == 'text':
            data['text_content'] = test_case['text_content']
        else:
            # Create temporary file for binary content
            temp_file = f'temp_test_file_{i}.bin'
            with open(temp_file, 'wb') as f:
                f.write(test_case['file_content'])
            files['content_file'] = open(temp_file, 'rb')
        
        try:
            # Start embedding
            print(f"Starting {test_case['name']} embedding...")
            response = requests.post(f"{API_BASE_URL}/embed", files=files, data=data)
            
            # Close files
            files['carrier_file'].close()
            if 'content_file' in files:
                files['content_file'].close()
                os.remove(temp_file)  # Clean up temp file
            
            if response.status_code != 200:
                print(f"❌ Request failed: {response.status_code}")
                print(f"Response: {response.text}")
                results.append(False)
                continue
            
            result = response.json()
            operation_id = result.get('operation_id')
            print(f"Operation ID: {operation_id}")
            
            # Poll for completion
            max_attempts = 30
            success = False
            for attempt in range(max_attempts):
                status_response = requests.get(f"{API_BASE_URL}/operations/{operation_id}/status")
                
                if status_response.status_code == 200:
                    status = status_response.json()
                    print(f"Status: {status.get('status')} - Progress: {status.get('progress', 0)}%")
                    
                    if status.get('status') == 'completed':
                        print(f"✅ {test_case['name']} embedding completed!")
                        result_data = status.get('result', {})
                        print(f"Output file: {result_data.get('filename', 'N/A')}")
                        print(f"Processing time: {result_data.get('processing_time', 'N/A')} seconds")
                        success = True
                        break
                    
                    elif status.get('status') == 'failed':
                        print(f"❌ {test_case['name']} embedding failed: {status.get('error')}")
                        break
                
                time.sleep(1)
            
            if not success and attempt >= max_attempts - 1:
                print(f"❌ {test_case['name']} embedding timed out")
            
            results.append(success)
            
        except Exception as e:
            print(f"❌ Exception during {test_case['name']} embedding: {e}")
            results.append(False)
            # Clean up on exception
            if 'content_file' in files and temp_file in locals():
                try:
                    files['content_file'].close()
                    os.remove(temp_file)
                except:
                    pass
    
    # Summary
    print(f"\n{'='*50}")
    print("CONTENT TYPE TEST SUMMARY")
    print(f"{'='*50}")
    
    for i, (test_case, success) in enumerate(zip(test_cases, results)):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_case['name']}: {status}")
    
    passed = sum(results)
    total = len(results)
    print(f"\nOverall: {passed}/{total} content types working")
    
    if passed == total:
        print("🎉 All content types are working perfectly!")
    else:
        print("⚠️ Some content types need attention.")
    
    return passed == total

if __name__ == "__main__":
    print("=== Content Type Compatibility Test ===")
    test_all_content_types()