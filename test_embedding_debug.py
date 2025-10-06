#!/usr/bin/env python3
"""
Debug the embedding process step by step
"""

from fast_video_stego import FastVideoSteganography
import cv2
import numpy as np
import os

def detailed_debug():
    print("🔍 DETAILED EMBEDDING DEBUG")
    
    # Create test video with known pixel values
    test_video = "debug_simple.mp4"
    
    # Create a simple frame with specific red channel values
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(test_video, fourcc, 5.0, (100, 100))
    
    # Create frame with red channel = 128 (binary: 10000000)
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    frame[:, :, 2] = 128  # Red channel = 128
    frame[:, :, 1] = 64   # Green = 64  
    frame[:, :, 0] = 32   # Blue = 32
    
    # Write single frame
    out.write(frame)
    out.release()
    
    print(f"✅ Created simple test video")
    print(f"Original red channel value: 128 (binary: {128:08b})")
    
    # Test embedding manually
    stego = FastVideoSteganography("test")
    
    # Read the video back
    cap = cv2.VideoCapture(test_video)
    ret, original_frame = cap.read()
    cap.release()
    
    if ret:
        print(f"Original frame shape: {original_frame.shape}")
        print(f"Original pixel (0,0) red: {original_frame[0,0,2]} (binary: {original_frame[0,0,2]:08b})")
        
        # Test the embedding logic on a single pixel
        test_bits = [1, 0, 1, 1, 0, 1, 0, 1]  # Test pattern
        
        modified_frame = original_frame.copy()
        
        # Manually apply embedding logic to first few pixels
        bit_index = 0
        for y in range(0, min(4, 100), 2):
            for x in range(0, min(4, 100), 2):
                if bit_index < len(test_bits):
                    original_red = modified_frame[y, x, 2]
                    
                    if test_bits[bit_index] == 1:
                        new_red = original_red | 0x0F  # Set lower 4 bits
                    else:
                        new_red = original_red & 0xF0  # Clear lower 4 bits
                    
                    modified_frame[y, x, 2] = new_red
                    
                    print(f"Pixel ({y},{x}): {original_red:08b} -> {new_red:08b} (bit: {test_bits[bit_index]})")
                    bit_index += 1
        
        # Save the manually modified frame
        debug_output = "debug_manual.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(debug_output, fourcc, 5.0, (100, 100))
        out.write(modified_frame)
        out.release()
        
        # Read it back and see if changes persist
        print(f"\n🔍 Checking if changes persist after video compression...")
        cap = cv2.VideoCapture(debug_output)
        ret, compressed_frame = cap.read()
        cap.release()
        
        if ret:
            for y in range(0, min(4, 100), 2):
                for x in range(0, min(4, 100), 2):
                    original_red = original_frame[y, x, 2] 
                    modified_red = modified_frame[y, x, 2]
                    compressed_red = compressed_frame[y, x, 2]
                    
                    print(f"Pixel ({y},{x}): orig={original_red:08b} -> mod={modified_red:08b} -> compressed={compressed_red:08b}")
                    
                    # Check if the lower 4 bits survived compression
                    lower_bits = compressed_red & 0x0F
                    print(f"  Lower 4 bits after compression: {lower_bits:04b} (value: {lower_bits})")
    
    # Cleanup
    for f in [test_video, debug_output]:
        if os.path.exists(f):
            os.remove(f)

if __name__ == '__main__':
    detailed_debug()