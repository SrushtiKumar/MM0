#!/usr/bin/env python3
"""
Test the robust approach with truly large video
"""

from fast_video_stego import FastVideoSteganography
import cv2
import numpy as np
import os

def test_very_large_video():
    print("🎬 TESTING VERY LARGE VIDEO (>500K pixels)")
    
    # Create a truly LARGE test video (> 500K pixels)
    test_video = "huge_test.mp4"
    
    width, height = 1000, 800  # 800K pixels > 500K threshold
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(test_video, fourcc, 5.0, (width, height))
    
    # Create frames with varied content
    for i in range(3):
        frame = np.random.randint(50, 200, (height, width, 3), dtype=np.uint8)
        out.write(frame)
    out.release()
    
    # Test with steganography
    stego = FastVideoSteganography("test123")
    
    test_data = "Large video test with robust embedding!"
    output_video = "huge_output.mp4"
    
    print(f"📝 Testing with: '{test_data}'")
    print(f"📐 Video size: {width}x{height} = {width*height} pixels")
    
    # Embed using the robust method
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
            print("❌ Failed to extract from very large video")
    
    # Cleanup
    for f in [test_video, output_video]:
        if os.path.exists(f):
            os.remove(f)

if __name__ == '__main__':
    test_very_large_video()