#!/usr/bin/env python3
"""
Test the web application with robust video steganography
"""

import requests
import os
import time

def test_web_video_steganography():
    """Test the web application video steganography endpoints"""
    
    print("🌐 TESTING WEB APPLICATION VIDEO STEGANOGRAPHY")
    
    base_url = "http://127.0.0.1:8002"
    
    # Test hide endpoint
    hide_url = f"{base_url}/api/hide"
    
    # Create test files
    test_video = "web_test_video.mp4"
    test_message = "web_test_message.txt"
    
    # Create test video file
    import cv2
    import numpy as np
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(test_video, fourcc, 10.0, (640, 480))
    
    for i in range(30):
        frame = np.random.randint(50, 200, (480, 640, 3), dtype=np.uint8)
        out.write(frame)
    out.release()
    
    # Create test message file
    with open(test_message, 'w') as f:
        f.write("This is a test message for the web application!")
    
    try:
        print(f"\n📤 Testing hide operation...")
        
        with open(test_video, 'rb') as video_file, open(test_message, 'rb') as msg_file:
            files = {
                'container_file': ('test_video.mp4', video_file, 'video/mp4'),
                'secret_file': ('test_message.txt', msg_file, 'text/plain')
            }
            data = {
                'password': 'test123',
                'is_enhanced': 'false'
            }
            
            response = requests.post(hide_url, files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                job_id = result.get('job_id')
                print(f"✅ Hide operation started, job ID: {job_id}")
                
                # Poll for completion
                job_url = f"{base_url}/api/job/{job_id}"
                
                for i in range(30):  # Wait up to 30 seconds
                    time.sleep(1)
                    job_response = requests.get(job_url)
                    
                    if job_response.status_code == 200:
                        job_data = job_response.json()
                        status = job_data.get('status')
                        
                        print(f"    Status: {status}")
                        
                        if status == 'completed':
                            print(f"✅ Hide operation completed!")
                            print(f"    Message: {job_data.get('message')}")
                            
                            # Test download
                            download_url = f"{base_url}/api/download/{job_id}"
                            download_response = requests.get(download_url)
                            
                            if download_response.status_code == 200:
                                output_video = 'downloaded_video.mp4'
                                with open(output_video, 'wb') as f:
                                    f.write(download_response.content)
                                print(f"✅ Downloaded output video: {output_video}")
                                
                                # Test extraction
                                print(f"\n📥 Testing extract operation...")
                                extract_url = f"{base_url}/api/extract"
                                
                                with open(output_video, 'rb') as video_file:
                                    extract_files = {
                                        'container_file': ('output_video.mp4', video_file, 'video/mp4')
                                    }
                                    extract_data = {
                                        'password': 'test123',
                                        'is_enhanced': 'false'
                                    }
                                    
                                    extract_response = requests.post(extract_url, files=extract_files, data=extract_data)
                                    
                                    if extract_response.status_code == 200:
                                        extract_result = extract_response.json()
                                        extract_job_id = extract_result.get('job_id')
                                        print(f"✅ Extract operation started, job ID: {extract_job_id}")
                                        
                                        # Poll for extraction completion
                                        extract_job_url = f"{base_url}/api/job/{extract_job_id}"
                                        
                                        for j in range(30):
                                            time.sleep(1)
                                            extract_job_response = requests.get(extract_job_url)
                                            
                                            if extract_job_response.status_code == 200:
                                                extract_job_data = extract_job_response.json()
                                                extract_status = extract_job_data.get('status')
                                                
                                                print(f"    Extract status: {extract_status}")
                                                
                                                if extract_status == 'completed':
                                                    print(f"🎉 EXTRACT OPERATION SUCCESSFUL!")
                                                    print(f"    Message: {extract_job_data.get('message')}")
                                                    
                                                    # Download extracted file
                                                    extract_download_url = f"{base_url}/api/download/{extract_job_id}"
                                                    extract_download_response = requests.get(extract_download_url)
                                                    
                                                    if extract_download_response.status_code == 200:
                                                        extracted_file = 'extracted_message.txt'
                                                        with open(extracted_file, 'wb') as f:
                                                            f.write(extract_download_response.content)
                                                        
                                                        with open(extracted_file, 'r') as f:
                                                            extracted_content = f.read()
                                                        
                                                        with open(test_message, 'r') as f:
                                                            original_content = f.read()
                                                        
                                                        print(f"📄 Original:  '{original_content}'")
                                                        print(f"📄 Extracted: '{extracted_content}'")
                                                        
                                                        if extracted_content == original_content:
                                                            print(f"🎉 WEB APPLICATION TEST PASSED!")
                                                        else:
                                                            print(f"❌ Content mismatch")
                                                    break
                                                elif extract_status == 'failed':
                                                    print(f"❌ Extract operation failed: {extract_job_data.get('message')}")
                                                    break
                                    else:
                                        print(f"❌ Extract request failed: {extract_response.status_code}")
                                
                                os.remove(output_video)
                            break
                        elif status == 'failed':
                            print(f"❌ Hide operation failed: {job_data.get('message')}")
                            break
            else:
                print(f"❌ Hide request failed: {response.status_code}")
                print(f"Response: {response.text}")
    
    finally:
        # Cleanup
        for f in [test_video, test_message, 'downloaded_video.mp4', 'extracted_message.txt']:
            if os.path.exists(f):
                os.remove(f)

if __name__ == '__main__':
    test_web_video_steganography()