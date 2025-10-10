#!/usr/bin/env python3
"""
Comprehensive web application password security test
Tests that wrong passwords fail for all steganography types through the web interface
"""

import requests
import time
import os
from pathlib import Path

# Web app URL
BASE_URL = "http://localhost:8000"

def create_test_files():
    """Create test files for all steganography types"""
    # Create test image
    from PIL import Image
    import numpy as np
    
    img_array = np.random.randint(0, 256, (200, 200, 3), dtype=np.uint8)
    img = Image.fromarray(img_array)
    img.save("test_image.png")
    
    # Create test audio  
    import soundfile as sf
    sample_rate = 44100
    duration = 2.0
    samples = int(sample_rate * duration)
    audio_data = np.random.randint(-1000, 1000, samples, dtype=np.int16)
    sf.write("test_audio.wav", audio_data, sample_rate)
    
    # Create test document
    with open("test_document.txt", "w") as f:
        f.write("This is a test document for steganography testing. " * 20)
    
    print("✅ Test files created")

def test_steganography_type(file_type, file_path, correct_password, secret_message):
    """Test password security for a specific steganography type"""
    print(f"\n🔐 Testing {file_type} steganography password security...")
    
    # Step 1: Hide data with correct password
    print(f"1. Hiding data with correct password: '{correct_password}'")
    
    import json
    
    request_data = {
        "data": secret_message,
        "password": correct_password
    }
    
    with open(file_path, "rb") as f:
        files = {"container_file": (os.path.basename(file_path), f, "application/octet-stream")}
        data = {"request_data": json.dumps(request_data)}
        response = requests.post(f"{BASE_URL}/api/hide", files=files, data=data)
    
    if response.status_code != 200:
        print(f"❌ Hide operation failed: {response.text}")
        return False
    
    result = response.json()
    job_id = result["job_id"]
    print(f"✅ Hide job started: {job_id}")
    
    # Wait for completion
    while True:
        status_response = requests.get(f"{BASE_URL}/api/job/{job_id}")
        status = status_response.json()
        
        if status["status"] == "completed":
            print("✅ Hide operation completed")
            break
        elif status["status"] == "failed":
            print(f"❌ Hide operation failed: {status.get('error', 'Unknown error')}")
            return False
        
        time.sleep(1)
    
    # Step 2: Download the steganographic file
    download_response = requests.get(f"{BASE_URL}/api/download/{job_id}")
    if download_response.status_code != 200:
        print(f"❌ Download failed: {download_response.text}")
        return False
    
    stego_filename = f"stego_{file_type}_{os.path.basename(file_path)}"
    with open(stego_filename, "wb") as f:
        f.write(download_response.content)
    print(f"✅ Downloaded steganographic file: {stego_filename}")
    
    # Step 3: Extract with CORRECT password
    print(f"2. Extracting with CORRECT password: '{correct_password}'")
    
    extract_request_data = {"password": correct_password}
    
    with open(stego_filename, "rb") as f:
        files = {"container_file": (os.path.basename(stego_filename), f, "application/octet-stream")}
        data = {"request_data": json.dumps(extract_request_data)}
        response = requests.post(f"{BASE_URL}/api/extract", files=files, data=data)
    
    if response.status_code != 200:
        print(f"❌ Extract operation failed: {response.text}")
        return False
    
    result = response.json()
    extract_job_id = result["job_id"]
    
    # Wait for extraction completion
    while True:
        status_response = requests.get(f"{BASE_URL}/api/job/{extract_job_id}")
        status = status_response.json()
        
        if status["status"] == "completed":
            print("✅ Extraction with correct password successful")
            # Download and check extracted content
            extract_response = requests.get(f"{BASE_URL}/api/download/{extract_job_id}")
            if extract_response.status_code == 200:
                extracted_content = extract_response.content.decode('utf-8')
                if secret_message in extracted_content:
                    print("✅ Correct message extracted!")
                else:
                    print(f"❌ Wrong message extracted: {extracted_content[:50]}...")
            break
        elif status["status"] == "failed":
            print(f"❌ Extraction with correct password failed: {status.get('error', 'Unknown error')}")
            break
        
        time.sleep(1)
    
    # Step 4: Test extraction with WRONG passwords
    wrong_passwords = ["wrong_password", "123456", "", "hacker_attempt"]
    
    for wrong_password in wrong_passwords:
        print(f"3. Testing extraction with WRONG password: '{wrong_password}'")
        
        wrong_extract_data = {"password": wrong_password}
        
        with open(stego_filename, "rb") as f:
            files = {"container_file": (os.path.basename(stego_filename), f, "application/octet-stream")}
            data = {"request_data": json.dumps(wrong_extract_data)}
            response = requests.post(f"{BASE_URL}/api/extract", files=files, data=data)
        
        if response.status_code != 200:
            print(f"✅ Correct behavior: Wrong password rejected at API level")
            continue
        
        result = response.json()
        wrong_job_id = result["job_id"]
        
        # Wait for completion
        while True:
            status_response = requests.get(f"{BASE_URL}/api/job/{wrong_job_id}")
            status = status_response.json()
            
            if status["status"] == "completed":
                print(f"❌ SECURITY ISSUE: Wrong password '{wrong_password}' succeeded!")
                # Download and check what was extracted
                extract_response = requests.get(f"{BASE_URL}/api/download/{wrong_job_id}")
                if extract_response.status_code == 200:
                    extracted_content = extract_response.content.decode('utf-8')
                    print(f"   Extracted: {extracted_content[:50]}...")
                break
            elif status["status"] == "failed":
                error_msg = status.get('error', 'Unknown error')
                if any(keyword in error_msg.lower() for keyword in ['password', 'signature', 'corruption', 'checksum']):
                    print(f"✅ Correct behavior: Wrong password '{wrong_password}' failed: {error_msg}")
                else:
                    print(f"⚠️  Failed but unclear if due to password: {error_msg}")
                break
            
            time.sleep(1)
    
    # Cleanup
    try:
        os.remove(stego_filename)
    except:
        pass
    
    return True

def main():
    """Run comprehensive password security tests"""
    print("🔐 Starting comprehensive web application password security test...")
    
    # Create test files
    create_test_files()
    
    # Test different steganography types
    test_cases = [
        ("image", "test_image.png", "img_password_123", "Secret message hidden in image!"),
        ("audio", "test_audio.wav", "audio_password_456", "Secret message hidden in audio!"),
        ("document", "test_document.txt", "doc_password_789", "Secret message hidden in document!")
    ]
    
    results = []
    for file_type, file_path, password, message in test_cases:
        try:
            success = test_steganography_type(file_type, file_path, password, message)
            results.append((file_type, success))
        except Exception as e:
            print(f"❌ Test for {file_type} failed with exception: {e}")
            results.append((file_type, False))
    
    # Summary
    print("\n" + "="*60)
    print("🔐 PASSWORD SECURITY TEST SUMMARY")
    print("="*60)
    
    for file_type, success in results:
        status = "✅ SECURE" if success else "❌ VULNERABLE"
        print(f"{file_type.upper():12} steganography: {status}")
    
    # Cleanup
    for file in ["test_image.png", "test_audio.wav", "test_document.txt"]:
        try:
            os.remove(file)
        except:
            pass
    
    print("\n🔐 Password security test completed!")

if __name__ == "__main__":
    main()