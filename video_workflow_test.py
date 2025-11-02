#!/usr/bin/env python3
"""
Video steganography workflow test: Embed image in video, then extract it
"""

import os
import requests
import time
from pathlib import Path

# Configuration
API_BASE = "http://localhost:8000"
TEST_DIR = Path(__file__).parent

def test_video_workflow():
    """Test the complete video embed -> extract workflow"""
    
    print("🧪 Testing Video Steganography Workflow...")
    
    # Use our test files
    carrier_video = "clean_carrier.mp4"
    test_image = "debug_embedded.png"
    password = "testpass123"
    
    if not Path(carrier_video).exists():
        print(f"❌ Carrier video not found: {carrier_video}")
        return False
        
    if not Path(test_image).exists():
        print(f"❌ Test image not found: {test_image}")
        return False
        
    print(f"📹 Using carrier video: {carrier_video}")
    print(f"🖼️  Using test image: {test_image}")
    print(f"🔐 Using password: {password}")
    
    # Get original image info
    with open(test_image, 'rb') as f:
        original_image_data = f.read()
    print(f"📊 Original image size: {len(original_image_data)} bytes")
    
    # Step 1: Embed image in video
    print("\n🔐 Step 1: Embedding image in video...")
    
    with open(carrier_video, 'rb') as carrier_f, open(test_image, 'rb') as content_f:
        embed_data = {
            'password': password,
            'output_format': 'auto',
            'carrier_type': 'video',
            'content_type': 'file'
        }
        embed_files = {
            'carrier_file': (carrier_video, carrier_f, 'video/mp4'),
            'content_file': (test_image, content_f, 'image/png')
        }
        
        response = requests.post(f"{API_BASE}/api/embed", data=embed_data, files=embed_files)
        if response.status_code != 200:
            print(f"❌ Embed request failed: {response.status_code}")
            print(response.text)
            return False
            
        embed_result = response.json()
        operation_id = embed_result['operation_id']
        print(f"✅ Embed operation started: {operation_id}")
        
    # Wait for embedding to complete
    print("⏳ Waiting for embedding to complete...")
    for i in range(30):  # 30 second timeout
        time.sleep(1)
        status_response = requests.get(f"{API_BASE}/api/operations/{operation_id}/status")
        if status_response.status_code == 200:
            status = status_response.json()['status']
            print(f"📊 Status: {status}", end='\r')
            if status == "completed":
                print(f"\n📊 Status: {status}")
                break
            elif status == "failed":
                print(f"\n❌ Embedding failed")
                return False
    else:
        print("\n❌ Embedding timeout")
        return False
        
    # Download the stego video
    download_response = requests.get(f"{API_BASE}/api/operations/{operation_id}/download")
    if download_response.status_code != 200:
        print(f"❌ Download failed: {download_response.status_code}")
        return False
        
    stego_video_path = f"test_video_stego_{int(time.time())}.mp4"
    with open(stego_video_path, 'wb') as f:
        f.write(download_response.content)
    print(f"✅ Stego video saved: {stego_video_path} ({len(download_response.content)} bytes)")
    
    # Step 2: Extract image from video  
    print("\n🔓 Step 2: Extracting image from video...")
    
    with open(stego_video_path, 'rb') as stego_f:
        extract_data = {
            'password': password,
            'output_format': 'auto'
        }
        extract_files = {
            'stego_file': (stego_video_path, stego_f, 'video/mp4')
        }
        
        response = requests.post(f"{API_BASE}/api/extract", data=extract_data, files=extract_files)
        if response.status_code != 200:
            print(f"❌ Extract request failed: {response.status_code}")
            print(response.text)
            return False
            
        extract_result = response.json()
        extract_operation_id = extract_result['operation_id']
        print(f"✅ Extract operation started: {extract_operation_id}")
        
    # Wait for extraction to complete
    print("⏳ Waiting for extraction to complete...")
    for i in range(30):  # 30 second timeout
        time.sleep(1)
        status_response = requests.get(f"{API_BASE}/api/operations/{extract_operation_id}/status")
        if status_response.status_code == 200:
            status_data = status_response.json()
            status = status_data['status']
            print(f"📊 Status: {status}", end='\r')
            if status == "completed":
                print(f"\n📊 Status: {status}")
                break
            elif status == "failed":
                error_msg = status_data.get('error', 'Unknown error')
                print(f"\n❌ Extract failed: {error_msg}")
                return False
    else:
        print("\n❌ Extraction timeout")
        return False
        
    # Download extracted file
    download_response = requests.get(f"{API_BASE}/api/operations/{extract_operation_id}/download")
    if download_response.status_code != 200:
        print(f"❌ Download failed: {download_response.status_code}")
        return False
        
    # Check Content-Disposition header for filename
    content_disp = download_response.headers.get('Content-Disposition', '')
    print(f"📋 Content-Disposition: {content_disp}")
    
    extracted_file = f"extracted_video_test_{int(time.time())}.bin"
    with open(extracted_file, 'wb') as f:
        f.write(download_response.content)
    
    extracted_size = len(download_response.content)
    print(f"✅ Extracted file saved: {extracted_file}")
    print(f"📊 Extracted size: {extracted_size} bytes")
    
    # Step 3: Verify the extracted image
    print("\n🔍 Step 3: Verifying extracted image...")
    
    # Size comparison
    if extracted_size == len(original_image_data):
        print(f"✅ Size match: {extracted_size} bytes")
    else:
        print(f"❌ Size mismatch: {extracted_size} vs {len(original_image_data)} bytes")
        return False
        
    # Binary comparison
    with open(extracted_file, 'rb') as f:
        extracted_data = f.read()
        
    if extracted_data == original_image_data:
        print("✅ Binary data match - files are identical!")
    else:
        print("❌ Binary data mismatch")
        return False
        
    # Try to open as image
    try:
        from PIL import Image
        img = Image.open(extracted_file)
        print(f"✅ Valid image: {img.format} ({img.size[0]}x{img.size[1]})")
    except Exception as e:
        print(f"❌ Not a valid image: {e}")
        return False
        
    # Cleanup
    try:
        os.unlink(stego_video_path)
        os.unlink(extracted_file)
        print("🧹 Cleanup completed")
    except:
        pass
        
    return True

if __name__ == "__main__":
    success = test_video_workflow()
    if success:
        print("\n🎉 ALL VIDEO TESTS PASSED!")
        print("✅ Image embedding in video works correctly")
        print("✅ Image extraction from video works correctly") 
        print("✅ Original image format and content preserved")
        print("✅ Video steganography corruption is COMPLETELY FIXED!")
    else:
        print("\n❌ VIDEO TESTS FAILED!")