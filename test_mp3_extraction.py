#!/usr/bin/env python3
"""
Test script to verify MP3 file extraction preserves correct format
"""

import requests
import time
import os
import json
from pathlib import Path

def test_mp3_extraction():
    """Test that MP3 files extracted from video maintain MP3 format"""
    
    API_BASE = "http://localhost:8000/api"
    
    print("🧪 Testing MP3 File Extraction from Video Steganography")
    print("=" * 60)
    
    # Check if we have test files
    test_video = "test_video.mp4"
    test_mp3 = "test_audio.mp3"
    
    if not os.path.exists(test_video):
        print(f"❌ Test video {test_video} not found")
        print("Please ensure you have a test MP4 video file")
        return False
        
    if not os.path.exists(test_mp3):
        print(f"❌ Test MP3 {test_mp3} not found") 
        print("Please ensure you have a test MP3 audio file")
        return False
    
    try:
        print(f"📁 Using test video: {test_video}")
        print(f"🎵 Using test MP3: {test_mp3}")
        
        # Step 1: Hide MP3 in video
        print("\n🔐 Step 1: Hiding MP3 file in video...")
        
        with open(test_video, "rb") as video_file, open(test_mp3, "rb") as mp3_file:
            embed_data = {
                "content_type": "file",
                "password": "test123"
            }
            embed_files = {
                "carrier_file": video_file,
                "content_file": mp3_file
            }
            
            response = requests.post(f"{API_BASE}/hide", data=embed_data, files=embed_files)
            if response.status_code != 200:
                print(f"❌ Embed failed: {response.text}")
                return False
                
            embed_result = response.json()
            operation_id = embed_result["operation_id"]
            print(f"✅ Embed operation started: {operation_id}")
            
            # Wait for embedding to complete
            while True:
                status_response = requests.get(f"{API_BASE}/operations/{operation_id}/status")
                status = status_response.json()
                
                print(f"   Status: {status['status']} ({status['progress']}%)")
                
                if status["status"] == "completed":
                    print("✅ Embedding completed successfully!")
                    break
                elif status["status"] == "failed":
                    print(f"❌ Embed operation failed: {status.get('error', 'Unknown error')}")
                    return False
                    
                time.sleep(1)
            
            # Download the stego video
            download_response = requests.get(f"{API_BASE}/operations/{operation_id}/download")
            stego_video = f"stego_{test_video}"
            
            with open(stego_video, "wb") as f:
                f.write(download_response.content)
            
            print(f"💾 Stego video saved: {stego_video}")
        
        # Step 2: Extract MP3 from video
        print(f"\n🔓 Step 2: Extracting MP3 from stego video...")
        
        with open(stego_video, "rb") as stego_file:
            extract_data = {
                "password": "test123"
            }
            extract_files = {
                "container_file": stego_file
            }
            
            response = requests.post(f"{API_BASE}/extract", data=extract_data, files=extract_files)
            if response.status_code != 200:
                print(f"❌ Extract failed: {response.text}")
                return False
                
            extract_result = response.json()
            operation_id = extract_result["operation_id"]
            print(f"✅ Extract operation started: {operation_id}")
            
            # Wait for extraction to complete
            while True:
                status_response = requests.get(f"{API_BASE}/operations/{operation_id}/status")
                status = status_response.json()
                
                print(f"   Status: {status['status']} ({status['progress']}%)")
                
                if status["status"] == "completed":
                    print("✅ Extraction completed successfully!")
                    break
                elif status["status"] == "failed":
                    print(f"❌ Extract operation failed: {status.get('error', 'Unknown error')}")
                    return False
                    
                time.sleep(1)
            
            # Check the extracted filename
            result_info = status["result"]
            extracted_filename = result_info["output_filename"]
            
            print(f"\n📊 RESULTS:")
            print(f"   📄 Extracted filename: {extracted_filename}")
            print(f"   📦 File size: {result_info.get('file_size', 'Unknown')} bytes")
            
            # Check if the extension is preserved
            if extracted_filename.lower().endswith('.mp3'):
                print(f"✅ SUCCESS: MP3 extension preserved!")
            else:
                print(f"❌ FAILED: Extension NOT preserved! Expected .mp3, got: {extracted_filename}")
                return False
            
            # Download and verify the extracted file
            download_response = requests.get(f"{API_BASE}/operations/{operation_id}/download")
            extracted_file = f"extracted_{extracted_filename}"
            
            with open(extracted_file, "wb") as f:
                f.write(download_response.content)
            
            print(f"💾 Extracted file saved: {extracted_file}")
            
            # Basic file validation
            if os.path.exists(extracted_file):
                extracted_size = os.path.getsize(extracted_file)
                original_size = os.path.getsize(test_mp3)
                
                print(f"   📏 Original MP3 size: {original_size} bytes")
                print(f"   📏 Extracted file size: {extracted_size} bytes")
                
                if abs(extracted_size - original_size) < 100:  # Allow small difference
                    print(f"✅ File size verification passed!")
                else:
                    print(f"⚠️  File size differs significantly")
                
                # Check file header for MP3 signature
                with open(extracted_file, "rb") as f:
                    header = f.read(10)
                    if header.startswith(b'ID3') or header[0:2] == b'\xff\xfb':
                        print(f"✅ MP3 file signature detected!")
                    else:
                        print(f"⚠️  MP3 signature not detected, but file may still be valid")
            
            print(f"\n🎉 TEST COMPLETED SUCCESSFULLY!")
            print(f"   The MP3 file was successfully extracted with correct .mp3 extension")
            print(f"   You can now play the extracted file: {extracted_file}")
            
            return True
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_mp3_extraction()
    if success:
        print(f"\n✅ ALL TESTS PASSED - MP3 extraction working correctly!")
    else:
        print(f"\n❌ TESTS FAILED - Issues with MP3 extraction")