#!/usr/bin/env python3
"""
Simple Video Steganography Test
"""

from video_steganography import VideoSteganographyManager
import cv2
import numpy as np

def create_small_test_video(filename="small_test.mp4"):
    """Create a small test video for quick testing"""
    width, height = 320, 240
    fps = 10
    frames = 20  # Just 2 seconds
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
    
    print(f"Creating small test video: {filename}")
    
    for i in range(frames):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:, :, 0] = (i * 10) % 256
        frame[:, :, 1] = 128
        frame[:, :, 2] = 255 - (i * 10) % 256
        
        # Add some pattern
        cv2.rectangle(frame, (50, 50), (150, 100), (255, 255, 255), 2)
        cv2.putText(frame, f"{i}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        out.write(frame)
    
    out.release()
    print(f"✅ Created {filename} with {frames} frames")
    return filename

def test_simple_video_steganography():
    """Test basic video steganography"""
    print("🎬 SIMPLE VIDEO STEGANOGRAPHY TEST 🎬\n")
    
    # Create small test video
    test_video = create_small_test_video()
    
    # Create manager
    manager = VideoSteganographyManager("test123")
    
    # Get video info
    info = manager.get_video_info(test_video)
    print(f"📹 Video Info:")
    print(f"  Resolution: {info['width']}x{info['height']}")
    print(f"  Frames: {info['total_frames']}")
    print(f"  Capacity: {info['max_capacity_bytes']} bytes")
    
    # Test with short message
    print(f"\n📝 Testing short message...")
    short_message = "Hello Video!"
    
    result = manager.hide_data(test_video, short_message, "stego_short.mp4")
    
    if result.get('success'):
        print(f"  ✅ Message embedded")
        
        # Extract
        extracted_data, filename = manager.extract_data("stego_short.mp4")
        if extracted_data:
            extracted_text = extracted_data.decode('utf-8')
            print(f"  ✅ Extracted: '{extracted_text}'")
            print(f"  ✅ Match: {'YES' if extracted_text == short_message else 'NO'}")
        else:
            print(f"  ❌ Extraction failed")
    else:
        print(f"  ❌ Embedding failed: {result.get('error')}")

if __name__ == '__main__':
    test_simple_video_steganography()