#!/usr/bin/env python3
"""
Test script to verify the improved file naming functionality
Tests both hide and extract operations with meaningful filenames
"""

import requests
import time
import json
import os
from pathlib import Path

# Test configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_video_file_naming():
    """Test video steganography with improved file naming"""
    print("\n🎬 Testing Video File Naming...")
    
    # Create test files
    test_video = "test_sample.mp4"
    test_secret = "secret_document.txt"
    
    # Create a small test video file if it doesn't exist
    if not Path(test_video).exists():
        print(f"Creating test video file: {test_video}")
        # Create a minimal MP4 file (this is just for filename testing)
        with open(test_video, "wb") as f:
            f.write(b"fake_mp4_data_for_testing" * 100)
    
    # Create test secret file
    with open(test_secret, "w") as f:
        f.write("This is a secret document for testing file naming improvements!\n")
    
    password = "test123"
    
    try:
        # Test Hide Operation
        print("Testing hide operation with video...")
        with open(test_video, "rb") as vf, open(test_secret, "rb") as sf:
            files = {
                "container_file": (test_video, vf, "video/mp4"),
                "secret_file": (test_secret, sf, "text/plain")
            }
            data = {"password": password}
            
            response = requests.post(f"{BASE_URL}/hide", files=files, data=data)
            if response.status_code != 200:
                print(f"❌ Hide request failed: {response.text}")
                return
            
            job_data = response.json()
            job_id = job_data["job_id"]
            print(f"Hide job started: {job_id}")
            
            # Wait for completion
            for i in range(TIMEOUT):
                status_response = requests.get(f"{BASE_URL}/status/{job_id}")
                status = status_response.json()
                
                if status["status"] == "completed":
                    print(f"✅ Hide completed!")
                    print(f"Output filename should be: test_sample_stego.mp4")
                    break
                elif status["status"] == "failed":
                    print(f"❌ Hide failed: {status.get('message', 'Unknown error')}")
                    return
                
                time.sleep(1)
            
            # Download the result
            download_response = requests.get(f"{BASE_URL}/download/{job_id}")
            if download_response.status_code == 200:
                # Check the filename from Content-Disposition header
                content_disposition = download_response.headers.get('Content-Disposition', '')
                print(f"📁 Download header: {content_disposition}")
                
                # Save for extraction test
                output_filename = "downloaded_test_sample_stego.mp4"
                with open(output_filename, "wb") as f:
                    f.write(download_response.content)
                print(f"✅ Downloaded to: {output_filename}")
                
                # Test Extract Operation
                print("Testing extract operation...")
                with open(output_filename, "rb") as f:
                    files = {"container_file": (output_filename, f, "video/mp4")}
                    data = {"password": password}
                    
                    extract_response = requests.post(f"{BASE_URL}/extract", files=files, data=data)
                    if extract_response.status_code != 200:
                        print(f"❌ Extract request failed: {extract_response.text}")
                        return
                    
                    extract_job_data = extract_response.json()
                    extract_job_id = extract_job_data["job_id"]
                    print(f"Extract job started: {extract_job_id}")
                    
                    # Wait for extraction completion
                    for i in range(TIMEOUT):
                        extract_status_response = requests.get(f"{BASE_URL}/status/{extract_job_id}")
                        extract_status = extract_status_response.json()
                        
                        if extract_status["status"] == "completed":
                            print(f"✅ Extract completed!")
                            print(f"Extracted filename should preserve: secret_document.txt")
                            break
                        elif extract_status["status"] == "failed":
                            print(f"❌ Extract failed: {extract_status.get('message', 'Unknown error')}")
                            return
                        
                        time.sleep(1)
                    
                    # Download extracted file
                    extract_download_response = requests.get(f"{BASE_URL}/download/{extract_job_id}")
                    if extract_download_response.status_code == 200:
                        extract_content_disposition = extract_download_response.headers.get('Content-Disposition', '')
                        print(f"📁 Extract download header: {extract_content_disposition}")
                        
                        extracted_content = extract_download_response.content.decode()
                        print(f"📄 Extracted content: {extracted_content[:100]}...")
                        print("✅ Video file naming test completed successfully!")
                    else:
                        print(f"❌ Extract download failed: {extract_download_response.status_code}")
            else:
                print(f"❌ Download failed: {download_response.status_code}")
    
    finally:
        # Cleanup
        for file in [test_video, test_secret, "downloaded_test_sample_stego.mp4"]:
            if Path(file).exists():
                os.remove(file)

