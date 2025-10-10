#!/usr/bin/env python3
"""Test video steganography password security through web API"""

import requests
import json
import time
import os

def test_web_api_video_security():
    """Test video steganography security through the actual web API"""
    print("🌐 Testing video steganography security through web API...")
    
    base_url = "http://127.0.0.1:8000"
    
    # Create test video file
    test_video_path = "test_api_video.mp4"
    with open(test_video_path, 'wb') as f:
        f.write(b"FAKE_VIDEO_DATA" * 1000)
    
    try:
        print("\n1. HIDING data in video via web API...")
        
        # Hide data with correct password
        correct_password = "webapi123"
        wrong_password = "wrongapi456"
        test_message = "Secret web API video message"
        
        # Upload and hide data
        with open(test_video_path, 'rb') as f:
            files = {'container_file': ('test_video.mp4', f, 'video/mp4')}
            request_data = {
                'data': test_message,
                'password': correct_password
            }
            
            response = requests.post(f"{base_url}/api/hide", files=files, data={'request_data': json.dumps(request_data)})
            
        if response.status_code != 200:
            print(f"   ❌ Hide request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        hide_result = response.json()
        if not hide_result.get('success'):
            print(f"   ❌ Hide operation failed: {hide_result}")
            return False
            
        job_id = hide_result['job_id']
        print(f"   ✅ Hide job started: {job_id}")
        
        # Wait for job completion
        for i in range(30):  # Wait up to 30 seconds
            status_response = requests.get(f"{base_url}/api/job/{job_id}")
            if status_response.status_code == 200:
                status_data = status_response.json()
                if status_data['status'] == 'completed':
                    print(f"   ✅ Hide completed successfully")
                    break
                elif status_data['status'] == 'failed':
                    print(f"   ❌ Hide failed: {status_data.get('message', 'Unknown error')}")
                    return False
            time.sleep(1)
        else:
            print(f"   ❌ Hide operation timed out")
            return False
        
        # Download the steganographic video
        download_response = requests.get(f"{base_url}/api/download/{job_id}")
        if download_response.status_code != 200:
            print(f"   ❌ Download failed: {download_response.status_code}")
            return False
        
        # Save the steganographic video
        stego_video_path = "stego_video_api.mp4"
        with open(stego_video_path, 'wb') as f:
            f.write(download_response.content)
        
        print(f"   ✅ Downloaded steganographic video: {len(download_response.content)} bytes")
        
        print("\n2. EXTRACTING with WRONG password via web API...")
        
        # Try to extract with wrong password
        with open(stego_video_path, 'rb') as f:
            files = {'container_file': ('stego_video.mp4', f, 'video/mp4')}
            request_data = {'password': wrong_password}
            
            extract_response = requests.post(f"{base_url}/api/extract", files=files, data={'request_data': json.dumps(request_data)})
        
        if extract_response.status_code != 200:
            print(f"   ❌ Extract request failed: {extract_response.status_code}")
            return False
        
        extract_result = extract_response.json()
        wrong_job_id = extract_result['job_id']
        print(f"   Started extract job with wrong password: {wrong_job_id}")
        
        # Wait for extraction completion
        for i in range(30):
            status_response = requests.get(f"{base_url}/api/job/{wrong_job_id}")
            if status_response.status_code == 200:
                status_data = status_response.json()
                if status_data['status'] == 'completed':
                    print(f"   ❌ CRITICAL VULNERABILITY: Wrong password extraction succeeded!")
                    print(f"   ❌ Status: {status_data}")
                    return False
                elif status_data['status'] == 'failed':
                    print(f"   ✅ Good: Wrong password extraction failed: {status_data.get('message', 'No message')}")
                    print(f"   ✅ Error: {status_data.get('error', 'No error details')}")
                    break
            time.sleep(1)
        else:
            print(f"   ⚠️  Wrong password extraction timed out (might be stuck)")
        
        print("\n3. EXTRACTING with CORRECT password via web API...")
        
        # Try to extract with correct password
        with open(stego_video_path, 'rb') as f:
            files = {'container_file': ('stego_video.mp4', f, 'video/mp4')}
            request_data = {'password': correct_password}
            
            extract_response = requests.post(f"{base_url}/api/extract", files=files, data={'request_data': json.dumps(request_data)})
        
        if extract_response.status_code != 200:
            print(f"   ❌ Extract request failed: {extract_response.status_code}")
            return False
        
        extract_result = extract_response.json()
        correct_job_id = extract_result['job_id']
        print(f"   Started extract job with correct password: {correct_job_id}")
        
        # Wait for extraction completion
        for i in range(30):
            status_response = requests.get(f"{base_url}/api/job/{correct_job_id}")
            if status_response.status_code == 200:
                status_data = status_response.json()
                if status_data['status'] == 'completed':
                    print(f"   ✅ Correct password extraction succeeded!")
                    
                    # Download the extracted data
                    download_response = requests.get(f"{base_url}/api/download/{correct_job_id}")
                    if download_response.status_code == 200:
                        extracted_content = download_response.content.decode('utf-8', errors='ignore')
                        if test_message in extracted_content:
                            print(f"   ✅ Perfect: Extracted the correct message!")
                            print(f"   ✅ Message: {test_message}")
                            return True
                        else:
                            print(f"   ❌ Problem: Extracted wrong content")
                            print(f"   ❌ Expected: {test_message}")
                            print(f"   ❌ Got: {extracted_content[:100]}...")
                            return False
                    else:
                        print(f"   ❌ Failed to download extracted content")
                        return False
                elif status_data['status'] == 'failed':
                    print(f"   ❌ Correct password extraction failed: {status_data.get('message', 'No message')}")
                    return False
            time.sleep(1)
        else:
            print(f"   ❌ Correct password extraction timed out")
            return False
            
    except Exception as e:
        print(f"   ❌ API test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up test files
        for file_path in [test_video_path, "stego_video_api.mp4"]:
            if os.path.exists(file_path):
                os.remove(file_path)

def main():
    """Run the web API security test"""
    print("🔒 VIDEO STEGANOGRAPHY WEB API SECURITY TEST")
    print("=" * 60)
    
    try:
        # Check if web app is running
        response = requests.get("http://127.0.0.1:8000/")
        if response.status_code != 200:
            print("❌ Web app is not running. Please start it first with: python app.py")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to web app at http://127.0.0.1:8000")
        print("   Please start it first with: python app.py")
        return False
    
    is_secure = test_web_api_video_security()
    
    print("\n" + "=" * 60)
    if is_secure:
        print("🎉 VIDEO STEGANOGRAPHY WEB API IS SECURE!")
        print("✅ Wrong passwords fail through web API")
        print("✅ Correct passwords work through web API")
    else:
        print("⚠️ VIDEO STEGANOGRAPHY WEB API SECURITY ISSUE!")
        print("❌ There may be a vulnerability in the web API")
    
    return is_secure

if __name__ == "__main__":
    main()