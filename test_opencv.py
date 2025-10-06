#!/usr/bin/env python3
"""
Simple Video Steganography Test
"""

import cv2
import numpy as np
import os

def test_opencv():
    """Test if OpenCV is working"""
    print("🔧 Testing OpenCV...")
    
    try:
        # Test basic video creation
        width, height = 320, 240
        fps = 10
        frames = 30
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter('test_simple.mp4', fourcc, fps, (width, height))
        
        print(f"Creating simple test video: {width}x{height}, {fps} fps, {frames} frames")
        
        for i in range(frames):
            # Create simple frame
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            frame[:, :, 0] = i * 8  # Red increases
            frame[:, :, 1] = 128   # Green constant
            frame[:, :, 2] = 255 - i * 8  # Blue decreases
            
            out.write(frame)
            
            if i % 10 == 0:
                print(f"  Frame {i}/{frames}")
        
        out.release()
        
        # Test reading the video
        cap = cv2.VideoCapture('test_simple.mp4')
        if cap.isOpened():
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            
            print(f"✅ Video created successfully:")
            print(f"   {width}x{height}, {fps} fps, {frame_count} frames")
            
            cap.release()
            return True
        else:
            print("❌ Failed to read created video")
            return False
            
    except Exception as e:
        print(f"❌ OpenCV test failed: {e}")
        return False

if __name__ == '__main__':
    if test_opencv():
        print("\n✅ OpenCV is working - video steganography should work!")
    else:
        print("\n❌ OpenCV issues detected - need to fix before video steganography")