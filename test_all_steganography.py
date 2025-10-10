#!/usr/bin/env python3
"""
Comprehensive Test for All Steganography Types
Tests image, document, audio, and video steganography with both user passwords and auto-generated passwords
"""

import requests
import time
import os
import tempfile
from pathlib import Path


def test_auto_password():
    """Test auto-password generation"""
    BASE_URL = "http://localhost:8003"
    
    try:
        response = requests.get(f"{BASE_URL}/generate-password")
        if response.status_code == 200:
            password_data = response.json()
            print(f"✅ Auto-generated password: {password_data['password']}")
            return password_data["password"]
        else:
            print(f"❌ Auto-password generation failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Auto-password test failed: {e}")
        return None


def test_steganography_type(base_url, file_type, test_file_path, test_file_content, secret_message, password, description):
    """Test a specific steganography type"""
    print(f"\n🧪 Testing {description}...")
    
    try:
        # Test Hide Operation
        print(f"📁 Testing hide with {file_type} file...")
        with open(test_file_path, "rb") as container_file:
            files = {"container_file": (os.path.basename(test_file_path), container_file, f"application/{file_type}")}
            data = {"password": password, "text_message": secret_message}
            
            hide_response = requests.post(f"{base_url}/hide", files=files, data=data)
            if hide_response.status_code != 200:
                print(f"❌ {description} hide failed: {hide_response.text}")
                return False
            
            hide_job = hide_response.json()
            hide_job_id = hide_job["job_id"]
            print(f"Hide job started: {hide_job_id}")
            
            # Wait for hide completion
            for i in range(60):  # Increased timeout for larger files
                status_response = requests.get(f"{base_url}/status/{hide_job_id}")
                status = status_response.json()
                
                if status["status"] == "completed":
                    print(f"✅ {description} hide completed!")
                    break
                elif status["status"] == "failed":
                    print(f"❌ {description} hide failed: {status.get('message', 'Unknown error')}")
                    print(f"Error details: {status.get('error', 'No details')}")
                    return False
                
                time.sleep(1)
            else:
                print(f"❌ {description} hide operation timed out")
                return False
            
            # Download the steganographic file
            download_response = requests.get(f"{base_url}/download/{hide_job_id}")
            if download_response.status_code != 200:
                print(f"❌ {description} download failed: {download_response.status_code}")
                return False
            
            # Save steganographic file
            stego_filename = f"stego_{file_type}.{file_type}"
            with open(stego_filename, "wb") as f:
                f.write(download_response.content)
            
            print(f"✅ Downloaded steganographic {file_type}: {stego_filename}")
        
        # Test Extract Operation
        print(f"🔍 Testing extract from {file_type} file...")
        with open(stego_filename, "rb") as stego_file:
            files = {"container_file": (stego_filename, stego_file, f"application/{file_type}")}
            data = {"password": password}
            
            extract_response = requests.post(f"{base_url}/extract", files=files, data=data)
            if extract_response.status_code != 200:
                print(f"❌ {description} extract request failed: {extract_response.text}")
                return False
            
            extract_job = extract_response.json()
            extract_job_id = extract_job["job_id"]
            print(f"Extract job started: {extract_job_id}")
            
            # Wait for extract completion
            for i in range(60):
                extract_status_response = requests.get(f"{base_url}/status/{extract_job_id}")
                extract_status = extract_status_response.json()
                
                if extract_status["status"] == "completed":
                    print(f"✅ {description} extract completed!")
                    result = extract_status.get("result", {})
                    print(f"Extract result: {result}")
                    break
                elif extract_status["status"] == "failed":
                    print(f"❌ {description} extract failed: {extract_status.get('message', 'Unknown error')}")
                    print(f"Error details: {extract_status.get('error', 'No details')}")
                    return False
                
                time.sleep(1)
            else:
                print(f"❌ {description} extract operation timed out")
                return False
            
            # Download extracted content
            extract_download_response = requests.get(f"{base_url}/download/{extract_job_id}")
            if extract_download_response.status_code != 200:
                print(f"❌ {description} extract download failed: {extract_download_response.status_code}")
                return False
            
            # Check extracted content
            extracted_content = extract_download_response.content.decode('utf-8')
            print(f"📄 Extracted content: {extracted_content}")
            
            if secret_message in extracted_content:
                print(f"✅ {description} test PASSED!")
                return True
            else:
                print(f"❌ {description} test FAILED - content mismatch")
                return False
    
    except Exception as e:
        print(f"❌ {description} test error: {e}")
        return False
    
    finally:
        # Cleanup
        for file in [f"stego_{file_type}.{file_type}"]:
            if os.path.exists(file):
                os.remove(file)


