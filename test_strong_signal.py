#!/usr/bin/env python3
"""
Test the new strong signal approach
"""

from fast_video_stego import FastVideoSteganography
import cv2
import numpy as np
import os

def test_strong_signal():
    print("💪 TESTING STRONG SIGNAL APPROACH")
    
    # Create test video
    test_video = "strong_test.mp4"
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(test_video, fourcc, 5.0, (100, 100))
    
    # Create frame with mid-range red values (128)
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    frame[:, :, 2] = 128  # Red = 128
    frame[:, :, 1] = 64   # Green = 64
    frame[:, :, 0] = 32   # Blue = 32
    
    out.write(frame)
    out.release()
    
    # Test with fast video steganography
    stego = FastVideoSteganography("test123")
    
    test_data = "TEST123"
    output_video = "strong_output.mp4"
    
    print(f"📝 Testing with: '{test_data}'")
    
    # Embed using the new method
    result = stego.embed_data(test_video, test_data, output_video)
    print(f"Embed result: {result}")
    
    if result.get('success'):
        # Check the pixel values after embedding
        cap = cv2.VideoCapture(output_video)
        ret, embedded_frame = cap.read()
        cap.release()
        
        if ret:
            print(f"\n🔍 Checking embedded pixels:")
            for y in range(0, min(8, embedded_frame.shape[0]), 2):
                for x in range(0, min(8, embedded_frame.shape[1]), 2):
                    red_val = int(embedded_frame[y, x, 2])
                    print(f"  Pixel ({y},{x}): red = {red_val}")
                    
                    # Check what bit this would be decoded as
                    if red_val > 200:
                        bit = 1
                    elif red_val < 50:
                        bit = 0
                    else:
                        bit = "?"
                    print(f"    -> Decoded as: {bit}")
        
        # Extract
        print(f"\n🔍 Extracting...")
        extracted_data, filename = stego.extract_data(output_video)
        
        if extracted_data:
            print(f"✅ SUCCESS! Extracted: '{extracted_data.decode('utf-8')}'")
            print(f"✅ Filename: {filename}")
        else:
            print("❌ Still failed to extract")
    
    # Cleanup
    for f in [test_video, output_video]:
        if os.path.exists(f):
            os.remove(f)

if __name__ == '__main__':
    test_strong_signal()