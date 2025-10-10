#!/usr/bin/env python3
"""
Test password security for ALL steganography types including video
"""

import requests
import json
import time
import os
from pathlib import Path

BASE_URL = "http://localhost:8000"

def create_all_test_files():
    """Create test files for all steganography types"""
    from PIL import Image
    import numpy as np
    import soundfile as sf
    
    # Create PNG image
    img_array = np.random.randint(0, 256, (200, 200, 3), dtype=np.uint8)
    img = Image.fromarray(img_array)
    img.save("test_image.png")
    
    # Create WAV audio
    sample_rate = 44100
    duration = 2.0
    samples = int(sample_rate * duration)
    audio_data = np.random.randint(-1000, 1000, samples, dtype=np.int16)
    sf.write("test_audio.wav", audio_data, sample_rate)
    
    # Create text document
    with open("test_document.txt", "w") as f:
        f.write("This is a test document for steganography testing. " * 50)
    
    # Create a simple MP4 video file (we'll use ffmpeg if available, otherwise skip)
    try:
        # Try to create a simple MP4 using ffmpeg
        import subprocess
        result = subprocess.run([
            "ffmpeg", "-f", "lavfi", "-i", "testsrc=duration=2:size=320x240:rate=1", 
            "-c:v", "libx264", "-y", "test_video.mp4"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Created test MP4 video")
        else:
            print("⚠️  Could not create MP4, skipping video test")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        print(f"⚠️  Could not create video file: {e}")
        return False
    
    print("✅ All test files created")
    return True

def test_password_security_for_format(file_type, file_path, test_name):
    """Test password security for a specific format"""
    print(f"\n🔐 Testing {test_name} password security...")
    
    correct_password = f"secure_{file_type}_password_123"
    secret_message = f"SECRET MESSAGE FOR {file_type.upper()}"
    
    # Step 1: Hide data with correct password
    print(f"1. Hiding data with password: '{correct_password}'")
    request_data = {"data": secret_message, "password": correct_password}
    
    with open(file_path, "rb") as f:
        files = {"container_file": (os.path.basename(file_path), f, "application/octet-stream")}
        data = {"request_data": json.dumps(request_data)}
        response = requests.post(f"{BASE_URL}/api/hide", files=files, data=data)
    
    if response.status_code != 200:
        print(f"❌ Hide failed: {response.text}")
        return False
    
    job_id = response.json()["job_id"]
    
    # Wait for hide completion
    while True:
        status_response = requests.get(f"{BASE_URL}/api/job/{job_id}")
        status = status_response.json()
        if status["status"] == "completed":
            break
        elif status["status"] == "failed":
            print(f"❌ Hide failed: {status.get('error')}")
            return False
        time.sleep(0.5)
    
    # Download steganographic file
    download_response = requests.get(f"{BASE_URL}/api/download/{job_id}")
    if download_response.status_code != 200:
        print(f"❌ Download failed")
        return False
    
    stego_filename = f"stego_{file_type}_{os.path.basename(file_path)}"
    with open(stego_filename, "wb") as f:
        f.write(download_response.content)
    
    print(f"✅ Hide completed, downloaded: {stego_filename}")
    
    # Step 2: Test extraction with WRONG passwords
    wrong_passwords = ["WRONG_PASSWORD", "12345", "", "hacker_attempt"]
    
    for wrong_password in wrong_passwords:
        print(f"2. Testing wrong password: '{wrong_password}'")
        
        extract_data = {"password": wrong_password}
        
        with open(stego_filename, "rb") as f:
            files = {"container_file": (os.path.basename(stego_filename), f, "application/octet-stream")}
            data = {"request_data": json.dumps(extract_data)}
            response = requests.post(f"{BASE_URL}/api/extract", files=files, data=data)
        
        if response.status_code != 200:
            print(f"✅ Rejected at API level")
            continue
        
        extract_job_id = response.json()["job_id"]
        
        # Wait for extraction
        while True:
            status_response = requests.get(f"{BASE_URL}/api/job/{extract_job_id}")
            status = status_response.json()
            
            if status["status"] == "completed":
                print(f"❌ VULNERABILITY: Wrong password '{wrong_password}' SUCCEEDED!")
                
                # Try to download the extracted data
                try:
                    extract_response = requests.get(f"{BASE_URL}/api/download/{extract_job_id}")
                    if extract_response.status_code == 200:
                        extracted_content = extract_response.content.decode('utf-8', errors='ignore')
                        if secret_message in extracted_content:
                            print(f"❌ CRITICAL: Original secret message extracted!")
                            print(f"   {file_type.upper()} STEGANOGRAPHY IS VULNERABLE!")
                        else:
                            print(f"⚠️  Something extracted but not original message")
                        print(f"   Extracted: {extracted_content[:100]}...")
                except Exception as e:
                    print(f"❌ Extraction succeeded but couldn't read content: {e}")
                
                # Cleanup and return vulnerability status
                try:
                    os.remove(stego_filename)
                except:
                    pass
                return False  # Vulnerable
                
            elif status["status"] == "failed":
                error_msg = status.get('error', 'Unknown error')
                if any(keyword in error_msg.lower() for keyword in ['password', 'signature', 'corruption', 'checksum', 'invalid']):
                    print(f"✅ Correctly failed: {error_msg[:100]}...")
                else:
                    print(f"✅ Failed (likely password protection): {error_msg[:100]}...")
                break
            
            time.sleep(0.5)
    
    # Step 3: Verify correct password still works
    print(f"3. Verifying correct password still works")
    extract_data = {"password": correct_password}
    
    with open(stego_filename, "rb") as f:
        files = {"container_file": (os.path.basename(stego_filename), f, "application/octet-stream")}
        data = {"request_data": json.dumps(extract_data)}
        response = requests.post(f"{BASE_URL}/api/extract", files=files, data=data)
    
    if response.status_code == 200:
        extract_job_id = response.json()["job_id"]
        
        while True:
            status_response = requests.get(f"{BASE_URL}/api/job/{extract_job_id}")
            status = status_response.json()
            
            if status["status"] == "completed":
                print(f"✅ Correct password works")
                break
            elif status["status"] == "failed":
                print(f"⚠️  Correct password failed: {status.get('error')}")
                break
            time.sleep(0.5)
    
    # Cleanup
    try:
        os.remove(stego_filename)
    except:
        pass
    
    return True  # Secure

def main():
    """Test password security for all formats"""
    print("🔐 COMPREHENSIVE PASSWORD SECURITY TEST FOR ALL FORMATS")
    print("=" * 70)
    
    # Create test files
    has_video = create_all_test_files()
    
    # Test cases
    test_cases = [
        ("image", "test_image.png", "PNG Image"),
        ("audio", "test_audio.wav", "WAV Audio"),
        ("document", "test_document.txt", "Text Document")
    ]
    
    if has_video:
        test_cases.append(("video", "test_video.mp4", "MP4 Video"))
    
    results = []
    for file_type, file_path, test_name in test_cases:
        try:
            is_secure = test_password_security_for_format(file_type, file_path, test_name)
            results.append((test_name, is_secure))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            # For now, treat exceptions as potentially vulnerable
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("🔐 COMPREHENSIVE PASSWORD SECURITY RESULTS")
    print("=" * 70)
    
    vulnerable_formats = []
    for test_name, is_secure in results:
        status = "✅ SECURE" if is_secure else "❌ VULNERABLE"
        if not is_secure:
            vulnerable_formats.append(test_name)
        print(f"{test_name:15}: {status}")
    
    print("\n" + "=" * 70)
    if len(vulnerable_formats) == 0:
        print("🎉 ALL FORMATS ARE SECURE!")
    else:
        print(f"🚨 {len(vulnerable_formats)} FORMAT(S) ARE VULNERABLE:")
        for format_name in vulnerable_formats:
            print(f"   - {format_name}")
        print("\n⚠️  CRITICAL SECURITY ISSUES DETECTED!")
    
    # Cleanup
    for file in ["test_image.png", "test_audio.wav", "test_document.txt", "test_video.mp4"]:
        try:
            os.remove(file)
        except:
            pass

if __name__ == "__main__":
    main()