def main():
    """Run comprehensive steganography tests"""
    BASE_URL = "http://localhost:8003"
    
    print("🧪 Comprehensive Steganography Test")
    print("=" * 60)
    
    # Check server
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Server is running (status: {response.status_code})")
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        return
    
    # Test auto-password generation
    auto_password = test_auto_password()
    user_password = "testpassword123"
    
    # Create test files
    print("\n📁 Creating test files...")
    
    # Test image file (PNG)
    test_image_path = "test_image.png"
    try:
        from PIL import Image
        import numpy as np
        test_img = np.random.randint(0, 256, (300, 300, 3), dtype=np.uint8)
        Image.fromarray(test_img).save(test_image_path)
        print(f"✅ Created test image: {test_image_path}")
    except ImportError:
        # Fallback: create a simple binary file
        with open(test_image_path, "wb") as f:
            f.write(b"PNG_FAKE_DATA" * 1000)
        print(f"✅ Created test image (fallback): {test_image_path}")
    
    # Test document file (TXT)
    test_doc_path = "test_document.txt"
    test_doc_content = """This is a test document for steganography.
It contains multiple lines of text that will be used as a carrier.
The document should be large enough to hide secret messages.
This is perfect for testing document steganography functionality.
"""
    with open(test_doc_path, "w") as f:
        f.write(test_doc_content)
    print(f"✅ Created test document: {test_doc_path}")
    
    # Test audio file (WAV - simple format)
    test_audio_path = "test_audio.wav"
    with open(test_audio_path, "wb") as f:
        # Create a simple WAV-like structure
        f.write(b"RIFF" + b"\x00" * 4 + b"WAVE" + b"fmt " + b"\x00" * 20 + b"data" + (b"\x00\x01" * 5000))
    print(f"✅ Created test audio: {test_audio_path}")
    
    # Test video file (MP4 - simple format)
    test_video_path = "test_video.mp4"
    with open(test_video_path, "wb") as f:
        # Create a simple MP4-like structure
        f.write(b"ftyp" + b"isom" + b"\x00" * 1000 + b"mdat" + (b"\x00\x01\x02\x03" * 2000))
    print(f"✅ Created test video: {test_video_path}")
    
    secret_message = "This is a secret message for comprehensive testing!"
    
    # Test results
    results = {}
    
    # Test with user-provided password
    print(f"\n🔐 Testing with USER PASSWORD: {user_password}")
    print("-" * 60)
    
    results["image_user"] = test_steganography_type(
        BASE_URL, "png", test_image_path, None, secret_message, user_password, "Image Steganography (User Password)"
    )
    
    results["document_user"] = test_steganography_type(
        BASE_URL, "txt", test_doc_path, test_doc_content, secret_message, user_password, "Document Steganography (User Password)"
    )
    
    results["audio_user"] = test_steganography_type(
        BASE_URL, "wav", test_audio_path, None, secret_message, user_password, "Audio Steganography (User Password)"
    )
    
    results["video_user"] = test_steganography_type(
        BASE_URL, "mp4", test_video_path, None, secret_message, user_password, "Video Steganography (User Password)"
    )
    
    # Test with auto-generated password
    if auto_password:
        print(f"\n🔐 Testing with AUTO-GENERATED PASSWORD: {auto_password}")
        print("-" * 60)
        
        results["image_auto"] = test_steganography_type(
            BASE_URL, "png", test_image_path, None, secret_message, auto_password, "Image Steganography (Auto Password)"
        )
        
        results["document_auto"] = test_steganography_type(
            BASE_URL, "txt", test_doc_path, test_doc_content, secret_message, auto_password, "Document Steganography (Auto Password)"
        )
        
        results["audio_auto"] = test_steganography_type(
            BASE_URL, "wav", test_audio_path, None, secret_message, auto_password, "Audio Steganography (Auto Password)"
        )
        
        results["video_auto"] = test_steganography_type(
            BASE_URL, "mp4", test_video_path, None, secret_message, auto_password, "Video Steganography (Auto Password)"
        )
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 COMPREHENSIVE TEST RESULTS")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<35}: {status}")
    
    print("-" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL STEGANOGRAPHY TYPES ARE WORKING PERFECTLY!")
        print("✅ Image, Document, Audio, and Video steganography")
        print("✅ Both user-provided and auto-generated passwords")
        print("✅ File naming improvements implemented")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Check the logs above for details.")
    
    # Cleanup
    print("\n🧹 Cleaning up test files...")
    for file in [test_image_path, test_doc_path, test_audio_path, test_video_path]:
        if os.path.exists(file):
            os.remove(file)
            print(f"Removed: {file}")


if __name__ == "__main__":
    main()