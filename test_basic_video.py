#!/usr/bin/env python3
"""
Test if the basic video steganography works with a smaller file
"""

from fast_video_stego import FastVideoSteganography
import cv2
import numpy as np
import os

def test_basic_functionality():
    print("🎬 TESTING BASIC VIDEO STEGANOGRAPHY FUNCTIONALITY")
    
    # Create a reasonable-sized test video (not too large)
    test_video = "basic_test.mp4"
    
    width, height = 400, 300  # 120K pixels (< 500K threshold for standard mode)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(test_video, fourcc, 5.0, (width, height))
    
    # Create frames with natural-looking content
    for i in range(5):
        frame = np.random.randint(80, 180, (height, width, 3), dtype=np.uint8)
        # Add some structure to make it more like real video
        frame[50:100, 50:100] = [255, 0, 0]  # Red block
        frame[150:200, 150:200] = [0, 255, 0]  # Green block
        out.write(frame)
    out.release()
    
    # Test with steganography
    stego = FastVideoSteganography("testpass123")
    
    test_data = "This is a basic functionality test!"
    output_video = "basic_output.mp4"
    
    print(f"📝 Testing with: '{test_data}'")
    print(f"📐 Video size: {width}x{height} = {width*height} pixels")
    
    # Embed
    result = stego.embed_data(test_video, test_data, output_video)
    print(f"Embed result: {result}")
    
    if result.get('success'):
        # Extract
        print(f"\n🔍 Extracting...")
        extracted_data, filename = stego.extract_data(output_video)
        
        if extracted_data:
            print(f"✅ SUCCESS! Extracted: '{extracted_data.decode('utf-8')}'")
            print(f"✅ Filename: {filename}")
            print(f"✅ Basic video steganography is working!")
        else:
            print("❌ Failed to extract from basic video")
    
    # Cleanup
    for f in [test_video, output_video]:
        if os.path.exists(f):
            os.remove(f)

if __name__ == '__main__':
    test_basic_functionality()