#!/usr/bin/env python3
"""
Test file creation and download path handling
"""

from robust_video_stego import RobustVideoSteganographyManager
import cv2
import numpy as np
import os
from pathlib import Path

def test_file_creation():
    """Test that files are created where expected"""
    
    print("🔧 TESTING FILE CREATION AND PATHS")
    
    # Simulate the web app's file structure
    outputs_dir = Path("outputs")
    outputs_dir.mkdir(exist_ok=True)
    
    # Create a test video similar to what users upload
    test_video = "path_test_input.mp4"
    
    # Create test video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(test_video, fourcc, 10.0, (640, 480))
    
    for i in range(30):
        frame = np.random.randint(60, 200, (480, 640, 3), dtype=np.uint8)
        out.write(frame)
    out.release()
    
    # Simulate the job ID and output path that the web app would create
    job_id = "test-job-12345"
    container_filename = "file_example_MP4_640_3MG.mp4"
    output_filename = f"{job_id}_output_{container_filename}"
    output_path = outputs_dir / output_filename
    
    print(f"📁 Input video: {test_video}")
    print(f"📁 Expected output: {output_path}")
    
    try:
        # Test with robust video steganography
        manager = RobustVideoSteganographyManager("test123")
        
        test_message = "Testing file creation and path handling!"
        
        print(f"\n🔒 Hiding message in video...")
        result = manager.hide_data(test_video, test_message, str(output_path), is_file=False)
        
        if result.get('success'):
            actual_output = result.get('output_path')
            print(f"✅ Hiding successful!")
            print(f"   Expected path: {output_path}")
            print(f"   Actual path:   {actual_output}")
            print(f"   Paths match:   {str(output_path) == actual_output}")
            
            # Check if file actually exists
            if os.path.exists(actual_output):
                file_size = os.path.getsize(actual_output)
                print(f"   File exists:   YES ({file_size} bytes)")
                
                # Test extraction to verify it works
                print(f"\n🔓 Testing extraction...")
                extracted_data, filename = manager.extract_data(actual_output)
                
                if extracted_data:
                    extracted_text = extracted_data.decode('utf-8')
                    print(f"✅ Extraction successful!")
                    print(f"   Original:  '{test_message}'")
                    print(f"   Extracted: '{extracted_text}'")
                    
                    if extracted_text == test_message:
                        print(f"🎉 PATH AND FILE CREATION TEST PASSED!")
                    else:
                        print(f"❌ Data mismatch")
                else:
                    print(f"❌ Extraction failed")
            else:
                print(f"   File exists:   NO - This is the problem!")
                
                # Check if it was created somewhere else
                print(f"\n🔍 Searching for created files...")
                for ext in ['.mp4', '.avi']:
                    possible_path = str(output_path).replace('.mp4', ext)
                    if os.path.exists(possible_path):
                        print(f"   Found file at: {possible_path}")
        else:
            print(f"❌ Hiding failed: {result.get('error')}")
    
    finally:
        # Cleanup
        for f in [test_video, str(output_path)]:
            if os.path.exists(f):
                os.remove(f)
        
        # Clean up any other files that might have been created
        for f in outputs_dir.glob(f"{job_id}_*"):
            if f.exists():
                f.unlink()

if __name__ == '__main__':
    test_file_creation()