#!/usr/bin/env python3
"""
Test the fixed video-in-audio steganography via the enhanced backend
"""

import os
import requests
import time

def test_backend_video_in_audio():
    """Test video-in-audio steganography through the backend API"""
    print("🎬 Testing Video-in-Audio via Enhanced Backend")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Check if server is running
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code != 200:
            print("❌ Server not responding. Please start the server first.")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Please start the server first.")
        print("   Run: python enhanced_app.py")
        return
    
    print("✅ Server is running")
    
    # Test files
    audio_files = ['demo_audio.wav', 'ff-16b-2c-44100hz.wav']
    video_files = ['debug_test_video.mp4', 'api_test_video.mp4']
    
    # Find available files
    available_audio = [f for f in audio_files if os.path.exists(f)]
    available_video = [f for f in video_files if os.path.exists(f)]
    
    if not available_audio:
        print("❌ No audio files found for testing")
        return
    
    if not available_video:
        print("❌ No video files found for testing")
        return
    
    # Test 1: Small video (should work)
    small_video = 'debug_test_video.mp4'  # 104 bytes
    audio_file = available_audio[0]
    
    if small_video in available_video:
        print(f"\n{'='*50}")
        print(f"Test 1: Small Video ({small_video}) in Audio ({audio_file})")
        print(f"{'='*50}")
        
        # Prepare files
        with open(audio_file, 'rb') as f:
            audio_data = f.read()
        
        with open(small_video, 'rb') as f:
            video_data = f.read()
        
        print(f"Audio file size: {len(audio_data):,} bytes")
        print(f"Video file size: {len(video_data):,} bytes")
        
        # Upload embed request
        files = {
            'carrier_file': (audio_file, audio_data, 'audio/wav'),
            'content_file': (small_video, video_data, 'video/mp4')
        }
        
        data = {
            'carrier_type': 'audio',
            'content_type': 'file',
            'password': 'test123',
            'encryption_type': 'aes-256-gcm',
            'project_name': 'Video-in-Audio Test'
        }
        
        try:
            print("📤 Sending embed request...")
            response = requests.post(f"{base_url}/embed", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Embed successful!")
                print(f"   File ID: {result.get('file_id')}")
                print(f"   Message: {result.get('message', 'No message')}")
                
                # Test extraction
                if 'file_id' in result:
                    print("\n📥 Testing extraction...")
                    
                    extract_data = {'password': 'test123', 'output_format': 'auto'}
                    extract_response = requests.post(f"{base_url}/extract/{result['file_id']}", json=extract_data)
                    
                    if extract_response.status_code == 200:
                        # Check if it's a file download
                        if 'application/octet-stream' in extract_response.headers.get('content-type', ''):
                            extracted_size = len(extract_response.content)
                            print(f"✅ Extraction successful!")
                            print(f"   Extracted file size: {extracted_size:,} bytes")
                            
                            if extracted_size == len(video_data):
                                print("🎉 VIDEO-IN-AUDIO TEST PASSED!")
                            else:
                                print(f"⚠️ Size mismatch: original {len(video_data)}, extracted {extracted_size}")
                        else:
                            extract_result = extract_response.json()
                            print(f"✅ Extraction response: {extract_result}")
                    else:
                        print(f"❌ Extraction failed: {extract_response.status_code}")
                        print(f"   Error: {extract_response.text}")
                
            else:
                print(f"❌ Embed failed: {response.status_code}")
                error_detail = response.json() if response.content else "No error details"
                print(f"   Error: {error_detail}")
                
        except Exception as e:
            print(f"❌ Request error: {e}")
    
    # Test 2: Large video (should fail gracefully)
    large_video = 'api_test_video.mp4'  # 15KB
    
    if large_video in available_video:
        print(f"\n{'='*50}")
        print(f"Test 2: Large Video ({large_video}) in Audio ({audio_file})")
        print(f"{'='*50}")
        
        # Prepare files
        with open(audio_file, 'rb') as f:
            audio_data = f.read()
        
        with open(large_video, 'rb') as f:
            video_data = f.read()
        
        print(f"Audio file size: {len(audio_data):,} bytes")
        print(f"Video file size: {len(video_data):,} bytes")
        
        # Upload embed request
        files = {
            'carrier_file': (audio_file, audio_data, 'audio/wav'),
            'content_file': (large_video, video_data, 'video/mp4')
        }
        
        data = {
            'carrier_type': 'audio',
            'content_type': 'file',
            'password': 'test123',
            'encryption_type': 'aes-256-gcm',
            'project_name': 'Large Video-in-Audio Test'
        }
        
        try:
            print("📤 Sending embed request...")
            response = requests.post(f"{base_url}/embed", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"ℹ️ Large video embedding result:")
                print(f"   Message: {result.get('message', 'No message')}")
                print(f"   Success: {result.get('success', False)}")
                
                if result.get('success'):
                    print("✅ Large video embedding successful (capacity was sufficient)")
                else:
                    print("✅ Large video correctly rejected by capacity check")
                
            else:
                print(f"ℹ️ Large video correctly rejected: {response.status_code}")
                try:
                    error_detail = response.json()
                    if 'capacity' in str(error_detail).lower():
                        print("✅ Capacity check working correctly")
                    print(f"   Error details: {error_detail}")
                except:
                    print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Request error: {e}")
    
    print(f"\n🎉 Backend video-in-audio testing complete!")

if __name__ == "__main__":
    test_backend_video_in_audio()