#!/usr/bin/env python3
"""
Direct test of video steganography manager with API-like paths
"""

import os
from final_video_steganography import FinalVideoSteganographyManager

def test_video_with_api_paths():
    """Test video steganography with paths similar to API"""
    
    print("=== Testing Video Manager with API-style paths ===")
    
    # Simulate API paths
    video_path = "comprehensive_test_video.mp4"
    output_path = "outputs/test_api_style_video.mp4"  # API-style path
    password = "test123"
    secret_message = "API_TEST_MESSAGE"
    
    # Create outputs directory if it doesn't exist
    os.makedirs("outputs", exist_ok=True)
    
    print(f"Input video: {video_path}")
    print(f"Expected output: {output_path}")
    print(f"Password: {password}")
    print(f"Message: {secret_message}")
    
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return False
    
    # Create manager with password
    manager = FinalVideoSteganographyManager(password=password)
    print(f"✅ Created manager")
    
    # Test embedding with API-style parameters
    print(f"\n1. Testing embedding...")
    result = manager.hide_data(
        video_path=video_path,
        payload=secret_message,
        output_path=output_path,  # This should be .mp4 but create .avi
        is_file=False,
        original_filename=None
    )
    
    print(f"Embed result: {result}")
    
    if not result.get('success'):
        print(f"❌ Embedding failed: {result.get('error')}")
        return False
    
    actual_output_path = result.get('output_path', output_path)
    print(f"✅ Embedding succeeded")
    print(f"Actual output path: {actual_output_path}")
    print(f"Expected output exists: {os.path.exists(output_path)}")
    print(f"Actual output exists: {os.path.exists(actual_output_path)}")
    
    # List files to see what was created
    print(f"\nFiles in outputs directory:")
    if os.path.exists("outputs"):
        for file in os.listdir("outputs"):
            if "test_api_style" in file:
                filepath = os.path.join("outputs", file)
                print(f"  {file} ({os.path.getsize(filepath)} bytes)")
    
    # Test extraction
    print(f"\n2. Testing extraction...")
    extracted_result = manager.extract_data(actual_output_path)
    
    if extracted_result is None:
        print(f"❌ Extraction returned None")
        return False
    
    extracted_data, filename = extracted_result
    if extracted_data is None:
        print(f"❌ No data extracted")
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
    success = test_video_with_api_paths()
    print(f"\n" + "="*50)
    print(f"VIDEO MANAGER API-STYLE TEST: {'✅ PASS' if success else '❌ FAIL'}")
    print(f"="*50)