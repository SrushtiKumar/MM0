#!/usr/bin/env python3
"""
Comprehensive test of video steganography through API to ensure no corruption
"""

import requests
import cv2
import numpy as np
import os
import time

def create_test_video_for_api():
    """Create test video for API testing"""
    filename = "api_test_video.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, 15.0, (320, 240))
    
    # Create 45 frames (3 seconds at 15 FPS)
    for i in range(45):
        frame = np.zeros((240, 320, 3), dtype=np.uint8)
        # Create a simple animated pattern
        frame[:, :, 0] = (i * 5) % 256
        frame[:, :, 1] = (i * 7) % 256  
        frame[:, :, 2] = (i * 11) % 256
        
        # Add moving rectangle
        x1 = 20 + (i * 4) % 200
        y1 = 20 + (i * 3) % 150
        cv2.rectangle(frame, (x1, y1), (x1+50, y1+50), (255, 255, 255), -1)
        
        out.write(frame)
    
    out.release()
    print(f"✅ Created API test video: {filename}")
    return filename

def test_video_steganography_api():
    """Test video steganography through the full API"""
    
    print("🧪 TESTING VIDEO STEGANOGRAPHY VIA API")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        base_url = "http://localhost:8000"
    except:
        try:
            response = requests.get("http://localhost:8001/health", timeout=2) 
            base_url = "http://localhost:8001"
        except:
            try:
                response = requests.get("http://localhost:8002/health", timeout=2)
                base_url = "http://localhost:8002"
            except:
                print("❌ No server running on port 8000, 8001, or 8002")
                print("   Please start the FastAPI server first")
                return False
    
    print(f"✅ Using server: {base_url}")
    
    # Create test video
    test_video = create_test_video_for_api()
    
    if not os.path.exists(test_video):
        print(f"❌ Failed to create test video")
        return False
    
    # Test data to hide
    secret_text = "This is secret video steganography data that should be preserved without corruption!"
    
    try:
        # Step 1: Embed secret in video via API
        print(f"\n🔐 Step 1: Embedding secret in video via API...")
        
        with open(test_video, 'rb') as f:
            embed_response = requests.post(
                f"{base_url}/embed/video",
                files={"file": f},
                data={
                    "text": secret_text,
                    "password": "test123"
                }
            )
        
        if embed_response.status_code != 200:
            print(f"❌ Embed request failed: {embed_response.status_code}")
            print(f"Response: {embed_response.text}")
            return False
        
        job_id = embed_response.json()["job_id"]
        print(f"✅ Embed job started: {job_id}")
        
        # Step 2: Wait for processing completion
        print(f"🔄 Step 2: Waiting for processing...")
        
        max_wait = 30  # 30 seconds max
        wait_time = 0
        
        while wait_time < max_wait:
            status_response = requests.get(f"{base_url}/status/{job_id}")
            if status_response.status_code != 200:
                print(f"❌ Status check failed: {status_response.status_code}")
                return False
            
            status_data = status_response.json()
            status = status_data["status"]
            progress = status_data.get("progress", 0)
            
            if status == "completed":
                print(f"✅ Processing completed! (100%)")
                break
            elif status == "failed":
                print(f"❌ Processing failed: {status_data.get('error', 'Unknown error')}")
                return False
            else:
                print(f"⏳ Status: {status} ({progress}%)")
                time.sleep(1)
                wait_time += 1
        
        if wait_time >= max_wait:
            print(f"❌ Processing timeout after {max_wait} seconds")
            return False
        
        # Step 3: Download processed video
        print(f"📥 Step 3: Downloading processed video...")
        
        download_response = requests.get(f"{base_url}/download/{job_id}")
        if download_response.status_code != 200:
            print(f"❌ Download failed: {download_response.status_code}")
            return False
        
        # Save processed video
        processed_video = f"processed_video_{job_id}.avi"  # Expect AVI format
        with open(processed_video, 'wb') as f:
            f.write(download_response.content)
        
        print(f"✅ Downloaded processed video: {processed_video}")
        print(f"   Size: {len(download_response.content)} bytes")
        
        # Step 4: Verify video is not corrupted
        print(f"🎬 Step 4: Verifying video integrity...")
        
        try:
            cap = cv2.VideoCapture(processed_video)
            
            if not cap.isOpened():
                print(f"❌ Cannot open processed video - FILE IS CORRUPTED")
                return False
            
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            print(f"✅ Video is readable and NOT corrupted!")
            print(f"   Frames: {frame_count}")
            print(f"   FPS: {fps}")
            print(f"   Resolution: {width}x{height}")
            
            # Test reading frames
            frames_read = 0
            for i in range(min(10, frame_count)):
                ret, frame = cap.read()
                if ret and frame is not None:
                    frames_read += 1
                else:
                    break
            
            cap.release()
            
            if frames_read > 0:
                print(f"✅ Successfully read {frames_read} frames - Video plays correctly!")
            else:
                print(f"❌ Cannot read frames - Video may be corrupted")
                return False
                
        except Exception as e:
            print(f"❌ Video integrity test failed: {e}")
            return False
        
        # Step 5: Extract secret data
        print(f"🔍 Step 5: Extracting secret data...")
        
        with open(processed_video, 'rb') as f:
            extract_response = requests.post(
                f"{base_url}/extract/video",
                files={"file": f},
                data={"password": "test123"}
            )
        
        if extract_response.status_code != 200:
            print(f"❌ Extract request failed: {extract_response.status_code}")
            print(f"Response: {extract_response.text}")
            return False
        
        extract_job_id = extract_response.json()["job_id"]
        print(f"✅ Extract job started: {extract_job_id}")
        
        # Step 6: Wait for extraction
        print(f"⏳ Step 6: Waiting for extraction...")
        
        wait_time = 0
        while wait_time < max_wait:
            status_response = requests.get(f"{base_url}/status/{extract_job_id}")
            if status_response.status_code != 200:
                print(f"❌ Extract status check failed")
                return False
            
            status_data = status_response.json()
            status = status_data["status"]
            
            if status == "completed":
                print(f"✅ Extraction completed!")
                break
            elif status == "failed":
                print(f"❌ Extraction failed: {status_data.get('error', 'Unknown')}")
                return False
            else:
                time.sleep(1)
                wait_time += 1
        
        # Step 7: Download extracted data
        print(f"📥 Step 7: Downloading extracted data...")
        
        extracted_response = requests.get(f"{base_url}/download/{extract_job_id}")
        if extracted_response.status_code != 200:
            print(f"❌ Extract download failed: {extracted_response.status_code}")
            return False
        
        extracted_content = extracted_response.text
        print(f"✅ Extracted content: {len(extracted_content)} chars")
        print(f"   Content: {extracted_content[:100]}{'...' if len(extracted_content) > 100 else ''}")
        
        # Step 8: Verify content matches
        if secret_text.strip() == extracted_content.strip():
            print(f"✅ SUCCESS: Extracted content matches original perfectly!")
            return True
        else:
            print(f"❌ CONTENT MISMATCH:")
            print(f"   Original: {secret_text}")
            print(f"   Extracted: {extracted_content}")
            return False
        
    finally:
        # Cleanup
        for file in [test_video, f"processed_video_{job_id}.avi" if 'job_id' in locals() else ""]:
            if file and os.path.exists(file):
                os.remove(file)
                print(f"🧹 Cleaned up: {file}")

def main():
    success = test_video_steganography_api()
    
    print(f"\n" + "=" * 60)
    print(f"🎯 VIDEO STEGANOGRAPHY API TEST RESULTS")
    print(f"=" * 60)
    
    if success:
        print(f"🎉 ALL TESTS PASSED!")
        print(f"✅ Video processed without corruption")
        print(f"✅ Video remains playable and readable") 
        print(f"✅ Secret data embedded and extracted successfully")
        print(f"✅ Complete API workflow functional")
        print(f"\n💡 Note: Videos are converted to AVI format to preserve steganography data")
    else:
        print(f"❌ TESTS FAILED!")
        print(f"⚠️  Video steganography issues detected")
        print(f"   Check server logs and video processing pipeline")

if __name__ == "__main__":
    main()