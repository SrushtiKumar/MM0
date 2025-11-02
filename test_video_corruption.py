#!/usr/bin/env python3
"""
Test video steganography to identify corruption issues
"""

import os
import cv2
import numpy as np
from final_video_steganography import FinalVideoSteganographyManager

def create_test_video(filename="test_video.mp4", duration=3):
    """Create a simple test video"""
    
    # Create a simple test video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, 10.0, (640, 480))
    
    frames = duration * 10  # 10 FPS for 3 seconds = 30 frames
    
    for i in range(frames):
        # Create a frame with changing colors
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Gradient effect
        frame[:, :, 0] = (i * 8) % 256  # Red channel
        frame[:, :, 1] = (i * 12) % 256  # Green channel  
        frame[:, :, 2] = (i * 16) % 256  # Blue channel
        
        # Add some pattern
        cv2.rectangle(frame, (50 + i*5, 50 + i*3), (150 + i*5, 150 + i*3), (255, 255, 255), 2)
        
        out.write(frame)
    
    out.release()
    print(f"✅ Created test video: {filename} ({frames} frames)")
    return filename

def test_video_steganography():
    """Test video steganography processing"""
    
    print("🧪 TESTING VIDEO STEGANOGRAPHY")
    print("=" * 50)
    
    # Create test video
    input_video = create_test_video("test_input_video.mp4", duration=3)
    
    if not os.path.exists(input_video):
        print(f"❌ Failed to create test video: {input_video}")
        return False
    
    # Test data to hide
    test_data = "This is secret data hidden in video using steganography!"
    output_video = "test_output_video.mp4"
    
    try:
        # Test video steganography
        print(f"\n🔐 Testing video steganography...")
        print(f"   Input: {input_video}")
        print(f"   Output: {output_video}")
        print(f"   Data: {test_data}")
        
        manager = FinalVideoSteganographyManager("test123")
        
        # Hide data in video
        result = manager.hide_data(
            input_video, 
            test_data, 
            output_video,
            is_file=False
        )
        
        print(f"\n📊 Embedding result: {result}")
        
        if not result.get('success'):
            print(f"❌ Embedding failed: {result}")
            return False
        
        # Check actual output file
        actual_output = result.get('output_path', output_video)
        print(f"✅ Embedding successful!")
        print(f"   Expected output: {output_video}")
        print(f"   Actual output: {actual_output}")
        print(f"   File exists: {os.path.exists(actual_output)}")
        
        if not os.path.exists(actual_output):
            print(f"❌ Output file doesn't exist: {actual_output}")
            return False
        
        # Test if output video is playable
        print(f"\n🎬 Testing output video playability...")
        
        try:
            cap = cv2.VideoCapture(actual_output)
            
            if not cap.isOpened():
                print(f"❌ Cannot open output video: {actual_output}")
                cap.release()
                return False
            
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            print(f"✅ Output video is readable!")
            print(f"   Frames: {frame_count}")
            print(f"   FPS: {fps}")
            print(f"   Resolution: {width}x{height}")
            
            # Try to read a few frames
            frames_read = 0
            for i in range(min(5, frame_count)):
                ret, frame = cap.read()
                if ret:
                    frames_read += 1
                else:
                    break
            
            cap.release()
            
            if frames_read > 0:
                print(f"✅ Successfully read {frames_read} frames - Video is NOT corrupted!")
            else:
                print(f"❌ Cannot read any frames - Video IS corrupted!")
                return False
                
        except Exception as e:
            print(f"❌ Error testing video playability: {e}")
            return False
        
        # Test extraction
        print(f"\n🔍 Testing data extraction...")
        
        extraction_result = manager.extract_data(actual_output)
        
        if extraction_result and isinstance(extraction_result, tuple):
            extracted_data, filename = extraction_result
            
            if isinstance(extracted_data, bytes):
                extracted_text = extracted_data.decode('utf-8')
            else:
                extracted_text = extracted_data
            
            print(f"✅ Extraction successful!")
            print(f"   Filename: {filename}")
            print(f"   Extracted: {extracted_text}")
            
            if test_data.strip() == extracted_text.strip():
                print(f"✅ Extracted data matches original!")
                return True
            else:
                print(f"❌ Data mismatch!")
                print(f"   Original: {test_data}")
                print(f"   Extracted: {extracted_text}")
                return False
        else:
            print(f"❌ Extraction failed: {extraction_result}")
            return False
    
    finally:
        # Cleanup
        for file in [input_video, output_video, "test_output_video.avi"]:
            if os.path.exists(file):
                os.remove(file)
                print(f"🧹 Cleaned up: {file}")

if __name__ == "__main__":
    success = test_video_steganography()
    
    print(f"\n" + "=" * 50)
    if success:
        print(f"🎉 VIDEO STEGANOGRAPHY: WORKING CORRECTLY!")
        print(f"✅ No corruption detected")
        print(f"✅ Video remains playable")
        print(f"✅ Data extraction successful")
    else:
        print(f"❌ VIDEO STEGANOGRAPHY: ISSUES DETECTED!")
        print(f"⚠️  Video corruption or processing issues found")