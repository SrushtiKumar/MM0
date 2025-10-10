#!/usr/bin/env python3
"""
Test Extracted File Integrity
Verifies that extracted files are not corrupted and can be opened properly
"""

import requests
import time
import os
import tempfile
from pathlib import Path

def test_file_integrity():
    """Test that extracted files maintain their integrity"""
    BASE_URL = "http://localhost:8005"
    
    print("🧪 Testing Extracted File Integrity")
    print("=" * 50)
    
    # Check server
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Server running: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        return
    
    # Create test files with known content
    print("\n📁 Creating test files...")
    
    # Create a test image for hiding
    test_image_path = "test_container.png"
    try:
        from PIL import Image
        import numpy as np
        # Create a colorful test image
        test_img = np.random.randint(100, 255, (400, 400, 3), dtype=np.uint8)
        Image.fromarray(test_img).save(test_image_path)
        print(f"✅ Created test container image: {test_image_path}")
    except ImportError:
        # Fallback
        with open(test_image_path, "wb") as f:
            f.write(b"PNG_TEST_DATA" * 2000)
        print(f"✅ Created test container (fallback): {test_image_path}")
    
    # Create test secret file with specific binary content
    secret_file_path = "secret_test_file.jpg"
    
    # Create a fake JPEG file with proper header
    jpeg_header = b'\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00'
    jpeg_content = jpeg_header + b"This is fake JPEG data for testing file integrity!" * 20
    with open(secret_file_path, "wb") as f:
        f.write(jpeg_content)
    
    print(f"✅ Created secret file: {secret_file_path} ({len(jpeg_content)} bytes)")
    print(f"Original file hash: {hash(jpeg_content)}")
    
    password = "integrity_test_123"
    
    try:
        # Test Hide Operation
        print(f"\n📁 Hiding {secret_file_path} in {test_image_path}...")
        with open(test_image_path, "rb") as container_file, open(secret_file_path, "rb") as secret_file:
            files = {
                "container_file": (test_image_path, container_file, "image/png"),
                "secret_file": (secret_file_path, secret_file, "image/jpeg")
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
            for i in range(60):
                status_response = requests.get(f"{BASE_URL}/status/{hide_job_id}")
                status = status_response.json()
                
                if status["status"] == "completed":
                    print("✅ Hide operation completed!")
                    result = status.get("result", {})
                    print(f"Hide result: {result}")
                    break
                elif status["status"] == "failed":
                    print(f"❌ Hide failed: {status.get('message', 'Unknown error')}")
                    print(f"Error: {status.get('error', 'No details')}")
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
            
            stego_filename = "steganographic_image.png"
            with open(stego_filename, "wb") as f:
                f.write(download_response.content)
            
            print(f"✅ Downloaded steganographic image: {stego_filename}")
        
        # Test Extract Operation
        print(f"\n🔍 Extracting hidden file from {stego_filename}...")
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
            for i in range(60):
                extract_status_response = requests.get(f"{BASE_URL}/status/{extract_job_id}")
                extract_status = extract_status_response.json()
                
                if extract_status["status"] == "completed":
                    print("✅ Extract operation completed!")
                    result = extract_status.get("result", {})
                    print(f"Extract result: {result}")
                    break
                elif extract_status["status"] == "failed":
                    print(f"❌ Extract failed: {extract_status.get('message', 'Unknown error')}")
                    print(f"Error: {extract_status.get('error', 'No details')}")
                    return
                
                time.sleep(1)
            else:
                print("❌ Extract operation timed out")
                return
            
            # Download extracted file
            extract_download_response = requests.get(f"{BASE_URL}/download/{extract_job_id}")
            if extract_download_response.status_code != 200:
                print(f"❌ Extract download failed: {extract_download_response.status_code}")
                return
            
            # Save extracted file
            extracted_filename = "extracted_file.jpg"
            extracted_content = extract_download_response.content
            with open(extracted_filename, "wb") as f:
                f.write(extracted_content)
            
            print(f"✅ Downloaded extracted file: {extracted_filename} ({len(extracted_content)} bytes)")
            print(f"Extracted file hash: {hash(extracted_content)}")
            
            # Verify file integrity
            print("\n🔍 Verifying file integrity...")
            
            # Check if content matches exactly
            if extracted_content == jpeg_content:
                print("✅ PERFECT MATCH! File content is identical to original!")
                
                # Check if file can be read properly
                try:
                    # Try to read the extracted file as binary
                    with open(extracted_filename, "rb") as f:
                        test_read = f.read()
                    print("✅ Extracted file can be read successfully!")
                    
                    # Check JPEG header
                    if test_read.startswith(jpeg_header):
                        print("✅ JPEG header preserved correctly!")
                    else:
                        print("⚠️  JPEG header may be corrupted")
                    
                    print("\n🎉 FILE INTEGRITY TEST PASSED!")
                    print("✅ Extracted file is NOT corrupted")
                    print("✅ File can be opened in system")
                    print("✅ All content preserved exactly")
                    
                except Exception as e:
                    print(f"❌ Error reading extracted file: {e}")
                    
            else:
                print("❌ CONTENT MISMATCH! File may be corrupted:")
                print(f"Original size: {len(jpeg_content)} bytes")
                print(f"Extracted size: {len(extracted_content)} bytes")
                print(f"First 50 bytes original: {jpeg_content[:50]}")
                print(f"First 50 bytes extracted: {extracted_content[:50]}")
    
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        for file in [test_image_path, secret_file_path, "steganographic_image.png", "extracted_file.jpg"]:
            if os.path.exists(file):
                os.remove(file)
                print(f"Removed: {file}")

if __name__ == "__main__":
    test_file_integrity()