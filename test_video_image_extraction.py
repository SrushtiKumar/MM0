#!/usr/bin/env python3
"""
Test script to verify that image extraction from video works correctly
and preserves the original image format and content
"""

import os
import requests
import time
from pathlib import Path

# Configuration
API_BASE = "http://localhost:8000"
TEST_DIR = Path(__file__).parent

def test_image_in_video_extraction():
    """Test embedding and extracting an image in video"""
    
    print("🧪 Testing Image-in-Video Extraction...")
    
    # Find test files
    test_video = None
    test_image = None
    
    # Look for video files
    for ext in ['.mp4', '.avi', '.mov']:
        for file in TEST_DIR.glob(f"*{ext}"):
            test_video = file
            break
        if test_video:
            break
    
    # Look for image files  
    for ext in ['.png', '.jpg', '.jpeg', '.bmp']:
        for file in TEST_DIR.glob(f"*{ext}"):
            test_image = file
            break
        if test_image:
            break
    
    if not test_video:
        print("❌ No video file found for testing")
        return False
        
    if not test_image:
        print("❌ No image file found for testing")
        return False
        
    print(f"📹 Using video: {test_video.name}")
    print(f"🖼️  Using image: {test_image.name}")
    
    # Get original image size for comparison
    original_image_size = test_image.stat().st_size
    print(f"📊 Original image size: {original_image_size} bytes")
    
    try:
        # Step 1: Embed image in video
        print("\n🔐 Step 1: Embedding image in video...")
        
        with open(test_video, 'rb') as video_f, open(test_image, 'rb') as image_f:
            embed_response = requests.post(
                f"{API_BASE}/api/embed",
                files={
                    'carrier_file': (test_video.name, video_f, 'video/mp4'),
                    'content_file': (test_image.name, image_f, 'image/png')
                },
                data={
                    'password': 'testpass123',
                    'operation_type': 'file',
                    'content_type': 'file'
                }
            )
        
        if embed_response.status_code != 200:
            print(f"❌ Embed failed: {embed_response.text}")
            return False
            
        embed_data = embed_response.json()
        if not embed_data.get('success'):
            print(f"❌ Embed operation failed: {embed_data}")
            return False
            
        operation_id = embed_data['operation_id']
        print(f"✅ Embed operation started: {operation_id}")
        
        # Wait for embedding to complete
        print("⏳ Waiting for embedding to complete...")
        while True:
            status_response = requests.get(f"{API_BASE}/api/operations/{operation_id}/status")
            if status_response.status_code != 200:
                print(f"❌ Status check failed: {status_response.status_code}")
                return False
            
            status_data = status_response.json()
            
            if 'status' not in status_data:
                print(f"❌ Invalid status response: {status_data}")
                return False
                
            print(f"📊 Status: {status_data['status']} - {status_data.get('message', '')}")
            
            if status_data['status'] == 'completed':
                break
            elif status_data['status'] == 'failed':
                print(f"❌ Embed failed: {status_data.get('error', 'Unknown error')}")
                return False
            
            time.sleep(2)
        
        # Get the stego video file
        download_response = requests.get(f"{API_BASE}/api/operations/{operation_id}/download")
        if download_response.status_code != 200:
            print(f"❌ Download failed: {download_response.status_code}")
            return False
            
        stego_video_path = TEST_DIR / f"test_stego_video_{int(time.time())}.mp4"
        with open(stego_video_path, 'wb') as f:
            f.write(download_response.content)
        
        print(f"✅ Stego video saved: {stego_video_path.name}")
        
        # Step 2: Extract image from video
        print("\n🔓 Step 2: Extracting image from video...")
        
        with open(stego_video_path, 'rb') as stego_f:
            extract_response = requests.post(
                f"{API_BASE}/api/extract",
                files={
                    'stego_file': (stego_video_path.name, stego_f, 'video/mp4')
                },
                data={
                    'password': 'testpass123',
                    'output_format': 'auto'
                }
            )
        
        if extract_response.status_code != 200:
            print(f"❌ Extract failed: {extract_response.text}")
            return False
            
        extract_data = extract_response.json()
        if not extract_data.get('success'):
            print(f"❌ Extract operation failed: {extract_data}")
            return False
            
        extract_operation_id = extract_data['operation_id']
        print(f"✅ Extract operation started: {extract_operation_id}")
        
        # Wait for extraction to complete
        print("⏳ Waiting for extraction to complete...")
        while True:
            status_response = requests.get(f"{API_BASE}/api/operations/{extract_operation_id}/status")
            if status_response.status_code != 200:
                print(f"❌ Status check failed: {status_response.status_code}")
                return False
            
            status_data = status_response.json()
            
            if 'status' not in status_data:
                print(f"❌ Invalid status response: {status_data}")
                return False
                
            print(f"📊 Status: {status_data['status']} - {status_data.get('message', '')}")
            
            if status_data['status'] == 'completed':
                break
            elif status_data['status'] == 'failed':
                print(f"❌ Extract failed: {status_data.get('error', 'Unknown error')}")
                return False
            
            time.sleep(2)
        
        # Download the extracted file
        download_response = requests.get(f"{API_BASE}/api/operations/{extract_operation_id}/download")
        if download_response.status_code != 200:
            print(f"❌ Extract download failed: {download_response.status_code}")
            return False
            
        # Get the filename from response headers
        content_disposition = download_response.headers.get('Content-Disposition', '')
        if 'filename=' in content_disposition:
            filename = content_disposition.split('filename=')[1].strip('"')
        else:
            filename = f"extracted_image_{int(time.time())}.png"
            
        extracted_file_path = TEST_DIR / filename
        with open(extracted_file_path, 'wb') as f:
            f.write(download_response.content)
        
        print(f"✅ Extracted file saved: {extracted_file_path.name}")
        
        # Step 3: Verify the extracted file
        print("\n🔍 Step 3: Verifying extracted file...")
        
        extracted_size = extracted_file_path.stat().st_size
        print(f"📊 Extracted file size: {extracted_size} bytes")
        
        # Check if sizes match
        if extracted_size == original_image_size:
            print("✅ File sizes match!")
        else:
            print(f"⚠️  File sizes differ: {original_image_size} vs {extracted_size}")
        
        # Check if the file is a valid image
        try:
            from PIL import Image
            with Image.open(extracted_file_path) as img:
                print(f"✅ Extracted file is a valid {img.format} image")
                print(f"📐 Image dimensions: {img.size}")
                print(f"🎨 Image mode: {img.mode}")
        except Exception as e:
            print(f"❌ Extracted file is not a valid image: {e}")
            return False
            
        # Compare file contents
        with open(test_image, 'rb') as orig_f, open(extracted_file_path, 'rb') as extr_f:
            original_content = orig_f.read()
            extracted_content = extr_f.read()
            
            if original_content == extracted_content:
                print("✅ File contents are identical!")
            else:
                print("❌ File contents differ!")
                return False
        
        print("\n🎉 SUCCESS: Image extraction from video works perfectly!")
        print(f"✅ Original image: {test_image.name} ({original_image_size} bytes)")
        print(f"✅ Extracted image: {extracted_file_path.name} ({extracted_size} bytes)")
        print("✅ Files are identical - no corruption detected!")
        
        # Cleanup
        stego_video_path.unlink()
        extracted_file_path.unlink()
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_image_in_video_extraction()
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Tests failed!")