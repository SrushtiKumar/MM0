#!/usr/bin/env python3
"""Test video steganography password security through web API - focused test"""

import requests
import json
import time
import os

def test_password_security():
    """Test password security specifically"""
    
    # Create test video
    test_video = "api_test_video.mp4" 
    with open(test_video, 'wb') as f:
        f.write(b"FAKE_VIDEO_DATA" * 1000)
    
    correct_password = "correct123"
    wrong_password = "wrong456"
    test_message = "Secret test message for API"
    
    print("🎬 Testing video steganography password security via API...")
    
    try:
        # 1. Hide data
        print("\n1. Hiding data with correct password...")
        with open(test_video, 'rb') as f:
            files = {'container_file': (test_video, f, 'video/mp4')}
            request_data = {'data': test_message, 'password': correct_password}
            
            hide_response = requests.post("http://127.0.0.1:8000/api/hide", 
                                        files=files, 
                                        data={'request_data': json.dumps(request_data)})
        
        if hide_response.status_code != 200:
            print(f"❌ Hide failed: {hide_response.status_code}")
            return False
        
        hide_result = hide_response.json()
        hide_job_id = hide_result['job_id']
        
        # Wait for hide completion
        for i in range(30):
            status_response = requests.get(f"http://127.0.0.1:8000/api/job/{hide_job_id}")
            if status_response.status_code == 200:
                status_data = status_response.json()
                if status_data['status'] == 'completed':
                    print("✅ Hide operation completed")
                    break
                elif status_data['status'] == 'failed':
                    print(f"❌ Hide failed: {status_data.get('message')}")
                    return False
            time.sleep(1)
        
        # Download steganographic video
        download_response = requests.get(f"http://127.0.0.1:8000/api/download/{hide_job_id}")
        if download_response.status_code != 200:
            print(f"❌ Download failed: {download_response.status_code}")
            return False
        
        stego_video = "stego_test_video.mp4"
        with open(stego_video, 'wb') as f:
            f.write(download_response.content)
        
        print(f"✅ Downloaded steganographic video: {len(download_response.content)} bytes")
        
        # 2. Try extraction with WRONG password
        print("\n2. Extracting with WRONG password...")
        with open(stego_video, 'rb') as f:
            files = {'container_file': (stego_video, f, 'video/mp4')}
            request_data = {'password': wrong_password}
            
            extract_response = requests.post("http://127.0.0.1:8000/api/extract", 
                                           files=files, 
                                           data={'request_data': json.dumps(request_data)})
        
        if extract_response.status_code != 200:
            print(f"❌ Wrong password extract failed: {extract_response.status_code}")
            return False
        
        wrong_result = extract_response.json()
        wrong_job_id = wrong_result['job_id']
        
        # Wait for wrong password extraction
        wrong_password_success = False
        for i in range(30):
            status_response = requests.get(f"http://127.0.0.1:8000/api/job/{wrong_job_id}")
            if status_response.status_code == 200:
                status_data = status_response.json()
                if status_data['status'] == 'completed':
                    print(f"❌ CRITICAL VULNERABILITY: Wrong password extraction succeeded!")
                    print(f"   Result: {status_data}")
                    wrong_password_success = True
                    break
                elif status_data['status'] == 'failed':
                    error_msg = status_data.get('message', '')
                    if 'password' in error_msg.lower() or 'corruption' in error_msg.lower():
                        print(f"✅ SECURE: Wrong password properly failed")
                        print(f"   Error: {error_msg}")
                    else:
                        print(f"⚠️  Wrong password failed with unexpected error: {error_msg}")
                    break
            time.sleep(1)
        
        if wrong_password_success:
            return False  # Security vulnerability detected
        
        # 3. Try extraction with CORRECT password
        print("\n3. Extracting with CORRECT password...")
        with open(stego_video, 'rb') as f:
            files = {'container_file': (stego_video, f, 'video/mp4')}
            request_data = {'password': correct_password}
            
            extract_response = requests.post("http://127.0.0.1:8000/api/extract", 
                                           files=files, 
                                           data={'request_data': json.dumps(request_data)})
        
        if extract_response.status_code != 200:
            print(f"❌ Correct password extract failed: {extract_response.status_code}")
            return False
        
        correct_result = extract_response.json()
        correct_job_id = correct_result['job_id']
        
        # Wait for correct password extraction
        for i in range(30):
            status_response = requests.get(f"http://127.0.0.1:8000/api/job/{correct_job_id}")
            if status_response.status_code == 200:
                status_data = status_response.json()
                if status_data['status'] == 'completed':
                    print("✅ Correct password extraction completed")
                    
                    # Download and verify extracted content
                    download_response = requests.get(f"http://127.0.0.1:8000/api/download/{correct_job_id}")
                    if download_response.status_code == 200:
                        content = download_response.content.decode('utf-8', errors='ignore')
                        if test_message in content:
                            print(f"✅ PERFECT: Correct message extracted!")
                            print(f"   Message: {test_message}")
                            return True
                        else:
                            print(f"❌ Wrong content extracted")
                            print(f"   Expected: {test_message}")
                            print(f"   Got: {content[:100]}...")
                            return False
                    else:
                        print(f"❌ Failed to download extracted content")
                        return False
                        
                elif status_data['status'] == 'failed':
                    print(f"❌ Correct password extraction failed: {status_data.get('message')}")
                    return False
            time.sleep(1)
        
        print("❌ Correct password extraction timed out")
        return False
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        for file in [test_video, stego_video]:
            if os.path.exists(file):
                os.remove(file)

if __name__ == "__main__":
    print("🔒 VIDEO STEGANOGRAPHY PASSWORD SECURITY TEST")
    print("=" * 50)
    
    is_secure = test_password_security()
    
    print("\n" + "=" * 50)
    if is_secure:
        print("🎉 VIDEO STEGANOGRAPHY IS SECURE!")
        print("✅ Wrong passwords fail appropriately")
        print("✅ Correct passwords extract data successfully")
    else:
        print("🚨 SECURITY VULNERABILITY DETECTED!")
        print("❌ Wrong passwords may be succeeding")
        print("❌ Immediate fix required!")