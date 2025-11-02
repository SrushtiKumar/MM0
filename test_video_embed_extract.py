#!/usr/bin/env python3
"""
Simple test to verify video steganography embed and extract workflow
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from final_video_steganography import FinalVideoSteganographyManager

def test_video_steganography():
    """Test the complete video steganography workflow"""
    
    print("🎬 Testing Video Steganography End-to-End")
    print("=" * 50)
    
    # Check for test video files
    test_videos = ['clean_carrier.mp4', 'simple_test_video.mp4', 'direct_test_video.mp4', 'comprehensive_test_video.mp4']
    input_video = None
    
    for video in test_videos:
        if os.path.exists(video):
            input_video = video
            break
    
    if not input_video:
        print("📹 No existing test video found. Creating a demo video...")
        try:
            # Try to create a demo video using OpenCV
            import cv2
            import numpy as np
            
            # Create a simple test video
            input_video = "demo_test_video.mp4"
            width, height = 320, 240
            fps = 10
            duration = 3  # seconds
            frames = fps * duration
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(input_video, fourcc, fps, (width, height))
            
            for i in range(frames):
                # Create a simple frame with changing colors
                frame = np.zeros((height, width, 3), dtype=np.uint8)
                color = (i * 8 % 256, (i * 4) % 256, (i * 12) % 256)
                cv2.rectangle(frame, (0, 0), (width, height), color, -1)
                cv2.putText(frame, f"Frame {i}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                out.write(frame)
            
            out.release()
            print(f"✅ Created demo video: {input_video}")
            
        except ImportError:
            print("❌ OpenCV not available. Please ensure one of these files exists:")
            for video in test_videos:
                print(f"   - {video}")
            return False
        except Exception as e:
            print(f"❌ Failed to create demo video: {e}")
            return False
    
    print(f"📹 Using video file: {input_video}")
    
    # Test message
    test_message = "Hello from video steganography test! 🎬🔒"
    password = "test123"
    output_video = "test_output_with_message.avi"
    
    # Initialize manager
    manager = FinalVideoSteganographyManager(password)
    
    try:
        print(f"\n📝 Step 1: Embedding message into video...")
        print(f"   Message: '{test_message}'")
        print(f"   Password: '{password}'")
        
        # Embed the message
        result = manager.hide_data(input_video, test_message, output_video)
        
        if not result.get('success', False):
            error = result.get('error', 'Unknown error')
            print(f"❌ Embedding failed: {error}")
            return False
        
        actual_output = result.get('output_path', output_video)
        print(f"✅ Embedding successful!")
        print(f"   Output file: {actual_output}")
        print(f"   File size: {os.path.getsize(actual_output) / (1024*1024):.1f} MB")
        
        print(f"\n🔍 Step 2: Extracting message from video...")
        
        # Extract the message
        extracted_data, filename = manager.extract_data(actual_output)
        
        if not extracted_data:
            print(f"❌ Extraction failed: No data found")
            return False
        
        # Convert bytes to string if needed
        if isinstance(extracted_data, bytes):
            extracted_message = extracted_data.decode('utf-8')
        else:
            extracted_message = str(extracted_data)
        
        print(f"✅ Extraction successful!")
        print(f"   Extracted: '{extracted_message}'")
        print(f"   Original:  '{test_message}'")
        
        # Verify the message matches
        if extracted_message.strip() == test_message.strip():
            print(f"\n🎉 SUCCESS: Messages match perfectly!")
            
            # Cleanup
            if os.path.exists(actual_output):
                os.remove(actual_output)
                print(f"🧹 Cleaned up test output file")
            
            return True
        else:
            print(f"\n❌ FAILURE: Messages don't match!")
            print(f"   Expected: '{test_message}'")
            print(f"   Got:      '{extracted_message}'")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = test_video_steganography()
    print(f"\n{'='*50}")
    if success:
        print("🎉 Video steganography test PASSED!")
    else:
        print("❌ Video steganography test FAILED!")
    print(f"{'='*50}")
    
    sys.exit(0 if success else 1)