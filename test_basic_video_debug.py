#!/usr/bin/env python3
"""
Test basic video text steganography
"""

import os
from video_steganography import VideoSteganographyManager

def test_basic_video_text_steganography():
    print("🎬 Testing Basic Video Text Steganography")
    
    # Check if we have a video file
    video_files = ['demo_video.mp4', 'test.mp4', 'sample.mp4', 'test_demo_video.mp4']
    input_file = None
    
    for video_file in video_files:
        if os.path.exists(video_file):
            input_file = video_file
            break
    
    if not input_file:
        print("❌ No video file found. Let's create a demo video")
        
        # Create demo video using OpenCV
        import cv2
        import numpy as np
        
        width, height = 320, 240  # Smaller for faster processing
        fps = 10
        frames = 30  # 3 seconds
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter('basic_demo_video.mp4', fourcc, fps, (width, height))
        
        for i in range(frames):
            # Create a simple colored frame
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            color = int(255 * (i / frames))
            frame[:, :] = [color, 128, 255 - color]
            out.write(frame)
        
        out.release()
        input_file = 'basic_demo_video.mp4'
        print(f"✅ Created basic demo video: {input_file}")
    
    print(f"📄 Using video file: {input_file}")
    
    # Test message
    test_message = "Hello Basic Video! This is a simple test."
    print(f"📝 Test message: '{test_message}'")
    
    # Create steganography manager
    video_manager = VideoSteganographyManager()
    
    # Create output directory
    os.makedirs('debug_outputs', exist_ok=True)
    output_path = os.path.join('debug_outputs', 'test_basic_video_output.mp4')
    
    try:
        print("\n🔒 HIDING TEXT MESSAGE IN VIDEO...")
        result = video_manager.hide_data(input_file, test_message, output_path)
        
        if result.get('success'):
            print(f"✅ Successfully hidden message in: {result.get('output_path', output_path)}")
            
            print("\n🔓 EXTRACTING TEXT MESSAGE FROM VIDEO...")
            extracted_data, filename = video_manager.extract_data(output_path)
            
            if extracted_data:
                # Convert bytes to text for comparison
                if isinstance(extracted_data, bytes):
                    extracted_message = extracted_data.decode('utf-8')
                else:
                    extracted_message = str(extracted_data)
                    
                print(f"✅ Successfully extracted: '{extracted_message}'")
                
                if extracted_message == test_message:
                    print("🎉 PERFECT MATCH! Basic video text steganography working correctly.")
                else:
                    print("⚠️ Message extracted but doesn't match exactly")
                    print(f"Original: '{test_message}'")
                    print(f"Extracted: '{extracted_message}'")
                    
                    # Check similarity
                    if test_message in extracted_message or extracted_message in test_message:
                        print("💡 Partial match found - likely working but with minor issues")
            else:
                print(f"❌ Extraction failed: No message returned")
        else:
            print(f"❌ Hiding failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_basic_video_text_steganography()