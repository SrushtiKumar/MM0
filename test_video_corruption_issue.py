#!/usr/bin/env python3
"""
Test video steganography corruption issues
"""

import os
import cv2
from final_video_steganography import FinalVideoSteganographyManager

def create_test_video():
    """Create a simple test video"""
    # Create a short test video
    width, height = 320, 240
    fps = 10
    duration = 2  # seconds
    
    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('test_video.avi', fourcc, fps, (width, height))
    
    total_frames = fps * duration
    
    for frame_num in range(total_frames):
        # Create a frame with changing colors
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Create a gradient effect
        color_value = int((frame_num / total_frames) * 255)
        frame[:, :] = [color_value, 255 - color_value, 128]
        
        # Add some text
        cv2.putText(frame, f'Frame {frame_num}', (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        out.write(frame)
    
    out.release()
    return 'test_video.avi'

def validate_video_file(video_path):
    """Validate if video file is properly formatted and playable"""
    
    print(f"🎬 VALIDATING VIDEO FILE: {video_path}")
    print("-" * 40)
    
    if not os.path.exists(video_path):
        print(f"❌ File does not exist")
        return False
    
    file_size = os.path.getsize(video_path)
    print(f"📏 File size: {file_size} bytes")
    
    if file_size == 0:
        print(f"❌ File is empty")
        return False
    
    try:
        # Test if OpenCV can read the video
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            print(f"❌ Cannot open video file")
            return False
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"📊 Video properties: {width}x{height}, {fps}fps, {frame_count} frames")
        
        if frame_count == 0:
            print(f"❌ No frames detected")
            cap.release()
            return False
        
        # Try to read first few frames
        frames_read = 0
        for i in range(min(5, frame_count)):
            ret, frame = cap.read()
            if ret:
                frames_read += 1
            else:
                break
        
        cap.release()
        
        print(f"📖 Successfully read {frames_read} frames")
        
        if frames_read > 0:
            print(f"✅ Video file is valid and playable")
            return True
        else:
            print(f"❌ Cannot read any frames")
            return False
            
    except Exception as e:
        print(f"❌ Video validation error: {e}")
        return False

def test_video_corruption_issue():
    """Test video steganography for corruption issues"""
    
    print("🧪 TESTING VIDEO STEGANOGRAPHY CORRUPTION")
    print("=" * 60)
    
    # Need numpy for video creation
    global np
    import numpy as np
    
    # Create test video
    video_file = create_test_video()
    secret_content = "Secret data hidden in video!"
    secret_file = "video_secret.txt"
    
    with open(secret_file, 'w') as f:
        f.write(secret_content)
    
    print(f"🎬 Created test video: {video_file}")
    
    # Validate original video
    print(f"\n📋 Original Video Validation:")
    original_valid = validate_video_file(video_file)
    
    if not original_valid:
        print(f"❌ Original video creation failed")
        return False
    
    try:
        # Test steganography
        stego = FinalVideoSteganographyManager("test123")
        output_file = "processed_video.avi"
        
        print(f"\n🔐 Embedding secret in video...")
        result = stego.hide_data(video_file, secret_file, output_file, is_file=True)
        
        if not result.get('success'):
            print(f"❌ Embedding failed: {result}")
            return False
        
        print(f"✅ Embedding successful")
        print(f"📊 Method: {result.get('method', 'unknown')}")
        
        # Validate processed video
        print(f"\n📋 Processed Video Validation:")
        processed_valid = validate_video_file(output_file)
        
        # Test extraction
        print(f"\n🔍 Testing extraction...")
        extraction_result = stego.extract_data(output_file)
        
        if extraction_result and isinstance(extraction_result, tuple):
            extracted_content, filename = extraction_result
            
            if isinstance(extracted_content, bytes):
                extracted_text = extracted_content.decode('utf-8')
            else:
                extracted_text = extracted_content
                
            if secret_content.strip() == extracted_text.strip():
                print(f"✅ Extraction successful - data preserved!")
                extraction_ok = True
            else:
                print(f"❌ Extraction data mismatch")
                print(f"   Expected: '{secret_content.strip()}'")
                print(f"   Got:      '{extracted_text.strip()}'")
                extraction_ok = False
        else:
            print(f"❌ Extraction failed: {extraction_result}")
            extraction_ok = False
        
        return processed_valid and extraction_ok
            
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        for file in [video_file, secret_file, "processed_video.avi"]:
            if os.path.exists(file):
                os.remove(file)

if __name__ == "__main__":
    success = test_video_corruption_issue()
    if success:
        print(f"\n🎉 VIDEO CORRUPTION TEST PASSED!")
    else:
        print(f"\n❌ VIDEO CORRUPTION TEST FAILED!")