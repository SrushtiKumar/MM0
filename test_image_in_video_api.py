#!/usr/bin/env python3
"""
Test Image-in-Video Embedding via Production API
Reproduce and verify fix for the bool encode error
"""

import requests
import tempfile
import os
import subprocess
import time
from PIL import Image
import numpy as np

def create_test_video():
    """Create a test MP4 video"""
    temp_dir = tempfile.mkdtemp()
    video_path = os.path.join(temp_dir, "test_video_api.mp4")
    
    try:
        cmd = [
            'ffmpeg', '-y', '-f', 'lavfi', 
            '-i', 'testsrc=duration=2:size=240x180:rate=15',
            '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
            video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return video_path
        else:
            print(f"Cannot create test video: {result.stderr}")
            return None
    except Exception as e:
        print(f"ffmpeg not available: {e}")
        return None

def create_test_image():
    """Create a test PNG image"""
    temp_dir = tempfile.mkdtemp()
    image_path = os.path.join(temp_dir, "secret_image.png")
    
    # Create a more interesting test image
    img_array = np.zeros((80, 120, 3), dtype=np.uint8)
    img_array[:, :40] = [255, 0, 0]  # Red section
    img_array[:, 40:80] = [0, 255, 0]  # Green section  
    img_array[:, 80:] = [0, 0, 255]  # Blue section
    
    img = Image.fromarray(img_array, 'RGB')
    img.save(image_path, 'PNG')
    return image_path

def check_video_integrity(video_path):
    """Check if video is still playable"""
    try:
        cmd = ['ffprobe', '-v', 'error', '-show_format', video_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def test_image_in_video_via_api():
    """Test embedding image in video via production API"""
    
    print("🌐 TESTING IMAGE-IN-VIDEO VIA PRODUCTION API")
    print("=" * 60)
    print("Goal: Verify bool encode error is fixed in production")
    print("=" * 60)
    
    # Create test files
    video_path = create_test_video()
    image_path = create_test_image()
    
    if not video_path or not image_path:
        print("❌ Cannot create test files")
        return False
    
    video_size = os.path.getsize(video_path)
    image_size = os.path.getsize(image_path)
    
    print(f"✅ Created test video: {video_size} bytes")
    print(f"✅ Created test image: {image_size} bytes")
    
    API_BASE = "http://localhost:8000"
    
    try:
        print(f"\n🔧 Embedding image inside video via API...")
        
        # Test the API embedding
        with open(video_path, 'rb') as video_f, open(image_path, 'rb') as image_f:
            files = {
                'carrier_file': ('test_video.mp4', video_f, 'video/mp4'),
                'content_file': ('secret_image.png', image_f, 'image/png')
            }
            data = {
                'content_type': 'document',  # Using document type for file embedding
                'password': 'test123'
            }
            
            response = requests.post(f"{API_BASE}/api/embed", files=files, data=data, timeout=30)
        
        print(f"API Response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            operation_id = result.get('operation_id')
            
            print(f"✅ Embedding initiated: {operation_id}")
            
            # Wait for processing
            print("⏳ Waiting for processing...")
            time.sleep(5)
            
            # Download result
            download_response = requests.get(f"{API_BASE}/api/operations/{operation_id}/download")
            
            if download_response.status_code == 200:
                # Save result
                result_path = video_path.replace('.mp4', '_with_image.mp4')
                with open(result_path, 'wb') as f:
                    f.write(download_response.content)
                
                result_size = len(download_response.content)
                print(f"✅ Download successful: {result_size} bytes")
                
                # Check video integrity
                print(f"\n🔍 Checking video integrity...")
                if check_video_integrity(result_path):
                    print(f"✅ Video remains playable after embedding!")
                    
                    # Test extraction
                    print(f"\n📤 Testing extraction via API...")
                    
                    with open(result_path, 'rb') as result_f:
                        files = {
                            'stego_file': ('video_with_image.mp4', result_f, 'video/mp4')
                        }
                        data = {'password': 'test123'}
                        
                        extract_response = requests.post(f"{API_BASE}/api/extract", files=files, data=data, timeout=30)
                    
                    if extract_response.status_code == 200:
                        extract_result = extract_response.json()
                        
                        if extract_result.get('success'):
                            print(f"✅ Extraction successful!")
                            print(f"   Extracted file: {extract_result.get('filename', 'N/A')}")
                            
                            # Calculate overhead
                            overhead = result_size - video_size
                            overhead_percent = (overhead / video_size) * 100
                            
                            print(f"\n📊 RESULTS:")
                            print(f"   Original video: {video_size} bytes")
                            print(f"   Hidden image: {image_size} bytes")  
                            print(f"   Final video: {result_size} bytes")
                            print(f"   Overhead: {overhead} bytes ({overhead_percent:.1f}%)")
                            
                            return True
                        else:
                            print(f"❌ Extraction failed: {extract_result}")
                    else:
                        print(f"❌ Extraction API error: {extract_response.status_code}")
                        print(f"   Response: {extract_response.text}")
                else:
                    print(f"❌ Video corrupted after embedding!")
            else:
                print(f"❌ Download failed: {download_response.status_code}")
                print(f"   Response: {download_response.text}")
        else:
            print(f"❌ API embedding failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        for path in [video_path, image_path]:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except:
                pass
    
    return False

if __name__ == "__main__":
    success = test_image_in_video_via_api()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 IMAGE-IN-VIDEO EMBEDDING COMPLETELY WORKING!")
        print("✅ Bool encode error FIXED in production API")
        print("✅ Videos remain playable with embedded images") 
        print("✅ Full encode/decode cycle successful")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ IMAGE-IN-VIDEO EMBEDDING FAILED")
        print("❌ May need additional debugging")
        print("=" * 60)