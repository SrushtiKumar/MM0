#!/usr/bin/env python3
"""
Test the web application video steganography functionality
"""

import requests
import os
import tempfile


def test_web_video_steganography():
    """Test video steganography through the web API"""
    print("🌐 Testing Web Application Video Steganography")
    
    base_url = "http://127.0.0.1:8000"
    
    # Create a test video file if needed
    test_video = 'web_test_video_upload.mp4'
    if not os.path.exists(test_video):
        print("Creating test video for upload...")
        import cv2
        import numpy as np
        
        width, height = 320, 240
        fps = 10
        frames = 10
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(test_video, fourcc, fps, (width, height))
        
        for i in range(frames):
            frame = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
            out.write(frame)
        
        out.release()
        print("✅ Test video created")
    
    # Test message
    test_message = "Hello from web video steganography! This is a test message."
    
    print(f"\n🔒 Testing video steganography with message: '{test_message}'")
    
    try:
        # Test hiding message in video
        with open(test_video, 'rb') as video_file:
            files = {
                'file': ('test_video.mp4', video_file, 'video/mp4')
            }
            data = {
                'payload': test_message,
                'password': '',
                'format': 'video'
            }
            
            print("  Sending hide request...")
            response = requests.post(f"{base_url}/hide", files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                print("✅ Hide request successful")
                
                # Save the result
                with open('web_result_video.mp4', 'wb') as output_file:
                    output_file.write(response.content)
                
                print("  Video with hidden message saved as 'web_result_video.mp4'")
                
                # Test extracting message
                print("\n🔓 Testing extraction...")
                with open('web_result_video.mp4', 'rb') as result_video:
                    files = {
                        'file': ('result_video.mp4', result_video, 'video/mp4')
                    }
                    data = {
                        'password': '',
                        'format': 'video'
                    }
                    
                    response = requests.post(f"{base_url}/extract", files=files, data=data, timeout=30)
                    
                    if response.status_code == 200:
                        extracted_content = response.content.decode('utf-8')
                        print(f"✅ Extracted message: '{extracted_content}'")
                        
                        if extracted_content == test_message:
                            print("🎉 Perfect match! Video steganography working correctly!")
                            return True
                        else:
                            print("⚠️ Message mismatch")
                            return False
                    else:
                        print(f"❌ Extraction failed: {response.status_code} - {response.text}")
                        return False
            else:
                print(f"❌ Hide request failed: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Web test failed: {e}")
        return False


if __name__ == "__main__":
    test_web_video_steganography()