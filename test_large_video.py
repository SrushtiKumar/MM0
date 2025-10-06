#!/usr/bin/env python3
"""
Test the robust large video approach
"""

from fast_video_stego import FastVideoSteganography
import cv2
import numpy as np
import os

def test_large_video_robust():
    print("🎬 TESTING LARGE VIDEO ROBUST APPROACH")
    
    # Create a LARGE test video (similar to 1920x1080)
    test_video = "large_test.mp4"
    
    width, height = 800, 600  # Smaller than 1920x1080 but still > 500K pixels (480K)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(test_video, fourcc, 5.0, (width, height))
    
    # Create frames with varied content (like real video)
    for i in range(5):
        frame = np.random.randint(50, 200, (height, width, 3), dtype=np.uint8)
        out.write(frame)
    out.release()
    
    # Test with steganography
    stego = FastVideoSteganography("test123")
    
    test_data = "This is a test for large video robustness!"
    output_video = "large_output.mp4"
    
    print(f"📝 Testing with: '{test_data}'")
    print(f"📐 Video size: {width}x{height} = {width*height} pixels")
    
    # Embed using the new robust method
    result = stego.embed_data(test_video, test_data, output_video)
    print(f"Embed result: {result}")
    
    if result.get('success'):
        # Extract
        print(f"\n🔍 Extracting...")
        extracted_data, filename = stego.extract_data(output_video)
        
        if extracted_data:
            print(f"✅ SUCCESS! Extracted: '{extracted_data.decode('utf-8')}'")
            print(f"✅ Filename: {filename}")
        else:
            print("❌ Failed to extract from large video")
    
    # Cleanup
    for f in [test_video, output_video]:
        if os.path.exists(f):
            os.remove(f)

if __name__ == '__main__':
    test_large_video_robust()