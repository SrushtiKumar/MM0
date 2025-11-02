#!/usr/bin/env python3
"""
Test video steganography for file corruption issues
"""

import os
import tempfile
import cv2
import numpy as np
from final_video_steganography import FinalVideoSteganographyManager

def create_test_video(path, duration_seconds=2, fps=10, width=320, height=240):
    """Create a test MP4 video file"""
    try:
        # Define codec and create VideoWriter
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(path, fourcc, fps, (width, height))
        
        # Generate frames
        total_frames = duration_seconds * fps
        for frame_num in range(total_frames):
            # Create a simple gradient frame
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Add some color variation based on frame number
            color_shift = (frame_num * 10) % 255
            frame[:, :] = [color_shift, 100, 200 - color_shift]
            
            # Add some pattern
            cv2.rectangle(frame, (50, 50), (width-50, height-50), (255, 255, 255), 2)
            cv2.putText(frame, f'Frame {frame_num}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            out.write(frame)
        
        out.release()
        print(f"✅ Created test video: {path}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create test video: {e}")
        return False

def test_video_integrity(video_path):
    """Test if video file can be opened and played"""
    try:
        # Try to open the video file
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            print(f"❌ Video file cannot be opened")
            return False
        
        # Check basic properties
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"✅ Video file readable: {frame_count} frames, {fps} fps, {width}x{height}")
        
        # Try to read a few frames
        frames_read = 0
        for i in range(min(5, frame_count)):  # Read first 5 frames or all if less
            ret, frame = cap.read()
            if ret:
                frames_read += 1
            else:
                break
        
        cap.release()
        
        if frames_read > 0:
            print(f"✅ Video file is valid and playable ({frames_read} frames read)")
            return True
        else:
            print(f"❌ Video file has no readable frames")
            return False
            
    except Exception as e:
        print(f"❌ Video file is corrupted: {e}")
        return False

def test_video_steganography():
    """Test video steganography for corruption issues"""
    
    print("🎬 Testing Video Steganography File Integrity")
    print("=" * 50)
    
    stego = FinalVideoSteganographyManager()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files
        carrier_video = os.path.join(temp_dir, "carrier.mp4")
        secret_file = os.path.join(temp_dir, "secret.txt")
        output_video = os.path.join(temp_dir, "stego_video.mp4")
        extract_dir = os.path.join(temp_dir, "extracted")
        
        # Create test video
        print("1️⃣ Creating test video file...")
        if not create_test_video(carrier_video):
            print("❌ Failed to create test video")
            return False
        
        # Create secret file
        print("2️⃣ Creating secret document...")
        secret_content = "This is secret video content!\nMultiple lines of hidden video data.\nLine 3 of secret video information."
        with open(secret_file, 'w') as f:
            f.write(secret_content)
        print(f"✅ Secret file created: {secret_file}")
        
        # Test original video integrity
        print("\n3️⃣ Testing original video integrity...")
        if not test_video_integrity(carrier_video):
            print("❌ Original video is already corrupted")
            return False
        
        # Test embedding
        print("\n4️⃣ Embedding secret in video...")
        try:
            result = stego.hide_data(carrier_video, secret_content, output_video)
            print(f"✅ Video embedding successful: {result}")
        except Exception as e:
            print(f"❌ Video embedding failed: {e}")
            return False
        
        # Test processed video integrity - THIS IS THE CRITICAL TEST
        print("\n5️⃣ Testing processed video integrity...")
        
        # Check if the actual output path is different (might be AVI instead of MP4)
        actual_output = result.get('output_path', output_video)
        print(f"🔍 Checking actual output file: {actual_output}")
        
        if not test_video_integrity(actual_output):
            print("❌ CORRUPTION DETECTED: Processed video file is corrupted!")
            return False
        
        print("✅ SUCCESS: Processed video file remains playable!")
        
        # Test extraction
        print("\n6️⃣ Testing extraction...")
        os.makedirs(extract_dir, exist_ok=True)
        
        try:
            extracted_content = stego.extract_data(actual_output)
            print(f"✅ Video extraction successful")
        except Exception as e:
            print(f"❌ Video extraction failed: {e}")
            return False
        
        # Verify content
        print("\n7️⃣ Verifying extracted content...")
        try:
            # Handle tuple return format (content, filename)
            if isinstance(extracted_content, tuple):
                actual_content = extracted_content[0].decode('utf-8') if isinstance(extracted_content[0], bytes) else extracted_content[0]
                filename = extracted_content[1]
                print(f"📄 Extracted filename: {filename}")
            else:
                actual_content = extracted_content
            
            if secret_content == actual_content:
                print("✅ SUCCESS: Extracted content matches original!")
                print(f"📝 Original: {repr(secret_content[:50])}...")
                print(f"📤 Extracted: {repr(actual_content[:50])}...")
            else:
                print("❌ Content mismatch")
                print(f"📝 Original: {repr(secret_content)}")
                print(f"📤 Extracted: {repr(actual_content)}")
                return False
                
        except Exception as e:
            print(f"❌ Content verification failed: {e}")
            return False
        
        print("\n🎉 VIDEO STEGANOGRAPHY SUCCESS!")
        print("✅ Video files remain playable after processing")
        print("✅ Hidden data is properly embedded and extracted")
        print("✅ No file corruption detected")
        return True

if __name__ == "__main__":
    success = test_video_steganography()
    if success:
        print("\n🎯 Video steganography is working without corruption!")
    else:
        print("\n❌ Video steganography has corruption issues")