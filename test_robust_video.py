#!/usr/bin/env python3
"""
Test the robust video steganography implementation
"""

from robust_video_stego import RobustVideoSteganography, RobustVideoSteganographyManager
import cv2
import numpy as np
import os

def create_test_video(filename: str, width: int, height: int, frames: int = 10):
    """Create a test video with specified dimensions"""
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, 10.0, (width, height))
    
    for i in range(frames):
        # Create frame with some texture (not solid color)
        frame = np.random.randint(80, 180, (height, width, 3), dtype=np.uint8)
        # Add some structure to simulate real video
        frame[::4, :] = np.random.randint(100, 200, (frame[::4, :].shape), dtype=np.uint8)
        out.write(frame)
    
    out.release()
    print(f"Created test video: {filename} ({width}x{height}, {frames} frames)")

def test_robust_video():
    print("🎬 TESTING ROBUST VIDEO STEGANOGRAPHY")
    
    # Test different video sizes
    test_cases = [
        ("small", 200, 150, "Small video test"),     # 30K pixels
        ("medium", 400, 300, "Medium video test"),   # 120K pixels  
        ("large", 800, 600, "Large video test"),     # 480K pixels
        ("huge", 1200, 900, "Huge video test")       # 1.08M pixels
    ]
    
    for size_name, width, height, test_message in test_cases:
        print(f"\n{'='*60}")
        print(f"Testing {size_name.upper()} video ({width}x{height} = {width*height:,} pixels)")
        print(f"{'='*60}")
        
        video_file = f"test_{size_name}.mp4"
        output_file = f"test_{size_name}_output.mp4"
        
        try:
            # Create test video
            create_test_video(video_file, width, height, 15)
            
            # Test steganography
            stego = RobustVideoSteganography("test123")
            
            # Embed
            print(f"\n📝 Embedding: '{test_message}'")
            result = stego.embed_data(video_file, test_message, output_file)
            
            if result.get('success'):
                print(f"✅ Embedding successful")
                print(f"   Frames processed: {result['frames_processed']}")
                print(f"   Bits embedded: {result['bits_embedded']}")
                print(f"   Redundancy: {result['redundancy']}")
                
                # Extract
                print(f"\n🔍 Extracting...")
                extracted_data, filename = stego.extract_data(output_file)
                
                if extracted_data:
                    extracted_text = extracted_data.decode('utf-8')
                    print(f"✅ Extraction successful!")
                    print(f"   Original:  '{test_message}'")
                    print(f"   Extracted: '{extracted_text}'")
                    print(f"   Filename:  '{filename}'")
                    
                    if extracted_text == test_message:
                        print(f"🎉 {size_name.upper()} TEST PASSED!")
                    else:
                        print(f"❌ {size_name.upper()} TEST FAILED - Data mismatch")
                else:
                    print(f"❌ {size_name.upper()} TEST FAILED - No data extracted")
            else:
                print(f"❌ {size_name.upper()} TEST FAILED - Embedding failed: {result.get('error')}")
            
        except Exception as e:
            print(f"❌ {size_name.upper()} TEST ERROR: {e}")
        
        finally:
            # Cleanup
            for f in [video_file, output_file]:
                if os.path.exists(f):
                    os.remove(f)
    
    print(f"\n{'='*60}")
    print("ROBUST VIDEO STEGANOGRAPHY TESTING COMPLETE")
    print(f"{'='*60}")

def test_manager_interface():
    """Test the manager interface that will be used by the web app"""
    print(f"\n🔧 TESTING MANAGER INTERFACE")
    
    # Create test video and file
    test_video = "manager_test.mp4"
    test_file = "test_document.txt"
    output_video = "manager_output.mp4"
    
    # Create test file
    with open(test_file, 'w') as f:
        f.write("This is a test document for file embedding!")
    
    # Create test video
    create_test_video(test_video, 600, 400, 10)
    
    try:
        manager = RobustVideoSteganographyManager("manager_test")
        
        # Test file embedding
        print(f"\n📁 Testing file embedding...")
        result = manager.hide_data(test_video, test_file, output_video, is_file=True)
        
        if result.get('success'):
            print(f"✅ File embedding successful")
            
            # Test extraction
            print(f"\n📁 Testing file extraction...")
            extracted_data, filename = manager.extract_data(output_video)
            
            if extracted_data:
                extracted_text = extracted_data.decode('utf-8')
                print(f"✅ File extraction successful!")
                print(f"   Filename: {filename}")
                print(f"   Content: {extracted_text}")
                
                with open(test_file, 'r') as f:
                    original_content = f.read()
                
                if extracted_text == original_content:
                    print(f"🎉 MANAGER TEST PASSED!")
                else:
                    print(f"❌ MANAGER TEST FAILED - Content mismatch")
            else:
                print(f"❌ MANAGER TEST FAILED - No data extracted")
        else:
            print(f"❌ MANAGER TEST FAILED - Embedding failed")
    
    finally:
        # Cleanup
        for f in [test_video, test_file, output_video]:
            if os.path.exists(f):
                os.remove(f)

if __name__ == '__main__':
    test_robust_video()
    test_manager_interface()