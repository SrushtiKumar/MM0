#!/usr/bin/env python3
"""
Quick test for audio vulnerability after fix
"""

import requests
import json
import time
import os
import numpy as np
import soundfile as sf

BASE_URL = "http://localhost:8000"

def create_test_audio():
    """Create test audio"""
    sample_rate = 44100
    duration = 2.0
    samples = int(sample_rate * duration)
    audio_data = np.random.randint(-1000, 1000, samples, dtype=np.int16)
    sf.write("quick_test_audio.wav", audio_data, sample_rate)
    return "quick_test_audio.wav"

def test_audio_after_fix():
    """Test audio vulnerability after password fix"""
    print("🔍 Testing audio vulnerability after password fix...")
    
    audio_file = create_test_audio()
    correct_password = "test_audio_password_123"
    secret_message = "SECRET AUDIO MESSAGE"
    
    # Hide with correct password
    print(f"1. Hiding with password: '{correct_password}'")
    request_data = {"data": secret_message, "password": correct_password}
    
    with open(audio_file, "rb") as f:
        files = {"container_file": (os.path.basename(audio_file), f, "application/octet-stream")}
        data = {"request_data": json.dumps(request_data)}
        response = requests.post(f"{BASE_URL}/api/hide", files=files, data=data)
    
    if response.status_code != 200:
        print(f"❌ Hide failed: {response.text}")
        return
    
    job_id = response.json()["job_id"]
    
    # Wait for completion
    while True:
        status_response = requests.get(f"{BASE_URL}/api/job/{job_id}")
        status = status_response.json()
        if status["status"] == "completed":
            break
        elif status["status"] == "failed":
            print(f"❌ Hide failed: {status.get('error')}")
            return
        time.sleep(0.5)
    
    # Download steganographic file
    download_response = requests.get(f"{BASE_URL}/api/download/{job_id}")
    if download_response.status_code != 200:
        print(f"❌ Download failed")
        return
    
    with open("stego_audio_test.wav", "wb") as f:
        f.write(download_response.content)
    
    print(f"✅ Hide completed successfully")
    
    # Test wrong password
    print(f"2. Testing wrong password: 'WRONG_PASSWORD'")
    extract_data = {"password": "WRONG_PASSWORD"}
    
    with open("stego_audio_test.wav", "rb") as f:
        files = {"container_file": ("stego_audio_test.wav", f, "application/octet-stream")}
        data = {"request_data": json.dumps(extract_data)}
        response = requests.post(f"{BASE_URL}/api/extract", files=files, data=data)
    
    if response.status_code != 200:
        print(f"✅ Wrong password rejected at API level")
        return
    
    extract_job_id = response.json()["job_id"]
    
    # Wait for extraction
    while True:
        status_response = requests.get(f"{BASE_URL}/api/job/{extract_job_id}")
        status = status_response.json()
        
        if status["status"] == "completed":
            print(f"❌ VULNERABILITY STILL EXISTS! Wrong password succeeded!")
            
            # Try to download extracted data
            extract_response = requests.get(f"{BASE_URL}/api/download/{extract_job_id}")
            if extract_response.status_code == 200:
                extracted_content = extract_response.content.decode('utf-8', errors='ignore')
                print(f"   Extracted: {extracted_content}")
                if secret_message in extracted_content:
                    print(f"❌ CRITICAL: Original secret message extracted!")
            break
            
        elif status["status"] == "failed":
            error_msg = status.get('error', 'Unknown error')
            print(f"✅ FIXED! Wrong password correctly failed: {error_msg}")
            break
        
        time.sleep(0.5)
    
    # Test correct password
    print(f"3. Testing correct password: '{correct_password}'")
    extract_data = {"password": correct_password}
    
    with open("stego_audio_test.wav", "rb") as f:
        files = {"container_file": ("stego_audio_test.wav", f, "application/octet-stream")}
        data = {"request_data": json.dumps(extract_data)}
        response = requests.post(f"{BASE_URL}/api/extract", files=files, data=data)
    
    extract_job_id = response.json()["job_id"]
    
    while True:
        status_response = requests.get(f"{BASE_URL}/api/job/{extract_job_id}")
        status = status_response.json()
        
        if status["status"] == "completed":
            print(f"✅ Correct password works!")
            break
        elif status["status"] == "failed":
            print(f"⚠️  Correct password failed: {status.get('error')}")
            break
        time.sleep(0.5)
    
    # Cleanup
    for file in ["quick_test_audio.wav", "stego_audio_test.wav"]:
        try:
            os.remove(file)
        except:
            pass

if __name__ == "__main__":
    test_audio_after_fix()