def test_text_message_naming():
    """Test text message steganography with improved file naming"""
    print("\n📝 Testing Text Message File Naming...")
    
    # Create test image
    test_image = "test_image.png"
    
    # Create a small test image file if it doesn't exist
    if not Path(test_image).exists():
        print(f"Creating test image file: {test_image}")
        with open(test_image, "wb") as f:
            f.write(b"fake_png_data_for_testing" * 100)
    
    password = "test123"
    text_message = "This is a secret text message for testing!"
    
    try:
        # Test Hide Text Message
        print("Testing hide text message...")
        with open(test_image, "rb") as f:
            files = {"container_file": (test_image, f, "image/png")}
            data = {"password": password, "text_message": text_message}
            
            response = requests.post(f"{BASE_URL}/hide", files=files, data=data)
            if response.status_code != 200:
                print(f"❌ Hide request failed: {response.text}")
                return
            
            job_data = response.json()
            job_id = job_data["job_id"]
            print(f"Hide text job started: {job_id}")
            
            # Wait for completion
            for i in range(TIMEOUT):
                status_response = requests.get(f"{BASE_URL}/status/{job_id}")
                status = status_response.json()
                
                if status["status"] == "completed":
                    print(f"✅ Text hide completed!")
                    print(f"Output filename should be: test_image_stego.png")
                    break
                elif status["status"] == "failed":
                    print(f"❌ Text hide failed: {status.get('message', 'Unknown error')}")
                    return
                
                time.sleep(1)
            
            # Download and test extract
            download_response = requests.get(f"{BASE_URL}/download/{job_id}")
            if download_response.status_code == 200:
                content_disposition = download_response.headers.get('Content-Disposition', '')
                print(f"📁 Text hide download header: {content_disposition}")
                
                # Save for extraction test
                output_filename = "downloaded_test_image_stego.png"
                with open(output_filename, "wb") as f:
                    f.write(download_response.content)
                
                # Extract text message
                print("Testing extract text message...")
                with open(output_filename, "rb") as f:
                    files = {"container_file": (output_filename, f, "image/png")}
                    data = {"password": password}
                    
                    extract_response = requests.post(f"{BASE_URL}/extract", files=files, data=data)
                    if extract_response.status_code != 200:
                        print(f"❌ Extract request failed: {extract_response.text}")
                        return
                    
                    extract_job_data = extract_response.json()
                    extract_job_id = extract_job_data["job_id"]
                    
                    # Wait for extraction completion
                    for i in range(TIMEOUT):
                        extract_status_response = requests.get(f"{BASE_URL}/status/{extract_job_id}")
                        extract_status = extract_status_response.json()
                        
                        if extract_status["status"] == "completed":
                            print(f"✅ Text extract completed!")
                            print(f"Extracted filename should be: secret_message.txt")
                            break
                        elif extract_status["status"] == "failed":
                            print(f"❌ Text extract failed: {extract_status.get('message', 'Unknown error')}")
                            return
                        
                        time.sleep(1)
                    
                    # Download extracted text
                    extract_download_response = requests.get(f"{BASE_URL}/download/{extract_job_id}")
                    if extract_download_response.status_code == 200:
                        extract_content_disposition = extract_download_response.headers.get('Content-Disposition', '')
                        print(f"📁 Text extract download header: {extract_content_disposition}")
                        
                        extracted_content = extract_download_response.content.decode()
                        print(f"📄 Extracted text content: {extracted_content}")
                        
                        if text_message in extracted_content:
                            print("✅ Text message file naming test completed successfully!")
                        else:
                            print("❌ Extracted text doesn't match original")
                    else:
                        print(f"❌ Text extract download failed: {extract_download_response.status_code}")
            else:
                print(f"❌ Text hide download failed: {download_response.status_code}")
    
    finally:
        # Cleanup
        for file in [test_image, "downloaded_test_image_stego.png"]:
            if Path(file).exists():
                os.remove(file)

def main():
    """Run all file naming tests"""
    print("🧪 Testing Improved File Naming Functionality")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print("❌ Server is not running or not accessible")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return
    
    print("✅ Server is running")
    
    # Run tests
    test_video_file_naming()
    test_text_message_naming()
    
    print("\n" + "=" * 50)
    print("🎉 File naming improvement tests completed!")

if __name__ == "__main__":
    main()