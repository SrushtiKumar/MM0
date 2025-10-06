#!/usr/bin/env python3
"""
Debug the fast video steganography issue
"""

from fast_video_stego import FastVideoSteganography
import cv2
import os

def test_debug():
    print("🐛 DEBUGGING FAST VIDEO STEGANOGRAPHY")
    
    # Create a simple test video
    test_video = "debug_test.mp4"
    
    # Create a simple 10-frame video for testing
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(test_video, fourcc, 5.0, (320, 240))
    
    # Create 10 frames of solid color
    import numpy as np
    for i in range(10):
        frame = np.full((240, 320, 3), (100, 150, 200), dtype=np.uint8)
        out.write(frame)
    
    out.release()
    print(f"✅ Created test video: {test_video}")
    
    # Test steganography
    stego = FastVideoSteganography("test123")
    
    # Test with simple text
    test_data = "Hello World!"
    output_video = "debug_output.mp4"
    
    print(f"\n📝 Testing with: '{test_data}'")
    
    # Embed
    result = stego.embed_data(test_video, test_data, output_video)
    print(f"Embed result: {result}")
    
    if result.get('success'):
        # Extract
        print(f"\n🔍 Extracting from: {output_video}")
        extracted_data, filename = stego.extract_data(output_video)
        
        if extracted_data:
            print(f"✅ Extracted: '{extracted_data.decode('utf-8')}'")
            print(f"✅ Filename: {filename}")
        else:
            print("❌ No data extracted")
            
            # Debug: Let's manually check the first frame
            print("\n🔍 Manual frame analysis...")
            cap = cv2.VideoCapture(output_video)
            ret, frame = cap.read()
            if ret:
                print(f"Frame shape: {frame.shape}")
                
                # Check some pixels in the pattern
                print("Sample pixel values (red channel):")
                for y in range(0, min(10, frame.shape[0]), 2):
                    for x in range(0, min(10, frame.shape[1]), 2):
                        red_val = int(frame[y, x, 2])
                        lower_bits = red_val & 0x0F
                        print(f"  ({y},{x}): {red_val} -> {lower_bits:04b} -> {'1' if lower_bits >= 8 else '0'}")
                
            cap.release()
    
    # Cleanup
    if os.path.exists(test_video):
        os.remove(test_video)
    if os.path.exists(output_video):
        os.remove(output_video)

if __name__ == '__main__':
    test_debug()