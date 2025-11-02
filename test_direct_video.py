#!/usr/bin/env python3
"""
Direct test of video steganography with encryption
"""

import os
from final_video_steganography import FinalVideoSteganographyManager

def test_video_encryption():
    print("=== Testing Video Steganography with Encryption ===\n")
    
    # Test parameters
    video_path = "comprehensive_test_video.mp4"  # Use existing video
    password = "test123"
    secret_message = "X"  # Simple test message
    
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return False
    
    print(f"Using video: {video_path}")
    print(f"Password: '{password}'")
    print(f"Message: '{secret_message}'")
    
    # Create manager with password
    manager = FinalVideoSteganographyManager(password=password)
    print(f"✅ Created manager with password")
    
    # Test embedding
    print(f"\n1. Embedding message...")
    result = manager.hide_data(
        video_path=video_path,
        payload=secret_message,
        output_path="test_video_encrypted.avi",
        is_file=False
    )
    
    if not result.get('success'):
        print(f"❌ Embedding failed: {result.get('error')}")
        return False
    
    output_path = result['output_path']
    print(f"✅ File embedded successfully in: {output_path}")
    
    # Test extraction with correct password
    print(f"\n2. Extracting with correct password...")
    extracted_result = manager.extract_data(output_path)
    
    if extracted_result is None:
        print(f"❌ ERROR: Extraction returned None")
        return False
    
    extracted_data, filename = extracted_result
    if extracted_data is None:
        print(f"❌ ERROR: No data extracted")
        return False
    
    try:
        extracted_message = extracted_data.decode('utf-8')
        print(f"✅ Extracted message: '{extracted_message}'")
        
        if extracted_message == secret_message:
            print(f"✅ SUCCESS: Messages match!")
            return True
        else:
            print(f"❌ ERROR: Messages don't match")
            print(f"   Expected: '{secret_message}'")
            print(f"   Got:      '{extracted_message}'")
            return False
    except Exception as e:
        print(f"❌ ERROR: Could not decode extracted data: {e}")
        print(f"   Raw data: {extracted_data}")
        return False

def test_video_without_password():
    print("\n=== Testing Video Steganography WITHOUT Encryption ===\n")
    
    # Test parameters
    video_path = "comprehensive_test_video.mp4"  # Use existing video
    secret_message = "Y"  # Simple test message
    
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return False
    
    print(f"Using video: {video_path}")
    print(f"Message: '{secret_message}'")
    
    # Create manager without password
    manager = FinalVideoSteganographyManager(password="")
    print(f"✅ Created manager without password")
    
    # Test embedding
    print(f"\n1. Embedding message...")
    result = manager.hide_data(
        video_path=video_path,
        payload=secret_message,
        output_path="test_video_no_password.avi",
        is_file=False
    )
    
    if not result.get('success'):
        print(f"❌ Embedding failed: {result.get('error')}")
        return False
    
    output_path = result['output_path']
    print(f"✅ File embedded successfully in: {output_path}")
    
    # Test extraction
    print(f"\n2. Extracting...")
    extracted_result = manager.extract_data(output_path)
    
    if extracted_result is None:
        print(f"❌ ERROR: Extraction returned None")
        return False
    
    extracted_data, filename = extracted_result
    if extracted_data is None:
        print(f"❌ ERROR: No data extracted")
        return False
    
    try:
        extracted_message = extracted_data.decode('utf-8')
        print(f"✅ Extracted message: '{extracted_message}'")
        
        if extracted_message == secret_message:
            print(f"✅ SUCCESS: Messages match!")
            return True
        else:
            print(f"❌ ERROR: Messages don't match")
            return False
    except Exception as e:
        print(f"❌ ERROR: Could not decode extracted data: {e}")
        return False

if __name__ == "__main__":
    success1 = test_video_encryption()
    success2 = test_video_without_password()
    
    print(f"\n" + "="*50)
    print(f"VIDEO STEGANOGRAPHY TEST RESULTS:")
    print(f"  With encryption: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"  Without encryption: {'✅ PASS' if success2 else '❌ FAIL'}")
    print(f"="*50)