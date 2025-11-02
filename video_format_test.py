#!/usr/bin/env python3
"""
Test video steganography with different video formats to identify audio corruption issues
"""

import os
import requests
import time
from pathlib import Path

# Configuration
API_BASE = "http://localhost:8000"
TEST_DIR = Path(__file__).parent

def test_video_format(video_file, format_name):
    """Test video steganography with specific format"""
    
    print(f"\n🧪 Testing {format_name} Format: {video_file}")
    
    if not Path(video_file).exists():
        print(f"❌ Video file not found: {video_file}")
        return False
        
    test_image = "debug_embedded.png"
    if not Path(test_image).exists():
        print(f"❌ Test image not found: {test_image}")
        return False
        
    password = "testpass123"
    
    # Get original video info
    original_size = Path(video_file).stat().st_size
    print(f"📊 Original {format_name} size: {original_size} bytes")
    
    # Step 1: Embed image in video
    print(f"🔐 Embedding image in {format_name}...")
    
    with open(video_file, 'rb') as carrier_f, open(test_image, 'rb') as content_f:
        embed_data = {
            'password': password,
            'output_format': 'auto',
            'carrier_type': 'video'
        }
        embed_files = {
            'carrier_file': (video_file, carrier_f, f'video/{format_name.lower()}'),
            'content_file': (test_image, content_f, 'image/png')
        }
        
        response = requests.post(f"{API_BASE}/api/embed", data=embed_data, files=embed_files)
        if response.status_code != 200:
            print(f"❌ Embed request failed: {response.status_code}")
            print(response.text)
            return False
            
        embed_result = response.json()
        operation_id = embed_result['operation_id']
        
    # Wait for embedding to complete
    for i in range(30):
        time.sleep(1)
        status_response = requests.get(f"{API_BASE}/api/operations/{operation_id}/status")
        if status_response.status_code == 200:
            status = status_response.json()['status']
            if status == "completed":
                break
            elif status == "failed":
                print(f"❌ Embedding failed")
                return False
    else:
        print("❌ Embedding timeout")
        return False
        
    # Download the stego video
    download_response = requests.get(f"{API_BASE}/api/operations/{operation_id}/download")
    if download_response.status_code != 200:
        print(f"❌ Download failed: {download_response.status_code}")
        return False
        
    stego_video_path = f"test_stego_{format_name.lower()}_{int(time.time())}.{Path(video_file).suffix[1:]}"
    with open(stego_video_path, 'wb') as f:
        f.write(download_response.content)
    
    stego_size = len(download_response.content)
    print(f"✅ Stego {format_name} saved: {stego_video_path} ({stego_size} bytes)")
    print(f"📊 Size increase: {stego_size - original_size} bytes")
    
    # Step 2: Test playback by checking file structure
    print(f"🔍 Analyzing {format_name} file structure...")
    
    try:
        # Check if this is a valid video file by examining headers
        with open(stego_video_path, 'rb') as f:
            header = f.read(16)
            
        if format_name.upper() == "MP4":
            # MP4 should start with ftyp box
            if b'ftyp' in header[:12]:
                print(f"✅ {format_name} header structure intact")
            else:
                print(f"⚠️ {format_name} header may be corrupted")
        elif format_name.upper() == "AVI":
            # AVI should start with RIFF
            if header.startswith(b'RIFF'):
                print(f"✅ {format_name} header structure intact")
            else:
                print(f"⚠️ {format_name} header may be corrupted")
                
    except Exception as e:
        print(f"❌ Error analyzing file: {e}")
        
    # Step 3: Test extraction
    print(f"🔓 Testing extraction from {format_name}...")
    
    with open(stego_video_path, 'rb') as stego_f:
        extract_data = {
            'password': password,
            'output_format': 'auto'
        }
        extract_files = {
            'stego_file': (stego_video_path, stego_f, f'video/{format_name.lower()}')
        }
        
        response = requests.post(f"{API_BASE}/api/extract", data=extract_data, files=extract_files)
        if response.status_code != 200:
            print(f"❌ Extract request failed: {response.status_code}")
            return False
            
        extract_result = response.json()
        extract_operation_id = extract_result['operation_id']
        
    # Wait for extraction to complete
    for i in range(30):
        time.sleep(1)
        status_response = requests.get(f"{API_BASE}/api/operations/{extract_operation_id}/status")
        if status_response.status_code == 200:
            status_data = status_response.json()
            status = status_data['status']
            if status == "completed":
                print(f"✅ Extraction from {format_name} successful")
                break
            elif status == "failed":
                error_msg = status_data.get('error', 'Unknown error')
                print(f"❌ Extract failed: {error_msg}")
                return False
    else:
        print("❌ Extraction timeout")
        return False
        
    # Cleanup
    try:
        os.unlink(stego_video_path)
    except:
        pass
        
    return True

def main():
    """Test different video formats"""
    
    print("🧪 Video Format Compatibility Test")
    print("=" * 50)
    
    # Start server
    print("🚀 Starting server...")
    os.system("start /B python enhanced_app.py")
    time.sleep(5)
    
    # Test MP4 format
    mp4_success = test_video_format("clean_carrier.mp4", "MP4")
    
    # Test AVI format if available
    avi_success = None
    avi_files = list(Path(".").glob("*.avi"))
    if avi_files:
        avi_success = test_video_format(str(avi_files[0]), "AVI")
    
    print("\n" + "=" * 50)
    print("🎯 RESULTS SUMMARY:")
    print(f"📹 MP4 Format: {'✅ PASS' if mp4_success else '❌ FAIL'}")
    if avi_success is not None:
        print(f"📹 AVI Format: {'✅ PASS' if avi_success else '❌ FAIL'}")
    else:
        print("📹 AVI Format: ⏭️ SKIPPED (no AVI files found)")
        
    if mp4_success and (avi_success is None or not avi_success):
        print("\n💡 RECOMMENDATION: Use MP4 format for video steganography")
        print("   AVI format may have audio playback issues due to container structure")

if __name__ == "__main__":
    main()